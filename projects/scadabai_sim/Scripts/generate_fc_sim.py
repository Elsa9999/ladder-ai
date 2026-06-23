# -*- coding: utf-8 -*-
"""
generate_fc_sim.py
Sinh FC_SCADA_Sim_B3to7.xml + PLC_Tags_B3to7.xml + HMI_Tags_B3to7_All.xml
Theo đúng pattern bài 1 (FC_SCADA_Simulation.xml)
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

OUT_PLC = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC"
OUT_HMI = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\HMI"
os.makedirs(OUT_PLC, exist_ok=True)
os.makedirs(OUT_HMI, exist_ok=True)

# ============================================================
# DANH SÁCH TAGS (prefix, suffix, lo, hi, unit)
# ============================================================
ALL_TAGS = [
    # ===== BÀI 3 - CIP PSC MODE =====
    ("AI_B3_", "Sequence_Count",     0,    100,  ""),
    ("AI_B3_", "Flow_CIP_Center",    100,  200,  "L/h"),
    ("AI_B3_", "Temp_CIP_Upper",     50,   80,   "°C"),
    ("AI_B3_", "Pressure_CIP_1",     7.0,  8.0,  "bar"),
    ("AI_B3_", "Temp_Chaff_1",       50,   80,   "°C"),
    ("AI_B3_", "Flow_CIP_Feed",      100,  200,  "L/h"),
    ("AI_B3_", "Temp_Steam_1",       50,   80,   "°C"),
    ("AI_B3_", "Flow_UCWW_1",        100,  200,  "L/h"),
    ("AI_B3_", "RPM_Screw_Conv",     800,  1200, "RPM"),
    ("AI_B3_", "Temp_Condensate_1",  50,   80,   "°C"),
    ("AI_B3_", "Pressure_Screw_1",   7.0,  8.0,  "bar"),
    ("AI_B3_", "Flow_CWW_Out",       100,  200,  "L/h"),
    ("AI_B3_", "Pressure_CWW_1",     7.0,  8.0,  "bar"),
    ("AI_B3_", "Temp_Decanter2",     50,   80,   "°C"),
    ("AI_B3_", "RPM_Rotary2",        800,  1200, "RPM"),
    ("AI_B3_", "RPM_Rotary1",        800,  1200, "RPM"),
    ("AI_B3_", "Temp_GroundSilo",    50,   80,   "°C"),
    ("AI_B3_", "Flow_GroundSilo",    100,  200,  "L/h"),
    ("AI_B3_", "Pressure_Mid_1",     7.0,  8.0,  "bar"),
    ("AI_B3_", "Flow_Condensate",    100,  200,  "L/h"),
    ("AI_B3_", "Flow_Sump_Out",      100,  200,  "L/h"),
    ("AI_B3_", "Level_Sump",         30,   80,   "%"),
    ("AI_B3_", "Pressure_Decant1",   7.0,  8.0,  "bar"),
    ("AI_B3_", "Pressure_Decant2",   7.0,  8.0,  "bar"),
    ("AI_B3_", "Flow_Decant1",       100,  200,  "L/h"),
    ("AI_B3_", "Temp_Decant1",       50,   80,   "°C"),
    ("AI_B3_", "Temp_FBB_Boiler",    50,   80,   "°C"),
    ("AI_B3_", "Temp_CWW_Out",       50,   80,   "°C"),
    ("AI_B3_", "Pressure_SUMP",      7.0,  8.0,  "bar"),
    ("AI_B3_", "Flow_SUMP",          100,  200,  "L/h"),
    ("AI_B3_", "Level_CWW",          30,   80,   "%"),
    ("AI_B3_", "Temp_FBB_Out",       50,   80,   "°C"),
    ("AI_B3_", "Pressure_FBB_Out",   7.0,  8.0,  "bar"),
    ("AI_B3_", "Flow_FBB_Out",       100,  200,  "L/h"),
    # ===== BÀI 4 - BOILER AIR AND FLUE GAS =====
    ("AI_B4_", "Daq_C",              0,    100,  ""),
    ("AI_B4_", "TPH_Total",          100,  200,  "T/h"),
    ("AI_B4_", "KG_CM_Main",         7.0,  8.0,  "kg/cm2"),
    ("AI_B4_", "DRM_LVL1",           30,   80,   "%"),
    ("AI_B4_", "DRM_LVL2",           30,   80,   "%"),
    ("AI_B4_", "MW_Output",          0,    50,   "MW"),
    ("AI_B4_", "KG_CM_2",            7.0,  8.0,  "kg/cm2"),
    ("AI_B4_", "Hc_Value",           0,    100,  ""),
    ("AI_B4_", "Temp_AirHeater_In1", 50,   80,   "°C"),
    ("AI_B4_", "Temp_AirHeater_In2", 50,   80,   "°C"),
    ("AI_B4_", "Temp_AirHeater_In3", 50,   80,   "°C"),
    ("AI_B4_", "Temp_AirHeater_Out1",50,   80,   "°C"),
    ("AI_B4_", "Temp_AirHeater_Out2",50,   80,   "°C"),
    ("AI_B4_", "Pres_AH_mmWC_1",     7.0,  8.0,  "mmWC"),
    ("AI_B4_", "Pres_AH_mmWC_2",     7.0,  8.0,  "mmWC"),
    ("AI_B4_", "Pres_AH_Pct_1",      20,   80,   "%"),
    ("AI_B4_", "Temp_AH_Out3",       50,   80,   "°C"),
    ("AI_B4_", "Pres_FDH_mmWC",      7.0,  8.0,  "mmWC"),
    ("AI_B4_", "RPM_PAF1",           800,  1200, "RPM"),
    ("AI_B4_", "Pct_RPC308_SP",      20,   80,   "%"),
    ("AI_B4_", "Pct_RPC308_PV",      20,   80,   "%"),
    ("AI_B4_", "Pres_PAF1_mmWC",     7.0,  8.0,  "mmWC"),
    ("AI_B4_", "Pct_FDF1_SP",        20,   80,   "%"),
    ("AI_B4_", "Pct_FDF1_PV",        20,   80,   "%"),
    ("AI_B4_", "Pct_FDF1_OUT",       20,   80,   "%"),
    ("AI_B4_", "RPM_FDF1",           800,  1200, "RPM"),
    ("AI_B4_", "Pct_RPC301_SP",      20,   80,   "%"),
    ("AI_B4_", "Pct_RPC301_PV",      20,   80,   "%"),
    ("AI_B4_", "Pct_RPC301_OUT",     20,   80,   "%"),
    ("AI_B4_", "mA_ESP1",            50,   200,  "mA"),
    ("AI_B4_", "mA_ESP2",            50,   200,  "mA"),
    ("AI_B4_", "mA_ESP3",            50,   200,  "mA"),
    ("AI_B4_", "mA_ESP4",            50,   200,  "mA"),
    ("AI_B4_", "V_ESP1",             0,    400,  "V"),
    ("AI_B4_", "V_ESP2",             0,    400,  "V"),
    ("AI_B4_", "V_ESP3",             0,    400,  "V"),
    ("AI_B4_", "V_ESP4",             0,    400,  "V"),
    ("AI_B4_", "Pct_RPC305_SP",      20,   80,   "%"),
    ("AI_B4_", "Pct_RPC305_PV",      20,   80,   "%"),
    ("AI_B4_", "RPM_IDF1",           800,  1200, "RPM"),
    ("AI_B4_", "Pct_RPC305_VFD",     20,   80,   "%"),
    ("AI_B4_", "Pct_FDF2_SP",        20,   80,   "%"),
    ("AI_B4_", "Pct_FDF2_PV",        20,   80,   "%"),
    ("AI_B4_", "Pct_FDF2_OUT",       20,   80,   "%"),
    ("AI_B4_", "RPM_FDF2",           800,  1200, "RPM"),
    ("AI_B4_", "Pct_RPC306_SP",      20,   80,   "%"),
    ("AI_B4_", "Pct_RPC306_PV",      20,   80,   "%"),
    ("AI_B4_", "Pct_RPC306_OUT",     20,   80,   "%"),
    ("AI_B4_", "RPM_IDF2",           800,  1200, "RPM"),
    ("AI_B4_", "Pct_RPC306_VFD",     20,   80,   "%"),
    ("AI_B4_", "Pres_FDF_mmWC",      7.0,  8.0,  "mmWC"),
    ("AI_B4_", "TEST1_Value",        0,    100,  ""),
    ("AI_B4_", "Pct_PAF1_SP",        20,   80,   "%"),
    ("AI_B4_", "Pct_PAF1_PV",        20,   80,   "%"),
    ("AI_B4_", "Pres_PAF2_mmWC",     7.0,  8.0,  "mmWC"),
    ("AI_B4_", "RPM_PAF2",           800,  1200, "RPM"),
    ("AI_B4_", "Pct_RPC308b_SP",     20,   80,   "%"),
    ("AI_B4_", "Pct_RPC308b_PV",     20,   80,   "%"),
    ("AI_B4_", "Pct_DAM303B_SP",     20,   80,   "%"),
    ("AI_B4_", "Pct_DAM304B_SP",     20,   80,   "%"),
    # ===== BÀI 5 - CEMENT MILL =====
    ("AI_B5_", "CA_Fan_Motor_DE_Temp",   50,  80,   "°C"),
    ("AI_B5_", "CA_Fan_Motor_NDE_Temp",  50,  80,   "°C"),
    ("AI_B5_", "CA_Fan_DE_Temp",         50,  80,   "°C"),
    ("AI_B5_", "CA_Fan_NDE_Temp",        50,  80,   "°C"),
    ("AI_B5_", "CA_Fan_DE_Vib",          0,   10,   "mm/s"),
    ("AI_B5_", "CA_Fan_NDE_Vib",         0,   10,   "mm/s"),
    ("AI_B5_", "SP_700FN03",             100, 200,  "L/h"),
    ("AI_B5_", "SP_700HES01",            100, 200,  "L/h"),
    ("AI_B5_", "SP_700DA4",              20,  30,   "Hz"),
    ("AI_B5_", "SP_700DA6",              20,  30,   "Hz"),
    ("AI_B5_", "SP_700DA7",              20,  30,   "Hz"),
    ("AI_B5_", "SP_700FN2_DA1",          20,  30,   "Hz"),
    ("AI_B5_", "Sep_Motor_Top_Temp",     50,  80,   "°C"),
    ("AI_B5_", "Sep_Bottom_Bear_Temp",   50,  80,   "°C"),
    ("AI_B5_", "Trend_Val_1",            0,   100,  "%"),
    ("AI_B5_", "Trend_Val_2",            0,   100,  "%"),
    ("AI_B5_", "Trend_Val_3",            0,   100,  "%"),
    ("AI_B5_", "700FN03_RPM",            800, 1200, "RPM"),
    ("AI_B5_", "700HES01_Flow",          100, 200,  "L/h"),
    ("AI_B5_", "700FN10_Speed",          20,  30,   "Hz"),
    ("AI_B5_", "700CM01_Current",        50,  200,  "A"),
    ("AI_B5_", "Lub_Stop_Time",          0,   300,  "Sec"),
    ("AI_B5_", "Main_Drive_ReHealth",    0,   300,  "Sec"),
    ("AI_B5_", "CM_LRS_IN",              50,  80,   "°C"),
    ("AI_B5_", "CM_LRS_OUT",             50,  80,   "°C"),
    ("AI_B5_", "CM_Mill_Oil_Temp",       50,  80,   "°C"),
    ("AI_B5_", "CM_OilTrun_BER_Temp",    50,  80,   "°C"),
    ("AI_B5_", "CM_OilTrun_BER2_Temp",   50,  80,   "°C"),
    ("AI_B5_", "CM_OilPinion_BER_Temp",  50,  80,   "°C"),
    ("AI_B5_", "CM_GB_IL_Shaft_BER",     50,  80,   "°C"),
    ("AI_B5_", "CM_Running_Hours",       0,   8760, "Hr"),
    ("AI_B5_", "CM_PS1_1_KG",            7,   8,    "bar"),
    ("AI_B5_", "CM_PS1_2_KG",            7,   8,    "bar"),
    ("AI_B5_", "NIBS_Value",             50,  200,  "A"),
    ("AI_B5_", "800DC1_Temp",            50,  80,   "°C"),
    ("AI_B5_", "800DC2_Temp",            50,  80,   "°C"),
    ("AI_B5_", "800FN1_Speed",           20,  30,   "Hz"),
    ("AI_B5_", "800FN2_Speed",           20,  30,   "Hz"),
    ("AI_B5_", "800YF1_Flow",            100, 200,  "L/h"),
    ("AI_B5_", "800YF2_Flow",            100, 200,  "L/h"),
    ("AI_B5_", "Silo1_Level_Bar1",       0,   100,  "%"),
    ("AI_B5_", "Silo1_Level_Bar2",       0,   100,  "%"),
    ("AI_B5_", "Silo2_Level_Bar1",       0,   100,  "%"),
    ("AI_B5_", "Silo2_Level_Bar2",       0,   100,  "%"),
    ("AI_B5_", "700FN01_Speed",          20,  30,   "Hz"),
    ("AI_B5_", "700FN02_Speed",          20,  30,   "Hz"),
    ("AI_B5_", "700AS07_Speed",          20,  30,   "Hz"),
    ("AI_B5_", "700AS08_Flow",           100, 200,  "L/h"),
    ("AI_B5_", "700FN09_Speed",          20,  30,   "Hz"),
    ("AI_B5_", "700SFM01_Speed",         20,  30,   "Hz"),
    ("AI_B5_", "700DA1_Flow",            100, 200,  "L/h"),
    ("AI_B5_", "700DA4_Flow",            100, 200,  "L/h"),
    ("AI_B5_", "700DA6_Temp",            50,  80,   "°C"),
    ("AI_B5_", "700DA7_Temp",            50,  80,   "°C"),
    ("AI_B5_", "700BL1_Load",            50,  200,  "A"),
    ("AI_B5_", "700BL2_Load",            50,  200,  "A"),
    ("AI_B5_", "700AS9_Flow",            100, 200,  "L/h"),
    ("AI_B5_", "700FN13_Speed",          20,  30,   "Hz"),
    # ===== BÀI 6 - CELL CULTURE FERMENTER =====
    ("AI_B6_", "TICR211_Temp",       50,  80,  "°C"),
    ("AI_B6_", "TICR210_Temp",       50,  80,  "°C"),
    ("AI_B6_", "TICR201_Tank_Temp",  50,  80,  "°C"),
    ("AI_B6_", "PT201_Pressure",     7.0, 8.0, "bar"),
    ("AI_B6_", "Ph201_pH",           6.0, 8.0, "pH"),
    ("AI_B6_", "ORP201_ORP",         20,  80,  "%"),
    ("AI_B6_", "DPL101_Level",       100, 500, "L"),
    ("AI_B6_", "TICR214_Temp",       50,  80,  "°C"),
    ("AI_B6_", "TICR204_Temp",       50,  80,  "°C"),
    ("AI_B6_", "TICR205_Temp",       50,  80,  "°C"),
    ("AI_B6_", "TICR206_Temp",       50,  80,  "°C"),
    ("AI_B6_", "FHC203_Flow",        100, 200, "L/h"),
    ("AI_B6_", "BPC201_Pressure",    7.0, 8.0, "bar"),
    # ===== BÀI 7 - PLANTPAX DISTILLATION =====
    ("AI_B7_", "K03_PT02_Pressure",    7,    8,    "bar"),
    ("AI_B7_", "K03_TT04_Temp",        50,   80,   "°C"),
    ("AI_B7_", "K03_TT05_Temp",        50,   80,   "°C"),
    ("AI_B7_", "K03_TT06_Temp",        50,   80,   "°C"),
    ("AI_B7_", "K03_TT07_Temp",        50,   80,   "°C"),
    ("AI_B7_", "K03_PT07_Pressure",    7,    8,    "bar"),
    ("AI_B7_", "K03_FT03_Flow",        100,  200,  "L/h"),
    ("AI_B7_", "K03_Density_1",        800,  1000, "kg/m3"),
    ("AI_B7_", "K03_LT01_Level",       20,   80,   "cm"),
    ("AI_B7_", "K03_LT02_Level",       20,   80,   "cm"),
    ("AI_B7_", "K03_TT01_Temp",        50,   80,   "°C"),
    ("AI_B7_", "K03_TT02_Temp",        50,   80,   "°C"),
    ("AI_B7_", "Reboiler_PV",          100,  200,  "L/h"),
    ("AI_B7_", "Reboiler_SP",          100,  200,  "L/h"),
    ("AI_B7_", "Reboiler_CV",          20,   80,   "%"),
    ("AI_B7_", "HE03_Primary_Temp",    50,   80,   "°C"),
    ("AI_B7_", "HE03_Secondary_Temp",  50,   80,   "°C"),
    ("AI_B7_", "K03_L08_Level",        20,   80,   "cm"),
    ("AI_B7_", "K03_L06_Level",        20,   80,   "cm"),
    ("AI_B7_", "K03_L05_Level",        20,   80,   "cm"),
    ("AI_B7_", "K03_L07_Level",        20,   80,   "cm"),
    ("AI_B7_", "K03_L04_Level",        20,   80,   "cm"),
    ("AI_B7_", "K03_L03_Level",        20,   80,   "cm"),
    ("AI_B7_", "V03A_Density",         800,  1000, "kg/m3"),
    ("AI_B7_", "Kettle_Flow_SP",       100,  200,  "kg/h"),
    ("AI_B7_", "Keboiler_Flow_SP",     100,  200,  "kg/h"),
    ("AI_B7_", "Reflux_Time_SP",       0,    60,   "Min"),
    ("AI_B7_", "Time_Remain",          0,    60,   "Min"),
    ("AI_B7_", "RD_Level_SP",          20,   80,   "cm"),
    ("AI_B7_", "Reflux_Flow_SP",       100,  200,  "L/h"),
    ("AI_B7_", "Collection_SP",        100,  200,  "L/h"),
    ("AI_B7_", "Total_Flowrate",       100,  200,  "L/h"),
    ("AI_B7_", "ML_Qty_SP",            0,    600,  "L"),
    ("AI_B7_", "ML_Qty_Total",         0,    600,  "L"),
    ("AI_B7_", "Material_Code",        0,    99,   ""),
    ("AI_B7_", "Stage_Number",         0,    20,   ""),
    ("AI_B7_", "Batch_Number",         0,    9999, ""),
    ("AI_B7_", "Current_User_ID",      0,    999,  ""),
    ("AI_B7_", "K_05_L_704_HI",        20,   80,   "cm"),
    ("AI_B7_", "Density_SP",           800,  1000, "kg/m3"),
    ("AI_B7_", "CTS_Flow_1",           100,  200,  "kg/h"),
    ("AI_B7_", "CTS_Flow_2",           100,  200,  "kg/h"),
    ("AI_B7_", "Steam_PT01_Temp",      50,   80,   "°C"),
    ("AI_B7_", "Steam_PT02_Temp",      50,   80,   "°C"),
    ("AI_B7_", "CWS_TT01_Temp",        50,   80,   "°C"),
    ("AI_B7_", "CWS_TT02_Temp",        50,   80,   "°C"),
    ("AI_B7_", "CWS_TT03_Temp",        50,   80,   "°C"),
    ("AI_B7_", "CWAR_TT01_Temp",       50,   80,   "°C"),
    ("AI_B7_", "CWAR_TT02_Temp",       50,   80,   "°C"),
    ("AI_B7_", "CWAR_TT03_Temp",       50,   80,   "°C"),
    ("AI_B7_", "CWAR_TT04_Temp",       50,   80,   "°C"),
    ("AI_B7_", "K03_CV01_PV",          20,   80,   "%"),
    ("AI_B7_", "K03_CV01_SP",          20,   80,   "%"),
    ("AI_B7_", "K03_CV01_CV",          20,   80,   "%"),
    ("AI_B7_", "Steam_CV01_PV",        20,   80,   "%"),
    ("AI_B7_", "Steam_CV01_SP",        20,   80,   "%"),
    ("AI_B7_", "Steam_CV01_CV",        20,   80,   "%"),
    ("AI_B7_", "K03_Jacket_PV",        50,   80,   "°C"),
    ("AI_B7_", "K03_Jacket_SP",        50,   80,   "°C"),
    ("AI_B7_", "K03_Jacket_CV",        20,   80,   "%"),
    ("AI_B7_", "CHWR_TT01_Temp",       50,   80,   "°C"),
    ("AI_B7_", "CHWR_TT02_Temp",       50,   80,   "°C"),
    ("AI_B7_", "CHWS_TT01_Temp",       50,   80,   "°C"),
    ("AI_B7_", "CHWS_TT02_Temp",       50,   80,   "°C"),
    ("AI_B7_", "K03_TT03_Temp",        50,   80,   "°C"),
]

print(f"Tổng số tags: {len(ALL_TAGS)}")

# ============================================================
# HELPER: UID counter
# ============================================================
_uid = [0]
def next_uid():
    _uid[0] += 1
    return _uid[0]

def reset_uid(start=0):
    _uid[0] = start

# ============================================================
# GENERATE FC XML
# ============================================================
def scale_x_network(cu_id, tag_name, lo, hi, title, uid_base):
    """Sinh 1 CompileUnit chứa lệnh SCALE_X theo pattern bài 1"""
    p_scale = uid_base       # Part Scale_X
    a_min   = uid_base + 1   # Access LiteralConstant (lo)
    a_norm  = uid_base + 2   # Access GlobalVariable  (Sim_Val_Norm)
    a_max   = uid_base + 3   # Access LiteralConstant (hi)
    a_tag   = uid_base + 4   # Access GlobalVariable  (tag)
    w_en    = uid_base + 5   # Wire Powerrail->en
    w_min   = uid_base + 6   # Wire min->min
    w_val   = uid_base + 7   # Wire value->value
    w_max   = uid_base + 8   # Wire max->max
    w_out   = uid_base + 9   # Wire out->tag

    flgnet = (
        f'<FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4">'
        f'<Parts>'
        f'<Access Scope="LiteralConstant" UId="{a_min}"><Constant><ConstantType>Real</ConstantType><ConstantValue>{float(lo)}</ConstantValue></Constant></Access>'
        f'<Access Scope="GlobalVariable" UId="{a_norm}"><Symbol><Component Name="Sim_Val_Norm" /></Symbol></Access>'
        f'<Access Scope="LiteralConstant" UId="{a_max}"><Constant><ConstantType>Real</ConstantType><ConstantValue>{float(hi)}</ConstantValue></Constant></Access>'
        f'<Access Scope="GlobalVariable" UId="{a_tag}"><Symbol><Component Name="{tag_name}" /></Symbol></Access>'
        f'<Part Name="Scale_X" DisabledENO="true" UId="{p_scale}"><TemplateValue Name="SrcType" Type="Type">Real</TemplateValue><TemplateValue Name="DestType" Type="Type">Real</TemplateValue></Part>'
        f'</Parts>'
        f'<Wires>'
        f'<Wire UId="{w_en}"><Powerrail /><NameCon UId="{p_scale}" Name="en" /></Wire>'
        f'<Wire UId="{w_min}"><IdentCon UId="{a_min}" /><NameCon UId="{p_scale}" Name="min" /></Wire>'
        f'<Wire UId="{w_val}"><IdentCon UId="{a_norm}" /><NameCon UId="{p_scale}" Name="value" /></Wire>'
        f'<Wire UId="{w_max}"><IdentCon UId="{a_max}" /><NameCon UId="{p_scale}" Name="max" /></Wire>'
        f'<Wire UId="{w_out}"><NameCon UId="{p_scale}" Name="out" /><IdentCon UId="{a_tag}" /></Wire>'
        f'</Wires>'
        f'</FlgNet>'
    )
    idx = cu_id - 200
    txt_id1 = 50000 + idx * 2
    txt_id2 = 50000 + idx * 2 + 1
    return f"""      <SW.Blocks.CompileUnit ID="{cu_id}" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource>
            {flgnet}
          </NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{txt_id1}" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="{txt_id2}" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>{title}</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>
