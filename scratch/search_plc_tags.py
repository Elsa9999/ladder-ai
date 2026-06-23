# -*- coding: utf-8 -*-
import re

plc_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\plc_tags_list.txt"
out_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\matched_tags.txt"

with open(plc_tags_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

current_plc = ""
tags = {"PLC1": [], "PLC2": []}

for line in lines:
    line = line.strip()
    if not line:
        continue
    if "PLC 1 TAGS" in line:
        current_plc = "PLC1"
        continue
    elif "PLC 2 TAGS" in line:
        current_plc = "PLC2"
        continue
    
    m = re.match(r"Name:\s*(\S+)\s*\|\s*Type:\s*(\S+)\s*\|\s*Addr:\s*(\S+)", line)
    if m:
        tags[current_plc].append({
            "name": m.group(1),
            "type": m.group(2),
            "addr": m.group(3)
        })

with open(out_path, "w", encoding="utf-8") as out:
    def search_pattern(pattern):
        out.write(f"\n=== Searching for: {pattern} ===\n")
        regex = re.compile(pattern, re.IGNORECASE)
        for plc in ["PLC1", "PLC2"]:
            out.write(f"--- {plc} ---\n")
            for tag in tags[plc]:
                if regex.search(tag["name"]) or regex.search(tag["addr"]):
                    out.write(f"  Name: {tag['name']:40s} | Type: {tag['type']:8s} | Addr: {tag['addr']}\n")

    search_pattern("FT3200|FQ3200|V32_30|V32_32|V32_33|V32_34|CV3201|LT3203|TT3204|AGTR3260|32_64|Pump3264")
    search_pattern("FT3205|FQ3205|V32_35|V32_37|V32_38|V32_39|CV3206|LT3209|TT3208|AGTR3261|Pump3264")
    search_pattern("FT3210|FQ3210|V32_40|V32_42|V32_43|V32_44|CV3211|LT3213|TT3214|AGTR3262|Pump3269")
    search_pattern("FT3215|FQ3215|V32_45|V32_47|V32_48|V32_49|CV3216|LT3218|TT3219|AGTR3263|Pump3265")
    search_pattern("32_64|32_65|32.64|32.65|Pump_ChuyenDich|Pump_TuanHoanLoc|Pump326")
    search_pattern("BonChua|3301|3302|3303|3306|3307|3308|3309|3310|3311|33.31|33.32|33.61|33.62|33.64|33.65")
    search_pattern("V32|CV32|FT32|FQ32|LT32|TT32|Pump32")

print("Done writing to matched_tags.txt.")
