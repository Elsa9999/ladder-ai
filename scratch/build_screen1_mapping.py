#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
build_screen1_mapping.py
Lập bảng mapping cho 24 IOField của Screen_1 dựa vào vị trí XY và PLC tag context.

Layout Screen_1 (1440x900):
  - 4 cột bồn trộn (Bon1~4) chia ngang: ~col1 x=100-380, col2=480-710, col3=780-1060, col4=1130-1410
  - Mỗi bồn: FT (flow), CV (van linear), LT (level), TT (temp), TT2 (temp thứ 2)
  - Phần giữa-dưới: Bồn chứa 1 (x=380-730) và Bồn chứa 2 (x=730-1100)

IOField layout (dựa vào tọa độ đã phân tích):
  Row A (y≈61-65, format=999999): FT cho từng bồn (L/h tích lũy) -> 4 ô
  Row B (y≈127-130): LT/TT row 1 -> 4 ô  
  Row C (y≈190-195): TT row 2 -> 4 ô
  Row D (y≈293-300): CV row -> 4 ô
  Sau đó: Bồn chứa 1 (x=400-460): LT,TT -> 2 ô
          Bồn chứa 2 (x=1130-1280): LT,TT,TT3 -> 3+2 ô
          + Đặc biệt: CV van, lưu lượng xa...

