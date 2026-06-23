import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PLC_TAGS_FILE = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\plc_tags_list.txt"

with open(PLC_TAGS_FILE, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Parse tags
plc1_tags = {}
plc2_tags = {}
current = None
for line in content.splitlines():
    if "=== PLC 1" in line or "=== PLC1" in line:
        current = "PLC1"
    elif "=== PLC 2" in line or "=== PLC2" in line:
        current = "PLC2"
    elif line.startswith("Name:") and current:
        parts = line.split("|")
        name = parts[0].replace("Name:","").strip()
        dtype = parts[1].replace("Type:","").strip() if len(parts)>1 else ""
        addr  = parts[2].replace("Addr:","").strip() if len(parts)>2 else ""
        if current == "PLC1":
            plc1_tags[name] = (dtype, addr)
        elif current == "PLC2":
            plc2_tags[name] = (dtype, addr)

print(f"PLC_1 tags total: {len(plc1_tags)}")
print(f"PLC_2 tags total: {len(plc2_tags)}")

# Tags to check
PLC1_CHECK = [
    "FQ3200_Bon1_Eff", "FQ3205_Bon2_Eff", "FQ3215_Bon4_Eff",
    "LT3203_Bon1_Eff", "LT3209_Bon2_Eff", "LT3218_Bon4_Eff",
    "TT3204_Bon1_Eff", "TT3208_Bon2_Eff", "TT3219_Bon4_Eff",
    "CV3201_Nuoc_Bon1_M", "CV3206_Hoi_Bon2_M", "CV3216_Hoi_Bon4_M",
    "LT3302_BonChua1_Eff", "TT3301_BonChua1_Eff",
    "LT3307_BonChua2_Eff", "TT3306_BonChua2_Eff",
    "TT3303_TraoDoiNhiet_Eff", "CV3304_Nuoc_Lam_Mat_M",
    "FT3309_Xa_Thanh_Pham_Eff",
]
PLC2_CHECK = [
    "FQ3210_Bon3_Eff", "LT3213_Bon3_Eff", "TT3214_Bon3_Eff", "CV3211_Nuoc_Bon3_M",
]

print("\n=== PLC_1 TAG VERIFICATION ===")
plc1_missing = []
plc1_ok = []
for t in PLC1_CHECK:
    if t in plc1_tags:
        dtype, addr = plc1_tags[t]
        print(f"  [OK]     {t:<40} Type={dtype}, Addr={addr}")
        plc1_ok.append(t)
    else:
        # Try fuzzy
        candidates = [k for k in plc1_tags if t.lower() in k.lower() or k.lower() in t.lower()]
        print(f"  [MISS]   {t:<40} Not found. Similar: {candidates[:3]}")
        plc1_missing.append(t)

print(f"\nPLC_1: {len(plc1_ok)} OK, {len(plc1_missing)} MISSING")
if plc1_missing:
    print("  Missing PLC_1 tags:")
    for t in plc1_missing:
        print(f"    - {t}")

print("\n=== PLC_2 TAG VERIFICATION ===")
plc2_missing = []
plc2_ok = []
for t in PLC2_CHECK:
    if t in plc2_tags:
        dtype, addr = plc2_tags[t]
        print(f"  [OK]     {t:<40} Type={dtype}, Addr={addr}")
        plc2_ok.append(t)
    else:
        candidates = [k for k in plc2_tags if t.lower() in k.lower() or k.lower() in t.lower()]
        print(f"  [MISS]   {t:<40} Not found. Similar: {candidates[:3]}")
        plc2_missing.append(t)

print(f"\nPLC_2: {len(plc2_ok)} OK, {len(plc2_missing)} MISSING")

# HMI Connection feasibility
print("\n=== HMI CONNECTION FEASIBILITY ===")
print("  HMI_Connection_1 -> PLC_1: EXISTS (confirmed)")
print("  HMI_Connection_2 -> PLC_2: DOES NOT EXIST")
print("  BLOCKER: 4 IOFields require PLC_2 tags via HMI_Connection_2")
print("  Options to create HMI_Connection_2:")
print("    A) Via TIA Portal UI: HMI_RT_1 > Connections > Add Connection > SIMATIC S7 1200 > select PLC_2")
print("    B) Via XML import: Modify HmiTarget XML to add Connection element")
print("    C) Via Openness API: hmiTarget.Connections.Create(...) - NOT available in public API")
print("  Recommendation: Option A (manual in TIA UI) is safest and most reliable")

# Readback HMI tags
print("\n=== CURRENT HMI TAGS READBACK (from prior session) ===")
print("  3 tags confirmed in HMI_RT_1:")
print("    1. Logged_In              | Internal | Connection=<Internal>")
print("    2. HMI_SP_PLC2_Nhiet_Do_Bon4 | PLC_2 tag | Connection=None (import error)")
print("    3. HMI_SP_PLC2_Nuoc_Bon3    | PLC_2 tag | Connection=None (import error)")
print("  Note: Tags 2-3 have Connection=None due to prior failed import attempt.")
print("        They are harmless but invalid until HMI_Connection_2 is established.")
