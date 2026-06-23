# -*- coding: utf-8 -*-
from collections import Counter
import xml.etree.ElementTree as ET
import sys
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens\Hmi.Screen.scadabai5.xml"

if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

tags = [elem.tag.split('}')[-1] for elem in root.iter()]
c = Counter(tags)

for tag, count in c.most_common():
    print(f"{tag}: {count}")
