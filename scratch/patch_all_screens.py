# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Input exported screens
SCRATCH_DIR = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch"
OUTPUT_DIR = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define HMI tags and units for mapping
B3_TAGS = [
    ("I/O field_1",  "AI_B3_Sequence_Count",     "",    0,    100),
    ("I/O field_6",  "AI_B3_Flow_CIP_Center",    "L/h", 100,  200),
    ("I/O field_5",  "AI_B3_Temp_CIP_Upper",     "°C",  50,   80),
    ("I/O field_3",  "AI_B3_Pressure_CIP_1",     "bar", 7,    8),
    ("I/O field_2",  "AI_B3_Temp_Chaff_1",       "°C",  50,   80),
    ("I/O field_4",  "AI_B3_Flow_CIP_Feed",      "L/h", 100,  200),
    ("I/O field_30", "AI_B3_Temp_Steam_1",       "°C",  50,   80),
    ("I/O field_8",  "AI_B3_Flow_UCWW_1",        "L/h", 100,  200),
    ("I/O field_9",  "AI_B3_RPM_Screw_Conv",     "RPM", 800,  1200),
    ("I/O field_7",  "AI_B3_Temp_Condensate_1",  "°C",  50,   80),
    ("I/O field_29", "AI_B3_Pressure_Screw_1",   "bar", 7,    8),
    ("I/O field_10", "AI_B3_Flow_CWW_Out",       "L/h", 100,  200),
    ("I/O field_11", "AI_B3_Pressure_CWW_1",     "bar", 7,    8),
    ("I/O field_33", "AI_B3_Temp_Decanter2",     "°C",  50,   80),
    ("I/O field_32", "AI_B3_RPM_Rotary2",        "RPM", 800,  1200),
    ("I/O field_31", "AI_B3_RPM_Rotary1",        "RPM", 800,  1200),
    ("I/O field_19", "AI_B3_Temp_GroundSilo",    "°C",  50,   80),
    ("I/O field_18", "AI_B3_Flow_GroundSilo",    "L/h", 100,  200),
    ("I/O field_20", "AI_B3_Pressure_Mid_1",     "bar", 7,    8),
    ("I/O field_34", "AI_B3_Flow_Condensate",    "L/h", 100,  200),
    ("I/O field_13", "AI_B3_Flow_Sump_Out",      "L/h", 100,  200),
    ("I/O field_12", "AI_B3_Level_Sump",         "%",   30,   80),
    ("I/O field_27", "AI_B3_Pressure_Decant1",   "bar", 7,    8),
    ("I/O field_28", "AI_B3_Pressure_Decant2",   "bar", 7,    8),
    ("I/O field_25", "AI_B3_Flow_Decant1",       "L/h", 100,  200),
    ("I/O field_26", "AI_B3_Temp_Decant1",       "°C",  50,   80),
    ("I/O field_21", "AI_B3_Temp_FBB_Boiler",    "°C",  50,   80),
    ("I/O field_14", "AI_B3_Temp_CWW_Out",       "°C",  50,   80),
    ("I/O field_15", "AI_B3_Pressure_SUMP",      "bar", 7,    8),
    ("I/O field_16", "AI_B3_Flow_SUMP",          "L/h", 100,  200),
    ("I/O field_17", "AI_B3_Level_CWW",          "%",   30,   80),
    ("I/O field_22", "AI_B3_Temp_FBB_Out",       "°C",  50,   80),
    ("I/O field_23", "AI_B3_Pressure_FBB_Out",   "bar", 7,    8),
    ("I/O field_24", "AI_B3_Flow_FBB_Out",       "L/h", 100,  200),
]

