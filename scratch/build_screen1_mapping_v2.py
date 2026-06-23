#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
build_screen1_mapping_v2.py
Mapping chinh xac sau khi xac minh PLC owner:
  - Bon1, Bon2, BonChua1, BonChua2, TraoDoiNhiet: PLC_1
  - Bon3, Bon4: PLC_2

IOFIELD: 24 o, layout 4 cot (Bon1 | Bon2 | Bon4 | Bon3) tu trai qua phai
  Row FQ  (y~61-65,  format=999999): FQ luu luong tich luy
  Row LT  (y~127-130, format=99.9): LT muc long
  Row TT  (y~190-195, format=99.9): TT nhiet do
  Row CV  (y~293-300, format=99.9): CV van tuyen tinh
  BonChua1 (x~412, y~586-713):     LT, TT
  BonChua2 (x~1135, y~589-711):    LT, TT
  Trao doi nhiet / lam mat (x~1280):TT3303, CV3304
  Hang duoi bon chua (y~589-741):   FT xa thanh pham, LT4
"""
import csv

# =============================================================================
# FINAL MAPPING - 24 IOFields
# Columns: ObjName,L,T,W,H,Fmt, PLC,Tag,DType,Conn,Owner,Conf,NeedConn2,Rationale
# =============================================================================
MAPPING = [
    # ===================== ROW FQ (y=61-65, format=999999) =====================
    # Col1 Bon1 (PLC_1)
    ("I/O field_1",  133,  61, 47, 32, "999999",
     "PLC_1","FQ3200_Bon1_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "Col1 Bon1, hang FQ, format=999999, PLC_1 xac nhan addr=%MD712"),

    # Col2 Bon2 (PLC_1)
    ("I/O field_7",  486,  65, 43, 28, "999999",
     "PLC_1","FQ3205_Bon2_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "Col2 Bon2, hang FQ, PLC_1 xac nhan addr=%MD744"),

    # Col3 Bon4 (PLC_2) - Bon4 o PLC_2
    ("I/O field_11", 804,  61, 43, 28, "999999",
     "PLC_2","FQ3215_Bon4_Eff","Real","HMI_Connection_2","PLC_2","HIGH","YES",
     "Col3 Bon4, hang FQ, PLC_2 xac nhan addr=%MD808 - BLOCKER: can HMI_Connection_2"),

    # Col4 Bon3 (PLC_2)
    ("I/O field_15", 1143,  62, 43, 28, "999999",
     "PLC_2","FQ3210_Bon3_Eff","Real","HMI_Connection_2","PLC_2","HIGH","YES",
     "Col4 Bon3, hang FQ, PLC_2 xac nhan addr=%MD776 - BLOCKER"),

    # ===================== ROW LT (y=127-130, format=99.9) =====================
    # Col1 Bon1
    ("I/O field_2",  300, 127, 43, 28, "99.9",
     "PLC_1","LT3203_Bon1_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "Col1 Bon1, hang LT, PLC_1 xac nhan addr=%MD720"),

    # Col2 Bon2
    ("I/O field_8",  636, 129, 43, 28, "99.9",
     "PLC_1","LT3209_Bon2_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "Col2 Bon2, hang LT, PLC_1 xac nhan addr=%MD752"),

    # Col3 Bon4 (PLC_2)
    ("I/O field_12", 965, 127, 43, 28, "99.9",
     "PLC_2","LT3218_Bon4_Eff","Real","HMI_Connection_2","PLC_2","HIGH","YES",
     "Col3 Bon4, hang LT, PLC_2 xac nhan addr=%MD816 - BLOCKER"),

    # Col4 Bon3 (PLC_2)
    ("I/O field_16", 1318, 130, 43, 28, "99.9",
     "PLC_2","LT3213_Bon3_Eff","Real","HMI_Connection_2","PLC_2","HIGH","YES",
     "Col4 Bon3, hang LT, PLC_2 xac nhan addr=%MD784 - BLOCKER"),

    # ===================== ROW TT (y=190-195, format=99.9) =====================
    # Col1 Bon1
    ("I/O field_5",  353, 195, 43, 28, "99.9",
     "PLC_1","TT3204_Bon1_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "Col1 Bon1, hang TT, PLC_1 xac nhan addr=%MD728"),

    # Col2 Bon2
    ("I/O field_9",  689, 192, 43, 28, "99.9",
     "PLC_1","TT3208_Bon2_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "Col2 Bon2, hang TT, PLC_1 xac nhan addr=%MD760"),

    # Col3 Bon4 (PLC_2)
    ("I/O field_13", 1016, 190, 43, 28, "99.9",
     "PLC_2","TT3219_Bon4_Eff","Real","HMI_Connection_2","PLC_2","HIGH","YES",
     "Col3 Bon4, hang TT, PLC_2 xac nhan addr=%MD824 - BLOCKER"),

    # Col4 Bon3 (PLC_2)
    ("I/O field_17", 1365, 193, 43, 28, "99.9",
     "PLC_2","TT3214_Bon3_Eff","Real","HMI_Connection_2","PLC_2","HIGH","YES",
     "Col4 Bon3, hang TT, PLC_2 xac nhan addr=%MD792 - BLOCKER"),

    # ===================== ROW CV (y=293-300, format=99.9) =====================
    # Col1 Bon1
    ("I/O field_6",  354, 296, 43, 28, "99.9",
     "PLC_1","CV3201_Nuoc_Bon1_M","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "Col1 Bon1, hang CV, PLC_1 xac nhan addr=%MD1200"),

    # Col2 Bon2
    ("I/O field_10", 688, 294, 43, 28, "99.9",
     "PLC_1","CV3206_Hoi_Bon2_M","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "Col2 Bon2, hang CV, PLC_1 xac nhan addr=%MD1208"),

    # Col3 Bon4 (PLC_2)
    ("I/O field_14", 1015, 293, 43, 28, "99.9",
     "PLC_2","CV3216_Hoi_Bon4_M","Real","HMI_Connection_2","PLC_2","HIGH","YES",
     "Col3 Bon4, hang CV, PLC_2 xac nhan addr=%MD1224 - BLOCKER"),

    # Col4 Bon3 (PLC_2)
    ("I/O field_18", 1367, 293, 43, 28, "99.9",
     "PLC_2","CV3211_Nuoc_Bon3_M","Real","HMI_Connection_2","PLC_2","HIGH","YES",
     "Col4 Bon3, hang CV, PLC_2 xac nhan addr=%MD1216 - BLOCKER"),

    # ===================== BON CHUA 1 (PLC_1) =====================
    ("I/O field_19", 412, 586, 43, 28, "99.9",
     "PLC_1","LT3302_BonChua1_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "BonChua1 vung trai, hang LT, PLC_1 xac nhan addr=%MD832"),

    ("I/O field_20", 417, 713, 43, 28, "99.9",
     "PLC_1","TT3301_BonChua1_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "BonChua1 vung trai, hang TT, PLC_1 xac nhan addr=%MD840"),

    # ===================== BON CHUA 2 (PLC_1) =====================
    ("I/O field_22", 1135, 589, 43, 28, "99.9",
     "PLC_1","LT3307_BonChua2_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "BonChua2 vung phai, hang LT, PLC_1 xac nhan addr=%MD856"),

    ("I/O field_21", 1134, 711, 43, 28, "99.9",
     "PLC_1","TT3306_BonChua2_Eff","Real","HMI_Connection_1","PLC_1","HIGH","no",
     "BonChua2 vung phai, hang TT, PLC_1 xac nhan addr=%MD864"),

    # ===================== TRAO DOI NHIET / LAM MAT (PLC_1) =====================
    # x=1280 vung phai ngoai cung
    ("I/O field_23", 1280, 616, 43, 28, "999999",
     "PLC_1","TT3303_TraoDoiNhiet_Eff","Real","HMI_Connection_1","PLC_1","MEDIUM","no",
     "x=1280,y=616, format=999999 ko match TT(99.9) - UNCERTAIN, co the PI hoac SP"),

    ("I/O field_24", 1280, 670, 43, 28, "99.9",
     "PLC_1","CV3304_Nuoc_Lam_Mat_M","Real","HMI_Connection_1","PLC_1","MEDIUM","no",
     "x=1280,y=670 ke ben TT3303, CO the CV nuoc lam mat addr=%MD1232"),

    # ===================== HANG DUOI BON CHUA =====================
    # FT xa thanh pham (x=832, y=741)
    ("I/O field_3",  832, 741, 51, 28, "99.9",
     "PLC_1","FT3309_Xa_Thanh_Pham_Eff","Real","HMI_Connection_1","PLC_1","MEDIUM","no",
     "x=832,y=741 giua 2 bonchua, FT xa thanh pham addr=%MD880"),

    # I/O field_4 (x=791, y=589) - gia tri kho dinh nghia
    ("I/O field_4",  791, 589, 44, 28, "99.9",
     "PLC_1","LT3302_BonChua1_Eff","Real","HMI_Connection_1","PLC_1","LOW","no",
     "x=791,y=589 giua 2 bonchua, UNCERTAIN: co the SP Bon1 hoac giao thoa BonChua"),
]

# ===================== SUMMARY =====================
total = len(MAPPING)
need_conn2 = [r for r in MAPPING if r[13]=="YES"]
plc1_rows  = [r for r in MAPPING if r[6]=="PLC_1"]
plc2_rows  = [r for r in MAPPING if r[6]=="PLC_2"]
high_conf  = [r for r in MAPPING if r[11]=="HIGH"]
low_conf   = [r for r in MAPPING if r[11]=="LOW"]
uncertain  = [r for r in MAPPING if r[11]=="MEDIUM"]

print("="*140)
print("SCREEN_1 FINAL MAPPING DRY-RUN REPORT")
print("="*140)
print(f"Total IOFields : {total}")
print(f"PLC_1 tags     : {len(plc1_rows)} (via HMI_Connection_1 - AVAILABLE)")
print(f"PLC_2 tags     : {len(plc2_rows)} (via HMI_Connection_2 - DOES NOT EXIST - BLOCKER)")
print(f"HIGH confidence: {len(high_conf)}")
print(f"MEDIUM conf    : {len(uncertain)}")
print(f"LOW conf       : {len(low_conf)}")
print()
print(f"{'#':<3} {'ObjectName':<18} {'L':>5} {'T':>5}  {'PLC':<6} {'Tag':<35} {'Conn':<20} {'Conf':<7} {'Conn2?'}")
print("-"*130)
for i, row in enumerate(MAPPING, 1):
    nm, L, T, W, H, fmt, plc, tag, dtype, conn, owner, conf, nc2, rat = row
    marker = " <BLOCKER>" if nc2 == "YES" else ""
    print(f"{i:<3} {nm:<18} {L:>5} {T:>5}  {plc:<6} {tag:<35} {conn:<20} {conf:<7} {nc2}{marker}")

print()
print("=== BLOCKER SUMMARY ===")
print(f"  {len(need_conn2)} IOFields BLOCKED by missing HMI_Connection_2:")
for r in need_conn2:
    print(f"    {r[0]:<18} -> {r[7]} ({r[6]})")

print()
print("=== LOW CONFIDENCE FIELDS ===")
for r in low_conf:
    print(f"  {r[0]:<18} L={r[1]} T={r[2]} -> {r[7]} | {r[13]}")

# Export CSV
OUT = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_mapping_dry_run.csv"
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["#","ObjectName","Left","Top","Width","Height","FormatPattern",
                     "PLC_Owner","Proposed_Tag","DataType","Proposed_Connection",
                     "Confidence","Need_HMI_Connection_2","Blocker","Rationale"])
    for i, row in enumerate(MAPPING, 1):
        nm, L, T, W, H, fmt, plc, tag, dtype, conn, owner, conf, nc2, rat = row
        blocker = "BLOCKER" if nc2 == "YES" else ""
        writer.writerow([i, nm, L, T, W, H, fmt, plc, tag, dtype, conn, conf, nc2, blocker, rat])
print(f"\nCSV saved: {OUT}")
