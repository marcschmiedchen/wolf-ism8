
import datetime
from time import time

ISM_HEADER = b"\x06\x20\xf0\x80"
ISM_CONN_HEADER = b"\x04\x00\x00\x00"
ISM_SERVICE_RECEIVE = b"\xF0\x06"
ISM_SERVICE_ACK = b"\xF0\x86"
ISM_SERVICE_TRANSMIT = b"\xF0\xC1"
ISM_SERVICE_READ_ALL = b"\xF0\xD0"
ISM_ACK_DP_OBJ = b"\x00\x00" + b"\x00\x00" + b"\x00"
ISM_ACK_DP_MSG = (
    ISM_HEADER + b"\x00\x11" + ISM_CONN_HEADER + ISM_SERVICE_ACK + ISM_ACK_DP_OBJ
)
ISM_REQ_DP_MSG = ISM_HEADER + b"\x00\x16" + ISM_CONN_HEADER + ISM_SERVICE_READ_ALL
# constant byte arrays for creating ISM8 network messages
# Msg: ISM_HEADER || bytearray(LENGTH_MSG) || ISM_CONN_HEADER || ISM_SERVICE_XX ||

DEVICES = {
    "HG1": "Heizgeraet (1) TOB, CGB-2, MGK-2, COB-2 oder TGB-2",
    "HG2": "Heizgeraet (2) TOB, CGB-2, MGK-2, COB-2 oder TGB-2",
    "HG3": "Heizgeraet (3) TOB, CGB-2, MGK-2, COB-2 oder TGB-2",
    "HG4": "Heizgeraet (4) TOB, CGB-2, MGK-2, COB-2 oder TGB-2",
    "SYM": "Systembedienmodul",
    "DKW": "Direkter Heizkreis + direktes Warmwasser",
    "MK1": "Mischerkreis 1 + Warmwasser 1",
    "MK2": "Mischerkreis 2 + Warmwasser 2",
    "MK3": "Mischerkreis 3 + Warmwasser 3",
    "KM": "Kaskadenmodul",
    "MM1": "Mischermodule 1",
    "MM2": "Mischermodule 2",
    "MM3": "Mischermodule 3",
    "SM": "Solarmodul",
    "CWL": "CWL Excellent / CWL 2",
    "BWL": "Heizgeraet (1) BWL-1S oder CHA",
    "BM2": "BM-2 Bedienmodul",
}

IX_DEVICENAME = 0
# index of Wolf ISM main device name
IX_NAME = 1
# index of datapoint name
IX_TYPE = 2
# index of datapoint type (as described in Wolf API)
IX_RW_FLAG = 3
# index of R/W-flag (writing not implemented so far)

