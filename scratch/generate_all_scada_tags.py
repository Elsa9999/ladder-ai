# -*- coding: utf-8 -*-
"""
generate_all_scada_tags.py
Sinh HMI Tags XML + PLC Tags XML cho tất cả 5 màn hình scadabai3→7
Tag prefix: AI_B3_, AI_B4_, AI_B5_, AI_B6_, AI_B7_
PLC address: %MD bắt đầu từ 0 cho B3, 200 cho B4, 400 cho B5, 600 cho B6, 800 cho B7
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\tags_output"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# ĐỊNH NGHĨA TAGS CHO TỪNG BÀI
# Format: (io_field_name, tag_suffix, sim_type, unit, sim_min, sim_max)
# sim_type: 'temp'|'pressure'|'flow'|'freq'|'rpm'|'level'|'count'|'current'|'percent'
# ============================================================

# -------------------------------------------------------------------
# BÀI 3 - scadabai3 - CIP PSC MODE (Coffee Processing Plant)
# 34 IO fields, prefix AI_B3_, %MD bắt đầu 0
# -------------------------------------------------------------------
B3_TAGS = [
    # (io_field_name,         tag_suffix,          sim_type,   unit,  lo,   hi)
    ("I/O field_1",  "Sequence_Count",     "count",    "",    0,    100),
    ("I/O field_6",  "Flow_CIP_Center",    "flow",     "L/h", 100,  200),
    ("I/O field_5",  "Temp_CIP_Upper",     "temp",     "°C",  50,   80),
    ("I/O field_3",  "Pressure_CIP_1",     "pressure", "bar", 7,    8),
    ("I/O field_2",  "Temp_Chaff_1",       "temp",     "°C",  50,   80),
    ("I/O field_4",  "Flow_CIP_Feed",      "flow",     "L/h", 100,  200),
    ("I/O field_30", "Temp_Steam_1",       "temp",     "°C",  50,   80),
    ("I/O field_8",  "Flow_UCWW_1",        "flow",     "L/h", 100,  200),
    ("I/O field_9",  "RPM_Screw_Conv",     "rpm",      "RPM", 800,  1200),
    ("I/O field_7",  "Temp_Condensate_1",  "temp",     "°C",  50,   80),
    ("I/O field_29", "Pressure_Screw_1",   "pressure", "bar", 7,    8),
    ("I/O field_10", "Flow_CWW_Out",       "flow",     "L/h", 100,  200),
    ("I/O field_11", "Pressure_CWW_1",     "pressure", "bar", 7,    8),
    ("I/O field_33", "Temp_Decanter2",     "temp",     "°C",  50,   80),
    ("I/O field_32", "RPM_Rotary2",        "rpm",      "RPM", 800,  1200),
    ("I/O field_31", "RPM_Rotary1",        "rpm",      "RPM", 800,  1200),
    ("I/O field_19", "Temp_GroundSilo",    "temp",     "°C",  50,   80),
    ("I/O field_18", "Flow_GroundSilo",    "flow",     "L/h", 100,  200),
    ("I/O field_20", "Pressure_Mid_1",     "pressure", "bar", 7,    8),
    ("I/O field_34", "Flow_Condensate",    "flow",     "L/h", 100,  200),
    ("I/O field_13", "Flow_Sump_Out",      "flow",     "L/h", 100,  200),
    ("I/O field_12", "Level_Sump",         "level",    "%",   30,   80),
    ("I/O field_27", "Pressure_Decant1",   "pressure", "bar", 7,    8),
    ("I/O field_28", "Pressure_Decant2",   "pressure", "bar", 7,    8),
    ("I/O field_25", "Flow_Decant1",       "flow",     "L/h", 100,  200),
    ("I/O field_26", "Temp_Decant1",       "temp",     "°C",  50,   80),
    ("I/O field_21", "Temp_FBB_Boiler",    "temp",     "°C",  50,   80),
    ("I/O field_14", "Temp_CWW_Out",       "temp",     "°C",  50,   80),
    ("I/O field_15", "Pressure_SUMP",      "pressure", "bar", 7,    8),
    ("I/O field_16", "Flow_SUMP",          "flow",     "L/h", 100,  200),
    ("I/O field_17", "Level_CWW",          "level",    "%",   30,   80),
    ("I/O field_22", "Temp_FBB_Out",       "temp",     "°C",  50,   80),
    ("I/O field_23", "Pressure_FBB_Out",   "pressure", "bar", 7,    8),
    ("I/O field_24", "Flow_FBB_Out",       "flow",     "L/h", 100,  200),
]

# -------------------------------------------------------------------
# BÀI 4 - scadabai4 - BOILER AIR AND FLUE GAS
# 60 IO fields, prefix AI_B4_, %MD bắt đầu 200
# -------------------------------------------------------------------
B4_TAGS = [
    ("I/O field_1",  "Daq_C",              "count",    "",    0,    100),
    ("I/O field_2",  "TPH_Total",          "flow",     "T/h", 100,  200),
    ("I/O field_3",  "KG_CM_Main",         "pressure", "kg/cm2", 7, 8),
    ("I/O field_4",  "DRM_LVL1",           "level",    "%",   30,   80),
    ("I/O field_5",  "DRM_LVL2",           "level",    "%",   30,   80),
    ("I/O field_6",  "MW_Output",          "count",    "MW",  0,    50),
    ("I/O field_7",  "KG_CM_2",            "pressure", "kg/cm2", 7, 8),
    ("I/O field_8",  "Hc_Value",           "count",    "",    0,    100),
    ("I/O field_9",  "Temp_AirHeater_In1", "temp",     "°C",  50,   80),
    ("I/O field_10", "Temp_AirHeater_In2", "temp",     "°C",  50,   80),
    ("I/O field_11", "Temp_AirHeater_In3", "temp",     "°C",  50,   80),
    ("I/O field_12", "Temp_AirHeater_Out1","temp",     "°C",  50,   80),
    ("I/O field_13", "Temp_AirHeater_Out2","temp",     "°C",  50,   80),
    ("I/O field_14", "Pres_AH_mmWC_1",    "pressure", "mmWC", 7,   8),
    ("I/O field_15", "Pres_AH_mmWC_2",    "pressure", "mmWC", 7,   8),
    ("I/O field_16", "Pres_AH_Pct_1",     "percent",  "%",   20,   80),
    ("I/O field_17", "Temp_AH_Out3",       "temp",     "°C",  50,   80),
    ("I/O field_18", "Pres_FDH_mmWC",     "pressure", "mmWC", 7,   8),
    ("I/O field_19", "RPM_PAF1",           "rpm",      "RPM", 800, 1200),
    ("I/O field_20", "Pct_RPC308_SP",      "percent",  "%",   20,   80),
    ("I/O field_21", "Pct_RPC308_PV",      "percent",  "%",   20,   80),
    ("I/O field_22", "Pres_PAF1_mmWC",    "pressure", "mmWC", 7,   8),
    ("I/O field_23", "Pct_FDF1_SP",        "percent",  "%",   20,   80),
    ("I/O field_24", "Pct_FDF1_PV",        "percent",  "%",   20,   80),
    ("I/O field_25", "Pct_FDF1_OUT",       "percent",  "%",   20,   80),
    ("I/O field_26", "RPM_FDF1",           "rpm",      "RPM", 800, 1200),
    ("I/O field_27", "Pct_RPC301_SP",      "percent",  "%",   20,   80),
    ("I/O field_28", "Pct_RPC301_PV",      "percent",  "%",   20,   80),
    ("I/O field_29", "Pct_RPC301_OUT",     "percent",  "%",   20,   80),
    ("I/O field_30", "mA_ESP1",            "current",  "mA",  50,   200),
    ("I/O field_31", "mA_ESP2",            "current",  "mA",  50,   200),
    ("I/O field_32", "mA_ESP3",            "current",  "mA",  50,   200),
    ("I/O field_33", "mA_ESP4",            "current",  "mA",  50,   200),
    ("I/O field_34", "V_ESP1",             "count",    "V",   0,    400),
    ("I/O field_35", "V_ESP2",             "count",    "V",   0,    400),
    ("I/O field_36", "V_ESP3",             "count",    "V",   0,    400),
    ("I/O field_37", "V_ESP4",             "count",    "V",   0,    400),
    ("I/O field_38", "Pct_RPC305_SP",      "percent",  "%",   20,   80),
    ("I/O field_39", "Pct_RPC305_PV",      "percent",  "%",   20,   80),
    ("I/O field_40", "RPM_IDF1",           "rpm",      "RPM", 800, 1200),
    ("I/O field_41", "Pct_RPC305_VFD",     "percent",  "%",   20,   80),
    ("I/O field_42", "Pct_FDF2_SP",        "percent",  "%",   20,   80),
    ("I/O field_43", "Pct_FDF2_PV",        "percent",  "%",   20,   80),
    ("I/O field_44", "Pct_FDF2_OUT",       "percent",  "%",   20,   80),
    ("I/O field_45", "RPM_FDF2",           "rpm",      "RPM", 800, 1200),
    ("I/O field_46", "Pct_RPC306_SP",      "percent",  "%",   20,   80),
    ("I/O field_47", "Pct_RPC306_PV",      "percent",  "%",   20,   80),
    ("I/O field_48", "Pct_RPC306_OUT",     "percent",  "%",   20,   80),
    ("I/O field_49", "RPM_IDF2",           "rpm",      "RPM", 800, 1200),
    ("I/O field_50", "Pct_RPC306_VFD",     "percent",  "%",   20,   80),
    ("I/O field_51", "Pres_FDF_mmWC",     "pressure", "mmWC", 7,   8),
    ("I/O field_52", "TEST1_Value",        "count",    "",    0,    100),
    ("I/O field_53", "Pct_PAF1_SP",        "percent",  "%",   20,   80),
    ("I/O field_54", "Pct_PAF1_PV",        "percent",  "%",   20,   80),
    ("I/O field_55", "Pres_PAF2_mmWC",    "pressure", "mmWC", 7,   8),
    ("I/O field_56", "RPM_PAF2",           "rpm",      "RPM", 800, 1200),
    ("I/O field_57", "Pct_RPC308b_SP",     "percent",  "%",   20,   80),
    ("I/O field_58", "Pct_RPC308b_PV",     "percent",  "%",   20,   80),
    ("I/O field_59", "Pct_DAM303B_SP",     "percent",  "%",   20,   80),
    ("I/O field_60", "Pct_DAM304B_SP",     "percent",  "%",   20,   80),
]

# -------------------------------------------------------------------
# BÀI 5 - scadabai5 - CEMENT MILL
# 58 IO fields, prefix AI_B5_, %MD bắt đầu 400
# Based on visible labels: CA FAN PARAMS, SEPARATOR PARAMS, CEMENT MILL PARAMS, SILOs
# -------------------------------------------------------------------
B5_TAGS = [
    # CA FAN PARAMETERS (left panel)
    ("I/O field_1",  "CA_Fan_Motor_DE_Temp",   "temp",     "°C",  50,  80),
    ("I/O field_2",  "CA_Fan_Motor_NDE_Temp",  "temp",     "°C",  50,  80),
    ("I/O field_3",  "CA_Fan_DE_Temp",         "temp",     "°C",  50,  80),
    ("I/O field_4",  "CA_Fan_NDE_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_5",  "CA_Fan_DE_Vib",          "count",    "mm/s", 0,  10),
    ("I/O field_6",  "CA_Fan_NDE_Vib",         "count",    "mm/s", 0,  10),
    # SET POINTS panel
    ("I/O field_7",  "SP_700FN03",             "flow",     "L/h", 100, 200),
    ("I/O field_8",  "SP_700HES01",            "flow",     "L/h", 100, 200),
    ("I/O field_9",  "SP_700DA4",              "freq",     "Hz",  20,  30),
    ("I/O field_10", "SP_700DA6",              "freq",     "Hz",  20,  30),
    ("I/O field_11", "SP_700DA7",              "freq",     "Hz",  20,  30),
    ("I/O field_12", "SP_700FN2_DA1",          "freq",     "Hz",  20,  30),
    # SEPARATOR PARAMETERS
    ("I/O field_13", "Sep_Motor_Top_Temp",     "temp",     "°C",  50,  80),
    ("I/O field_14", "Sep_Bottom_Bear_Temp",   "temp",     "°C",  50,  80),
    # Top trend area - bar graph values
    ("I/O field_15", "Trend_Val_1",            "percent",  "%",   0,   100),
    ("I/O field_16", "Trend_Val_2",            "percent",  "%",   0,   100),
    ("I/O field_17", "Trend_Val_3",            "percent",  "%",   0,   100),
    # Center area - main fan RPM / flow
    ("I/O field_18", "700FN03_RPM",            "rpm",      "RPM", 800, 1200),
    ("I/O field_19", "700HES01_Flow",          "flow",     "L/h", 100, 200),
    ("I/O field_20", "700FN10_Speed",          "freq",     "Hz",  20,  30),
    ("I/O field_21", "700CM01_Current",        "current",  "A",   50,  200),
    # LUB timers
    ("I/O field_22", "Lub_Stop_Time",          "count",    "Sec", 0,   300),
    ("I/O field_23", "Main_Drive_ReHealth",    "count",    "Sec", 0,   300),
    # CEMENT MILL PARAMETERS
    ("I/O field_24", "CM_LRS_IN",              "temp",     "°C",  50,  80),
    ("I/O field_25", "CM_LRS_OUT",             "temp",     "°C",  50,  80),
    ("I/O field_26", "CM_Mill_Oil_Temp",       "temp",     "°C",  50,  80),
    ("I/O field_27", "CM_OilTrun_BER_Temp",    "temp",     "°C",  50,  80),
    ("I/O field_28", "CM_OilTrun_BER2_Temp",   "temp",     "°C",  50,  80),
    ("I/O field_29", "CM_OilPinion_BER_Temp",  "temp",     "°C",  50,  80),
    ("I/O field_30", "CM_GB_IL_Shaft_BER",     "temp",     "°C",  50,  80),
    # Running hours / pressures
    ("I/O field_31", "CM_Running_Hours",       "count",    "Hr",  0,   8760),
    ("I/O field_32", "CM_PS1_1_KG",            "pressure", "bar", 7,   8),
    ("I/O field_33", "CM_PS1_2_KG",            "pressure", "bar", 7,   8),
    # NIBS / bottom area
    ("I/O field_34", "NIBS_Value",             "current",  "A",   50,  200),
    # Right side 800DC area
    ("I/O field_35", "800DC1_Temp",            "temp",     "°C",  50,  80),
    ("I/O field_36", "800DC2_Temp",            "temp",     "°C",  50,  80),
    ("I/O field_37", "800FN1_Speed",           "freq",     "Hz",  20,  30),
    ("I/O field_38", "800FN2_Speed",           "freq",     "Hz",  20,  30),
    ("I/O field_39", "800YF1_Flow",            "flow",     "L/h", 100, 200),
    ("I/O field_40", "800YF2_Flow",            "flow",     "L/h", 100, 200),
    # Silo 1 & 2 levels (bar graphs)
    ("I/O field_41", "Silo1_Level_Bar1",       "level",    "%",   0,   100),
    ("I/O field_42", "Silo1_Level_Bar2",       "level",    "%",   0,   100),
    ("I/O field_43", "Silo2_Level_Bar1",       "level",    "%",   0,   100),
    ("I/O field_44", "Silo2_Level_Bar2",       "level",    "%",   0,   100),
    # Additional sensors
    ("I/O field_45", "700FN01_Speed",          "freq",     "Hz",  20,  30),
    ("I/O field_46", "700FN02_Speed",          "freq",     "Hz",  20,  30),
    ("I/O field_47", "700AS07_Speed",          "freq",     "Hz",  20,  30),
    ("I/O field_48", "700AS08_Flow",           "flow",     "L/h", 100, 200),
    ("I/O field_49", "700FN09_Speed",          "freq",     "Hz",  20,  30),
    ("I/O field_50", "700SFM01_Speed",         "freq",     "Hz",  20,  30),
    ("I/O field_51", "700DA1_Flow",            "flow",     "L/h", 100, 200),
    ("I/O field_52", "700DA4_Flow",            "flow",     "L/h", 100, 200),
    ("I/O field_53", "700DA6_Temp",            "temp",     "°C",  50,  80),
    ("I/O field_54", "700DA7_Temp",            "temp",     "°C",  50,  80),
    ("I/O field_55", "700BL1_Load",            "current",  "A",   50,  200),
    ("I/O field_56", "700BL2_Load",            "current",  "A",   50,  200),
    ("I/O field_57", "700AS9_Flow",            "flow",     "L/h", 100, 200),
    ("I/O field_58", "700FN13_Speed",          "freq",     "Hz",  20,  30),
]

# -------------------------------------------------------------------
# BÀI 6 - scadabai6 - 600L CELL CULTURE FERMENTER
# 13 IO fields, prefix AI_B6_, %MD bắt đầu 600
# -------------------------------------------------------------------
B6_TAGS = [
    ("I/O field_1",  "TICR211_Temp",      "temp",     "°C",  50,  80),
    ("I/O field_2",  "TICR210_Temp",      "temp",     "°C",  50,  80),
    ("I/O field_3",  "TICR201_Tank_Temp", "temp",     "°C",  50,  80),
    ("I/O field_4",  "PT201_Pressure",    "pressure", "bar", 7,   8),
    ("I/O field_5",  "Ph201_pH",          "count",    "pH",  6,   8),
    ("I/O field_6",  "ORP201_ORP",        "count",    "%",   20,  80),
    ("I/O field_7",  "DPL101_Level",      "level",    "L",   100, 500),
    ("I/O field_8",  "TICR214_Temp",      "temp",     "°C",  50,  80),
    ("I/O field_9",  "TICR204_Temp",      "temp",     "°C",  50,  80),
    ("I/O field_10", "TICR205_Temp",      "temp",     "°C",  50,  80),
    ("I/O field_11", "TICR206_Temp",      "temp",     "°C",  50,  80),
    ("I/O field_12", "FHC203_Flow",       "flow",     "L/h", 100, 200),
    ("I/O field_13", "BPC201_Pressure",   "pressure", "bar", 7,   8),
]

# -------------------------------------------------------------------
# BÀI 7 - scadabai7 - PLANTPAX DISTILLATION (29-K-03)
# 65 IO fields, prefix AI_B7_, %MD bắt đầu 800
# -------------------------------------------------------------------
B7_TAGS = [
    # Top instruments
    ("I/O field_1",  "K03_PT02_Pressure",    "pressure", "bar", 7,   8),
    ("I/O field_2",  "K03_TT04_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_3",  "K03_TT05_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_4",  "K03_TT06_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_5",  "K03_TT07_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_6",  "K03_PT07_Pressure",    "pressure", "bar", 7,   8),
    ("I/O field_7",  "K03_FT03_Flow",        "flow",     "L/h", 100, 200),
    ("I/O field_8",  "K03_Density_1",        "count",    "kg/m3", 800, 1000),
    ("I/O field_9",  "K03_LT01_Level",       "level",    "cm",  20,  80),
    ("I/O field_10", "K03_LT02_Level",       "level",    "cm",  20,  80),
    ("I/O field_11", "K03_TT01_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_12", "K03_TT02_Temp",        "temp",     "°C",  50,  80),
    # Reboiler control loop
    ("I/O field_13", "Reboiler_PV",          "flow",     "L/h", 100, 200),
    ("I/O field_14", "Reboiler_SP",          "flow",     "L/h", 100, 200),
    ("I/O field_15", "Reboiler_CV",          "percent",  "%",   20,  80),
    # HE-03 Primary/Secondary
    ("I/O field_16", "HE03_Primary_Temp",    "temp",     "°C",  50,  80),
    ("I/O field_17", "HE03_Secondary_Temp",  "temp",     "°C",  50,  80),
    # Tank levels collection
    ("I/O field_18", "K03_L08_Level",        "level",    "cm",  20,  80),
    ("I/O field_19", "K03_L06_Level",        "level",    "cm",  20,  80),
    ("I/O field_20", "K03_L05_Level",        "level",    "cm",  20,  80),
    ("I/O field_21", "K03_L07_Level",        "level",    "cm",  20,  80),
    ("I/O field_22", "K03_L04_Level",        "level",    "cm",  20,  80),
    ("I/O field_23", "K03_L03_Level",        "level",    "cm",  20,  80),
    # Phase separator
    ("I/O field_24", "V03A_Density",         "count",    "kg/m3", 800, 1000),
    # Kettle/Keboiler control
    ("I/O field_25", "Kettle_Flow_SP",       "flow",     "kg/h", 100, 200),
    ("I/O field_26", "Keboiler_Flow_SP",     "flow",     "kg/h", 100, 200),
    # Reflux time SP
    ("I/O field_27", "Reflux_Time_SP",       "count",    "Min", 0,   60),
    ("I/O field_28", "Time_Remain",          "count",    "Min", 0,   60),
    # RD Level SP / Collection SP
    ("I/O field_29", "RD_Level_SP",          "level",    "cm",  20,  80),
    ("I/O field_30", "Reflux_Flow_SP",       "flow",     "L/h", 100, 200),
    ("I/O field_31", "Collection_SP",        "flow",     "L/h", 100, 200),
    ("I/O field_32", "Total_Flowrate",       "flow",     "L/h", 100, 200),
    # ML Charging
    ("I/O field_33", "ML_Qty_SP",            "count",    "L",   0,   600),
    ("I/O field_34", "ML_Qty_Total",         "count",    "L",   0,   600),
    # Batch info
    ("I/O field_35", "Material_Code",        "count",    "",    0,   99),
    ("I/O field_36", "Stage_Number",         "count",    "",    0,   20),
    ("I/O field_37", "Batch_Number",         "count",    "",    0,   9999),
    # Current User
    ("I/O field_38", "Current_User_ID",      "count",    "",    0,   999),
    ("I/O field_39", "K_05_L_704_HI",        "level",    "cm",  20,  80),
    # Density SP
    ("I/O field_40", "Density_SP",           "count",    "kg/m3", 800, 1000),
    # CTS / Steam flows
    ("I/O field_41", "CTS_Flow_1",           "flow",     "kg/h", 100, 200),
    ("I/O field_42", "CTS_Flow_2",           "flow",     "kg/h", 100, 200),
    # Steam / CWS / CWAR temps
    ("I/O field_43", "Steam_PT01_Temp",      "temp",     "°C",  50,  80),
    ("I/O field_44", "Steam_PT02_Temp",      "temp",     "°C",  50,  80),
    ("I/O field_45", "CWS_TT01_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_46", "CWS_TT02_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_47", "CWS_TT03_Temp",        "temp",     "°C",  50,  80),
    ("I/O field_48", "CWAR_TT01_Temp",       "temp",     "°C",  50,  80),
    ("I/O field_49", "CWAR_TT02_Temp",       "temp",     "°C",  50,  80),
    ("I/O field_50", "CWAR_TT03_Temp",       "temp",     "°C",  50,  80),
    ("I/O field_51", "CWAR_TT04_Temp",       "temp",     "°C",  50,  80),
    # K03 CV01 control
    ("I/O field_52", "K03_CV01_PV",          "percent",  "%",   20,  80),
    ("I/O field_53", "K03_CV01_SP",          "percent",  "%",   20,  80),
    ("I/O field_54", "K03_CV01_CV",          "percent",  "%",   20,  80),
    # Steam CV01
    ("I/O field_55", "Steam_CV01_PV",        "percent",  "%",   20,  80),
    ("I/O field_56", "Steam_CV01_SP",        "percent",  "%",   20,  80),
    ("I/O field_57", "Steam_CV01_CV",        "percent",  "%",   20,  80),
    # K03 Jacket
    ("I/O field_58", "K03_Jacket_PV",        "temp",     "°C",  50,  80),
    ("I/O field_59", "K03_Jacket_SP",        "temp",     "°C",  50,  80),
    ("I/O field_60", "K03_Jacket_CV",        "percent",  "%",   20,  80),
    # CHWT temps
    ("I/O field_61", "CHWR_TT01_Temp",       "temp",     "°C",  50,  80),
    ("I/O field_62", "CHWR_TT02_Temp",       "temp",     "°C",  50,  80),
    ("I/O field_63", "CHWS_TT01_Temp",       "temp",     "°C",  50,  80),
    ("I/O field_64", "CHWS_TT02_Temp",       "temp",     "°C",  50,  80),
    ("I/O field_65", "K03_TT03_Temp",        "temp",     "°C",  50,  80),
]

# ============================================================
# CONFIGURATION
# ============================================================
SCREENS = [
    {"bai": 3, "prefix": "AI_B3_", "table": "AI_B3_Tags", "addr_start": 0,   "tags": B3_TAGS, "screen": "scadabai3"},
    {"bai": 4, "prefix": "AI_B4_", "table": "AI_B4_Tags", "addr_start": 200, "tags": B4_TAGS, "screen": "scadabai4"},
    {"bai": 5, "prefix": "AI_B5_", "table": "AI_B5_Tags", "addr_start": 400, "tags": B5_TAGS, "screen": "scadabai5"},
    {"bai": 6, "prefix": "AI_B6_", "table": "AI_B6_Tags", "addr_start": 600, "tags": B6_TAGS, "screen": "scadabai6"},
    {"bai": 7, "prefix": "AI_B7_", "table": "AI_B7_Tags", "addr_start": 800, "tags": B7_TAGS, "screen": "scadabai7"},
]

HMI_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-12T02:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
    <InstalledProducts>
      <Product>
        <DisplayName>Totally Integrated Automation Portal</DisplayName>
        <DisplayVersion>V18</DisplayVersion>
      </Product>
      <OptionPackage>
        <DisplayName>TIA Portal Openness</DisplayName>
        <DisplayVersion>V18</DisplayVersion>
      </OptionPackage>
    </InstalledProducts>
  </DocumentInfo>
'''

PLC_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-12T02:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
'''

def hmi_tag_xml(tag_id, tag_name, plc_tag_name, comment=""):
    return f"""      <Hmi.Tag.Tag ID="{tag_id}" CompositionName="Tags">
        <AttributeList>
          <AcquisitionTriggerMode>Visible</AcquisitionTriggerMode>
          <AddressAccessMode>Symbolic</AddressAccessMode>
          <Coding>IEEE754Float</Coding>
          <ConfirmationType>None</ConfirmationType>
          <GmpRelevant>false</GmpRelevant>
          <JobNumber>0</JobNumber>
          <Length>4</Length>
          <LinearScaling>false</LinearScaling>
          <LogicalAddress />
          <MandatoryCommenting>false</MandatoryCommenting>
          <Name>{tag_name}</Name>
          <Persistency>false</Persistency>
          <QualityCode>false</QualityCode>
          <StartValue />
          <SubstituteValue />
          <SubstituteValueUsage>None</SubstituteValueUsage>
          <Synchronization>false</Synchronization>
          <UpdateMode>ProjectWide</UpdateMode>
          <UseMultiplexing>false</UseMultiplexing>
        </AttributeList>
        <LinkList>
          <AcquisitionCycle TargetID="@OpenLink">
            <Name>1 s</Name>
          </AcquisitionCycle>
          <Connection TargetID="@OpenLink">
            <Name>HMI_Connection_1</Name>
          </Connection>
          <ControllerTag TargetID="@OpenLink">
            <Name>{plc_tag_name}</Name>
          </ControllerTag>
          <DataType TargetID="@OpenLink">
            <Name>Real</Name>
          </DataType>
          <HmiDataType TargetID="@OpenLink">
            <Name>Real</Name>
          </HmiDataType>
        </LinkList>
        <ObjectList>
          <MultilingualText ID="{tag_id+1000}" CompositionName="Comment">
            <ObjectList>
              <MultilingualTextItem ID="{tag_id+2000}" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>{comment}</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </Hmi.Tag.Tag>
