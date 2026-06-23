import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml")
root = tree.getroot()

def dump_tag(tag_name):
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local == "Tag" or tag_local == "Hmi.Tag.Tag":
            name_el = elem.find(".//{*}Name")
            if name_el is not None and name_el.text == tag_name:
                print(f"\n--- Tag: {tag_name} ---")
                print(ET.tostring(elem, encoding='utf-8').decode('utf-8'))
                return
    print(f"Tag {tag_name} not found!")

dump_tag("CV3201_Nuoc_Bon1_M")
dump_tag("HMI_SP_PLC1_Nuoc_Bon1")