Các IOField và mapping đề xuất:
"""

import csv

# =============================================================================
# MAPPING TABLE - dựa vào tọa độ và context hệ thống
# =============================================================================
# Format:
# ObjectName, Left, Top, W, H, Format, Proposed_PLC, Proposed_Tag, DataType,
# Connection, PLC_Owner, Confidence, Rationale

MAPPING = [
    # --- ROW A: y=61-65, format=999999, Dòng tích lũy FQ (L) ---
    # Col1 (x=133): Bon 1
    ("I/O field_1",  133,  61, 47, 32, "999999", "PLC_1", "FQ3200_Bon1_Eff",  "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=133 -> cot Bon1, y=61 -> hang FQ, format=999999 phu hop gia tri lon"),

    # Col2 (x=486): Bon 2
    ("I/O field_7",  486,  65, 43, 28, "999999", "PLC_1", "FQ3205_Bon2_Eff",  "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=486 -> cot Bon2, y=65 -> hang FQ"),

    # Col3 (x=804): Bon 4 (thu tu trong project: Bon1,2,4,3 theo PID)
    ("I/O field_11", 804,  61, 43, 28, "999999", "PLC_1", "FQ3215_Bon4_Eff",  "Real", "HMI_Connection_1", "PLC_1",
     "MEDIUM", "x=804 -> cot Bon3/Bon4 phu thuoc thu tu; kiem tra voi Man Tong Quan"),

    # Col4 (x=1143): Bon 3
    ("I/O field_15", 1143, 62, 43, 28, "999999", "PLC_2", "FQ3210_Bon3_Eff",  "Real", "HMI_Connection_2", "PLC_2",
     "MEDIUM", "x=1143 -> cot cuoi, Bon3 tren PLC_2"),

    # --- ROW B: y=127-130, format=99.9, LT muc do ---
    # Col1 (x=300): LT Bon1
    ("I/O field_2",  300, 127, 43, 28, "99.9", "PLC_1", "LT3203_Bon1_Eff",   "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=300 -> cot Bon1 (phu), y=127 -> hang LT"),

    # Col2 (x=636): LT Bon2
    ("I/O field_8",  636, 129, 43, 28, "99.9", "PLC_1", "LT3209_Bon2_Eff",   "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=636 -> cot Bon2, y=129 -> hang LT"),

    # Col3 (x=965): LT Bon4
    ("I/O field_12", 965, 127, 43, 28, "99.9", "PLC_1", "LT3218_Bon4_Eff",   "Real", "HMI_Connection_1", "PLC_1",
     "MEDIUM", "x=965 -> cot Bon4"),

    # Col4 (x=1318): LT Bon3
    ("I/O field_16", 1318, 130, 43, 28, "99.9", "PLC_2", "LT3213_Bon3_Eff",  "Real", "HMI_Connection_2", "PLC_2",
     "MEDIUM", "x=1318 -> cot Bon3 tren PLC_2"),

    # --- ROW C: y=190-195, format=99.9, TT nhiet do ---
    # Col1 (x=353): TT Bon1
    ("I/O field_5",  353, 195, 43, 28, "99.9", "PLC_1", "TT3204_Bon1_Eff",   "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=353 -> cot Bon1 (phu), y=195 -> hang TT"),

    # Col2 (x=689): TT Bon2
    ("I/O field_9",  689, 192, 43, 28, "99.9", "PLC_1", "TT3208_Bon2_Eff",   "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=689 -> cot Bon2"),

    # Col3 (x=1016): TT Bon4
    ("I/O field_13", 1016, 190, 43, 28, "99.9", "PLC_1", "TT3219_Bon4_Eff",  "Real", "HMI_Connection_1", "PLC_1",
     "MEDIUM", "x=1016 -> cot Bon4"),

    # Col4 (x=1365): TT Bon3
    ("I/O field_17", 1365, 193, 43, 28, "99.9", "PLC_2", "TT3214_Bon3_Eff",  "Real", "HMI_Connection_2", "PLC_2",
     "MEDIUM", "x=1365 -> cot Bon3 tren PLC_2"),

    # --- ROW D: y=293-300, format=99.9, CV van tuyến tính ---
    # Col1 (x=354): CV Bon1 (nuoc nong/hoi)
    ("I/O field_6",  354, 296, 43, 28, "99.9", "PLC_1", "CV3201_Nuoc_Bon1_M", "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=354 -> cot Bon1, y=296 -> hang CV"),

    # Col2 (x=688): CV Bon2
    ("I/O field_10", 688, 294, 43, 28, "99.9", "PLC_1", "CV3206_Hoi_Bon2_M",  "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=688 -> cot Bon2"),

    # Col3 (x=1015): CV Bon4
    ("I/O field_14", 1015, 293, 43, 28, "99.9", "PLC_1", "CV3216_Hoi_Bon4_M", "Real", "HMI_Connection_1", "PLC_1",
     "MEDIUM", "x=1015 -> cot Bon4"),

    # Col4 (x=1367): CV Bon3
    ("I/O field_18", 1367, 293, 43, 28, "99.9", "PLC_2", "CV3211_Nuoc_Bon3_M", "Real", "HMI_Connection_2", "PLC_2",
     "MEDIUM", "x=1367 -> cot Bon3 tren PLC_2"),

    # --- VUNG BON CHUA 1 (x=400-465, y=580-720) ---
    # LT Bon Chua 1
    ("I/O field_19", 412, 586, 43, 28, "99.9", "PLC_1", "LT3302_BonChua1_Eff", "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=412,y=586 -> vung BonChua1, LT (muc)"),

    # TT Bon Chua 1
    ("I/O field_20", 417, 713, 43, 28, "99.9", "PLC_1", "TT3301_BonChua1_Eff", "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=417,y=713 -> vung BonChua1, TT (nhiet)"),

    # --- VUNG BON CHUA 2 (x=800-1300, y=580-760) ---
    # LT Bon Chua 2
    ("I/O field_22", 1135, 589, 43, 28, "99.9", "PLC_1", "LT3307_BonChua2_Eff", "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=1135,y=589 -> vung BonChua2, LT"),

    # TT Bon Chua 2
    ("I/O field_21", 1134, 711, 43, 28, "99.9", "PLC_1", "TT3306_BonChua2_Eff", "Real", "HMI_Connection_1", "PLC_1",
     "HIGH", "x=1134,y=711 -> vung BonChua2, TT"),

    # TT Trao Doi Nhiet / Nuoc Lam Mat (x=1280, y=616)
    ("I/O field_23", 1280, 616, 43, 28, "999999", "PLC_1", "TT3303_TraoDoiNhiet_Eff", "Real", "HMI_Connection_1", "PLC_1",
     "LOW", "x=1280,y=616 -> vung phai, co the TT trao doi nhiet hoac CV; format=999999 khong khop TT (99.9)"),

    # CV Nuoc Lam Mat (x=1280, y=670)
    ("I/O field_24", 1280, 670, 43, 28, "99.9", "PLC_1", "CV3304_Nuoc_Lam_Mat_M", "Real", "HMI_Connection_1", "PLC_1",
     "LOW", "x=1280,y=670 -> vung phai duoi; co the CV nuoc lam mat"),

    # --- BON CHUA - hang duoi (y=740-850) ---
    # FT xa thanh pham (x=832, y=741)
    ("I/O field_3",  832, 741, 51, 28, "99.9", "PLC_1", "FT3309_Xa_Thanh_Pham_Eff", "Real", "HMI_Connection_1", "PLC_1",
     "MEDIUM", "x=832,y=741 -> duoi BonChua, FT xa thanh pham"),

    # LT / SP (x=791, y=589)
    ("I/O field_4",  791, 589, 44, 28, "99.9", "PLC_1", "LT3302_BonChua1_Eff", "Real", "HMI_Connection_1", "PLC_1",
     "LOW", "x=791,y=589 -> giua 2 bonchua; UNCERTAIN - co the SP hoac LT khac"),
]

# Cac tag can kiem tra ton tai tren PLC
PLC1_TAGS_TO_VERIFY = [
    "FQ3200_Bon1_Eff", "FQ3205_Bon2_Eff", "FQ3215_Bon4_Eff",
    "LT3203_Bon1_Eff", "LT3209_Bon2_Eff", "LT3218_Bon4_Eff",
    "TT3204_Bon1_Eff", "TT3208_Bon2_Eff", "TT3219_Bon4_Eff",
    "CV3201_Nuoc_Bon1_M", "CV3206_Hoi_Bon2_M", "CV3216_Hoi_Bon4_M",
    "LT3302_BonChua1_Eff", "TT3301_BonChua1_Eff",
    "LT3307_BonChua2_Eff", "TT3306_BonChua2_Eff",
    "TT3303_TraoDoiNhiet_Eff", "CV3304_Nuoc_Lam_Mat_M",
    "FT3309_Xa_Thanh_Pham_Eff",
]
PLC2_TAGS_TO_VERIFY = [
    "FQ3210_Bon3_Eff", "LT3213_Bon3_Eff", "TT3214_Bon3_Eff", "CV3211_Nuoc_Bon3_M",
]

print("=== SCREEN_1 PROPOSED MAPPING (24 IOFields) ===")
print(f"{'#':<3} {'ObjectName':<18} {'L':>5} {'T':>5}  {'Proposed Tag':<35} {'PLC':<6} {'Conn':<20} {'Confidence':<8} Rationale")
print("="*150)
for i, row in enumerate(MAPPING, 1):
    nm, L, T, W, H, fmt, plc, tag, dtype, conn, owner, conf, rat = row
    print(f"{i:<3} {nm:<18} {L:>5} {T:>5}  {tag:<35} {plc:<6} {conn:<20} {conf:<8} {rat[:60]}")

print(f"\nTotal IOFields mapped: {len(MAPPING)}")
pho_plc2 = [r for r in MAPPING if r[6]=="PLC_2"]
print(f"  PLC_1 tags (HMI_Connection_1): {len(MAPPING)-len(pho_plc2)}")
print(f"  PLC_2 tags (HMI_Connection_2): {len(pho_plc2)} <-- BLOCKER: connection chua ton tai")

# Export CSV
OUT = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_mapping_dry_run.csv"
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["#","ObjectName","Left","Top","Width","Height","FormatPattern",
                     "Proposed_PLC","Proposed_Tag","DataType","Connection","PLC_Owner",
                     "Confidence","NeedHMI_Connection2","Rationale"])
    for i, row in enumerate(MAPPING, 1):
        nm, L, T, W, H, fmt, plc, tag, dtype, conn, owner, conf, rat = row
        need_conn2 = "YES" if plc == "PLC_2" else "no"
        writer.writerow([i, nm, L, T, W, H, fmt, plc, tag, dtype, conn, owner, conf, need_conn2, rat])
print(f"\nCSV saved: {OUT}")

# Tag verification
print(f"\n=== PLC_1 tags to verify ({len(PLC1_TAGS_TO_VERIFY)}) ===")
for t in PLC1_TAGS_TO_VERIFY:
    print(f"  {t}")
print(f"\n=== PLC_2 tags to verify ({len(PLC2_TAGS_TO_VERIFY)}) ===")
for t in PLC2_TAGS_TO_VERIFY:
    print(f"  {t}")
