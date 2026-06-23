import csv
import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

csv_mapping_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_mapping_dry_run.csv"
screen_xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_export.xml"

if not os.path.exists(csv_mapping_path):
    print(f"Error: CSV mapping file not found at {csv_mapping_path}")
    sys.exit(1)

if not os.path.exists(screen_xml_path):
    print(f"Error: Screen XML file not found at {screen_xml_path}")
    sys.exit(1)

# 1. Load CSV Mapping
csv_mapping = {}
with open(csv_mapping_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    # Skip any comment line or empty line
    for row in reader:
        if not row or row[0].startswith('#'):
            continue
        obj_name = row[1]
        if obj_name == 'ObjectName' or obj_name == '(missing)':
            continue
        csv_mapping[obj_name] = {
            "ObjectName": obj_name,
            "Left": int(row[2]),
            "Top": int(row[3]),
            "Width": int(row[4]),
            "Height": int(row[5]),
            "FormatPattern": row[6],
            "Proposed_Tag": row[8],
            "DataType": row[9],
            "Proposed_Connection": row[10]
        }

print(f"Loaded {len(csv_mapping)} mapping records from CSV.")

# 2. Parse Screen XML
tree = ET.parse(screen_xml_path)
root = tree.getroot()

xml_iofields = {}
ns = {"hmi": "http://www.siemens.com/automation/Openness/HMI/Screen/v2"} # open namespace fallback

# We iter through all elements to find IOFields
for elem in root.iter():
    local_tag = elem.tag.split('}')[-1]
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
                
                xml_iofields[obj_name] = {
                    "ObjectName": obj_name,
                    "Left": left,
                    "Top": top,
                    "Width": width,
                    "Height": height,
                    "Element": elem
                }

print(f"Found {len(xml_iofields)} IOFields in Screen_1 XML.")

# 3. Match and Validate
mismatch_count = 0
not_in_csv = []
not_in_xml = []

for name, xml_data in xml_iofields.items():
    if name not in csv_mapping:
        not_in_csv.append(name)
        continue
    csv_data = csv_mapping[name]
    # Check coordinates
    coords_match = (
        xml_data["Left"] == csv_data["Left"] and
        xml_data["Top"] == csv_data["Top"] and
        xml_data["Width"] == csv_data["Width"] and
        xml_data["Height"] == csv_data["Height"]
    )
    if not coords_match:
        print(f"  [MISMATCH] Coordinates mismatch for '{name}':")
        print(f"    XML: Left={xml_data['Left']}, Top={xml_data['Top']}, Width={xml_data['Width']}, Height={xml_data['Height']}")
        print(f"    CSV: Left={csv_data['Left']}, Top={csv_data['Top']}, Width={csv_data['Width']}, Height={csv_data['Height']}")
        mismatch_count += 1

for name in csv_mapping.keys():
    if name not in xml_iofields:
        not_in_xml.append(name)

if not_in_csv:
    print(f"  [ERROR] IOFields found in XML but NOT in CSV: {not_in_csv}")
if not_in_xml:
    print(f"  [ERROR] IOFields expected in CSV but NOT found in XML: {not_in_xml}")

if len(xml_iofields) != 24:
    print(f"  [FAIL] Expected exactly 24 IOFields, but found {len(xml_iofields)}.")
    sys.exit(1)

if mismatch_count > 0 or not_in_csv or not_in_xml:
    print("  [FAIL] Preflight validation failed due to mismatches.")
    sys.exit(1)

print("  [SUCCESS] Preflight validation passed: exactly 24 IOFields match perfectly!")
sys.exit(0)
