import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

tree1 = ET.parse(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_export.xml")
tree2 = ET.parse(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_2_export.xml")

sl1 = {}
for elem in tree1.getroot().iter():
    if elem.tag.endswith("SymbolLibrary"):
        attrs = elem.find("AttributeList")
        if attrs is not None:
            name = attrs.find("ObjectName").text
            left = int(attrs.find("Left").text)
            top = int(attrs.find("Top").text)
            w = int(attrs.find("Width").text)
            h = int(attrs.find("Height").text)
            sl1[name] = (left, top, w, h)

sl2 = {}
for elem in tree2.getroot().iter():
    if elem.tag.endswith("SymbolLibrary"):
        attrs = elem.find("AttributeList")
        if attrs is not None:
            name = attrs.find("ObjectName").text
            left = int(attrs.find("Left").text)
            top = int(attrs.find("Top").text)
            w = int(attrs.find("Width").text)
            h = int(attrs.find("Height").text)
            sl2[name] = (left, top, w, h)

print("Bồn 1 SymbolLibraries:")
for name, coords in sorted(sl1.items(), key=lambda x: x[1][0]):
    print(f"  {name}: {coords}")

print("\nBồn 2 SymbolLibraries:")
for name, coords in sorted(sl2.items(), key=lambda x: x[1][0]):
    print(f"  {name}: {coords}")
