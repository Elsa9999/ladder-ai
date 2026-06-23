import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_export.xml")
root = tree.getroot()

print("Labels in Bồn 1:")
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local.endswith("TextField"):
        mult_txt = elem.find(".//{*}MultilingualTextItem")
        if mult_txt is not None:
            txt_elem = mult_txt.find(".//{*}Text")
            if txt_elem is not None:
                text_val = "".join(txt_elem.itertext()).strip()
                print(f"  Label: '{text_val}' on object '{elem.find('AttributeList/ObjectName').text if elem.find('AttributeList/ObjectName') is not None else ''}' at ({elem.find('AttributeList/Left').text},{elem.find('AttributeList/Top').text})")
                
print("\nSymbolLibraries in Bồn 1:")
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if tag_local.endswith("SymbolLibrary"):
        attrs = elem.find("AttributeList")
        if attrs is not None:
            print(f"  SL: '{attrs.find('ObjectName').text}' at ({attrs.find('Left').text},{attrs.find('Top').text}) size {attrs.find('Width').text}x{attrs.find('Height').text}")
