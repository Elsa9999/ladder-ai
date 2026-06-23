import xml.etree.ElementTree as ET

tree = ET.parse(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_export.xml")
root = tree.getroot()

for elem in root.iter():
    if "IOField" in elem.tag:
        attrs = elem.find("AttributeList")
        if attrs is not None:
            name = attrs.find("ObjectName")
            if name is not None and name.text in ["I/O field_11", "I/O field_4", "I/O field_6"]:
                print("========================================")
                print(name.text)
                print("========================================")
                for attr in attrs:
                    print(f"  {attr.tag.split('}')[-1]}: {attr.text}")