"""

# Header networks (copy exact từ bài 1, chỉ thay IDs để không trùng)
FC_HEADER_NETWORKS = """      <SW.Blocks.CompileUnit ID="21" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource>
            <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"><Parts><Access Scope="GlobalVariable" UId="22"><Symbol><Component Name="Timer_Sim_Pulse_Output" /></Symbol></Access><Access Scope="TypedConstant" UId="28"><Constant><ConstantValue>T#50MS</ConstantValue></Constant></Access><Access Scope="GlobalVariable" UId="32"><Symbol><Component Name="Timer_Sim_Pulse_Output" /></Symbol></Access><Part Name="Contact" UId="23"><Negated Name="operand" /></Part><Part Name="TON" Version="1.0" UId="27"><Instance Scope="GlobalVariable" UId="26"><Component Name="Timer_Sim_DB" /></Instance><TemplateValue Name="time_type" Type="Type">Time</TemplateValue></Part></Parts><Wires><Wire UId="24"><Powerrail /><NameCon UId="23" Name="in" /></Wire><Wire UId="25"><IdentCon UId="22" /><NameCon UId="23" Name="operand" /></Wire><Wire UId="29"><NameCon UId="23" Name="out" /><NameCon UId="27" Name="IN" /></Wire><Wire UId="30"><IdentCon UId="28" /><NameCon UId="27" Name="PT" /></Wire><Wire UId="31"><NameCon UId="27" Name="Q" /><IdentCon UId="32" /></Wire><Wire UId="34"><NameCon UId="27" Name="ET" /><OpenCon UId="33" /></Wire></Wires></FlgNet>
          </NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="35" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="36" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>Tạo xung kích hoạt chu kỳ mô phỏng (50ms)</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>
      <SW.Blocks.CompileUnit ID="37" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource>
            <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"><Parts><Access Scope="GlobalVariable" UId="38"><Symbol><Component Name="Timer_Sim_Pulse_Output" /></Symbol></Access><Access Scope="GlobalVariable" UId="42"><Symbol><Component Name="Sim_Dir" /></Symbol></Access><Access Scope="GlobalVariable" UId="47"><Symbol><Component Name="Sim_Counter" /></Symbol></Access><Access Scope="LiteralConstant" UId="48"><Constant><ConstantType>Real</ConstantType><ConstantValue>1.0</ConstantValue></Constant></Access><Access Scope="GlobalVariable" UId="49"><Symbol><Component Name="Sim_Counter" /></Symbol></Access><Part Name="Contact" UId="39" /><Part Name="Contact" UId="43"><Negated Name="operand" /></Part><Part Name="Add" UId="46"><TemplateValue Name="Card" Type="Cardinality">2</TemplateValue><TemplateValue Name="SrcType" Type="Type">Real</TemplateValue></Part></Parts><Wires><Wire UId="40"><Powerrail /><NameCon UId="39" Name="in" /></Wire><Wire UId="41"><IdentCon UId="38" /><NameCon UId="39" Name="operand" /></Wire><Wire UId="44"><NameCon UId="39" Name="out" /><NameCon UId="43" Name="in" /></Wire><Wire UId="45"><IdentCon UId="42" /><NameCon UId="43" Name="operand" /></Wire><Wire UId="50"><NameCon UId="43" Name="out" /><NameCon UId="46" Name="en" /></Wire><Wire UId="51"><IdentCon UId="47" /><NameCon UId="46" Name="in1" /></Wire><Wire UId="52"><IdentCon UId="48" /><NameCon UId="46" Name="in2" /></Wire><Wire UId="53"><NameCon UId="46" Name="out" /><IdentCon UId="49" /></Wire></Wires></FlgNet>
          </NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="54" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="55" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>Cộng Sim_Counter khi hướng đếm là Tăng (Sim_Dir = 0)</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>
      <SW.Blocks.CompileUnit ID="56" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource>
            <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"><Parts><Access Scope="GlobalVariable" UId="57"><Symbol><Component Name="Sim_Counter" /></Symbol></Access><Access Scope="LiteralConstant" UId="58"><Constant><ConstantType>Real</ConstantType><ConstantValue>100.0</ConstantValue></Constant></Access><Access Scope="GlobalVariable" UId="63"><Symbol><Component Name="Sim_Dir" /></Symbol></Access><Part Name="Ge" UId="59"><TemplateValue Name="SrcType" Type="Type">Real</TemplateValue></Part><Part Name="SCoil" UId="64" /></Parts><Wires><Wire UId="60"><Powerrail /><NameCon UId="59" Name="pre" /></Wire><Wire UId="61"><IdentCon UId="57" /><NameCon UId="59" Name="in1" /></Wire><Wire UId="62"><IdentCon UId="58" /><NameCon UId="59" Name="in2" /></Wire><Wire UId="65"><NameCon UId="59" Name="out" /><NameCon UId="64" Name="in" /></Wire><Wire UId="66"><IdentCon UId="63" /><NameCon UId="64" Name="operand" /></Wire></Wires></FlgNet>
          </NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="67" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="68" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>Chuyển sang hướng giảm khi Sim_Counter đạt cực đại &gt;= 100.0</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>
      <SW.Blocks.CompileUnit ID="69" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource>
            <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"><Parts><Access Scope="GlobalVariable" UId="70"><Symbol><Component Name="Timer_Sim_Pulse_Output" /></Symbol></Access><Access Scope="GlobalVariable" UId="74"><Symbol><Component Name="Sim_Dir" /></Symbol></Access><Access Scope="GlobalVariable" UId="79"><Symbol><Component Name="Sim_Counter" /></Symbol></Access><Access Scope="LiteralConstant" UId="80"><Constant><ConstantType>Real</ConstantType><ConstantValue>1.0</ConstantValue></Constant></Access><Access Scope="GlobalVariable" UId="81"><Symbol><Component Name="Sim_Counter" /></Symbol></Access><Part Name="Contact" UId="71" /><Part Name="Contact" UId="75" /><Part Name="Sub" UId="78"><TemplateValue Name="SrcType" Type="Type">Real</TemplateValue></Part></Parts><Wires><Wire UId="72"><Powerrail /><NameCon UId="71" Name="in" /></Wire><Wire UId="73"><IdentCon UId="70" /><NameCon UId="71" Name="operand" /></Wire><Wire UId="76"><NameCon UId="71" Name="out" /><NameCon UId="75" Name="in" /></Wire><Wire UId="77"><IdentCon UId="74" /><NameCon UId="75" Name="operand" /></Wire><Wire UId="82"><NameCon UId="75" Name="out" /><NameCon UId="78" Name="en" /></Wire><Wire UId="83"><IdentCon UId="79" /><NameCon UId="78" Name="in1" /></Wire><Wire UId="84"><IdentCon UId="80" /><NameCon UId="78" Name="in2" /></Wire><Wire UId="85"><NameCon UId="78" Name="out" /><IdentCon UId="81" /></Wire></Wires></FlgNet>
          </NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="86" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="87" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>Trừ Sim_Counter khi hướng đếm là Giảm (Sim_Dir = 1)</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>
      <SW.Blocks.CompileUnit ID="88" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource>
            <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"><Parts><Access Scope="GlobalVariable" UId="89"><Symbol><Component Name="Sim_Counter" /></Symbol></Access><Access Scope="LiteralConstant" UId="90"><Constant><ConstantType>Real</ConstantType><ConstantValue>0.0</ConstantValue></Constant></Access><Access Scope="GlobalVariable" UId="95"><Symbol><Component Name="Sim_Dir" /></Symbol></Access><Part Name="Le" UId="91"><TemplateValue Name="SrcType" Type="Type">Real</TemplateValue></Part><Part Name="RCoil" UId="96" /></Parts><Wires><Wire UId="92"><Powerrail /><NameCon UId="91" Name="pre" /></Wire><Wire UId="93"><IdentCon UId="89" /><NameCon UId="91" Name="in1" /></Wire><Wire UId="94"><IdentCon UId="90" /><NameCon UId="91" Name="in2" /></Wire><Wire UId="97"><NameCon UId="91" Name="out" /><NameCon UId="96" Name="in" /></Wire><Wire UId="98"><IdentCon UId="95" /><NameCon UId="96" Name="operand" /></Wire></Wires></FlgNet>
          </NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="99" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="100" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>Chuyển sang hướng tăng khi Sim_Counter đạt cực tiểu &lt;= 0.0</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>
      <SW.Blocks.CompileUnit ID="101" CompositionName="CompileUnits">
        <AttributeList>
          <NetworkSource>
            <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"><Parts><Access Scope="LiteralConstant" UId="104"><Constant><ConstantType>Real</ConstantType><ConstantValue>0.0</ConstantValue></Constant></Access><Access Scope="GlobalVariable" UId="106"><Symbol><Component Name="Sim_Counter" /></Symbol></Access><Access Scope="LiteralConstant" UId="108"><Constant><ConstantType>Real</ConstantType><ConstantValue>100.0</ConstantValue></Constant></Access><Access Scope="GlobalVariable" UId="110"><Symbol><Component Name="Sim_Val_Norm" /></Symbol></Access><Part Name="Normalize" DisabledENO="true" UId="102"><TemplateValue Name="SrcType" Type="Type">Real</TemplateValue><TemplateValue Name="DestType" Type="Type">Real</TemplateValue></Part></Parts><Wires><Wire UId="103"><Powerrail /><NameCon UId="102" Name="en" /></Wire><Wire UId="105"><IdentCon UId="104" /><NameCon UId="102" Name="min" /></Wire><Wire UId="107"><IdentCon UId="106" /><NameCon UId="102" Name="value" /></Wire><Wire UId="109"><IdentCon UId="108" /><NameCon UId="102" Name="max" /></Wire><Wire UId="111"><NameCon UId="102" Name="out" /><IdentCon UId="110" /></Wire></Wires></FlgNet>
          </NetworkSource>
          <ProgrammingLanguage>LAD</ProgrammingLanguage>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="112" CompositionName="Title">
            <ObjectList>
              <MultilingualTextItem ID="113" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>Chuẩn hóa Sim_Counter từ dải 0.0-100.0 về dải 0.0-1.0 (Sim_Val_Norm)</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Blocks.CompileUnit>
