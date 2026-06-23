import xml.etree.ElementTree as ET
import sys

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_export.xml"

tree = ET.parse(xml_path)
root = tree.getroot()

for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    if "Button" in tag_local or "IOField" in tag_local:
        # check parent/child name or ObjectName
        attrs = elem.find("AttributeList")
        if attrs is not None:
            name_el = attrs.find("ObjectName")
            if name_el is not None and name_el.text in ["Button_10", "I/O field_6", "I/O field_4", "I/O field_11"]:
                print(f"\n========================================")
                print(f" ELEMENT: {name_el.text}")
                print(f"========================================")
                ET.indent(elem)
                xml_str = ET.tostring(elem, encoding="utf-8").decode("utf-8")
                print(xml_str)