B4_TAGS = [
    ("I/O field_1",  "AI_B4_Daq_C",              "",    0,    100),
    ("I/O field_2",  "AI_B4_TPH_Total",          "T/h", 100,  200),
    ("I/O field_3",  "AI_B4_KG_CM_Main",         "kg/cm2", 7, 8),
    ("I/O field_4",  "AI_B4_DRM_LVL1",           "%",   30,   80),
    ("I/O field_5",  "AI_B4_DRM_LVL2",           "%",   30,   80),
    ("I/O field_6",  "AI_B4_MW_Output",          "MW",  0,    50),
    ("I/O field_7",  "AI_B4_KG_CM_2",            "kg/cm2", 7, 8),
    ("I/O field_8",  "AI_B4_Hc_Value",           "",    0,    100),
    ("I/O field_9",  "AI_B4_Temp_AirHeater_In1", "°C",  50,   80),
    ("I/O field_10", "AI_B4_Temp_AirHeater_In2", "°C",  50,   80),
    ("I/O field_11", "AI_B4_Temp_AirHeater_In3", "°C",  50,   80),
    ("I/O field_12", "AI_B4_Temp_AirHeater_Out1","°C",  50,   80),
    ("I/O field_13", "AI_B4_Temp_AirHeater_Out2","°C",  50,   80),
    ("I/O field_14", "AI_B4_Pres_AH_mmWC_1",     "mmWC", 7,   8),
    ("I/O field_15", "AI_B4_Pres_AH_mmWC_2",     "mmWC", 7,   8),
    ("I/O field_16", "AI_B4_Pres_AH_Pct_1",      "%",   20,   80),
    ("I/O field_17", "AI_B4_Temp_AH_Out3",       "°C",  50,   80),
    ("I/O field_18", "AI_B4_Pres_FDH_mmWC",      "mmWC", 7,   8),
    ("I/O field_19", "AI_B4_RPM_PAF1",           "RPM", 800,  1200),
    ("I/O field_20", "AI_B4_Pct_RPC308_SP",      "%",   20,   80),
    ("I/O field_21", "AI_B4_Pct_RPC308_PV",      "%",   20,   80),
    ("I/O field_22", "AI_B4_Pres_PAF1_mmWC",     "mmWC", 7,   8),
    ("I/O field_23", "AI_B4_Pct_FDF1_SP",        "%",   20,   80),
    ("I/O field_24", "AI_B4_Pct_FDF1_PV",        "%",   20,   80),
    ("I/O field_25", "AI_B4_Pct_FDF1_OUT",       "%",   20,   80),
    ("I/O field_26", "AI_B4_RPM_FDF1",           "RPM", 800,  1200),
    ("I/O field_27", "AI_B4_Pct_RPC301_SP",      "%",   20,   80),
    ("I/O field_28", "AI_B4_Pct_RPC301_PV",      "%",   20,   80),
    ("I/O field_29", "AI_B4_Pct_RPC301_OUT",     "%",   20,   80),
    ("I/O field_30", "AI_B4_mA_ESP1",            "mA",  50,   200),
    ("I/O field_31", "AI_B4_mA_ESP2",            "mA",  50,   200),
    ("I/O field_32", "AI_B4_mA_ESP3",            "mA",  50,   200),
    ("I/O field_33", "AI_B4_mA_ESP4",            "mA",  50,   200),
    ("I/O field_34", "AI_B4_V_ESP1",             "V",   0,    400),
    ("I/O field_35", "AI_B4_V_ESP2",             "V",   0,    400),
    ("I/O field_36", "AI_B4_V_ESP3",             "V",   0,    400),
    ("I/O field_37", "AI_B4_V_ESP4",             "V",   0,    400),
    ("I/O field_38", "AI_B4_Pct_RPC305_SP",      "%",   20,   80),
    ("I/O field_39", "AI_B4_Pct_RPC305_PV",      "%",   20,   80),
    ("I/O field_40", "AI_B4_RPM_IDF1",           "RPM", 800,  1200),
    ("I/O field_41", "AI_B4_Pct_RPC305_VFD",     "%",   20,   80),
    ("I/O field_42", "AI_B4_Pct_FDF2_SP",        "%",   20,   80),
    ("I/O field_43", "AI_B4_Pct_FDF2_PV",        "%",   20,   80),
    ("I/O field_44", "AI_B4_Pct_FDF2_OUT",       "%",   20,   80),
    ("I/O field_45", "AI_B4_RPM_FDF2",           "RPM", 800,  1200),
    ("I/O field_46", "AI_B4_Pct_RPC306_SP",      "%",   20,   80),
    ("I/O field_47", "AI_B4_Pct_RPC306_PV",      "%",   20,   80),
    ("I/O field_48", "AI_B4_Pct_RPC306_OUT",     "%",   20,   80),
    ("I/O field_49", "AI_B4_RPM_IDF2",           "RPM", 800,  1200),
    ("I/O field_50", "AI_B4_Pct_RPC306_VFD",     "%",   20,   80),
    ("I/O field_51", "AI_B4_Pres_FDF_mmWC",      "mmWC", 7,   8),
    ("I/O field_52", "AI_B4_TEST1_Value",        "",    0,    100),
    ("I/O field_53", "AI_B4_Pct_PAF1_SP",        "%",   20,   80),
    ("I/O field_54", "AI_B4_Pct_PAF1_PV",        "%",   20,   80),
    ("I/O field_55", "AI_B4_Pres_PAF2_mmWC",     "mmWC", 7,   8),
    ("I/O field_56", "AI_B4_RPM_PAF2",           "RPM", 800,  1200),
    ("I/O field_57", "AI_B4_Pct_RPC308b_SP",     "%",   20,   80),
    ("I/O field_58", "AI_B4_Pct_RPC308b_PV",     "%",   20,   80),
    ("I/O field_59", "AI_B4_Pct_DAM303B_SP",     "%",   20,   80),
    ("I/O field_60", "AI_B4_Pct_DAM304B_SP",     "%",   20,   80),
]