"""

# Build FC XML
fc_xml = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-12T02:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Blocks.FC ID="0">
    <AttributeList>
      <AutoNumber>true</AutoNumber>
      <HeaderVersion>0.1</HeaderVersion>
      <Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
        <Section Name="Input" />
        <Section Name="Output" />
        <Section Name="InOut" />
        <Section Name="Temp" />
        <Section Name="Constant" />
        <Section Name="Return"><Member Name="Ret_Val" Datatype="Void" Accessibility="Public" /></Section>
      </Sections></Interface>
      <IsIECCheckEnabled>false</IsIECCheckEnabled>
      <MemoryLayout>Optimized</MemoryLayout>
      <Name>FC_SCADA_Sim_B3to7</Name>
      <Namespace />
      <Number>11</Number>
      <ProgrammingLanguage>LAD</ProgrammingLanguage>
    </AttributeList>
    <ObjectList>
'''

fc_xml += FC_HEADER_NETWORKS

# Add SCALE_X networks for each tag
for idx, (prefix, suffix, lo, hi, unit) in enumerate(ALL_TAGS):
    tag_name = f"{prefix}{suffix}"
    cu_id = 200 + idx        # CompileUnit IDs: 200, 201, 202...
    uid_base = 10000 + idx * 10  # UIds: 10000-10009, 10010-10019...
    
    title = f"Tỷ lệ hóa {tag_name} ({float(lo)} - {float(hi)} {unit})"
    fc_xml += scale_x_network(cu_id, tag_name, lo, hi, title, uid_base)

fc_xml += '''    </ObjectList>
  </SW.Blocks.FC>
</Document>
'''

fc_path = os.path.join(OUT_PLC, "FC_SCADA_Sim_B3to7.xml")
with open(fc_path, "w", encoding="utf-8") as f:
    f.write(fc_xml)
print(f"✅ FC XML: {fc_path} ({len(fc_xml)//1024} KB, {len(ALL_TAGS)+6} networks)")

# ============================================================
# GENERATE PLC TAGS XML (All 230 + Sim control tags)
# ============================================================
plc_xml = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-12T02:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Tags.PlcTagTable ID="0">
    <AttributeList>
      <Name>PLC_Tags_B3to7</Name>
    </AttributeList>
    <ObjectList>
'''

def plc_tag(tid, name, dtype, addr, comment):
    return f"""      <SW.Tags.PlcTag ID="{tid}" CompositionName="Tags">
        <AttributeList>
          <DataTypeName>{dtype}</DataTypeName>
          <ExternalAccessible>true</ExternalAccessible>
          <ExternalVisible>true</ExternalVisible>
          <ExternalWritable>true</ExternalWritable>
          <LogicalAddress>{addr}</LogicalAddress>
          <Name>{name}</Name>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{tid+1}" CompositionName="Comment">
            <ObjectList>
              <MultilingualTextItem ID="{tid+2}" CompositionName="Items">
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

