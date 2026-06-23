#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
build_screen1_mapping_v3.py
Mapping chinh xac theo correction cua user (2026-06-22 22:21):

Dieu chinh:
  I/O field_4   -> TT3303_TraoDoiNhiet_Eff, PLC_1, 99.9
  I/O field_3   -> CV3304_Nuoc_Lam_Mat_M,   PLC_1, 999.9
  I/O field_23  -> PI3308_Truoc_Filter_Eff,  PLC_1, 99.9
  I/O field_24  -> FT3309_Xa_Thanh_Pham_Eff, PLC_1, 999.9

Format rule:
  FQ, LT, CV  -> 999.9
  TT, PI      -> 99.9

Ghi chu:
  CV_Filler_Cap_Dich_M: tag ton tai trong PLC_1 nhung khong co IOField tuong ung
  trong Screen_1 (24 o hien co). Cho nguoi dung dat thu cong.
"""
import csv

# =============================================================================
# FINAL MAPPING v3 - 24 IOFields
# Tuple: (ObjectName, Left, Top, W, H, FormatPattern,
#         PLC_Owner, Proposed_Tag, DataType, Connection,
#         Confidence, Need_HMI_Connection_2, Rationale)
# =============================================================================
MAPPING = [
    # ===================== ROW FQ (y=61-65) =====================
    # format=999.9 (luu luong tich luy lon)
    ("I/O field_1",  133,  61, 47, 32, "999.9",
     "PLC_1","FQ3200_Bon1_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "Col1 Bon1, hang FQ, PLC_1 addr=%MD712"),

    ("I/O field_7",  486,  65, 43, 28, "999.9",
     "PLC_1","FQ3205_Bon2_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "Col2 Bon2, hang FQ, PLC_1 addr=%MD744"),

    ("I/O field_11", 804,  61, 43, 28, "999.9",
     "PLC_2","FQ3215_Bon4_Eff","Real","HMI_Connection_2",
     "HIGH","YES",
     "Col3 Bon4, hang FQ, PLC_2 addr=%MD808 - BLOCKER: can HMI_Connection_2"),

    ("I/O field_15", 1143, 62, 43, 28, "999.9",
     "PLC_2","FQ3210_Bon3_Eff","Real","HMI_Connection_2",
     "HIGH","YES",
     "Col4 Bon3, hang FQ, PLC_2 addr=%MD776 - BLOCKER"),

    # ===================== ROW LT (y=127-130) =====================
    # format=999.9 (muc long %)
    ("I/O field_2",  300, 127, 43, 28, "999.9",
     "PLC_1","LT3203_Bon1_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "Col1 Bon1, hang LT, PLC_1 addr=%MD720"),

    ("I/O field_8",  636, 129, 43, 28, "999.9",
     "PLC_1","LT3209_Bon2_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "Col2 Bon2, hang LT, PLC_1 addr=%MD752"),

    ("I/O field_12", 965, 127, 43, 28, "999.9",
     "PLC_2","LT3218_Bon4_Eff","Real","HMI_Connection_2",
     "HIGH","YES",
     "Col3 Bon4, hang LT, PLC_2 addr=%MD816 - BLOCKER"),

    ("I/O field_16", 1318, 130, 43, 28, "999.9",
     "PLC_2","LT3213_Bon3_Eff","Real","HMI_Connection_2",
     "HIGH","YES",
     "Col4 Bon3, hang LT, PLC_2 addr=%MD784 - BLOCKER"),

    # ===================== ROW TT (y=190-195) =====================
    # format=99.9 (nhiet do °C)
    ("I/O field_5",  353, 195, 43, 28, "99.9",
     "PLC_1","TT3204_Bon1_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "Col1 Bon1, hang TT, PLC_1 addr=%MD728"),

    ("I/O field_9",  689, 192, 43, 28, "99.9",
     "PLC_1","TT3208_Bon2_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "Col2 Bon2, hang TT, PLC_1 addr=%MD760"),

    ("I/O field_13", 1016, 190, 43, 28, "99.9",
     "PLC_2","TT3219_Bon4_Eff","Real","HMI_Connection_2",
     "HIGH","YES",
     "Col3 Bon4, hang TT, PLC_2 addr=%MD824 - BLOCKER"),

    ("I/O field_17", 1365, 193, 43, 28, "99.9",
     "PLC_2","TT3214_Bon3_Eff","Real","HMI_Connection_2",
     "HIGH","YES",
     "Col4 Bon3, hang TT, PLC_2 addr=%MD792 - BLOCKER"),

    # ===================== ROW CV (y=293-300) =====================
    # format=999.9 (van tuyen tinh %)
    ("I/O field_6",  354, 296, 43, 28, "999.9",
     "PLC_1","CV3201_Nuoc_Bon1_M","Real","HMI_Connection_1",
     "HIGH","no",
     "Col1 Bon1, hang CV, PLC_1 addr=%MD1200"),

    ("I/O field_10", 688, 294, 43, 28, "999.9",
     "PLC_1","CV3206_Hoi_Bon2_M","Real","HMI_Connection_1",
     "HIGH","no",
     "Col2 Bon2, hang CV, PLC_1 addr=%MD1208"),

    ("I/O field_14", 1015, 293, 43, 28, "999.9",
     "PLC_2","CV3216_Hoi_Bon4_M","Real","HMI_Connection_2",
     "HIGH","YES",
     "Col3 Bon4, hang CV, PLC_2 addr=%MD1224 - BLOCKER"),

    ("I/O field_18", 1367, 293, 43, 28, "999.9",
     "PLC_2","CV3211_Nuoc_Bon3_M","Real","HMI_Connection_2",
     "HIGH","YES",
     "Col4 Bon3, hang CV, PLC_2 addr=%MD1216 - BLOCKER"),

    # ===================== BON CHUA 1 (PLC_1) =====================
    ("I/O field_19", 412, 586, 43, 28, "999.9",
     "PLC_1","LT3302_BonChua1_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "BonChua1 trai, LT muc long, PLC_1 addr=%MD832"),

    ("I/O field_20", 417, 713, 43, 28, "99.9",
     "PLC_1","TT3301_BonChua1_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "BonChua1 trai, TT nhiet do, PLC_1 addr=%MD840"),

    # ===================== BON CHUA 2 (PLC_1) =====================
    ("I/O field_22", 1135, 589, 43, 28, "999.9",
     "PLC_1","LT3307_BonChua2_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "BonChua2 phai, LT muc long, PLC_1 addr=%MD856"),

    ("I/O field_21", 1134, 711, 43, 28, "99.9",
     "PLC_1","TT3306_BonChua2_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "BonChua2 phai, TT nhiet do, PLC_1 addr=%MD864"),

    # ===================== VUNG PHAI NGOAI (x=1280) =====================
    # I/O field_23 -> PI3308 (ap suat truoc filter), format=99.9
    ("I/O field_23", 1280, 616, 43, 28, "99.9",
     "PLC_1","PI3308_Truoc_Filter_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "x=1280,y=616, ap suat truoc filter, PLC_1, format=99.9 (bar)"),

    # I/O field_24 -> FT3309 xa thanh pham, format=999.9
    ("I/O field_24", 1280, 670, 43, 28, "999.9",
     "PLC_1","FT3309_Xa_Thanh_Pham_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "x=1280,y=670, FT xa thanh pham, PLC_1 addr=%MD880, format=999.9 (L/h)"),

    # ===================== HANG DUOI BON CHUA =====================
    # I/O field_3 -> CV3304_Nuoc_Lam_Mat_M, format=999.9
    ("I/O field_3",  832, 741, 51, 28, "999.9",
     "PLC_1","CV3304_Nuoc_Lam_Mat_M","Real","HMI_Connection_1",
     "HIGH","no",
     "x=832,y=741, CV nuoc lam mat, PLC_1 addr=%MD1232, format=999.9 (%)"),

    # I/O field_4 -> TT3303_TraoDoiNhiet_Eff, format=99.9
    ("I/O field_4",  791, 589, 44, 28, "99.9",
     "PLC_1","TT3303_TraoDoiNhiet_Eff","Real","HMI_Connection_1",
     "HIGH","no",
     "x=791,y=589, TT trao doi nhiet, PLC_1 addr=%MD848, format=99.9 (°C)"),
]

# ===================== MISSING FIELD NOTE =====================
MISSING = {
    "Tag": "CV_Filler_Cap_Dich_M",
    "DataType": "Real",
    "PLC_Owner": "PLC_1",
    "Connection": "HMI_Connection_1",
    "FormatPattern": "999.9",
    "Unit": "%",
    "Addr": "%MD1236",
    "Note": "KHONG CO IOField tuong ung trong Screen_1 (24 o hien co). "
            "Cho nguoi dung dat thu cong. Khong tu tao o hoac sua layout."
}

# ===================== PRINT SUMMARY =====================
total       = len(MAPPING)
need_conn2  = [r for r in MAPPING if r[11] == "YES"]
plc1_rows   = [r for r in MAPPING if r[6] == "PLC_1"]
plc2_rows   = [r for r in MAPPING if r[6] == "PLC_2"]

print("=" * 130)
print("SCREEN_1 MAPPING DRY-RUN v3  (corrections applied 2026-06-22)")
print("=" * 130)
print(f"Total IOFields         : {total}")
print(f"PLC_1 (Conn1, ready)   : {len(plc1_rows)}")
print(f"PLC_2 (Conn2, BLOCKED) : {len(plc2_rows)}")
print(f"Missing from screen    : CV_Filler_Cap_Dich_M (chua co IOField)")
print()
print(f"{'#':<3} {'ObjectName':<18} {'L':>5} {'T':>5}  {'Fmt':<7} {'PLC':<6} {'Tag':<35} {'Conn':<20} {'Conf':<6} {'Conn2?'}")
print("-" * 130)
for i, row in enumerate(MAPPING, 1):
    nm, L, T, W, H, fmt, plc, tag, dtype, conn, conf, nc2, rat = row
    marker = " <BLOCKER>" if nc2 == "YES" else ""
    print(f"{i:<3} {nm:<18} {L:>5} {T:>5}  {fmt:<7} {plc:<6} {tag:<35} {conn:<20} {conf:<6} {nc2}{marker}")

print()
print("=== BLOCKED (need HMI_Connection_2 for HMI reads from PLC_2) ===")
for r in need_conn2:
    print(f"  {r[0]:<18} -> {r[7]} ({r[6]}) addr={r[9]}")

print()
print("=== MISSING IOField ===")
for k, v in MISSING.items():
    print(f"  {k}: {v}")

# ===================== EXPORT CSV =====================
OUT = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_mapping_dry_run.csv"
FIELDNAMES = ["#","ObjectName","Left","Top","Width","Height","FormatPattern",
              "PLC_Owner","Proposed_Tag","DataType","Proposed_Connection",
              "Confidence","Need_HMI_Connection_2","Blocker","Rationale"]
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    for i, row in enumerate(MAPPING, 1):
        nm, L, T, W, H, fmt, plc, tag, dtype, conn, conf, nc2, rat = row
        writer.writerow({
            "#": i,
            "ObjectName": nm,
            "Left": L, "Top": T, "Width": W, "Height": H,
            "FormatPattern": fmt,
            "PLC_Owner": plc,
            "Proposed_Tag": tag,
            "DataType": dtype,
            "Proposed_Connection": conn,
            "Confidence": conf,
            "Need_HMI_Connection_2": nc2,
            "Blocker": "BLOCKER" if nc2 == "YES" else "",
            "Rationale": rat,
        })
    # Append missing note as last row
    writer.writerow({
        "#": "N/A",
        "ObjectName": "(missing)",
        "Left": "", "Top": "", "Width": "", "Height": "",
        "FormatPattern": MISSING["FormatPattern"],
        "PLC_Owner": MISSING["PLC_Owner"],
        "Proposed_Tag": MISSING["Tag"],
        "DataType": MISSING["DataType"],
        "Proposed_Connection": MISSING["Connection"],
        "Confidence": "N/A",
        "Need_HMI_Connection_2": "no",
        "Blocker": "NO_IOFIELD",
        "Rationale": MISSING["Note"],
    })

print(f"\nCSV saved: {OUT}")
