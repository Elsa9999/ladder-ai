# -*- coding: utf-8 -*-
import csv
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

csv_numeric_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_mapping_dry_run.csv"
csv_graphic_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\graphic_mapping_dry_run.csv"
tags_xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags_readback.xml"
screen_xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_readback.xml"

errors = []

def log_error(msg):
    errors.append(msg)
    print(f"[FAIL] {msg}")

def log_pass(msg):
    print(f"[PASS] {msg}")

# 1. Load CSV Mappings
numeric_mapping = {}
if os.path.exists(csv_numeric_path):
    with open(csv_numeric_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            obj_name = row[1].strip()
            if obj_name == 'ObjectName' or obj_name == '(missing)' or not obj_name:
                continue
            numeric_mapping[obj_name] = {
                "ObjectName": obj_name,
                "Left": int(row[2]),
                "Top": int(row[3]),
                "Width": int(row[4]),
                "Height": int(row[5]),
                "FormatPattern": row[6].strip(),
                "Proposed_Tag": row[8].strip(),
                "DataType": row[9].strip(),
                "Proposed_Connection": row[10].strip()
            }
else:
    log_error(f"Numeric CSV mapping not found at {csv_numeric_path}")
    sys.exit(1)

graphic_mapping = {}
if os.path.exists(csv_graphic_path):
    with open(csv_graphic_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            obj_name = row[0].strip()
            if obj_name == 'ObjectName' or obj_name == '(missing)' or not obj_name:
                continue
            graphic_mapping[obj_name] = {
                "ObjectName": obj_name,
                "Left": int(row[1]),
                "Top": int(row[2]),
                "Width": int(row[3]),
                "Height": int(row[4]),
                "GraphicList": row[5].strip(),
                "Proposed_Tag": row[6].strip(),
                "PLC_Owner": row[7].strip(),
                "Proposed_Connection": row[8].strip(),
                "DataType": row[9].strip(),
                "ProposedMode": row[11].strip()
            }
else:
    log_error(f"Graphic CSV mapping not found at {csv_graphic_path}")
    sys.exit(1)

print(f"Loaded {len(numeric_mapping)} numeric mapping records.")
print(f"Loaded {len(graphic_mapping)} graphic mapping records.")

# 2. Parse HMI Tag Table Readback
if not os.path.exists(tags_xml_path):
    log_error(f"Tags readback XML not found at {tags_xml_path}")
    sys.exit(1)

tags_tree = ET.parse(tags_xml_path)
tags_root = tags_tree.getroot()

imported_tags = {}
for elem in tags_root.iter():
    local_tag = elem.tag.split('}')[-1]
    if local_tag == "Hmi.Tag.Tag":
        attr_list = elem.find("AttributeList")
        link_list = elem.find("LinkList")
        if attr_list is not None and link_list is not None:
            name_el = attr_list.find("Name")
            if name_el is not None and name_el.text:
                tag_name = name_el.text.strip()
                
                conn_name = ""
                conn_el = link_list.find("Connection")
                if conn_el is not None:
                    name_child = conn_el.find("Name")
                    if name_child is not None and name_child.text:
                        conn_name = name_child.text.strip()
                
                dtype_name = ""
                dtype_el = link_list.find("DataType")
                if dtype_el is not None:
                    name_child = dtype_el.find("Name")
                    if name_child is not None and name_child.text:
                        dtype_name = name_child.text.strip()
                        
                imported_tags[tag_name] = {
                    "Name": tag_name,
                    "Connection": conn_name,
                    "DataType": dtype_name
                }

print(f"Parsed {len(imported_tags)} tags from HMI Tag Table readback.")

# Verify tag counts and connection distribution
conn1_count = sum(1 for t in imported_tags.values() if t["Connection"] == "HMI_Connection_1")
conn2_count = sum(1 for t in imported_tags.values() if t["Connection"] == "HMI_Connection_2")
print(f"  Tags on HMI_Connection_1: {conn1_count} (expected 44: 16 numeric + 28 graphic)")
print(f"  Tags on HMI_Connection_2: {conn2_count} (expected 21: 8 numeric + 13 graphic)")

if len(imported_tags) not in [65, 69]:
    log_error(f"Expected 65 or 69 unique tags, but got {len(imported_tags)}.")

if conn1_count != 44 or conn2_count != 21:
    log_error("Tag connection distribution is incorrect.")

# Check prefix AI_
ai_prefixed_tags = [t for t in imported_tags.keys() if t.upper().startswith("AI_")]
if ai_prefixed_tags:
    log_error(f"Found tags with prefix 'AI_': {ai_prefixed_tags}")

# Verify all expected tags are defined correctly in HMI Tag Table
for name, csv_data in numeric_mapping.items():
    tname = csv_data["Proposed_Tag"]
    if tname not in imported_tags:
        log_error(f"Numeric tag '{tname}' for '{name}' is missing in HMI Tag Table!")
    else:
        hmi_tag = imported_tags[tname]
        if hmi_tag["DataType"] != csv_data["DataType"] or hmi_tag["Connection"] != csv_data["Proposed_Connection"]:
            log_error(f"Tag definition mismatch for '{tname}': Expected ({csv_data['DataType']}, {csv_data['Proposed_Connection']}) vs HMI Table: ({hmi_tag['DataType']}, {hmi_tag['Connection']})")

for name, csv_data in graphic_mapping.items():
    tname = csv_data["Proposed_Tag"]
    if tname not in imported_tags:
        log_error(f"Graphic tag '{tname}' for '{name}' is missing in HMI Tag Table!")
    else:
        hmi_tag = imported_tags[tname]
        if hmi_tag["DataType"] != csv_data["DataType"] or hmi_tag["Connection"] != csv_data["Proposed_Connection"]:
            log_error(f"Tag definition mismatch for '{tname}': Expected ({csv_data['DataType']}, {csv_data['Proposed_Connection']}) vs HMI Table: ({hmi_tag['DataType']}, {hmi_tag['Connection']})")

if not errors:
    log_pass("Tag Table checks passed successfully!")

# 3. Parse Screen XML Readback
if not os.path.exists(screen_xml_path):
    log_error(f"Screen readback XML not found at {screen_xml_path}")
    sys.exit(1)

screen_tree = ET.parse(screen_xml_path)
screen_root = screen_tree.getroot()

xml_iofields = {}
xml_graphicfields = {}

for elem in screen_root.iter():
    local_tag = elem.tag.split('}')[-1]
    
    # Parse Numeric IOFields
    if local_tag == "Hmi.Screen.IOField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name_elem = attrs.find("ObjectName")
            if obj_name_elem is not None and obj_name_elem.text:
                obj_name = obj_name_elem.text.strip()
                
                left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
                top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
                width = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
                height = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
                
                halign = attrs.find("HorizontalAlignment").text if attrs.find("HorizontalAlignment") is not None else ""
                valign = attrs.find("VerticalAlignment").text if attrs.find("VerticalAlignment") is not None else ""
                fmt = attrs.find("FormatPattern").text if attrs.find("FormatPattern") is not None else ""
                
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
                                        
                xml_iofields[obj_name] = {
                    "ObjectName": obj_name,
                    "Left": left,
                    "Top": top,
                    "Width": width,
                    "Height": height,
                    "HorizontalAlignment": halign,
                    "VerticalAlignment": valign,
                    "FormatPattern": fmt,
                    "BoundTag": bound_tag
                }

    # Parse GraphicIOFields
    elif local_tag == "Hmi.Screen.GraphicIOField":
        attrs = elem.find("AttributeList")
        if attrs is not None:
            obj_name_elem = attrs.find("ObjectName")
            if obj_name_elem is not None and obj_name_elem.text:
                obj_name = obj_name_elem.text.strip()
                
                left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
                top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
                width = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
                height = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
                
                mode = attrs.find("Mode").text if attrs.find("Mode") is not None else ""
                
                pic_list = "None"
                links = elem.find("LinkList")
                if links is not None:
                    pic_el = links.find(".//PictureList") or links.find(".//Picture")
                    if pic_el is not None:
                        name_el = pic_el.find("Name")
                        if name_el is not None:
                            pic_list = name_el.text.strip()
                
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
                                        
                xml_graphicfields[obj_name] = {
                    "ObjectName": obj_name,
                    "Left": left,
                    "Top": top,
                    "Width": width,
                    "Height": height,
                    "Mode": mode,
                    "GraphicList": pic_list,
                    "BoundTag": bound_tag
                }

print(f"Parsed {len(xml_iofields)} numeric IOFields from screen XML.")
print(f"Parsed {len(xml_graphicfields)} graphic IOFields from screen XML.")

# Verify numeric IOFields
for name, csv_data in numeric_mapping.items():
    if name not in xml_iofields:
        log_error(f"Expected numeric IOField '{name}' is missing in Screen XML readback!")
        continue
    xml_data = xml_iofields[name]
    
    # 1. Coords
    if (xml_data["Left"] != csv_data["Left"] or xml_data["Top"] != csv_data["Top"] or
        xml_data["Width"] != csv_data["Width"] or xml_data["Height"] != csv_data["Height"]):
        log_error(f"Numeric IOField '{name}' coordinate mismatch!")
        
    # 2. Alignment
    if xml_data["HorizontalAlignment"] != "Center" or xml_data["VerticalAlignment"] != "Middle":
        log_error(f"Numeric IOField '{name}' alignment mismatch! Got: H={xml_data['HorizontalAlignment']}, V={xml_data['VerticalAlignment']}")
        
    # 3. FormatPattern
    if xml_data["FormatPattern"] != csv_data["FormatPattern"]:
        log_error(f"Numeric IOField '{name}' format pattern mismatch! Expected: {csv_data['FormatPattern']}, Got: {xml_data['FormatPattern']}")
        
    # 4. Binding
    if xml_data["BoundTag"] != csv_data["Proposed_Tag"]:
        log_error(f"Numeric IOField '{name}' binding mismatch! Expected: '{csv_data['Proposed_Tag']}', Got: '{xml_data['BoundTag']}'")

# Verify GraphicIOFields
for name, csv_data in graphic_mapping.items():
    if name not in xml_graphicfields:
        log_error(f"Expected graphic IOField '{name}' is missing in Screen XML readback!")
        continue
    xml_data = xml_graphicfields[name]
    
    # 1. Coords
    if (xml_data["Left"] != csv_data["Left"] or xml_data["Top"] != csv_data["Top"] or
        xml_data["Width"] != csv_data["Width"] or xml_data["Height"] != csv_data["Height"]):
        log_error(f"Graphic IOField '{name}' coordinate mismatch!")
        
    # 2. Mode (must always be Output)
    if xml_data["Mode"] != "Output":
        log_error(f"Graphic IOField '{name}' mode is not Output! Got: '{xml_data['Mode']}'")
        
    # 3. GraphicList
    if xml_data["GraphicList"] != csv_data["GraphicList"]:
        log_error(f"Graphic IOField '{name}' GraphicList mismatch! Expected: '{csv_data['GraphicList']}', Got: '{xml_data['GraphicList']}'")
        
    # 4. Binding
    if xml_data["BoundTag"] != csv_data["Proposed_Tag"]:
        log_error(f"Graphic IOField '{name}' binding mismatch! Expected: '{csv_data['Proposed_Tag']}', Got: '{xml_data['BoundTag']}'")

# 5. Check for empty or extra/unbound fields in Screen XML
for name, data in xml_iofields.items():
    if not data["BoundTag"]:
        log_error(f"Numeric IOField '{name}' has an empty/unbound Process Tag!")
    elif name not in numeric_mapping:
        log_error(f"Numeric IOField '{name}' in XML is not defined in expected mapping!")

for name, data in xml_graphicfields.items():
    if not data["BoundTag"]:
        log_error(f"Graphic IOField '{name}' has an empty/unbound Process Tag!")
    elif name not in graphic_mapping:
        log_error(f"Graphic IOField '{name}' in XML is not defined in expected mapping!")

# Verify Agitator Tank physical layout order (Bồn 1 -> Bồn 2 -> Bồn 4 -> Bồn 3)
agitators = ["Graphic I/O field_38", "Graphic I/O field_39", "Graphic I/O field_40", "Graphic I/O field_41"]
for ag in agitators:
    if ag not in xml_graphicfields:
        log_error(f"Expected agitator field '{ag}' not found in Screen XML!")
        sys.exit(1)

left_1 = xml_graphicfields["Graphic I/O field_38"]["Left"]
left_2 = xml_graphicfields["Graphic I/O field_39"]["Left"]
left_4 = xml_graphicfields["Graphic I/O field_40"]["Left"]
left_3 = xml_graphicfields["Graphic I/O field_41"]["Left"]

print(f"Agitators X Positions: Bon1={left_1}, Bon2={left_2}, Bon4={left_4}, Bon3={left_3}")
if not (left_1 < left_2 < left_4 < left_3):
    log_error(f"Agitator physical layout order on HMI screen is incorrect! Expected Bon1 < Bon2 < Bon4 < Bon3, got positions {left_1} < {left_2} < {left_4} < {left_3}")
else:
    log_pass("Agitator physical layout order verified: Bồn 1 -> Bồn 2 -> Bồn 4 -> Bồn 3")

# Report results
print("\n--- READBACK SUMMARY ---")
print(f"Total Numeric IOFields Checked: {len(xml_iofields)} / 24")
print(f"Total Graphic IOFields Checked: {len(xml_graphicfields)} / 41")
print(f"Total Errors Found: {len(errors)}")

if errors:
    print("\n[FAIL] TIA Screen_1 Readback Verification FAILED!")
    sys.exit(1)
else:
    print("\n[PASS] TIA Screen_1 Readback Verification PASSED 100%!")
    sys.exit(0)