B5_TAGS = [
    ("I/O field_1",  "AI_B5_CA_Fan_Motor_DE_Temp",   "°C",  50,  80),
    ("I/O field_2",  "AI_B5_CA_Fan_Motor_NDE_Temp",  "°C",  50,  80),
    ("I/O field_3",  "AI_B5_CA_Fan_DE_Temp",         "°C",  50,  80),
    ("I/O field_4",  "AI_B5_CA_Fan_NDE_Temp",        "°C",  50,  80),
    ("I/O field_5",  "AI_B5_CA_Fan_DE_Vib",          "mm/s", 0,  10),
    ("I/O field_6",  "AI_B5_CA_Fan_NDE_Vib",         "mm/s", 0,  10),
    ("I/O field_7",  "AI_B5_SP_700FN03",             "L/h", 100, 200),
    ("I/O field_8",  "AI_B5_SP_700HES01",            "L/h", 100, 200),
    ("I/O field_9",  "AI_B5_SP_700DA4",              "Hz",  20,  30),
    ("I/O field_10", "AI_B5_SP_700DA6",              "Hz",  20,  30),
    ("I/O field_11", "AI_B5_SP_700DA7",              "Hz",  20,  30),
    ("I/O field_12", "AI_B5_SP_700FN2_DA1",          "Hz",  20,  30),
    ("I/O field_13", "AI_B5_Sep_Motor_Top_Temp",     "°C",  50,  80),
    ("I/O field_14", "AI_B5_Sep_Bottom_Bear_Temp",   "°C",  50,  80),
    ("I/O field_15", "AI_B5_Trend_Val_1",            "%",   0,   100),
    ("I/O field_16", "AI_B5_Trend_Val_2",            "%",   0,   100),
    ("I/O field_17", "AI_B5_Trend_Val_3",            "%",   0,   100),
    ("I/O field_18", "AI_B5_700FN03_RPM",            "RPM", 800, 1200),
    ("I/O field_19", "AI_B5_700HES01_Flow",          "L/h", 100, 200),
    ("I/O field_20", "AI_B5_700FN10_Speed",          "Hz",  20,  30),
    ("I/O field_21", "AI_B5_700CM01_Current",        "A",   50,  200),
    ("I/O field_22", "AI_B5_Lub_Stop_Time",          "Sec", 0,   300),
    ("I/O field_23", "AI_B5_Main_Drive_ReHealth",    "Sec", 0,   300),
    ("I/O field_24", "AI_B5_CM_LRS_IN",              "°C",  50,  80),
    ("I/O field_25", "AI_B5_CM_LRS_OUT",             "°C",  50,  80),
    ("I/O field_26", "AI_B5_CM_Mill_Oil_Temp",       "°C",  50,  80),
    ("I/O field_27", "AI_B5_CM_OilTrun_BER_Temp",    "°C",  50,  80),
    ("I/O field_28", "AI_B5_CM_OilTrun_BER2_Temp",   "°C",  50,  80),
    ("I/O field_29", "AI_B5_CM_OilPinion_BER_Temp",  "°C",  50,  80),
    ("I/O field_30", "AI_B5_CM_GB_IL_Shaft_BER",     "°C",  50,  80),
    ("I/O field_31", "AI_B5_CM_Running_Hours",       "Hr",  0,   8760),
    ("I/O field_32", "AI_B5_CM_PS1_1_KG",            "bar", 7,   8),
    ("I/O field_33", "AI_B5_CM_PS1_2_KG",            "bar", 7,   8),
    ("I/O field_34", "AI_B5_NIBS_Value",             "A",   50,  200),
    ("I/O field_35", "AI_B5_800DC1_Temp",            "°C",  50,  80),
    ("I/O field_36", "AI_B5_800DC2_Temp",            "°C",  50,  80),
    ("I/O field_37", "AI_B5_800FN1_Speed",           "Hz",  20,  30),
    ("I/O field_38", "AI_B5_800FN2_Speed",           "Hz",  20,  30),
    ("I/O field_39", "AI_B5_800YF1_Flow",            "L/h", 100, 200),
    ("I/O field_40", "AI_B5_800YF2_Flow",            "L/h", 100, 200),
    ("I/O field_41", "AI_B5_Silo1_Level_Bar1",       "%",   0,   100),
    ("I/O field_42", "AI_B5_Silo1_Level_Bar2",       "%",   0,   100),
    ("I/O field_43", "AI_B5_Silo2_Level_Bar1",       "%",   0,   100),
    ("I/O field_44", "AI_B5_Silo2_Level_Bar2",       "%",   0,   100),
    ("I/O field_45", "AI_B5_700FN01_Speed",          "Hz",  20,  30),
    ("I/O field_46", "AI_B5_700FN02_Speed",          "Hz",  20,  30),
    ("I/O field_47", "AI_B5_700AS07_Speed",          "Hz",  20,  30),
    ("I/O field_48", "AI_B5_700AS08_Flow",           "L/h", 100, 200),
    ("I/O field_49", "AI_B5_700FN09_Speed",          "Hz",  20,  30),
    ("I/O field_50", "AI_B5_700SFM01_Speed",         "Hz",  20,  30),
    ("I/O field_51", "AI_B5_700DA1_Flow",            "L/h", 100, 200),
    ("I/O field_52", "AI_B5_700DA4_Flow",            "L/h", 100, 200),
    ("I/O field_53", "AI_B5_700DA6_Temp",            "°C",  50,  80),
    ("I/O field_54", "AI_B5_700DA7_Temp",            "°C",  50,  80),
    ("I/O field_55", "AI_B5_700BL1_Load",            "A",   50,  200),
    ("I/O field_56", "AI_B5_700BL2_Load",            "A",   50,  200),
    ("I/O field_57", "AI_B5_700AS9_Flow",            "L/h", 100, 200),
    ("I/O field_58", "AI_B5_700FN13_Speed",          "Hz",  20,  30),
]

