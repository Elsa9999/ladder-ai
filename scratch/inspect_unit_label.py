# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

unit_tf = None
for elem in root.iter():
    if elem.tag.endswith("TextField"):
        name_el = elem.find("AttributeList/ObjectName")
        if name_el is not None and name_el.text == "Text_field_Unit_I_O_field_1":
            unit_tf = elem
            break

if unit_tf is not None:
    object_list = unit_tf.find("ObjectList")
    if object_list is not None:
        for obj in object_list:
            print(f"Child Tag: {obj.tag} | ID: {obj.get('ID')} | Composition: {obj.get('CompositionName')}")
            # print XML string of child
            ET.indent(obj)
            print(ET.tostring(obj, encoding="utf-8").decode("utf-8"))
else:
    print("No Text_field_Unit_I_O_field_1 found!")
