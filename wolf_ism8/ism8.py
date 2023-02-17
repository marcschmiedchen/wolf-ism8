"""
Module for gathering info and sending commands from/to Wolf HVAC System via ISM8 adapter
"""

import logging
import asyncio

if __name__ != "__main__":
    from .ism8_constants import *


class Ism8(asyncio.Protocol):
    """
    This protocol class listens to message from ISM8 module and
    feeds data into internal data array. Also provides functionality for
    writing datapoints.
    """

    log = logging.getLogger(__name__)

    @staticmethod
    def get_datatype(dp_id: int):
        """returns python datatype allowed for datapoint"""
        ism_datatype = DATAPOINTS.get(dp_id, ["", "", "", "", ""])[IX_TYPE]
        return DATATYPES.get(ism_datatype, ["", "", "", "", ""])[DT_PYTHONTYPE]

    @staticmethod
    def get_step_value(dp_id: int):
        """returns step value for datapoint"""
        datatype = DATAPOINTS.get(dp_id, ["", "", "", "", ""])[IX_TYPE]
        return DATATYPES.get(datatype, ["", "", "", "", ""])[DT_STEP]

    @staticmethod
    def get_unit(dp_id: int):
        """returns unit for datapoint"""
        datatype = DATAPOINTS.get(dp_id, ["", "", "", "", ""])[IX_TYPE]
        return DATATYPES.get(datatype, ["", "", "", "", ""])[DT_UNIT]

    @staticmethod
    def get_all_sensors():
        """returns pointer to all possible values of ISM8 datapoints"""
        return DATAPOINTS

    @staticmethod
    def decode_HVACMode(input: int) -> str:
        return HVACModes.get(input, "unbekannter Modus")

    @staticmethod
    def encode_HVACMode(input: str) -> bytearray:
        for key in HVACModes:
            if HVACModes[key].lower() == input.lower().strip():
                return bytearray([key])
        Ism8.log.error("HVAC Mode %s is not valid", input)
        return bytearray()

    @staticmethod
    def decode_Scaling(input: int) -> float:
        # scale by 100/255 according to Docs
        return 100 / 255 * input

    @staticmethod
    def encode_Scaling(input: float) -> bytearray:
        # scale by 100/255 according to Docs
        return bytearray([round(input / (100 / 255))])

    @staticmethod
    def decode_DHWMode(input: int) -> str:
        return DHWModes.get(input, "unbekannter Modus")

    @staticmethod
    def encode_DHWMode(input: str) -> bytearray:
        for key in DHWModes:
            if DHWModes[key].lower() == input.lower().strip():
                return bytearray([key])
        Ism8.log.error("DHW mode %s is not valid", input)
        return bytearray()

    @staticmethod
    def decode_HVACContrMode(input: int) -> str:
        return HVACContrModes.get(input, "unbekannter Modus")

    @staticmethod
    def encode_HVACContrMode(input: str) -> bytearray:
        for key in HVACContrModes:
            if HVACContrModes[key].lower() == input.lower().strip():
                return bytearray([key])
        Ism8.log.error("HVAC Control mode %s is not valid", input)
        return bytearray()

    @staticmethod
    def decode_Bool(input: int) -> bool:
        # take 1st bit and cast to Bool
        return bool(input & 0b1)

    @staticmethod
    def encode_Bool(input: bool) -> bytearray:
        return bytearray([int(input)])

    @staticmethod
    def decode_Int(input: int) -> int:
        return int(input)

    @staticmethod
    def decode_ScaledInt(input: int) -> float:
        return float(0.0001 * input)

    @staticmethod
    def decode_Float(input: int) -> float:
        _sign = (input & 0b1000000000000000) >> 15
        _exponent = (input & 0b0111100000000000) >> 11
        _mantisse = input & 0b0000011111111111
        if _sign == 1:
            _mantisse = -(~(_mantisse - 1) & 0x07FF)
        decoded_float = float(0.01 * (2**_exponent) * _mantisse)
        Ism8.log.debug("decoded %s -> %s", input, decoded_float)
        return decoded_float

    @staticmethod
    def encode_Float(input: float) -> bytearray:
        input = round(input, 2)
        data = [0, 0]
        encoded_float = bytearray()
        _exponent = 0
        _mantisse_calc = round(abs(input) * 100)
        while _mantisse_calc.bit_length() > 11:
            _exponent += 1
            _mantisse_calc = round(_mantisse_calc / 2)
        _mantisse = round(input * 100 / (1 << _exponent))
        if input < 0:
            data[0] |= 0x80
            _mantisse = round((~(_mantisse * -1) + 1) & 0x07FF)
        data[0] |= (_exponent & 0x0F) << 3
        data[0] |= (_mantisse >> 8) & 0x7
        data[1] |= _mantisse & 0xFF
        for bit in data:
            encoded_float.append(bit)
        Ism8.log.debug("encoded %s -> %s", input, encoded_float)
        return encoded_float

    def __init__(self):
        self._dp_values = {}
        # the datapoint-values (IDs matching the list above) are stored here
        self._transport = None
        self._connected = False

    def factory(self):
        return self

    def request_all_datapoints(self):
        """send 'request all datapoints' to ISM8"""
        req_msg = bytearray(ISM_REQ_DP_MSG)
        Ism8.log.debug("Sending REQ_DP: %s ", self.__encode_bytes(req_msg))
        self._transport.write(req_msg)

    def connection_made(self, transport):
        """is called as soon as an ISM8 connects to server"""
        _peername = transport.get_extra_info("peername")
        Ism8.log.info("Connection from ISM8: %s", _peername)
        self._transport = transport
        self._connected = True

    def data_received(self, data):
        """is called whenever data is ready"""
        _header_ptr = 0
        msg_length = 0
        # Ism8.log.debug("Raw data received: %s", self.__encode_bytes(data))
        while _header_ptr < len(data):
            _header_ptr = data.find(ISM_HEADER, _header_ptr)
            if _header_ptr >= 0:
                if len(data[_header_ptr:]) >= 9:
                    # smallest processable data:
                    # hdr plus 5 bytes=>at least 9 bytes
                    msg_length = 256 * data[_header_ptr + 4] + data[_header_ptr + 5]
                    # msg_length comes in bytes 4 and 5
                else:
                    msg_length = len(data) + 1

            # 2 possible outcomes here: Buffer is to short for message=>abort
            # buffer is larger => than msg: process 1 message,
            # then continue loop
            if len(data) < _header_ptr + msg_length:
                Ism8.log.debug("Buffer shorter than expected / broken Message.")
                Ism8.log.debug("Discarding: %s ", data[_header_ptr:])
                # setting Ptr to end of data will end loop
                _header_ptr = len(data)
            else:
                # send ACK to ISM8 according to API: ISM Header,
                # then msg-length(17), then ACK w/ 2 bytes from original msg
                ack_msg = bytearray(ISM_ACK_DP_MSG)
                ack_msg[12] = data[_header_ptr + 12]
                ack_msg[13] = data[_header_ptr + 13]
                # Ism8.log.debug("Sending ACK: %s ", self.__encode_bytes(ack_msg))
                self._transport.write(ack_msg)
                # process message without header (first 10 bytes)
                self.process_msg(data[_header_ptr + 10 : _header_ptr + msg_length])

                # prepare to get next message; advance Ptr to next Msg
                _header_ptr += msg_length

    def process_msg(self, msg):
        """
        Processes received datagram(s) according to ISM8 API specification
        into message length, command, values delivered
        """
        # number of datapoints in message are coded into bytes 4 and 5
        max_dp = msg[4] * 256 + msg[5]
        # i keeps track of the bytes
        i = 0
        # loop over datapoint counter, until all dps are processed
        dp_ctr = 1
        while dp_ctr <= max_dp:
            # Ism8.log.debug("DP %d / %d in datagram:", dp_ctr, max_dp)
            dp_id = msg[i + 6] * 256 + msg[i + 7]
            # dp_command = msg[i + 8]
            # to be implemented for writing values to ISM8
            dp_length = msg[i + 9]
            dp_raw_value = bytearray(msg[i + 10 : i + 10 + dp_length])
            Ism8.log.debug(
                "Processing DP-ID %s, message: %s",
                dp_id,
                dp_raw_value,
            )
            self.extract_datapoint(dp_id, dp_raw_value)
            # now advance byte counter and datapoint counter
            dp_ctr += 1
            i = i + 10 + dp_length

    def extract_datapoint(self, dp_id: int, raw_bytes: bytearray) -> None:
        """
        receives raw bytes and decodes them according to ISM8-API data type
        """
        result = 0
        for single_byte in raw_bytes:
            result = result * 256 + int(single_byte)

        dp_type = "DPT_unknown"
        if dp_id in DATAPOINTS:
            dp_type = DATAPOINTS[dp_id][IX_TYPE]
        else:
            Ism8.log.error("unknown datapoint: %s, data:%s", dp_id, result)

        if dp_type in ("DPT_Switch", "DPT_Bool", "DPT_Enable", "DPT_OpenClose"):
            self._dp_values.update({dp_id: Ism8.decode_Bool(result)})

        elif dp_type in (
            "DPT_Value_Temp",
            "DPT_Value_Tempd",
            "DPT_Tempd",
            "DPT_Value_Pres",
            "DPT_Power",
            "DPT_Value_Volume_Flow",
        ):
            self._dp_values.update({dp_id: Ism8.decode_Float(result)})

        elif dp_type == "DPT_HVACMode":
            self._dp_values.update({dp_id: Ism8.decode_HVACMode(result)})

        elif dp_type == "DPT_Scaling":
            self._dp_values.update({dp_id: Ism8.decode_Scaling(result)})

        elif dp_type == "DPT_DHWMode":
            self._dp_values.update({dp_id: Ism8.decode_DHWMode(result)})

        elif dp_type == "DPT_HVACContrMode":
            self._dp_values.update({dp_id: Ism8.decode_HVACContrMode(result)})

        elif dp_type in ("DPT_ActiveEnergy", "DPT_ActiveEnergy_kWh"):
            self._dp_values.update({dp_id: Ism8.decode_Int(result)})
        else:
            Ism8.log.debug("datatype unknown, using INT: %s ", dp_type)
            self._dp_values.update({dp_id: Ism8.decode_Int(result)})
            return

        Ism8.log.debug(f"decoded DP {dp_id} {DATAPOINTS.get(dp_id)[1]} = {self._dp_values[dp_id]}")

    def validate_dp_value(self, dp_id: int, value) -> bool:
        """
        checks if value is valid for the datapoint before sending to ISM
        """
        if dp_id not in DATAPOINTS:
            Ism8.log.error("unknown datapoint: %s, value: %s", dp_id, value)
            return False
        if not DATAPOINTS[dp_id][IX_RW_FLAG]:
            Ism8.log.error("datapoint %s not writable", dp_id)
            return False

        ism_datatype = DATAPOINTS.get(dp_id, ["", "", "", "", ""])[IX_TYPE]
        python_datatype = DATATYPES.get(ism_datatype, ["", "", "", "", ""])[DT_PYTHONTYPE]
        if not isinstance(value, python_datatype):
            Ism8.log.error(
                "value has invalid datatype %s, valid datatype is %s",
                type(value),
                self.get_datatype(dp_id),
            )
            return False

        if type(value) != str:
            if value not in DP_VALUES_ALLOWED.get(dp_id):
                Ism8.log.error(
                    "value %d is out of range(%d)",
                    value,DP_VALUES_ALLOWED.get(dp_id)
                )
                return False
        return True

    def send_dp_value(self, dp_id: int, value) -> None:
        if not self.validate_dp_value(dp_id, value):
            return

        if not self._connected or self._transport is None:
            Ism8.log.error("No Connection to ISM8 Module")
            return
        dp_type = DATAPOINTS[dp_id][IX_TYPE]
        encoded_value = 0b0

        if dp_type in ("DPT_Switch", "DPT_Bool", "DPT_Enable", "DPT_OpenClose"):
            encoded_value = Ism8.encode_Bool(value)
        elif dp_type == "DPT_HVACMode":
            encoded_value = Ism8.encode_HVACMode(value)
        elif dp_type == "DPT_Scaling":
            encoded_value = Ism8.encode_Scaling(value)
        elif dp_type == "DPT_DHWMode":
            encoded_value = Ism8.encode_DHWMode(value)
        elif dp_type == "DPT_HVACContrMode":
            encoded_value = Ism8.encode_HVACContrMode(value)
        elif dp_type in (
            "DPT_Value_Temp",
            "DPT_Value_Tempd",
            "DPT_Tempd",
            "DPT_Value_Pres",
            "DPT_Power",
            "DPT_Value_Volume_Flow",
        ):
            encoded_value = Ism8.encode_Float(value)
        elif dp_type in ("DPT_ActiveEnergy", "DPT_ActiveEnergy_kWh"):
            encoded_value = Ism8.encode_Int(value)
        else:
            Ism8.log.error("datatype unknown, using INT: %s ", dp_type)
            encoded_value = Ism8.encode_Int(value)
        Ism8.log.debug("encoded DP %s : %s = %s\n", dp_id, value, encoded_value)

        # prepare frame with obj info
        update_msg = bytearray()
        update_msg.extend(ISM_HEADER)
        update_msg.extend((0).to_bytes(2, byteorder="big"))
        update_msg.extend(ISM_CONN_HEADER)
        update_msg.extend(ISM_SERVICE_TRANSMIT)
        update_msg.extend(dp_id.to_bytes(2, byteorder="big"))
        update_msg.extend((1).to_bytes(2, byteorder="big"))

        update_msg.extend(dp_id.to_bytes(2, byteorder="big"))
        update_msg.extend((0).to_bytes(1, byteorder="big"))
        update_msg.extend((len(encoded_value)).to_bytes(1, byteorder="big"))
        update_msg.extend(encoded_value)
        frame_size = len(update_msg).to_bytes(2, byteorder="big")
        update_msg[4] = frame_size[0]
        update_msg[5] = frame_size[1]

        # send message
        Ism8.log.debug(
            "send message dp %d from val %s to %s\n%s",
            dp_id,
            self.read(dp_id),
            value,
            self.__encode_bytes(update_msg),
        )
        self._transport.write(update_msg)

    def connection_lost(self, exc):
        """
        Is called when connection ends. closes socket.
        """
        Ism8.log.debug("ISM8 closed the connection.Stopping")
        self._connected = False
        self._transport.close()

    def read(self, dp_id):
        """
        Returns sensor value from private array of sensor-readings
        """
        if dp_id in self._dp_values.keys():
            return self._dp_values[dp_id]
        else:
            return None

    def __encode_bytes(self, msg: bytes) -> str:
        """encode the byte array too make it more readable"""
        msg_hex = msg.hex()
        n = 0
        ret = ""
        while n < len(msg_hex):
            ret += msg_hex[n]
            n += 1
            if (n % 2) == 0:
                ret += " "
        return ret.strip()


if __name__ == "__main__":
    from ism8_constants import *

    logging.basicConfig(level=logging.DEBUG)
    _LOGGER = logging.getLogger(__name__)

    # let the server print its debug logs, just for proof of concept
    my_ism8 = Ism8()
    for keys, values in my_ism8.get_all_sensors().items():
        _LOGGER.debug("%s:  %s" % (keys, values))

    _eventloop = asyncio.get_event_loop()
    coro = _eventloop.create_server(my_ism8.factory, "", 12004)
    _server = _eventloop.run_until_complete(coro)
    _LOGGER.debug("Waiting for ISM8 connection on %s", _server.sockets[0].getsockname())
    try:
        # Serve requests until Ctrl+C is pressed
        _eventloop.run_forever()
    except:
        pass
