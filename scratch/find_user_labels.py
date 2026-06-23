# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

print("Searching for text labels...")
# Let's search all elements in the XML for any text containing "1400" or similar
for elem in root.iter():
    text_content = "".join(elem.itertext()).strip()
    if any(tag in text_content for tag in ["1400FT115", "1400 1-02", "1400FT101", "1406 TX35", "1400TT64", "1400TT32", "1400FS51", "1400LGFE01", "1400FY301"]):
        print(f"Found match: Tag='{elem.tag}' | ID='{elem.get('ID')}' | Text='{text_content}'")
