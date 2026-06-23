# -*- coding: utf-8 -*-
"""
plc_sim_all_screens.py
Mô phỏng 230 tags cho 5 màn hình scadabai3→7
Viết giá trị dao động vào PLC qua WinCC RT connection
(Dùng OPC UA hoặc shared memory -- ở đây dùng pymodbus TCP)
"""
import sys, os, time, math, random
sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("SCADA SIMULATION - ALL SCREENS (B3→B7)")
print("Nhiệt độ: 50-80°C | Áp suất: 7-8 bar")
print("Lưu lượng: 100-200 L/h | Tần số: 20-30 Hz")
print("="*60)
print()

# ============================================================
# SIMULATION DATA - tất cả tags với thông số dao động
# Format: (tag_name, sim_min, sim_max, phase_offset, unit)
# ============================================================

SIM_TAGS = {
    # ===== BÀI 3 - CIP PSC MODE =====
    "AI_B3_Sequence_Count":    (0,    100,  0.0,  "count"),
    "AI_B3_Flow_CIP_Center":   (100,  200,  0.1,  "L/h"),
    "AI_B3_Temp_CIP_Upper":    (50,   80,   0.2,  "°C"),
    "AI_B3_Pressure_CIP_1":    (7.0,  8.0,  0.3,  "bar"),
    "AI_B3_Temp_Chaff_1":      (50,   80,   0.4,  "°C"),
    "AI_B3_Flow_CIP_Feed":     (100,  200,  0.5,  "L/h"),
    "AI_B3_Temp_Steam_1":      (50,   80,   0.6,  "°C"),
    "AI_B3_Flow_UCWW_1":       (100,  200,  0.7,  "L/h"),
    "AI_B3_RPM_Screw_Conv":    (800,  1200, 0.8,  "RPM"),
    "AI_B3_Temp_Condensate_1": (50,   80,   0.9,  "°C"),
    "AI_B3_Pressure_Screw_1":  (7.0,  8.0,  1.0,  "bar"),
    "AI_B3_Flow_CWW_Out":      (100,  200,  1.1,  "L/h"),
    "AI_B3_Pressure_CWW_1":    (7.0,  8.0,  1.2,  "bar"),
    "AI_B3_Temp_Decanter2":    (50,   80,   1.3,  "°C"),
    "AI_B3_RPM_Rotary2":       (800,  1200, 1.4,  "RPM"),
    "AI_B3_RPM_Rotary1":       (800,  1200, 1.5,  "RPM"),
    "AI_B3_Temp_GroundSilo":   (50,   80,   1.6,  "°C"),
    "AI_B3_Flow_GroundSilo":   (100,  200,  1.7,  "L/h"),
    "AI_B3_Pressure_Mid_1":    (7.0,  8.0,  1.8,  "bar"),
    "AI_B3_Flow_Condensate":   (100,  200,  1.9,  "L/h"),
    "AI_B3_Flow_Sump_Out":     (100,  200,  2.0,  "L/h"),
    "AI_B3_Level_Sump":        (30,   80,   2.1,  "%"),
    "AI_B3_Pressure_Decant1":  (7.0,  8.0,  2.2,  "bar"),
    "AI_B3_Pressure_Decant2":  (7.0,  8.0,  2.3,  "bar"),
    "AI_B3_Flow_Decant1":      (100,  200,  2.4,  "L/h"),
    "AI_B3_Temp_Decant1":      (50,   80,   2.5,  "°C"),
    "AI_B3_Temp_FBB_Boiler":   (50,   80,   2.6,  "°C"),
    "AI_B3_Temp_CWW_Out":      (50,   80,   2.7,  "°C"),
    "AI_B3_Pressure_SUMP":     (7.0,  8.0,  2.8,  "bar"),
    "AI_B3_Flow_SUMP":         (100,  200,  2.9,  "L/h"),
    "AI_B3_Level_CWW":         (30,   80,   3.0,  "%"),
    "AI_B3_Temp_FBB_Out":      (50,   80,   3.1,  "°C"),
    "AI_B3_Pressure_FBB_Out":  (7.0,  8.0,  3.2,  "bar"),
    "AI_B3_Flow_FBB_Out":      (100,  200,  3.3,  "L/h"),

    # ===== BÀI 4 - BOILER AIR AND FLUE GAS =====
    "AI_B4_Daq_C":             (0,    100,  0.5,  ""),
    "AI_B4_TPH_Total":         (100,  200,  0.6,  "T/h"),
    "AI_B4_KG_CM_Main":        (7.0,  8.0,  0.7,  "kg/cm2"),
    "AI_B4_DRM_LVL1":          (30,   80,   0.8,  "%"),
    "AI_B4_DRM_LVL2":          (30,   80,   0.9,  "%"),
    "AI_B4_MW_Output":         (0,    50,   1.0,  "MW"),
    "AI_B4_KG_CM_2":           (7.0,  8.0,  1.1,  "kg/cm2"),
    "AI_B4_Hc_Value":          (0,    100,  1.2,  ""),
    "AI_B4_Temp_AirHeater_In1":(50,   80,   1.3,  "°C"),
    "AI_B4_Temp_AirHeater_In2":(50,   80,   1.4,  "°C"),
    "AI_B4_Temp_AirHeater_In3":(50,   80,   1.5,  "°C"),
    "AI_B4_Temp_AirHeater_Out1":(50,  80,   1.6,  "°C"),
    "AI_B4_Temp_AirHeater_Out2":(50,  80,   1.7,  "°C"),
    "AI_B4_Pres_AH_mmWC_1":   (7.0,  8.0,  1.8,  "mmWC"),
    "AI_B4_Pres_AH_mmWC_2":   (7.0,  8.0,  1.9,  "mmWC"),
    "AI_B4_Pres_AH_Pct_1":    (20,   80,   2.0,  "%"),
    "AI_B4_Temp_AH_Out3":      (50,   80,   2.1,  "°C"),
    "AI_B4_Pres_FDH_mmWC":    (7.0,  8.0,  2.2,  "mmWC"),
    "AI_B4_RPM_PAF1":          (800,  1200, 2.3,  "RPM"),
    "AI_B4_Pct_RPC308_SP":     (20,   80,   2.4,  "%"),
    "AI_B4_Pct_RPC308_PV":     (20,   80,   2.5,  "%"),
    "AI_B4_Pres_PAF1_mmWC":   (7.0,  8.0,  2.6,  "mmWC"),
    "AI_B4_Pct_FDF1_SP":       (20,   80,   2.7,  "%"),
    "AI_B4_Pct_FDF1_PV":       (20,   80,   2.8,  "%"),
    "AI_B4_Pct_FDF1_OUT":      (20,   80,   2.9,  "%"),
    "AI_B4_RPM_FDF1":          (800,  1200, 3.0,  "RPM"),
    "AI_B4_Pct_RPC301_SP":     (20,   80,   3.1,  "%"),
    "AI_B4_Pct_RPC301_PV":     (20,   80,   3.2,  "%"),
    "AI_B4_Pct_RPC301_OUT":    (20,   80,   3.3,  "%"),
    "AI_B4_mA_ESP1":           (50,   200,  3.4,  "mA"),
    "AI_B4_mA_ESP2":           (50,   200,  3.5,  "mA"),
    "AI_B4_mA_ESP3":           (50,   200,  3.6,  "mA"),
    "AI_B4_mA_ESP4":           (50,   200,  3.7,  "mA"),
    "AI_B4_V_ESP1":            (0,    400,  3.8,  "V"),
    "AI_B4_V_ESP2":            (0,    400,  3.9,  "V"),
    "AI_B4_V_ESP3":            (0,    400,  4.0,  "V"),
    "AI_B4_V_ESP4":            (0,    400,  4.1,  "V"),
    "AI_B4_Pct_RPC305_SP":     (20,   80,   4.2,  "%"),
    "AI_B4_Pct_RPC305_PV":     (20,   80,   4.3,  "%"),
    "AI_B4_RPM_IDF1":          (800,  1200, 4.4,  "RPM"),
    "AI_B4_Pct_RPC305_VFD":    (20,   80,   4.5,  "%"),
    "AI_B4_Pct_FDF2_SP":       (20,   80,   4.6,  "%"),
    "AI_B4_Pct_FDF2_PV":       (20,   80,   4.7,  "%"),
    "AI_B4_Pct_FDF2_OUT":      (20,   80,   4.8,  "%"),
    "AI_B4_RPM_FDF2":          (800,  1200, 4.9,  "RPM"),
    "AI_B4_Pct_RPC306_SP":     (20,   80,   5.0,  "%"),
    "AI_B4_Pct_RPC306_PV":     (20,   80,   5.1,  "%"),
    "AI_B4_Pct_RPC306_OUT":    (20,   80,   5.2,  "%"),
    "AI_B4_RPM_IDF2":          (800,  1200, 5.3,  "RPM"),
    "AI_B4_Pct_RPC306_VFD":    (20,   80,   5.4,  "%"),
    "AI_B4_Pres_FDF_mmWC":    (7.0,  8.0,  5.5,  "mmWC"),
    "AI_B4_TEST1_Value":       (0,    100,  5.6,  ""),
    "AI_B4_Pct_PAF1_SP":       (20,   80,   5.7,  "%"),
    "AI_B4_Pct_PAF1_PV":       (20,   80,   5.8,  "%"),
    "AI_B4_Pres_PAF2_mmWC":   (7.0,  8.0,  5.9,  "mmWC"),
    "AI_B4_RPM_PAF2":          (800,  1200, 6.0,  "RPM"),
    "AI_B4_Pct_RPC308b_SP":    (20,   80,   6.1,  "%"),
    "AI_B4_Pct_RPC308b_PV":    (20,   80,   6.2,  "%"),
    "AI_B4_Pct_DAM303B_SP":    (20,   80,   6.3,  "%"),
    "AI_B4_Pct_DAM304B_SP":    (20,   80,   6.4,  "%"),

    # ===== BÀI 5 - CEMENT MILL =====
    "AI_B5_CA_Fan_Motor_DE_Temp":   (50, 80,  1.0, "°C"),
    "AI_B5_CA_Fan_Motor_NDE_Temp":  (50, 80,  1.1, "°C"),
    "AI_B5_CA_Fan_DE_Temp":         (50, 80,  1.2, "°C"),
    "AI_B5_CA_Fan_NDE_Temp":        (50, 80,  1.3, "°C"),
    "AI_B5_CA_Fan_DE_Vib":          (0,  10,  1.4, "mm/s"),
    "AI_B5_CA_Fan_NDE_Vib":         (0,  10,  1.5, "mm/s"),
    "AI_B5_SP_700FN03":             (100,200, 1.6, "L/h"),
    "AI_B5_SP_700HES01":            (100,200, 1.7, "L/h"),
    "AI_B5_SP_700DA4":              (20, 30,  1.8, "Hz"),
    "AI_B5_SP_700DA6":              (20, 30,  1.9, "Hz"),
    "AI_B5_SP_700DA7":              (20, 30,  2.0, "Hz"),
    "AI_B5_SP_700FN2_DA1":          (20, 30,  2.1, "Hz"),
    "AI_B5_Sep_Motor_Top_Temp":     (50, 80,  2.2, "°C"),
    "AI_B5_Sep_Bottom_Bear_Temp":   (50, 80,  2.3, "°C"),
    "AI_B5_Trend_Val_1":            (0,  100, 2.4, "%"),
    "AI_B5_Trend_Val_2":            (0,  100, 2.5, "%"),
    "AI_B5_Trend_Val_3":            (0,  100, 2.6, "%"),
    "AI_B5_700FN03_RPM":            (800,1200,2.7, "RPM"),
    "AI_B5_700HES01_Flow":          (100,200, 2.8, "L/h"),
    "AI_B5_700FN10_Speed":          (20, 30,  2.9, "Hz"),
    "AI_B5_700CM01_Current":        (50, 200, 3.0, "A"),
    "AI_B5_Lub_Stop_Time":          (0,  300, 3.1, "Sec"),
    "AI_B5_Main_Drive_ReHealth":    (0,  300, 3.2, "Sec"),
    "AI_B5_CM_LRS_IN":              (50, 80,  3.3, "°C"),
    "AI_B5_CM_LRS_OUT":             (50, 80,  3.4, "°C"),
    "AI_B5_CM_Mill_Oil_Temp":       (50, 80,  3.5, "°C"),
    "AI_B5_CM_OilTrun_BER_Temp":    (50, 80,  3.6, "°C"),
    "AI_B5_CM_OilTrun_BER2_Temp":   (50, 80,  3.7, "°C"),
    "AI_B5_CM_OilPinion_BER_Temp":  (50, 80,  3.8, "°C"),
    "AI_B5_CM_GB_IL_Shaft_BER":     (50, 80,  3.9, "°C"),
    "AI_B5_CM_Running_Hours":       (0,  8760,4.0, "Hr"),
    "AI_B5_CM_PS1_1_KG":            (7,  8,   4.1, "bar"),
    "AI_B5_CM_PS1_2_KG":            (7,  8,   4.2, "bar"),
    "AI_B5_NIBS_Value":             (50, 200, 4.3, "A"),
    "AI_B5_800DC1_Temp":            (50, 80,  4.4, "°C"),
    "AI_B5_800DC2_Temp":            (50, 80,  4.5, "°C"),
    "AI_B5_800FN1_Speed":           (20, 30,  4.6, "Hz"),
    "AI_B5_800FN2_Speed":           (20, 30,  4.7, "Hz"),
    "AI_B5_800YF1_Flow":            (100,200, 4.8, "L/h"),
    "AI_B5_800YF2_Flow":            (100,200, 4.9, "L/h"),
    "AI_B5_Silo1_Level_Bar1":       (0,  100, 5.0, "%"),
    "AI_B5_Silo1_Level_Bar2":       (0,  100, 5.1, "%"),
    "AI_B5_Silo2_Level_Bar1":       (0,  100, 5.2, "%"),
    "AI_B5_Silo2_Level_Bar2":       (0,  100, 5.3, "%"),
    "AI_B5_700FN01_Speed":          (20, 30,  5.4, "Hz"),
    "AI_B5_700FN02_Speed":          (20, 30,  5.5, "Hz"),
    "AI_B5_700AS07_Speed":          (20, 30,  5.6, "Hz"),
    "AI_B5_700AS08_Flow":           (100,200, 5.7, "L/h"),
    "AI_B5_700FN09_Speed":          (20, 30,  5.8, "Hz"),
    "AI_B5_700SFM01_Speed":         (20, 30,  5.9, "Hz"),
    "AI_B5_700DA1_Flow":            (100,200, 6.0, "L/h"),
    "AI_B5_700DA4_Flow":            (100,200, 6.1, "L/h"),
    "AI_B5_700DA6_Temp":            (50, 80,  6.2, "°C"),
    "AI_B5_700DA7_Temp":            (50, 80,  6.3, "°C"),
    "AI_B5_700BL1_Load":            (50, 200, 6.4, "A"),
    "AI_B5_700BL2_Load":            (50, 200, 6.5, "A"),
    "AI_B5_700AS9_Flow":            (100,200, 6.6, "L/h"),
    "AI_B5_700FN13_Speed":          (20, 30,  6.7, "Hz"),

    # ===== BÀI 6 - CELL CULTURE FERMENTER =====
    "AI_B6_TICR211_Temp":      (50, 80,  2.0, "°C"),
    "AI_B6_TICR210_Temp":      (50, 80,  2.1, "°C"),
    "AI_B6_TICR201_Tank_Temp": (50, 80,  2.2, "°C"),
    "AI_B6_PT201_Pressure":    (7.0, 8.0, 2.3, "bar"),
    "AI_B6_Ph201_pH":          (6.0, 8.0, 2.4, "pH"),
    "AI_B6_ORP201_ORP":        (20, 80,  2.5, "%"),
    "AI_B6_DPL101_Level":      (100, 500, 2.6, "L"),
    "AI_B6_TICR214_Temp":      (50, 80,  2.7, "°C"),
    "AI_B6_TICR204_Temp":      (50, 80,  2.8, "°C"),
    "AI_B6_TICR205_Temp":      (50, 80,  2.9, "°C"),
    "AI_B6_TICR206_Temp":      (50, 80,  3.0, "°C"),
    "AI_B6_FHC203_Flow":       (100, 200, 3.1, "L/h"),
    "AI_B6_BPC201_Pressure":   (7.0, 8.0, 3.2, "bar"),

    # ===== BÀI 7 - PLANTPAX DISTILLATION =====
    "AI_B7_K03_PT02_Pressure":   (7,8,    3.0, "bar"),
    "AI_B7_K03_TT04_Temp":       (50,80,  3.1, "°C"),
    "AI_B7_K03_TT05_Temp":       (50,80,  3.2, "°C"),
    "AI_B7_K03_TT06_Temp":       (50,80,  3.3, "°C"),
    "AI_B7_K03_TT07_Temp":       (50,80,  3.4, "°C"),
    "AI_B7_K03_PT07_Pressure":   (7,8,    3.5, "bar"),
    "AI_B7_K03_FT03_Flow":       (100,200,3.6, "L/h"),
    "AI_B7_K03_Density_1":       (800,1000,3.7,"kg/m3"),
    "AI_B7_K03_LT01_Level":      (20,80,  3.8, "cm"),
    "AI_B7_K03_LT02_Level":      (20,80,  3.9, "cm"),
    "AI_B7_K03_TT01_Temp":       (50,80,  4.0, "°C"),
    "AI_B7_K03_TT02_Temp":       (50,80,  4.1, "°C"),
    "AI_B7_Reboiler_PV":         (100,200,4.2, "L/h"),
    "AI_B7_Reboiler_SP":         (100,200,4.3, "L/h"),
    "AI_B7_Reboiler_CV":         (20,80,  4.4, "%"),
    "AI_B7_HE03_Primary_Temp":   (50,80,  4.5, "°C"),
    "AI_B7_HE03_Secondary_Temp": (50,80,  4.6, "°C"),
    "AI_B7_K03_L08_Level":       (20,80,  4.7, "cm"),
    "AI_B7_K03_L06_Level":       (20,80,  4.8, "cm"),
    "AI_B7_K03_L05_Level":       (20,80,  4.9, "cm"),
    "AI_B7_K03_L07_Level":       (20,80,  5.0, "cm"),
    "AI_B7_K03_L04_Level":       (20,80,  5.1, "cm"),
    "AI_B7_K03_L03_Level":       (20,80,  5.2, "cm"),
    "AI_B7_V03A_Density":        (800,1000,5.3,"kg/m3"),
    "AI_B7_Kettle_Flow_SP":      (100,200,5.4, "kg/h"),
    "AI_B7_Keboiler_Flow_SP":    (100,200,5.5, "kg/h"),
    "AI_B7_Reflux_Time_SP":      (0,60,   5.6, "Min"),
    "AI_B7_Time_Remain":         (0,60,   5.7, "Min"),
    "AI_B7_RD_Level_SP":         (20,80,  5.8, "cm"),
    "AI_B7_Reflux_Flow_SP":      (100,200,5.9, "L/h"),
    "AI_B7_Collection_SP":       (100,200,6.0, "L/h"),
    "AI_B7_Total_Flowrate":      (100,200,6.1, "L/h"),
    "AI_B7_ML_Qty_SP":           (0,600,  6.2, "L"),
    "AI_B7_ML_Qty_Total":        (0,600,  6.3, "L"),
    "AI_B7_Material_Code":       (0,99,   6.4, ""),
    "AI_B7_Stage_Number":        (0,20,   6.5, ""),
    "AI_B7_Batch_Number":        (0,9999, 6.6, ""),
    "AI_B7_Current_User_ID":     (0,999,  6.7, ""),
    "AI_B7_K_05_L_704_HI":       (20,80,  6.8, "cm"),
    "AI_B7_Density_SP":          (800,1000,6.9,"kg/m3"),
    "AI_B7_CTS_Flow_1":          (100,200,7.0, "kg/h"),
    "AI_B7_CTS_Flow_2":          (100,200,7.1, "kg/h"),
    "AI_B7_Steam_PT01_Temp":     (50,80,  7.2, "°C"),
    "AI_B7_Steam_PT02_Temp":     (50,80,  7.3, "°C"),
    "AI_B7_CWS_TT01_Temp":       (50,80,  7.4, "°C"),
    "AI_B7_CWS_TT02_Temp":       (50,80,  7.5, "°C"),
    "AI_B7_CWS_TT03_Temp":       (50,80,  7.6, "°C"),
    "AI_B7_CWAR_TT01_Temp":      (50,80,  7.7, "°C"),
    "AI_B7_CWAR_TT02_Temp":      (50,80,  7.8, "°C"),
    "AI_B7_CWAR_TT03_Temp":      (50,80,  7.9, "°C"),
    "AI_B7_CWAR_TT04_Temp":      (50,80,  8.0, "°C"),
    "AI_B7_K03_CV01_PV":         (20,80,  8.1, "%"),
    "AI_B7_K03_CV01_SP":         (20,80,  8.2, "%"),
    "AI_B7_K03_CV01_CV":         (20,80,  8.3, "%"),
    "AI_B7_Steam_CV01_PV":       (20,80,  8.4, "%"),
    "AI_B7_Steam_CV01_SP":       (20,80,  8.5, "%"),
    "AI_B7_Steam_CV01_CV":       (20,80,  8.6, "%"),
    "AI_B7_K03_Jacket_PV":       (50,80,  8.7, "°C"),
    "AI_B7_K03_Jacket_SP":       (50,80,  8.8, "°C"),
    "AI_B7_K03_Jacket_CV":       (20,80,  8.9, "%"),
    "AI_B7_CHWR_TT01_Temp":      (50,80,  9.0, "°C"),
    "AI_B7_CHWR_TT02_Temp":      (50,80,  9.1, "°C"),
    "AI_B7_CHWS_TT01_Temp":      (50,80,  9.2, "°C"),
    "AI_B7_CHWS_TT02_Temp":      (50,80,  9.3, "°C"),
    "AI_B7_K03_TT03_Temp":       (50,80,  9.4, "°C"),
}

