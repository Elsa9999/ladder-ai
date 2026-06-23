import os
import csv
import xml.etree.ElementTree as ET

PROJECT_DIR = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026"
WATCH_DIR = os.path.join(PROJECT_DIR, "watch_tables")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

# Mapping of CSV files to PLC target
PLC_TARGET = {
    "PLC1_Watch_Main_Sequence.csv": "PLC1",
    "PLC1_Watch_PID_VFD.csv": "PLC1",
    "PLC1_Watch_Fake_PLC2_Modbus_Return.csv": "PLC1",
    "PLC2_Watch_Main_Sequence.csv": "PLC2",
    "PLC2_Watch_PID_Sim.csv": "PLC2",
    "PLC2_Watch_Fake_PLC1_Modbus_Command.csv": "PLC2",
}

def load_plc_tags(xml_path):
    tags = set()
    if not os.path.exists(xml_path):
        print(f"Error: Tag file not found: {xml_path}")
        return tags
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local == 'SW.Tags.PlcTag' or tag_local == 'PlcTag':
            name_node = elem.find('.//Name')
            if name_node is not None and name_node.text:
                tags.add(name_node.text.strip())
    return tags

def load_db_members(db_xml_path, db_name):
    members = set()
    if not os.path.exists(db_xml_path):
        print(f"Error: DB XML file not found: {db_xml_path}")
        return members
    
    tree = ET.parse(db_xml_path)
    root = tree.getroot()
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local == 'Member':
            name = elem.attrib.get('Name')
            if name:
                members.add(f'"{db_name}".{name}')
    return members

def verify():
    # 1. Load all valid tags for PLC1 and PLC2
    plc1_tags = load_plc_tags(os.path.join(OUTPUT_DIR, "AI_Tags_PLC1.xml"))
    plc2_tags = load_plc_tags(os.path.join(OUTPUT_DIR, "AI_Tags_PLC2.xml"))
    
    # Load DB members and format them as "DBName".MemberName
    plc1_db_recv = load_db_members(os.path.join(OUTPUT_DIR, "DB_PLC1_Recv_From_PLC2_DB.xml"), "DB_PLC1_Recv_From_PLC2_DB")
    plc1_db_send = load_db_members(os.path.join(OUTPUT_DIR, "DB_PLC1_Send_To_PLC2_DB.xml"), "DB_PLC1_Send_To_PLC2_DB")
    plc2_db_mb = load_db_members(os.path.join(OUTPUT_DIR, "DB_Modbus_Holding_Register_DB.xml"), "DB_Modbus_Holding_Register_DB")
    
    # Combine plc1 and plc2 tag sets
    valid_tags_plc1 = plc1_tags | plc1_db_recv | plc1_db_send
    valid_tags_plc2 = plc2_tags | plc2_db_mb
    
    print(f"Loaded {len(plc1_tags)} tags for PLC1 (+ {len(plc1_db_recv) + len(plc1_db_send)} DB tags)")
    print(f"Loaded {len(plc2_tags)} tags for PLC2 (+ {len(plc2_db_mb)} DB tags)")
    
    all_ok = True
    
    for csv_file, plc in PLC_TARGET.items():
        csv_path = os.path.join(WATCH_DIR, csv_file)
        if not os.path.exists(csv_path):
            print(f"Skipping {csv_file} (not found)")
            continue
            
        print(f"\nChecking Watch Table: {csv_file} (PLC: {plc})")
        seen_tags = set()
        
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            row_idx = 1
            for row in reader:
                row_idx += 1
                # Check for empty rows
                if not row or not any(row):
                    print(f"  [ERROR] Row {row_idx}: Empty row found.")
                    all_ok = False
                    continue
                    
                tag_name = row[0].strip()
                comment = row[1].strip() if len(row) > 1 else ""
                
                # Check for empty tag name
                if not tag_name:
                    print(f"  [ERROR] Row {row_idx}: Tag name is empty.")
                    all_ok = False
                    continue
                
                # Check for duplicate
                if tag_name in seen_tags:
                    print(f"  [ERROR] Row {row_idx}: Duplicate tag '{tag_name}' found.")
                    all_ok = False
                seen_tags.add(tag_name)
                
                # Check existence
                valid_set = valid_tags_plc1 if plc == "PLC1" else valid_tags_plc2
                if tag_name not in valid_set:
                    # Let's check with or without quotes
                    unquoted = tag_name.replace('"', '')
                    found = False
                    for valid_tag in valid_set:
                        if valid_tag.replace('"', '') == unquoted:
                            found = True
                            break
                    if not found:
                        print(f"  [ERROR] Row {row_idx}: Tag '{tag_name}' does not exist in {plc} project definitions!")
                        all_ok = False
        
        print(f"  Total tags checked: {len(seen_tags)}")
        
    if all_ok:
        print("\n=== SUCCESS: All Watch Tables passed validation checks! ===")
        exit(0)
    else:
        print("\n=== FAILURE: Some Watch Tables failed validation! ===")
        exit(1)

if __name__ == "__main__":
    verify()
