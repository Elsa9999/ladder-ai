import sys,io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import xml.etree.ElementTree as ET

tree = ET.parse(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\screen1_export_20260622_220027\Screen_1.xml")
root = tree.getroot()

found_any = False
for node in root.iter("Hmi.Screen.IOField"):
    al = node.find("AttributeList")
    nm = ""
    if al is not None:
        nm_el = al.find("ObjectName")
        if nm_el is not None and nm_el.text:
            nm = nm_el.text.strip()
    ol = node.find("ObjectList")
    bindings = []
    if ol is not None:
        for pb in ol.iter("PropertyBinding"):
            b_name = pb.get("Name","")
            bindings.append(b_name)
    if bindings:
        print(f"{nm}: {bindings}")
        found_any = True

if not found_any:
    print("NO IOField has any PropertyBinding.")
    print("All 24 IOFields are UNBOUND (no ProcessValue assigned).")

# Also check any tag reference anywhere
print("\n--- Scanning all elements for TagName attribute ---")
count = 0
for node in root.iter():
    tn = node.get("TagName","")
    if tn:
        print(f"  Tag: {node.tag}, TagName={tn}")
        count += 1
if count == 0:
    print("  None found.")

# Check TextFields to understand the screen layout
print("\n--- TextField content (first 30) ---")
shown = 0
for node in root.iter("Hmi.Screen.TextField"):
    al = node.find("AttributeList")
    if al is None: continue
    nm_el = al.find("ObjectName")
    left_el = al.find("Left")
    top_el = al.find("Top")
    nm = nm_el.text.strip() if nm_el is not None and nm_el.text else ""
    left = left_el.text.strip() if left_el is not None and left_el.text else "?"
    top = top_el.text.strip() if top_el is not None and top_el.text else "?"
    # Get text
    text = ""
    for mti in node.iter("MultilingualTextItem"):
        mti_al = mti.find("AttributeList")
        if mti_al is not None:
            t_el = mti_al.find("Text")
            if t_el is not None and t_el.text and t_el.text.strip():
                text = t_el.text.strip()
                break
    print(f"  [{nm}] ({left},{top}) text={text!r}")
    shown += 1
    if shown >= 30:
        break