B6_TAGS = [
    ("I/O field_1",  "AI_B6_TICR211_Temp",      "°C",  50,  80),
    ("I/O field_2",  "AI_B6_TICR210_Temp",      "°C",  50,  80),
    ("I/O field_3",  "AI_B6_TICR201_Tank_Temp", "°C",  50,  80),
    ("I/O field_4",  "AI_B6_PT201_Pressure",    "bar", 7,   8),
    ("I/O field_5",  "AI_B6_Ph201_pH",          "pH",  6,   8),
    ("I/O field_6",  "AI_B6_ORP201_ORP",        "%",   20,  80),
    ("I/O field_7",  "AI_B6_DPL101_Level",      "L",   100, 500),
    ("I/O field_8",  "AI_B6_TICR214_Temp",      "°C",  50,  80),
    ("I/O field_9",  "AI_B6_TICR204_Temp",      "°C",  50,  80),
    ("I/O field_10", "AI_B6_TICR205_Temp",      "°C",  50,  80),
    ("I/O field_11", "AI_B6_TICR206_Temp",      "°C",  50,  80),
    ("I/O field_12", "AI_B6_FHC203_Flow",       "L/h", 100, 200),
    ("I/O field_13", "AI_B6_BPC201_Pressure",   "bar", 7,   8),
]

