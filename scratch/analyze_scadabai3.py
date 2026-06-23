import xml.etree.ElementTree as ET
import os

xml_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml"
if not os.path.exists(xml_path):
    print("Error: XML file does not exist at", xml_path)
    exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

def get_local_tag(elem):
    return elem.tag.split("}")[-1]

def find_local(elem, local_name):
    if elem is None:
        return None
    for child in elem:
        if get_local_tag(child) == local_name:
            return child
    return None

# Find ObjectList of ScreenLayer
object_list = None
for elem in root.iter():
    if get_local_tag(elem) == "Hmi.Screen.ScreenLayer":
        object_list = find_local(elem, "ObjectList")
        if object_list is not None:
            break

if object_list is None:
    print("Error: ObjectList of ScreenLayer not found!")
    exit(1)

io_fields = []
text_fields = []

for elem in object_list:
    local_tag = get_local_tag(elem)
    if local_tag == "Hmi.Screen.IOField":
        attrs = find_local(elem, "AttributeList")
        if attrs is not None:
            name_el = find_local(attrs, "ObjectName")
            left_el = find_local(attrs, "Left")
            top_el = find_local(attrs, "Top")
            width_el = find_local(attrs, "Width")
            height_el = find_local(attrs, "Height")
            fp_el = find_local(attrs, "FormatPattern")
            
            name = name_el.text if name_el is not None else "Unknown"
            left = left_el.text if left_el is not None else "0"
            top = top_el.text if top_el is not None else "0"
            width = width_el.text if width_el is not None else "0"
            height = height_el.text if height_el is not None else "0"
            fp = fp_el.text if fp_el is not None else "None"
            
            # Find current tag binding
            tag_name = "NONE"
            objs = find_local(elem, "ObjectList")
            if objs is not None:
                for prop in objs:
                    if get_local_tag(prop) == "Hmi.Screen.Property":
                        p_attrs = find_local(prop, "AttributeList")
                        if p_attrs is not None:
                            p_name = find_local(p_attrs, "Name")
                            if p_name is not None and p_name.text == "ProcessValue":
                                p_objs = find_local(prop, "ObjectList")
                                if p_objs is not None:
                                    conn = find_local(p_objs, "Hmi.Dynamic.TagConnectionDynamic")
                                    if conn is not None:
                                        links = find_local(conn, "LinkList")
                                        if links is not None:
                                            tag_el = find_local(links, "Tag")
                                            if tag_el is not None:
                                                t_name_el = find_local(tag_el, "Name")
                                                if t_name_el is not None:
                                                    tag_name = t_name_el.text
            
            io_fields.append({
                "name": name,
                "left": int(left),
                "top": int(top),
                "width": int(width),
                "height": int(height),
                "format": fp,
                "tag": tag_name
            })
    elif local_tag == "Hmi.Screen.TextField":
        attrs = find_local(elem, "AttributeList")
        if attrs is not None:
            name_el = find_local(attrs, "ObjectName")
            left_el = find_local(attrs, "Left")
            top_el = find_local(attrs, "Top")
            name = name_el.text if name_el is not None else "Unknown"
            left = left_el.text if left_el is not None else "0"
            top = top_el.text if top_el is not None else "0"
            
            txt_el = None
            objs = find_local(elem, "ObjectList")
            if objs is not None:
                m_text = find_local(objs, "MultilingualText")
                if m_text is not None:
                    m_objs = find_local(m_text, "ObjectList")
                    if m_objs is not None:
                        m_item = find_local(m_objs, "MultilingualTextItem")
                        if m_item is not None:
                            m_attrs = find_local(m_item, "AttributeList")
                            if m_attrs is not None:
                                txt_el = find_local(m_attrs, "Text")
            
            txt = txt_el.text if txt_el is not None else ""
            if txt is None:
                txt = ""
            text_fields.append({
                "name": name,
                "left": int(left),
                "top": int(top),
                "text": txt
            })

# Sort by Top, then Left
io_fields.sort(key=lambda x: (x["top"], x["left"]))

print(f"=== IO FIELDS IN scadabai3 ({len(io_fields)} fields) ===")
for io in io_fields:
    print(f"Name: {io['name']:15s} | Left: {io['left']:4d} | Top: {io['top']:4d} | Width: {io['width']:3d} | Height: {io['height']:3d} | Format: {io['format']:10s} | Tag: {io['tag']}")

print(f"\n=== TEXT FIELDS IN scadabai3 ({len(text_fields)} fields) ===")
for tf in sorted(text_fields, key=lambda x: (x["top"], x["left"])):
    print(f"Name: {tf['name']:25s} | Left: {tf['left']:4d} | Top: {tf['top']:4d} | Text: {tf['text'][:100].strip()}")