DATAPOINTS = {
    1: ("HG1", "Stoerung", "DPT_Switch", False),
    2: ("HG1", "Betriebsart", "DPT_HVACContrMode", False),
    3: ("HG1", "Brennerleistung", "DPT_Scaling", False),
    4: ("HG1", "Kesseltemperatur", "DPT_Value_Temp", False),
    5: ("HG1", "Sammlertemperatur", "DPT_Value_Temp", False),
    6: ("HG1", "Ruecklauftemperatur", "DPT_Value_Temp", False),
    7: ("HG1", "Warmwassertemperatur", "DPT_Value_Temp", False),
    8: ("HG1", "Aussentemperatur", "DPT_Value_Temp", False),
    9: ("HG1", "Status Brenner", "DPT_Switch", False),
    10: ("HG1", "Status Heizkreispumpe", "DPT_Switch", False),
    11: ("HG1", "Status Speicherladepumpe", "DPT_Switch", False),
    12: ("HG1", "Status 3W-Umschaltventil", "DPT_OpenClose", False),
    13: ("HG1", "Anlagendruck", "DPT_Value_Pres", False),
    14: ("HG2", "Stoerung", "DPT_Switch", False),
    15: ("HG2", "Betriebsart", "DPT_HVACContrMode", False),
    16: ("HG2", "Brennerleistung", "DPT_Scaling", False),
    17: ("HG2", "Kesseltemperatur", "DPT_Value_Temp", False),
    18: ("HG2", "Sammlertemperatur", "DPT_Value_Temp", False),
    19: ("HG2", "Ruecklauftemperatur", "DPT_Value_Temp", False),
    20: ("HG2", "Warmwassertemperatur", "DPT_Value_Temp", False),
    21: ("HG2", "Aussentemperatur", "DPT_Value_Temp", False),
    22: ("HG2", "Status Brenner", "DPT_Switch", False),
    23: ("HG2", "Status Heizkreispumpe", "DPT_Switch", False),
    24: ("HG2", "Status Speicherladepumpe", "DPT_Switch", False),
    25: ("HG2", "Status 3W-Umschaltventil", "DPT_OpenClose", False),
    26: ("HG2", "Anlagendruck", "DPT_Value_Pres", False),
    27: ("HG3", "Stoerung", "DPT_Switch", False),
    28: ("HG3", "Betriebsart", "DPT_HVACContrMode", False),
    29: ("HG3", "Brennerleistung", "DPT_Scaling", False),
    30: ("HG3", "Kesseltemperatur", "DPT_Value_Temp", False),
    31: ("HG3", "Sammlertemperatur", "DPT_Value_Temp", False),
    32: ("HG3", "Ruecklauftemperatur", "DPT_Value_Temp", False),
    33: ("HG3", "Warmwassertemperatur", "DPT_Value_Temp", False),
    34: ("HG3", "Aussentemperatur", "DPT_Value_Temp", False),
    35: ("HG3", "Status Brenner", "DPT_Switch", False),
    36: ("HG3", "Status Heizkreispumpe", "DPT_Switch", False),
    37: ("HG3", "Status Speicherladepumpe", "DPT_Switch", False),
    38: ("HG3", "Status 3W-Umschaltventil", "DPT_OpenClose", False),
    39: ("HG3", "Anlagendruck", "DPT_Value_Pres", False),
    40: ("HG4", "Stoerung", "DPT_Switch", False),
    41: ("HG4", "Betriebsart", "DPT_HVACContrMode", False),
    42: ("HG4", "Brennerleistung", "DPT_Scaling", False),
    43: ("HG4", "Kesseltemperatur", "DPT_Value_Temp", False),
    44: ("HG4", "Sammlertemperatur", "DPT_Value_Temp", False),
    45: ("HG4", "Ruecklauftemperatur", "DPT_Value_Temp", False),
    46: ("HG4", "Warmwassertemperatur", "DPT_Value_Temp", False),
    47: ("HG4", "Aussentemperatur", "DPT_Value_Temp", False),
    48: ("HG4", "Status Brenner", "DPT_Switch", False),
    49: ("HG4", "Status Heizkreispumpe", "DPT_Switch", False),
    50: ("HG4", "Status Speicherladepumpe", "DPT_Switch", False),
    51: ("HG4", "Status 3W-Umschaltventil", "DPT_OpenClose", False),
    52: ("HG4", "Anlagendruck", "DPT_Value_Pres", False),
    53: ("SYM", "Stoerung", "DPT_Switch", False),
    54: ("SYM", "Aussentemperatur", "DPT_Value_Temp", False),
    55: ("DKW", "Raumtemperatur", "DPT_Value_Temp", False),
    56: ("DKW", "Warmwassersolltemperatur", "DPT_Value_Temp", True),
    57: ("DKW", "Programmwahl Heizkreis", "DPT_HVACMode", True),
    58: ("DKW", "Programmwahl Warmwasser", "DPT_DHWMode", True),
    59: ("DKW", "Heizkreis Zeitprogramm 1", "DPT_Switch", True),
    60: ("DKW", "Heizkreis Zeitprogramm 2", "DPT_Switch", True),
    61: ("DKW", "Heizkreis Zeitprogramm 3", "DPT_Switch", True),
    62: ("DKW", "Warmwasser Zeitprogramm 1", "DPT_Switch", True),
    63: ("DKW", "Warmwasser Zeitprogramm 2", "DPT_Switch", True),
    64: ("DKW", "Warmwasser Zeitprogramm 3", "DPT_Switch", True),
    65: ("DKW", "Sollwertkorrektur", "DPT_Tempd", True),
    66: ("DKW", "Sparfaktor", "DPT_Tempd", True),
    67: ("MK1", "Stoerung", "DPT_Switch", False),
    68: ("MK1", "Raumtemperatur", "DPT_Value_Temp", False),
    69: ("MK1", "Warmwassersolltemperatur", "DPT_Value_Temp", True),
    70: ("MK1", "Programmwahl Mischer", "DPT_HVACMode", True),
    71: ("MK1", "Programmwahl Warmwasser", "DPT_DHWMode", True),
    72: ("MK1", "Mischer Zeitprogramm 1", "DPT_Switch", True),
    73: ("MK1", "Mischer Zeitprogramm 2", "DPT_Switch", True),
    74: ("MK1", "Mischer Zeitprogramm 3", "DPT_Switch", True),
    75: ("MK1", "Warmwasser Zeitprogramm 1", "DPT_Switch", True),
    76: ("MK1", "Warmwasser Zeitprogramm 2", "DPT_Switch", True),
    77: ("MK1", "Warmwasser Zeitprogramm 3", "DPT_Switch", True),
    78: ("MK1", "Sollwertkorrektur", "DPT_Tempd", True),
    79: ("MK1", "Sparfaktor", "DPT_Tempd", True),
    80: ("MK2", "Stoerung", "DPT_Switch", False),
    82: ("MK2", "Warmwassersolltemperatur", "DPT_Value_Temp", True),
    83: ("MK2", "Programmwahl Mischer", "DPT_HVACMode", True),
    84: ("MK2", "Programmwahl Warmwasser", "DPT_DHWMode", True),
    85: ("MK2", "Mischer Zeitprogramm 1", "DPT_Switch", True),
    86: ("MK2", "Mischer Zeitprogramm 2", "DPT_Switch", True),
    87: ("MK2", "Mischer Zeitprogramm 3", "DPT_Switch", True),
    88: ("MK2", "Warmwasser Zeitprogramm 1", "DPT_Switch", True),
    89: ("MK2", "Warmwasser Zeitprogramm 2", "DPT_Switch", True),
    90: ("MK2", "Warmwasser Zeitprogramm 3", "DPT_Switch", True),
    91: ("MK2", "Sollwertkorrektur", "DPT_Tempd", True),
    92: ("MK2", "Sparfaktor", "DPT_Tempd", True),
    94: ("MK3", "Raumtemperatur", "DPT_Value_Temp", False),
    95: ("MK3", "Warmwassersolltemperatur", "DPT_Value_Temp", True),
    96: ("MK3", "Programmwahl Mischer", "DPT_HVACMode", True),
    97: ("MK3", "Programmwahl Warmwasser", "DPT_DHWMode", True),
    98: ("MK3", "Mischer Zeitprogramm 1", "DPT_Switch", True),
    99: ("MK3", "Mischer Zeitprogramm 2", "DPT_Switch", True),
    100: ("MK3", "Mischer Zeitprogramm 3", "DPT_Switch", True),
    101: ("MK3", "Warmwasser Zeitprogramm 1", "DPT_Switch", True),
    102: ("MK3", "Warmwasser Zeitprogramm 2", "DPT_Switch", True),
    103: ("MK3", "Warmwasser Zeitprogramm 3", "DPT_Switch", True),
    104: ("MK3", "Sollwertkorrektur", "DPT_Tempd", True),
    105: ("MK3", "Sparfaktor", "DPT_Tempd", True),
    106: ("KM", "Stoerung", "DPT_Switch", False),
    107: ("KM", "Sammlertemperatur", "DPT_Value_Temp", False),
    108: ("KM", "Gesamtmodulationsgrad", "DPT_Scaling", False),
    109: ("KM", "Vorlauftemperatur Mischer", "DPT_Value_Temp", False),
    110: ("KM", "Status Mischerkreispumpe", "DPT_Switch", False),
    111: ("KM", "Status Ausgang A1", "DPT_Enable", False),
    112: ("KM", "Eingang E1", "DPT_Value_Temp", False),
    113: ("KM", "Eingang E2", "DPT_Value_Temp", False),
    114: ("MM1", "Stoerung", "DPT_Switch", False),
    115: ("MM1", "Warmwassertemperatur", "DPT_Value_Temp", False),
    116: ("MM1", "Vorlauftemperatur Mischer", "DPT_Value_Temp", False),
    117: ("MM1", "Status Mischerkreispumpe", "DPT_Switch", False),
    118: ("MM1", "Status Ausgang A1", "DPT_Enable", False),
    119: ("MM1", "Eingang E1", "DPT_Value_Temp", False),
    120: ("MM1", "Eingang E2", "DPT_Value_Temp", False),
    121: ("MM2", "Stoerung", "DPT_Switch", False),
    122: ("MM2", "Warmwassertemperatur", "DPT_Value_Temp", False),
    123: ("MM2", "Vorlauftemperatur Mischer", "DPT_Value_Temp", False),
    124: ("MM2", "Status Mischerkreispumpe", "DPT_Switch", False),
    125: ("MM2", "Status Ausgang A1", "DPT_Enable", False),
    126: ("MM2", "Eingang E1", "DPT_Value_Temp", False),
    127: ("MM2", "Eingang E2", "DPT_Value_Temp", False),
    128: ("MM3", "Stoerung", "DPT_Switch", False),
    129: ("MM3", "Warmwassertemperatur", "DPT_Value_Temp", False),
    130: ("MM3", "Vorlauftemperatur Mischer", "DPT_Value_Temp", False),
    131: ("MM3", "Status Mischerkreispumpe", "DPT_Switch", False),
    132: ("MM3", "Status Ausgang A1", "DPT_Enable", False),
    133: ("MM3", "Eingang E1", "DPT_Value_Temp", False),
    134: ("MM3", "Eingang E2", "DPT_Value_Temp", False),
    135: ("SM", "Stoerung", "DPT_Switch", False),
    136: ("SM", "Warmwassertemperatur Solar 1", "DPT_Value_Temp", False),
    137: ("SM", "Temperatur Kollektor 1", "DPT_Value_Temp", False),
    138: ("SM", "Eingang E1", "DPT_Value_Temp", False),
    139: ("SM", "Eingang E2 (Durchfluss)", "DPT_Value_Volume_Flow", False),
    140: ("SM", "Eingang E3", "DPT_Value_Temp", False),
    141: ("SM", "Status Solarkreispumpe SKP1", "DPT_Switch", False),
    142: ("SM", "Status Ausgang A1", "DPT_Enable", False),
    143: ("SM", "Status Ausgang A2", "DPT_Enable", False),
    144: ("SM", "Status Ausgang A3", "DPT_Enable", False),
    145: ("SM", "Status Ausgang A4", "DPT_Enable", False),
    146: ("SM", "Durchfluss", "DPT_Value_Volume_Flow", False),
    147: ("SM", "aktuelle Leistung", "DPT_Power", False),
    148: ("CWL", "Stoerung", "DPT_Switch", False),
    149: ("CWL", "Programm", "DPT_DHWMode", True),
    150: ("CWL", "Zeitprogramm 1", "DPT_Switch", True),
    151: ("CWL", "Zeitprogramm 2", "DPT_Switch", True),
    152: ("CWL", "Zeitprogramm 3", "DPT_Switch", True),
    153: ("CWL", "Intensivlueftung AN_AUS", "DPT_Switch", True),
    154: ("CWL", "Intensivlueftung Startdatum", "DPT_Date", True),
    155: ("CWL", "Intensivlueftung Enddatum", "DPT_Date", True),
    156: ("CWL", "Intensivlueftung Startzeit", "DPT_TimeOfDay", True),
    157: ("CWL", "Intensivlueftung Endzeit", "DPT_TimeOfDay", True),
    158: ("CWL", "Zeitw. Feuchteschutz AN_AUS", "DPT_Switch", True),
    159: ("CWL", "Zeitw. Feuchteschutz Startdatum", "DPT_Date", True),
    160: ("CWL", "Zeitw. Feuchteschutz Enddatum", "DPT_Date", True),
    161: ("CWL", "Zeitw. Feuchteschutz Startzeit", "DPT_TimeOfDay", True),
    162: ("CWL", "Zeitw. Feuchteschutz Endzeit", "DPT_TimeOfDay", True),
    163: ("CWL", "Lueftungsstufe", "DPT_Scaling", False),
    164: ("CWL", "Ablufttemperatur", "DPT_Value_Temp", False),
    165: ("CWL", "Frischlufttemperatur", "DPT_Value_Temp", False),
    166: ("CWL", "Durchsatz Zuluft", "DPT_FlowRate_m3/h", False),
    167: ("CWL", "Durchsatz Abluft", "DPT_FlowRate_m3/h", False),
    168: ("CWL", "Bypass Initialisierung", "DPT_Bool", False),
    169: ("CWL", "Bypass oeffnet_offen", "DPT_Bool", False),
    170: ("CWL", "Bypass schliesst_geschlossen", "DPT_Bool", False),
    171: ("CWL", "Bypass Fehler", "DPT_Bool", False),
    172: ("CWL", "Frost Status: Init_Warte", "DPT_Bool", False),
    173: ("CWL", "Frost Status: Kein Frost", "DPT_Bool", False),
    174: ("CWL", "Frost Status: Vorwaermer", "DPT_Bool", False),
    175: ("CWL", "Frost Status: Fehler", "DPT_Bool", False),
    176: ("BWL", "Stoerung", "DPT_Switch", False),
    177: ("BWL", "Betriebsart", "DPT_HVACContrMode", False),
    178: ("BWL", "Heizleistung", "DPT_Power", False),
    179: ("BWL", "Kuehlleistung", "DPT_Power", False),
    180: ("BWL", "Kesseltemperatur", "DPT_Value_Temp", False),
    181: ("BWL", "Sammlertemperatur", "DPT_Value_Temp", False),
    182: ("BWL", "Ruecklauftemperatur", "DPT_Value_Temp", False),
    183: ("BWL", "Warmwassertemperatur", "DPT_Value_Temp", False),
    184: ("BWL", "Aussentemperatur", "DPT_Value_Temp", False),
    185: ("BWL", "Status Heizkreispumpe", "DPT_Switch", False),
    186: ("BWL", "Status Aux-Pumpe", "DPT_Switch", False),
    187: ("BWL", "3W-Umschaltventil HZ_WW", "DPT_OpenClose", False),
    188: ("BWL", "3W-Umschaltventil HZ_K", "DPT_OpenClose", False),
    189: ("BWL", "Status E-Heizung", "DPT_Switch", False),
    190: ("BWL", "Anlagendruck", "DPT_Value_Pres", False),
    191: ("BWL", "Leistungsaufnahme", "DPT_Power", False),
    192: ("CWL", "Filterwarnung aktiv", "DPT_Switch", False),
    193: ("CWL", "Filterwarnung zuruecksetzen", "DPT_Switch", True),
    194: ("SYM", "1x Warmwasserladung (gobal)", "DPT_Switch", True),
    195: ("SM", "Tagesertrag", "DPT_ActiveEnergy", False),
    196: ("SM", "Gesamtertrag", "DPT_ActiveEnergy_kWh", False),
    197: ("HG1", "Abgastemperatur", "DPT_Value_Temp", False),
    198: ("HG1", "Leistungsvorgabe", "DPT_Scaling", True),
    199: ("HG1", "Kesseltemperaturvorgabe", "DPT_Value_Temp", True),
    200: ("HG2", "Abgastemperatur", "DPT_Value_Temp", False),
    201: ("HG2", "Leistungsvorgabe", "DPT_Scaling", True),
    202: ("HG2", "Kesseltemperaturvorgabe", "DPT_Value_Temp", True),
    203: ("HG3", "Abgastemperatur", "DPT_Value_Temp", False),
    204: ("HG3", "Leistungsvorgabe", "DPT_Scaling", True),
    205: ("HG3", "Kesseltemperaturvorgabe", "DPT_Value_Temp", True),
    206: ("HG4", "Abgastemperatur", "DPT_Value_Temp", False),
    207: ("HG4", "Leistungsvorgabe", "DPT_Scaling", True),
    208: ("HG4", "Kesseltemperaturvorgabe", "DPT_Value_Temp", True),
    209: ("KM", "Gesamtmodulationsgradvorgabe", "DPT_Scaling", True),
    210: ("KM", "Sammlertemperaturvorgabe", "DPT_Value_Temp", True),
    211: ("KM", "Betriebsart Heizen/Kuehlen", "DPT_Switch", False),
    251: ("BM2", "Erkennung Heiz-/ Mischerkreise", "DPT_Value_1_Ucount", False),
    346: ("CWL", "undokumentiert_346", "DPT_unknown", False),
    349: ("CWL", "undokumentiert_349", "DPT_unknown", False),
    351: ("CWL", "undokumentiert_351", "DPT_unknown", False),
    350: ("CWL", "undokumentiert_351", "DPT_unknown", False),
    352: ("CWL", "undokumentiert_352", "DPT_unknown", False),
    353: ("CWL", "undokumentiert_353", "DPT_unknown", False),
    354: ("CWL", "undokumentiert_354", "DPT_unknown", False),
    355: ("BM2", "Erkennung verfuegbarer Geraete 1", "DPT_Value_2_Ucount", False),
    356: ("BM2", "Erkennung verfuegbarer Geraete 2", "DPT_Value_2_Ucount", False),
    357: (
        "BM2",
        "Unterscheidung Heizgeraetetyp (HG1)",
        "DPT_Value_1_Ucount",
        False,
    ),
    358: ("BM2", "Erkennung Warmwasserkreise", "DPT_Value_1_Ucount", False),
    359: (
        "BM2",
        "Unterscheidung Heizgeraetetyp (HG2)",
        "DPT_Value_1_Ucount",
        False,
    ),
    360: (
        "BM2",
        "Unterscheidung Heizgeraetetyp (HG3)",
        "DPT_Value_1_Ucount",
        False,
    ),
    361: (
        "BM2",
        "Unterscheidung Heizgeraetetyp (HG4)",
        "DPT_Value_1_Ucount",
        False,
    ),
    364: ("HG1", "Kesselsolltemperatur HG1 - lesen", "DPT_Value_Temp", False),
    365: ("HG1", "Kesselsolltemperatur HG2 - lesen", "DPT_Value_Temp", False),
    366: ("HG1", "Kesselsolltemperatur HG3 - lesen", "DPT_Value_Temp", False),
    367: ("HG1", "Kesselsolltemperatur HG4 - lesen", "DPT_Value_Temp", False),
    368: ("BM2", "Vorlaufsolltemperatur dir. HK - lesen", "DPT_Value_Temp", False),
    369: ("BM2", "Mischersolltemperatur MK1 - lesen ", "DPT_Value_Temp", False),
    370: ("BM2", "Mischersolltemperatur MK2 - lesen ", "DPT_Value_Temp", False),
    371: ("BM2", "Mischersolltemperatur MK3 - lesen ", "DPT_Value_Temp", False),
    372: ("SYM", "Zuletzt aktiver Stoercode", "DPT_Value_1_Ucount", False),
}

