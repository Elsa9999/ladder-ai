import os
import csv
import xml.sax.saxutils as saxutils
from datetime import datetime

CSV_DIR = os.path.dirname(os.path.abspath(__file__))
XML_OUT_DIR = os.path.join(CSV_DIR, "xml")

# Mapping from CSV filename to (Target PLC, Table Name)
MAPPING = {
    "PLC1_Watch_Main_Sequence.csv": ("PLC_1", "WT_PLC1_Main_Sequence"),
    "PLC1_Watch_PID_VFD.csv": ("PLC_1", "WT_PLC1_PID_VFD"),
    "PLC1_Watch_Fake_PLC2_Modbus_Return.csv": ("PLC_1", "WT_PLC1_Fake_PLC2_Modbus_Return"),
    "PLC2_Watch_Main_Sequence.csv": ("PLC_2", "WT_PLC2_Main_Sequence"),
    "PLC2_Watch_PID_Sim.csv": ("PLC_2", "WT_PLC2_PID_Sim"),
    "PLC2_Watch_Fake_PLC1_Modbus_Command.csv": ("PLC_2", "WT_PLC2_Fake_PLC1_Modbus_Command"),
}

def clean_tag_name(tag_name):
    # Strip any leading/trailing whitespace
    tag_name = tag_name.strip()
    return tag_name

def generate_watch_table_xml(table_name, tags):
    created_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    xml_lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<Document>',
        '  <Engineering version="V18" />',
        '  <DocumentInfo>',
        f'    <Created>{created_time}</Created>',
        '    <ExportSetting>WithDefaults</ExportSetting>',
        '  </DocumentInfo>',
        '  <SW.WatchAndForceTables.PlcWatchTable ID="0">',
        '    <AttributeList>',
        f'      <Name>{table_name}</Name>',
        '    </AttributeList>',
        '    <ObjectList>'
    ]
    
    for idx, tag in enumerate(tags, 1):
        escaped_tag = saxutils.escape(tag, {'"': '&quot;'})
        xml_lines.append(f'      <SW.WatchAndForceTables.PlcWatchTableEntry ID="{idx}" CompositionName="Entries">')
        xml_lines.append('        <AttributeList>')
        xml_lines.append(f'          <Name>{escaped_tag}</Name>')
        xml_lines.append('        </AttributeList>')
        xml_lines.append('      </SW.WatchAndForceTables.PlcWatchTableEntry>')
        
    xml_lines.extend([
        '    </ObjectList>',
        '  </SW.WatchAndForceTables.PlcWatchTable>',
        '</Document>'
    ])
    
    return "\n".join(xml_lines)

def main():
    if not os.path.exists(XML_OUT_DIR):
        os.makedirs(XML_OUT_DIR)
        print(f"Created XML output directory: {XML_OUT_DIR}")
        
    for csv_file, (plc_name, table_name) in MAPPING.items():
        csv_path = os.path.join(CSV_DIR, csv_file)
        if not os.path.exists(csv_path):
            print(f"Warning: CSV file not found: {csv_path}")
            continue
            
        print(f"Processing {csv_file} -> PLC: {plc_name}, Table: {table_name}")
        
        tags = []
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip header row
            header = next(reader, None)
            for row in reader:
                if not row or not row[0]:
                    continue
                tag_name = clean_tag_name(row[0])
                if tag_name:
                    tags.append(tag_name)
                    
        xml_content = generate_watch_table_xml(table_name, tags)
        xml_path = os.path.join(XML_OUT_DIR, f"{table_name}.xml")
        
        with open(xml_path, mode='w', encoding='utf-8') as f:
            f.write(xml_content)
            
        print(f"  Generated XML: {xml_path} with {len(tags)} tags")

if __name__ == "__main__":
    main()