# Sim control tags (không trùng với B3-B7 data range MD0-1056)
plc_xml += plc_tag(1, "Timer_Sim_Pulse_Output", "Bool", "%M210.0", "Xung 50ms cho simulation")
plc_xml += plc_tag(4, "Sim_Dir", "Bool", "%M210.1", "Hướng đếm: 0=Tăng, 1=Giảm")
plc_xml += plc_tag(7, "Sim_Counter", "Real", "%MD1200", "Bộ đếm 0-100 cho simulation")
plc_xml += plc_tag(10, "Sim_Val_Norm", "Real", "%MD1204", "Giá trị chuẩn hóa 0.0-1.0")

# B3 tags: MD0-MD132 (34 tags x 4)
# B4 tags: MD200-MD436 (60 tags x 4)
# B5 tags: MD400-MD628 (58 tags x 4)  ← NOTE: B4 ends at 436, B5 starts 400, overlapping!
# Fix: B5 starts at MD500
# B6 tags: MD800-MD848 (13 tags x 4)
# B7 tags: MD1000-MD1256 (65 tags x 4)  ← NOTE: Sim_Counter at MD1200 overlaps!
# Fix: Sim_Counter at MD2000+, B7 ends at MD1256 so use MD2000+

# Corrected address ranges:
# B3: MD0-MD132     (34 x 4 = 136 bytes, ends before MD136)
# B4: MD200-MD436   (60 x 4 = 240 bytes, ends before MD440)
# B5: MD500-MD728   (58 x 4 = 232 bytes, ends before MD732)
# B6: MD800-MD848   (13 x 4 = 52 bytes)
# B7: MD900-MD1156  (65 x 4 = 260 bytes)
# Sim: MD2000+