IX_VALUE_AREA = 1
# index of datapoint value area according to ism8 api, if applicable

DP_VALUES_ALLOWED = {
    56: tuple(range(20, 81, 1)),
    57: tuple(range(0, 4, 1)),
    58: tuple(range(0, 5, 2)),
    59: (0, 1),
    60: (0, 1),
    61: (0, 1),
    62: (0, 1),
    63: (0, 1),
    64: (0, 1),
    65: tuple(range(-40, 45, 5)),
    66: tuple(range(0, 105, 5)),
    69: tuple(range(20, 81, 1)),
    70: tuple(range(0, 4, 1)),
    71: tuple(range(0, 5, 2)),
    72: (0, 1),
    73: (0, 1),
    74: (0, 1),
    74: (0, 1),
    75: (0, 1),
    76: (0, 1),
    77: (0, 1),
    78: tuple([(i / 10) for i in range(-40, 45, 5)]),
    79: tuple([(i / 10) for i in range(0, 105, 5)]),
    82: tuple(range(20, 81, 1)),
    83: tuple(range(0, 4, 1)),
    84: tuple(range(0, 5, 2)),
    85: (0, 1),
    86: (0, 1),
    87: (0, 1),
    88: (0, 1),
    89: (0, 1),
    90: (0, 1),
    91: tuple(range(-40, 45, 5)),
    92: tuple(range(0, 105, 5)),
    95: tuple(range(20, 81, 1)),
    96: tuple(range(0, 4, 1)),
    97: tuple(range(0, 5, 2)),
    98: (0, 1),
    99: (0, 1),
    100: (0, 1),
    101: (0, 1),
    102: (0, 1),
    103: (0, 1),
    104: (0, 1),
    105: (0, 1),
    149: (0, 1, 3),
    150: (0, 1),
    151: (0, 1),
    152: (0, 1),
    153: (0, 1),
    158: (0, 1),
    193: (0, 1),
    194: (0, 1),
}