B7_TAGS = [
    ("I/O field_1",  "AI_B7_K03_PT02_Pressure",    "bar", 7,   8),
    ("I/O field_2",  "AI_B7_K03_TT04_Temp",        "°C",  50,  80),
    ("I/O field_3",  "AI_B7_K03_TT05_Temp",        "°C",  50,  80),
    ("I/O field_4",  "AI_B7_K03_TT06_Temp",        "°C",  50,  80),
    ("I/O field_5",  "AI_B7_K03_TT07_Temp",        "°C",  50,  80),
    ("I/O field_6",  "AI_B7_K03_PT07_Pressure",    "bar", 7,   8),
    ("I/O field_7",  "AI_B7_K03_FT03_Flow",        "L/h", 100, 200),
    ("I/O field_8",  "AI_B7_K03_Density_1",        "kg/m3", 800, 1000),
    ("I/O field_9",  "AI_B7_K03_LT01_Level",       "cm",  20,  80),
    ("I/O field_10", "AI_B7_K03_LT02_Level",       "cm",  20,  80),
    ("I/O field_11", "AI_B7_K03_TT01_Temp",        "°C",  50,  80),
    ("I/O field_12", "AI_B7_K03_TT02_Temp",        "°C",  50,  80),
    ("I/O field_13", "AI_B7_Reboiler_PV",          "L/h", 100, 200),
    ("I/O field_14", "AI_B7_Reboiler_SP",          "L/h", 100, 200),
    ("I/O field_15", "AI_B7_Reboiler_CV",          "%",   20,  80),
    ("I/O field_16", "AI_B7_HE03_Primary_Temp",    "°C",  50,  80),
    ("I/O field_17", "AI_B7_HE03_Secondary_Temp",  "°C",  50,  80),
    ("I/O field_18", "AI_B7_K03_L08_Level",        "cm",  20,  80),
    ("I/O field_19", "AI_B7_K03_L06_Level",        "cm",  20,  80),
    ("I/O field_20", "AI_B7_K03_L05_Level",        "cm",  20,  80),
    ("I/O field_21", "AI_B7_K03_L07_Level",        "cm",  20,  80),
    ("I/O field_22", "AI_B7_K03_L04_Level",        "cm",  20,  80),
    ("I/O field_23", "AI_B7_K03_L03_Level",        "cm",  20,  80),
    ("I/O field_24", "AI_B7_V03A_Density",         "kg/m3", 800, 1000),
    ("I/O field_25", "AI_B7_Kettle_Flow_SP",       "kg/h", 100, 200),
    ("I/O field_26", "AI_B7_Keboiler_Flow_SP",     "kg/h", 100, 200),
    ("I/O field_27", "AI_B7_Reflux_Time_SP",       "Min", 0,   60),
    ("I/O field_28", "AI_B7_Time_Remain",          "Min", 0,   60),
    ("I/O field_29", "AI_B7_RD_Level_SP",          "cm",  20,  80),
    ("I/O field_30", "AI_B7_Reflux_Flow_SP",       "L/h", 100, 200),
    ("I/O field_31", "AI_B7_Collection_SP",        "L/h", 100, 200),
    ("I/O field_32", "AI_B7_Total_Flowrate",       "L/h", 100, 200),
    ("I/O field_33", "AI_B7_ML_Qty_SP",            "L",   0,   600),
    ("I/O field_34", "AI_B7_ML_Qty_Total",         "L",   0,   600),
    ("I/O field_35", "AI_B7_Material_Code",        "",    0,   99),
    ("I/O field_36", "AI_B7_Stage_Number",         "",    0,   20),
    ("I/O field_37", "AI_B7_Batch_Number",         "",    0,   9999),
    ("I/O field_38", "AI_B7_Current_User_ID",      "",    0,   999),
    ("I/O field_39", "AI_B7_K_05_L_704_HI",        "cm",  20,  80),
    ("I/O field_40", "AI_B7_Density_SP",           "kg/m3", 800, 1000),
    ("I/O field_41", "AI_B7_CTS_Flow_1",           "kg/h", 100, 200),
    ("I/O field_42", "AI_B7_CTS_Flow_2",           "kg/h", 100, 200),
    ("I/O field_43", "AI_B7_Steam_PT01_Temp",      "°C",  50,  80),
    ("I/O field_44", "AI_B7_Steam_PT02_Temp",      "°C",  50,  80),
    ("I/O field_45", "AI_B7_CWS_TT01_Temp",        "°C",  50,  80),
    ("I/O field_46", "AI_B7_CWS_TT02_Temp",        "°C",  50,  80),
    ("I/O field_47", "AI_B7_CWS_TT03_Temp",        "°C",  50,  80),
    ("I/O field_48", "AI_B7_CWAR_TT01_Temp",       "°C",  50,  80),
    ("I/O field_49", "AI_B7_CWAR_TT02_Temp",       "°C",  50,  80),
    ("I/O field_50", "AI_B7_CWAR_TT03_Temp",       "°C",  50,  80),
    ("I/O field_51", "AI_B7_CWAR_TT04_Temp",       "°C",  50,  80),
    ("I/O field_52", "AI_B7_K03_CV01_PV",          "%",   20,  80),
    ("I/O field_53", "AI_B7_K03_CV01_SP",          "%",   20,  80),
    ("I/O field_54", "AI_B7_K03_CV01_CV",          "%",   20,  80),
    ("I/O field_55", "AI_B7_Steam_CV01_PV",        "%",   20,  80),
    ("I/O field_56", "AI_B7_Steam_CV01_SP",        "%",   20,  80),
    ("I/O field_57", "AI_B7_Steam_CV01_CV",        "%",   20,  80),
    ("I/O field_58", "AI_B7_K03_Jacket_PV",        "°C",  50,  80),
    ("I/O field_59", "AI_B7_K03_Jacket_SP",        "°C",  50,  80),
    ("I/O field_60", "AI_B7_K03_Jacket_CV",        "%",   20,  80),
    ("I/O field_61", "AI_B7_CHWR_TT01_Temp",       "°C",  50,  80),
    ("I/O field_62", "AI_B7_CHWR_TT02_Temp",       "°C",  50,  80),
    ("I/O field_63", "AI_B7_CHWS_TT01_Temp",       "°C",  50,  80),
    ("I/O field_64", "AI_B7_CHWS_TT02_Temp",       "°C",  50,  80),
    ("I/O field_65", "AI_B7_K03_TT03_Temp",        "°C",  50,  80),
]

