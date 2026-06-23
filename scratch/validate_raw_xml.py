import os
import xml.etree.ElementTree as ET

raw_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_patterns"
if not os.path.exists(raw_patterns_dir):
    print("Error: raw_patterns directory does not exist.")
    exit(1)

success = True
print("--- VALIDATING RAW XML PATTERNS ---")

for folder in os.listdir(raw_patterns_dir):
    folder_path = os.path.join(raw_patterns_dir, folder)
    if not os.path.isdir(folder_path):
        continue
    
    xml_path = os.path.join(folder_path, "pattern.raw.xml")
    if os.path.exists(xml_path):
        try:
            # Try to parse the XML
            ET.parse(xml_path)
            print(f"[WELL-FORMED] {folder}/pattern.raw.xml")
        except ET.ParseError as pe:
            print(f"[INVALID XML] {folder}/pattern.raw.xml: {pe}")
            success = False
        except Exception as e:
            print(f"[ERROR] {folder}/pattern.raw.xml: {e}")
            success = False

if success:
    print("\n[SUCCESS] All extracted raw patterns are well-formed XML!")
else:
    print("\n[FAILED] Some raw patterns have XML syntax errors.")