addr_bases = {
    "AI_B3_": 0,
    "AI_B4_": 200,
    "AI_B5_": 500,
    "AI_B6_": 800,
    "AI_B7_": 900,
}
counters = {p: 0 for p in addr_bases}

tid = 20  # start tag ID after sim control tags
for prefix, suffix, lo, hi, unit in ALL_TAGS:
    tag_name = f"{prefix}{suffix}"
    idx = counters[prefix]
    addr = addr_bases[prefix] + idx * 4
    counters[prefix] += 1
    comment = f"{lo}-{hi} {unit}".strip()
    plc_xml += plc_tag(tid, tag_name, "Real", f"%MD{addr}", comment)
    tid += 3

plc_xml += '''    </ObjectList>
  </SW.Tags.PlcTagTable>
</Document>
'''

plc_path = os.path.join(OUT_PLC, "PLC_Tags_B3to7.xml")
with open(plc_path, "w", encoding="utf-8") as f:
    f.write(plc_xml)
print(f"✅ PLC Tags: {plc_path} ({len(ALL_TAGS)+4} tags)")

# ============================================================
# GENERATE COMBINED HMI TAGS XML (All 230 tags, 1 table)
# ============================================================
hmi_xml = '''<?xml version="1.0" encoding="utf-8"?>
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
  <Hmi.Tag.TagTable ID="0">
    <AttributeList>
      <Name>HMI_Tags_B3to7</Name>
    </AttributeList>
    <ObjectList>
'''