ALL_SCREENS_TAGS = {
    "scadabai3": B3_TAGS,
    "scadabai4": B4_TAGS,
    "scadabai5": B5_TAGS,
    "scadabai6": B6_TAGS,
    "scadabai7": B7_TAGS,
}

for screen_name, tags_def in ALL_SCREENS_TAGS.items():
    source_file = os.path.join(SCRATCH_DIR, f"{screen_name}_export.xml")
    dest_file = os.path.join(OUTPUT_DIR, f"Hmi.Screen.{screen_name}.xml")
    
    if not os.path.exists(source_file):
        print(f"[ERROR] Source file not found: {source_file}")
        continue
        
    print(f"\nProcessing screen: {screen_name}...")
    
    # Register namespaces to preserve XML format
    ET.register_namespace('', '')
    tree = ET.parse(source_file)
    root = tree.getroot()
    
    # 1. Determine max ID to prevent collisions
    max_id = 0
    for elem in root.iter():
        id_attr = elem.get("ID")
        if id_attr:
            try:
                val = int(id_attr, 16)
                if val > max_id:
                    max_id = val
            except ValueError:
                pass
    id_counter = max_id + 1000
    
    def get_next_id():
        global id_counter
        res = hex(id_counter)[2:].upper()
        id_counter += 1
        return res

    # Find the Screen Layer containing ScreenItems
    layer = root.find(".//Hmi.Screen.ScreenLayer")
    if layer is None:
        print(f"  [ERROR] Hmi.Screen.ScreenLayer not found in {screen_name}")
        continue
        
    object_list = layer.find("ObjectList")
    if object_list is None:
        object_list = ET.SubElement(layer, "ObjectList")

    # Map tags definitions for quick lookup
    tag_map = {item[0]: item for item in tags_def}
    
    # 2. Iterate and patch IOFields
    io_fields_patched = 0
    for elem in object_list:
        if elem.tag.endswith("IOField"):
            name_el = elem.find("AttributeList/ObjectName")
            if name_el is not None and name_el.text:
                io_name = name_el.text.strip()
                if io_name in tag_map:
                    _, tag_name, unit_val, lo, hi = tag_map[io_name]
                    
                    # A. Bind Tag to IOField ProcessValue property
                    props_list = elem.find("ObjectList")
                    if props_list is None:
                        props_list = ET.SubElement(elem, "ObjectList")
                        
                    prop_val = None
                    for prop in props_list:
                        if prop.tag.endswith("Property"):
                            n_el = prop.find("AttributeList/Name")
                            if n_el is not None and n_el.text == "ProcessValue":
                                prop_val = prop
                                break
                                
                    if prop_val is None:
                        prop_val = ET.SubElement(props_list, "Hmi.Screen.Property", {
                            "ID": get_next_id(),
                            "CompositionName": "Properties"
                        })
                        prop_attrs = ET.SubElement(prop_val, "AttributeList")
                        ET.SubElement(prop_attrs, "Name").text = "ProcessValue"
                        
                    prop_objs = prop_val.find("ObjectList")
                    if prop_objs is None:
                        prop_objs = ET.SubElement(prop_val, "ObjectList")
                        
                    tag_conn = prop_objs.find(".//TagConnectionDynamic") or prop_objs.find(".//Hmi.Dynamic.TagConnectionDynamic")
                    if tag_conn is None:
                        tag_conn = ET.SubElement(prop_objs, "Hmi.Dynamic.TagConnectionDynamic", {
                            "ID": get_next_id(),
                            "CompositionName": "Dynamic"
                        })
                        conn_attrs = ET.SubElement(tag_conn, "AttributeList")
                        ET.SubElement(conn_attrs, "Indirect").text = "false"
                        link_list = ET.SubElement(tag_conn, "LinkList")
                        tag_el = ET.SubElement(link_list, "Tag", {"TargetID": "@OpenLink"})
                        ET.SubElement(tag_el, "Name").text = tag_name
                    else:
                        tag_el = tag_conn.find(".//Tag")
                        if tag_el is not None:
                            name_el = tag_el.find("Name")
                            if name_el is not None: name_el.text = tag_name
                            else: ET.SubElement(tag_el, "Name").text = tag_name
                        else:
                            link_list = tag_conn.find("LinkList") or ET.SubElement(tag_conn, "LinkList")
                            tag_el = ET.SubElement(link_list, "Tag", {"TargetID": "@OpenLink"})
                            ET.SubElement(tag_el, "Name").text = tag_name

                    # B. Align Center/Middle and Set FormatPattern based on Max value
                    attr_list = elem.find("AttributeList")
                    if attr_list is not None:
                        ha = attr_list.find("HorizontalAlignment")
                        if ha is not None: ha.text = "Center"
                        else: ET.SubElement(attr_list, "HorizontalAlignment").text = "Center"
                        
                        va = attr_list.find("VerticalAlignment")
                        if va is not None: va.text = "Middle"
                        else: ET.SubElement(attr_list, "VerticalAlignment").text = "Middle"
                        
                        # Formatting rule: hi < 100 -> 99.9, hi >= 100 -> 999.9
                        format_pat = "99.9" if hi < 100 else "999.9"
                        fp_el = attr_list.find("FormatPattern")
                        if fp_el is not None: fp_el.text = format_pat
                        else: ET.SubElement(attr_list, "FormatPattern").text = format_pat
                        
                        # Get coordinates for unit label placement
                        left_el = attr_list.find("Left")
                        top_el = attr_list.find("Top")
                        width_el = attr_list.find("Width")
                        height_el = attr_list.find("Height")
                        
                        io_left = int(left_el.text) if (left_el is not None and left_el.text) else 0
                        io_top = int(top_el.text) if (top_el is not None and top_el.text) else 0
                        io_w = int(width_el.text) if (width_el is not None and width_el.text) else 0
                        io_h = int(height_el.text) if (height_el is not None and height_el.text) else 0

                        # C. Handle Unit Label TextField (Right 8px, Arial 13 Bold)
                        if unit_val:
                            unit_obj_name = f"Text_field_Unit_{io_name}"
                            unit_tf = None
                            
                            # Search for existing unit text field
                            for sub_el in object_list:
                                if sub_el.tag.endswith("TextField"):
                                    sub_name = sub_el.find("AttributeList/ObjectName")
                                    if sub_name is not None and sub_name.text == unit_obj_name:
                                        unit_tf = sub_el
                                        break
                                        
                            tf_left = io_left + io_w + 8
                            tf_top = io_top
                            tf_width = 50
                            tf_height = io_h
                            
                            if unit_tf is None:
                                # Create new unit label
                                unit_tf = ET.SubElement(object_list, "Hmi.Screen.TextField", {
                                    "ID": get_next_id(),
                                    "CompositionName": "ScreenItems"
                                })
                                ut_attrs = ET.SubElement(unit_tf, "AttributeList")
                                ET.SubElement(ut_attrs, "BackColor").text = "255, 255, 255"
                                ET.SubElement(ut_attrs, "BackFillStyle").text = "Transparent"
                                ET.SubElement(ut_attrs, "BorderWidth").text = "0"
                                ET.SubElement(ut_attrs, "ForeColor").text = "0, 0, 0"
                                ET.SubElement(ut_attrs, "Height").text = str(tf_height)
                                ET.SubElement(ut_attrs, "HorizontalAlignment").text = "Left"
                                ET.SubElement(ut_attrs, "Left").text = str(tf_left)
                                ET.SubElement(ut_attrs, "ObjectName").text = unit_obj_name
                                ET.SubElement(ut_attrs, "Top").text = str(tf_top)
                                ET.SubElement(ut_attrs, "VerticalAlignment").text = "Middle"
                                ET.SubElement(ut_attrs, "Width").text = str(tf_width)
                                
                                ut_objs = ET.SubElement(unit_tf, "ObjectList")
                                
                                # Multilingual font
                                font = ET.SubElement(ut_objs, "Hmi.Globalization.MultiLingualFont", {
                                    "ID": get_next_id(),
                                    "CompositionName": "Font"
                                })
                                font_objs = ET.SubElement(font, "ObjectList")
                                font_item = ET.SubElement(font_objs, "Hmi.Globalization.FontItem", {
                                    "ID": get_next_id(),
                                    "CompositionName": "Items"
                                })
                                fi_attrs = ET.SubElement(font_item, "AttributeList")
                                ET.SubElement(fi_attrs, "Culture").text = "en-US"
                                ET.SubElement(fi_attrs, "FontFamily").text = "Arial"
                                ET.SubElement(fi_attrs, "FontSize").text = "13"
                                ET.SubElement(fi_attrs, "FontStyle").text = "Bold"
                                
                                # Multilingual text
                                ml_text = ET.SubElement(ut_objs, "MultilingualText", {
                                    "ID": get_next_id(),
                                    "CompositionName": "Text"
                                })
                                ml_objs = ET.SubElement(ml_text, "ObjectList")
                                ml_item = ET.SubElement(ml_objs, "MultilingualTextItem", {
                                    "ID": get_next_id(),
                                    "CompositionName": "Items"
                                })
                                item_attrs = ET.SubElement(ml_item, "AttributeList")
                                ET.SubElement(item_attrs, "Culture").text = "en-US"
                                ET.SubElement(item_attrs, "Text").text = f"<body><p>{unit_val}</p></body>"
                            else:
                                # Update existing unit label
                                ut_attrs = unit_tf.find("AttributeList")
                                if ut_attrs is not None:
                                    left_el = ut_attrs.find("Left")
                                    if left_el is not None: left_el.text = str(tf_left)
                                    else: ET.SubElement(ut_attrs, "Left").text = str(tf_left)
                                    
                                    top_el = ut_attrs.find("Top")
                                    if top_el is not None: top_el.text = str(tf_top)
                                    else: ET.SubElement(ut_attrs, "Top").text = str(tf_top)
                                    
                                    ha_el = ut_attrs.find("HorizontalAlignment")
                                    if ha_el is not None: ha_el.text = "Left"
                                    
                                    va_el = ut_attrs.find("VerticalAlignment")
                                    if va_el is not None: va_el.text = "Middle"
                                    
                                    fs_el = ut_attrs.find("BackFillStyle")
                                    if fs_el is not None: fs_el.text = "Transparent"
                                    
                                    bw_el = ut_attrs.find("BorderWidth")
                                    if bw_el is not None: bw_el.text = "0"
                                    
                                text_item = unit_tf.find(".//MultilingualTextItem/AttributeList")
                                if text_item is not None:
                                    txt_el = text_item.find("Text")
                                    if txt_el is not None:
                                        txt_el.text = f"<body><p>{unit_val}</p></body>"
                                        
                                font_item_attrs = unit_tf.find(".//Hmi.Globalization.FontItem/AttributeList")
                                if font_item_attrs is not None:
                                    ff = font_item_attrs.find("FontFamily")
                                    if ff is not None: ff.text = "Arial"
                                    fs = font_item_attrs.find("FontSize")
                                    if fs is not None: fs.text = "13"
                                    fsty = font_item_attrs.find("FontStyle")
                                    if fsty is not None: fsty.text = "Bold"

                    io_fields_patched += 1
                    
    # Write the patched screen XML back
    tree.write(dest_file, encoding="utf-8", xml_declaration=True)
    print(f"  [OK] Patched {io_fields_patched} IOFields on screen. Saved to: {dest_file}")

print("\nAll screens patched successfully!")
