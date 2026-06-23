# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# We verify the ACTUAL exported files from TIA Portal (readback)
patched_screens = {
    "bon_tron_1": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_readback.xml",
    "bon_tron_2": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_2_readback.xml",
    "bon_tron_3": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_3_readback.xml",
    "bon_tron_4": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_4_readback.xml"
}

hmi_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags_readback.xml"
dryrun_csv = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\graphic_mapping_dry_run_detail.csv"

# 1. Load HMI Tag Table tags
if not os.path.exists(hmi_tags_path):
    print(f"Error: {hmi_tags_path} not found!")
    sys.exit(1)

tag_tree = ET.parse(hmi_tags_path)
tag_root = tag_tree.getroot()

existing_hmi_tags = set()
for elem in tag_root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Tag" or tag_local == "Hmi.Tag.Tag":
        name_el = elem.find(".//{*}Name")
        if name_el is not None and name_el.text:
            existing_hmi_tags.add(name_el.text.strip())

print(f"Loaded {len(existing_hmi_tags)} HMI tags from readback table.")

# Check for AI_ prefix
ai_tags = [t for t in existing_hmi_tags if t.upper().startswith("AI_")]
if ai_tags:
    print(f"ERROR: Found {len(ai_tags)} tags with forbidden 'AI_' prefix in HMI Tag Table!")
    for t in ai_tags[:5]:
        print(f"  - {t}")
    sys.exit(1)
else:
    print("[PASS] No 'AI_' prefix tags found in HMI Tag Table.")

# 2. Parse dry-run mapping
if not os.path.exists(dryrun_csv):
    print(f"Error: {dryrun_csv} not found!")
    sys.exit(1)

mapped_records = []
with open(dryrun_csv, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        mapped_records.append({
            "ScreenName": row[0],
            "ObjectType": row[1],
            "ObjectName": row[2],
            "Left": int(row[3]),
            "Top": int(row[4]),
            "Width": int(row[5]),
            "Height": int(row[6]),
            "ProposedTag": row[7],
            "PLC_Owner": row[8],
            "Connection": row[9],
            "DataType": row[10],
            "FormatPattern": row[11],
            "ProposedMode": row[12]
        })

print(f"Loaded {len(mapped_records)} mapping records from dry-run CSV.")

# 3. Check each patched screen
errors_found = 0
for scr_name, scr_path in patched_screens.items():
    if not os.path.exists(scr_path):
        print(f"Error: Readback file {scr_path} not found!")
        errors_found += 1
        continue
        
    print(f"\nVerifying TIA readback screen: {scr_name}...")
    tree = ET.parse(scr_path)
    root = tree.getroot()
    
    # Check screen dimensions (1440x900 max)
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local == "Screen" or tag_local == "Hmi.Screen.Screen":
            attrs = elem.find("AttributeList")
            if attrs is not None:
                w_el = attrs.find("Width")
                h_el = attrs.find("Height")
                w = int(w_el.text) if w_el is not None else 1440
                h = int(h_el.text) if h_el is not None else 900
                print(f"  Screen dimensions: {w}x{h}")
                if w > 1440 or h > 900:
                    print(f"  ERROR: Screen size {w}x{h} exceeds 1440x900 boundary!")
                    errors_found += 1
                    
    # Check all objects on screen for border overflow and bindings
    screen_bindings = {} # object_name -> tag_name
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local not in ["IOField", "Hmi.Screen.IOField", "SymbolLibrary", "Hmi.Screen.SymbolLibrary", "GraphicView", "Hmi.Screen.GraphicView"]:
            continue
            
        attrs = elem.find("AttributeList")
        if attrs is None:
            continue
            
        obj_name = attrs.find("ObjectName").text
        left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
        top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
        w = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
        h = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
        
        # Check boundary
        right = left + w
        bottom = top + h
        if right > 1440 or bottom > 900:
            print(f"  ERROR: Object '{obj_name}' at ({left},{top}) size {w}x{h} overflows 1440x900 screen boundary! (Right={right}, Bottom={bottom})")
            errors_found += 1
            
        # Check bound tag
        bound_tag = ""
        obj_list = elem.find("ObjectList")
        if obj_list is not None:
            for prop in obj_list.findall("Hmi.Screen.Property"):
                pname_el = prop.find("AttributeList/Name")
                if pname_el is not None and pname_el.text == "ProcessValue":
                    dyn = prop.find("ObjectList/Hmi.Dynamic.TagConnectionDynamic")
                    if dyn is not None:
                        tag_el = dyn.find("LinkList/Tag")
                        if tag_el is not None:
                            tag_name_el = tag_el.find("Name")
                            if tag_name_el is not None and tag_name_el.text:
                                bound_tag = tag_name_el.text.strip()
                                
        if bound_tag:
            screen_bindings[obj_name] = bound_tag
            
            # Check if tag is in HMI Tag Table
            if bound_tag not in existing_hmi_tags:
                print(f"  ERROR: Object '{obj_name}' bound to tag '{bound_tag}' which is MISSING in HMI Tag Table!")
                errors_found += 1
                
            # Check if tag starts with AI_
            if bound_tag.upper().startswith("AI_"):
                print(f"  ERROR: Object '{obj_name}' bound to tag '{bound_tag}' which has forbidden 'AI_' prefix!")
                errors_found += 1
                
            # If IOField, verify formatting & alignment
            if tag_local.endswith("IOField"):
                h_align = attrs.find("HorizontalAlignment")
                v_align = attrs.find("VerticalAlignment")
                fmt = attrs.find("FormatPattern")
                
                h_align_text = h_align.text if h_align is not None else ""
                v_align_text = v_align.text if v_align is not None else ""
                fmt_text = fmt.text if fmt is not None else ""
                
                if h_align_text != "Center" or v_align_text != "Middle":
                    print(f"  ERROR: IOField '{obj_name}' alignment is not Center/Middle! (H={h_align_text}, V={v_align_text})")
                    errors_found += 1
                    
                # Flow/Level/Temp/CV must be 999.9 or 99.9, Binary must be 1
                if not (fmt_text == "999.9" or fmt_text == "99.9" or fmt_text == "9999" or fmt_text == "1"):
                    print(f"  ERROR: IOField '{obj_name}' has invalid FormatPattern '{fmt_text}'!")
                    errors_found += 1

    # Cross check with dry-run CSV
    scr_records = [r for r in mapped_records if r["ScreenName"] == scr_name]
    for rec in scr_records:
        obj_name = rec["ObjectName"]
        expected_tag = rec["ProposedTag"]
        
        if obj_name not in screen_bindings:
            print(f"  ERROR: Object '{obj_name}' listed in CSV is UNBOUND in readback screen XML!")
            errors_found += 1
        elif screen_bindings[obj_name] != expected_tag:
            print(f"  ERROR: Object '{obj_name}' is bound to tag '{screen_bindings[obj_name]}', expected '{expected_tag}'!")
            errors_found += 1

print(f"\n========================================")
print(f"VERIFICATION RESULTS: {errors_found} errors found.")
print(f"========================================")
if errors_found == 0:
    print("[PASS] TIA Portal Exported Readbacks validation PASSED 100%!")
    sys.exit(0)
else:
    print("[FAIL] TIA Portal Exported Readbacks validation failed!")
    sys.exit(1)