for idx, (prefix, suffix, lo, hi, unit) in enumerate(ALL_TAGS):
    tag_name = f"{prefix}{suffix}"
    tid = idx * 3 + 1
    comment = f"{lo}-{hi} {unit}".strip()
    hmi_xml += f"""      <Hmi.Tag.Tag ID="{tid}" CompositionName="Tags">
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
            <Name>{tag_name}</Name>
          </ControllerTag>
          <DataType TargetID="@OpenLink">
            <Name>Real</Name>
          </DataType>
          <HmiDataType TargetID="@OpenLink">
            <Name>Real</Name>
          </HmiDataType>
        </LinkList>
        <ObjectList>
          <MultilingualText ID="{tid+1}" CompositionName="Comment">
            <ObjectList>
              <MultilingualTextItem ID="{tid+2}" CompositionName="Items">
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

hmi_xml += '''    </ObjectList>
  </Hmi.Tag.TagTable>
</Document>
'''

hmi_path = os.path.join(OUT_HMI, "HMI_Tags_B3to7_All.xml")
with open(hmi_path, "w", encoding="utf-8") as f:
    f.write(hmi_xml)
print(f"✅ HMI Tags: {hmi_path} ({len(ALL_TAGS)} tags)")

# ============================================================
# SINH Timer_Sim_DB XML (IEC_Timer instance)
# ============================================================
timer_db = '''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-12T02:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Blocks.InstanceDB ID="0">
    <AttributeList>
      <AutoNumber>true</AutoNumber>
      <InstanceOfName>IEC_TIMER</InstanceOfName>
      <Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
  <Section Name="Static">
    <Member Name="PT" Datatype="Time" Remanence="NonRetain" Accessibility="Public"><AttributeList><BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute></AttributeList></Member>
    <Member Name="ET" Datatype="Time" Remanence="NonRetain" Accessibility="Public"><AttributeList><BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalWritable" SystemDefined="true">false</BooleanAttribute><BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute></AttributeList></Member>
    <Member Name="IN" Datatype="Bool" Remanence="NonRetain" Accessibility="Public"><AttributeList><BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute></AttributeList></Member>
    <Member Name="Q" Datatype="Bool" Remanence="NonRetain" Accessibility="Public"><AttributeList><BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalWritable" SystemDefined="true">false</BooleanAttribute><BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute></AttributeList></Member>
  </Section>
</Sections></Interface>
      <Name>Timer_Sim_DB</Name>
      <Namespace />
      <Number>12</Number>
      <OfSystemLibElement>IEC_TIMER</OfSystemLibElement>
      <OfSystemLibVersion>1.0</OfSystemLibVersion>
      <ProgrammingLanguage>DB</ProgrammingLanguage>
    </AttributeList>
    <ObjectList />
  </SW.Blocks.InstanceDB>
</Document>
'''
timer_db_path = os.path.join(OUT_PLC, "Timer_Sim_DB.xml")
with open(timer_db_path, "w", encoding="utf-8") as f:
    f.write(timer_db)
print(f"✅ Timer DB: {timer_db_path}")

print(f"""
============================================================
TỔNG KẾT:
  FC XML  : {os.path.basename(fc_path)}  ({len(ALL_TAGS)+6} networks)
  PLC Tags: {os.path.basename(plc_path)} ({len(ALL_TAGS)+4} tags)
  HMI Tags: {os.path.basename(hmi_path)} ({len(ALL_TAGS)} tags)
  Timer DB: {os.path.basename(timer_db_path)}

BƯỚC TIẾP THEO - Import vào TIA Portal theo thứ tự:
  1. Import PLC_Tags_B3to7.xml  → PLC_1 > Tags
  2. Import Timer_Sim_DB.xml    → PLC_1 > Program blocks
  3. Import FC_SCADA_Sim_B3to7.xml → PLC_1 > Program blocks
  4. Import HMI_Tags_B3to7_All.xml → HMI_RT_1 > HMI tags
  5. Gọi FC_SCADA_Sim_B3to7 từ OB1 (hoặc OB30 cyclic)
  6. Compile & Download
============================================================
""")