"""

def plc_tag_xml(tag_id, tag_name, addr_offset, comment=""):
    addr = f"%MD{addr_offset}"
    return f"""      <SW.Tags.PlcTag ID="{tag_id}" CompositionName="Tags">
        <AttributeList>
          <DataTypeName>Real</DataTypeName>
          <ExternalAccessible>true</ExternalAccessible>
          <ExternalVisible>true</ExternalVisible>
          <ExternalWritable>true</ExternalWritable>
          <LogicalAddress>{addr}</LogicalAddress>
          <Name>{tag_name}</Name>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{tag_id+1000}" CompositionName="Comment">
            <ObjectList>
              <MultilingualTextItem ID="{tag_id+2000}" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>{comment}</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Tags.PlcTag>
"""

# ============================================================
# GENERATE FILES
# ============================================================
total_tags = 0
all_hmi_tags = []   # (prefix+suffix, plc_name) for simulation summary

for screen in SCREENS:
    bai = screen["bai"]
    prefix = screen["prefix"]
    table_name = screen["table"]
    addr_start = screen["addr_start"]
    tags = screen["tags"]

    print(f"\n=== Bài {bai}: {screen['screen']} - {len(tags)} tags ===")

    # --- HMI Tags XML ---
    hmi_xml = HMI_HEADER
    hmi_xml += f'  <Hmi.Tag.TagTable ID="0">\n'
    hmi_xml += f'    <AttributeList>\n      <Name>{table_name}</Name>\n    </AttributeList>\n'
    hmi_xml += f'    <ObjectList>\n'

    # --- PLC Tags XML ---
    plc_xml = PLC_HEADER
    plc_xml += f'  <SW.Tags.PlcTagTable ID="0">\n'
    plc_xml += f'    <AttributeList>\n      <Name>PLC_{table_name}</Name>\n    </AttributeList>\n'
    plc_xml += f'    <ObjectList>\n'

    for idx, (io_name, suffix, sim_type, unit, lo, hi) in enumerate(tags):
        tag_id = idx * 10 + 1
        full_name = f"{prefix}{suffix}"
        comment = f"{sim_type.upper()} {lo}-{hi} {unit}"
        addr_offset = addr_start + idx * 4  # 4 bytes per Real

        hmi_xml += hmi_tag_xml(tag_id, full_name, full_name, comment)
        plc_xml += plc_tag_xml(tag_id, full_name, addr_offset, comment)
        all_hmi_tags.append((full_name, sim_type, lo, hi))
        total_tags += 1

        print(f"  [{idx+1:2d}] {full_name:45s} | {sim_type:10s} | {lo:6.1f}-{hi:6.1f} {unit}")

    hmi_xml += f'    </ObjectList>\n  </Hmi.Tag.TagTable>\n</Document>\n'
    plc_xml += f'    </ObjectList>\n  </SW.Tags.PlcTagTable>\n</Document>\n'

    # Save files
    hmi_path = os.path.join(OUT_DIR, f"HMI_Tags_B{bai}.xml")
    plc_path = os.path.join(OUT_DIR, f"PLC_Tags_B{bai}.xml")

    with open(hmi_path, "w", encoding="utf-8") as f:
        f.write(hmi_xml)
    with open(plc_path, "w", encoding="utf-8") as f:
        f.write(plc_xml)

    print(f"  -> HMI: {hmi_path}")
    print(f"  -> PLC: {plc_path}")

print(f"\n=== TỔNG: {total_tags} tags cho 5 màn hình ===")
print(f"Output thư mục: {OUT_DIR}")
