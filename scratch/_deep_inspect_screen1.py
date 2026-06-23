import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import xml.etree.ElementTree as ET, json, csv, math

XML = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_export_20260622_220027\Screen_1.xml"
tree = ET.parse(XML)
root = tree.getroot()

def al(node, tag):
    a = node.find("AttributeList")
    if a is None: return ""
    e = a.find(tag)
    return (e.text or "").strip() if e is not None else ""

def get_tf_text(node):
    """Get MultilingualText content from node."""
    for mti in node.iter("MultilingualTextItem"):
        a = mti.find("AttributeList")
        if a is not None:
            t = a.find("Text")
            if t is not None and t.text and t.text.strip():
                return t.text.strip()
    return ""

# All TextFields
print("=== ALL TextFields ===")
tfs = []
for node in root.iter("Hmi.Screen.TextField"):
    name = al(node, "ObjectName")
    try:
        L = int(float(al(node, "Left") or 0))
        T = int(float(al(node, "Top") or 0))
        W = int(float(al(node, "Width") or 0))
        H = int(float(al(node, "Height") or 0))
    except: L=T=W=H=0
    txt = get_tf_text(node)
    # Also check Caption / Text in AttributeList directly
    cap = al(node, "Text") or al(node, "Caption")
    if not txt and cap:
        txt = cap
    tfs.append((name, L, T, W, H, txt))

for nm,L,T,W,H,txt in tfs:
    print(f"  [{nm}] ({L},{T},{W}x{H}) text={txt!r}")

# Screen dimensions
print("\n=== SCREEN DIMENSIONS ===")
scr = root.find("Hmi.Screen.Screen")
if scr is None:
    for n in root.iter("Hmi.Screen.Screen"):
        scr = n; break
if scr is not None:
    print(f"  Width : {al(scr,'Width')}")
    print(f"  Height: {al(scr,'Height')}")
    print(f"  Name  : {al(scr,'Name')}")

# Check ALL attributes in AttributeList of IOfield_1
print("\n=== IOField_1 ALL AttributeList tags ===")
for node in root.iter("Hmi.Screen.IOField"):
    nm = al(node, "ObjectName")
    if nm == "I/O field_1":
        a = node.find("AttributeList")
        if a is not None:
            for child in a:
                print(f"  <{child.tag}>{child.text or ''}</{child.tag}>")
        break

# Now check GraphicView (background image)
print("\n=== GraphicView items (first 5) ===")
shown = 0
for node in root.iter("Hmi.Screen.GraphicView"):
    nm = al(node, "ObjectName")
    gn = al(node, "GraphicName") or al(node, "SourcePath") or al(node, "GraphicItem")
    try:
        L = int(float(al(node, "Left") or 0))
        T = int(float(al(node, "Top") or 0))
        W = int(float(al(node, "Width") or 0))
        H = int(float(al(node, "Height") or 0))
    except: L=T=W=H=0
    print(f"  [{nm}] ({L},{T}) {W}x{H} graphic={gn!r}")
    shown += 1
    if shown >= 5: break