DT_MIN = 0
# index of min value allowed by datatype according to ism8 doc
DT_MAX = 1
# index of max value allowed by datatype according to ism8 doc
DT_TYPE = 2
# index of python datatype
DT_STEP = 3
# index of step value according to ism8 doc
DT_UNIT = 4
# index of datatype unit according to ism8 doc

DATATYPES = {
    "DPT_Switch": (0, 1, int, 1, None),
    "DPT_Bool": (0, 1, int, 1, None),
    "DPT_Enable": (0, 1, int, 1, None),
    "DPT_OpenClose": (0, 1, int, 1, None),
    "DPT_Scaling": (0.00, 100.00, float, 100 / 255, "%"),
    "DPT_Value_Temp": (-273.00, 670760.00, float, 1 / 100, "C"),
    "DPT_Value_Tempd": (-670760.00, 670760.00, float, 1 / 100, "K"),
    "DPT_Tempd": (-670760.00, 670760.00, float, 1 / 100, "K"),
    "DPT_Value_Pres": (0, 670760.00, float, 1 / 100, "Pa"),
    "DPT_Power": (-670760.00, 670760.00, float, 1 / 100, "kW"),
    "DPT_Value_Volume_Flow": (-670760.00, 670760.00, float, 1 / 100, "l/h"),
    "DPT_TimeOfDay": (None, None, type(time), None, None),
    "DPT_Date": (None, None, datetime, None, None),
    "DPT_Value_1_Ucount": (0, 255, int, 1, None),
    "DPT_Value_2_Ucount": (0, 65535, int, 1, None),
    "DPT_FlowRate_m3/h": (-2147483647, 2147483647, int, 1 / 10000, "m3/h"),
    "DPT_HVACMode": (0, 4, int, 1, None),
    "DPT_DHWMode": (0, 4, int, 1, None),
    "DPT_HVACContrMode": (0, 20, int, 1, None),
}

HVACModes = {
    0: "Auto",
    1: "Comfort",
    2: "Standby",
    3: "Economy",
    4: "Building Protection",
}

HVACContrModes = {
    0: "Auto",
    1: "Heat",
    2: "Morning Warmup",
    3: "Cool",
    4: "Night Purge",
    5: "Precool",
    6: "Off",
    7: "Test",
    8: "Emergency Heat",
    9: "Fan Only",
    10: "Free Cool",
    11: "Ice",
    12: "Maximum Heating Mode",
    13: "Economic Heat/Cool Mode",
    14: "Dehumidification",
    15: "Calibration Mode",
    16: "Emergency Cool Mode",
    17: "Emergency Steam Mode",
    20: "NoDem",
}

DHWModes = {0: "Auto", 1: "LegioProtect", 2: "Normal", 3: "Reduced", 4: "Off"}