def compute_value(lo, hi, phase, t):
    """Tính giá trị dao động hình sin + nhiễu nhỏ"""
    mid = (lo + hi) / 2.0
    amp = (hi - lo) / 2.0
    period = 30.0  # giây
    noise = random.uniform(-amp * 0.02, amp * 0.02)
    val = mid + amp * math.sin(2 * math.pi * t / period + phase) + noise
    return max(lo, min(hi, val))

print(f"Tổng số tags mô phỏng: {len(SIM_TAGS)}")
print("\nChạy standalone - hiển thị giá trị (không kết nối PLC thật)")
print("Ctrl+C để dừng\n")
print(f"{'Tag name':<45} | {'Value':>10} | {'Unit':<8}")
print("-" * 70)

# Standalone display mode
DISPLAY_INTERVAL = 3  # seconds
TAG_NAMES = list(SIM_TAGS.keys())

t = 0
cycle = 0
try:
    while True:
        t += DISPLAY_INTERVAL
        cycle += 1
        
        # In mẫu 10 tags ngẫu nhiên mỗi chu kỳ
        sample = random.sample(TAG_NAMES, min(10, len(TAG_NAMES)))
        print(f"\n--- Chu kỳ {cycle} | t={t}s ---")
        for name in sample:
            lo, hi, phase, unit = SIM_TAGS[name]
            val = compute_value(lo, hi, phase, t)
            print(f"  {name:<43} = {val:8.2f} {unit}")
        
        time.sleep(DISPLAY_INTERVAL)

except KeyboardInterrupt:
    print("\n\nDừng mô phỏng.")
    print(f"Đã mô phỏng {cycle} chu kỳ ({cycle * DISPLAY_INTERVAL}s)")
