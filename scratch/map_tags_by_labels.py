# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import sys
import math

sys.stdout.reconfigure(encoding='utf-8')

# Paths
HMI_TAGS_XML = r"D:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai1\HMI\AI_HMI_Tags.xml"
INPUT_SCREEN_XML = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Screen_2.xml"
OUTPUT_DIR = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
OUTPUT_SCREEN_XML = os.path.join(OUTPUT_DIR, "Hmi.Screen.Screen_2.xml")

if not os.path.exists(INPUT_SCREEN_XML):
    print(f"[ERROR] Source HMI Screen XML not found at: {INPUT_SCREEN_XML}")
    exit(1)

if not os.path.exists(HMI_TAGS_XML):
    print(f"[ERROR] HMI Tags XML not found at: {HMI_TAGS_XML}")
    exit(1)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Normalize name function
def normalize_name(s):
    s = s.upper().strip()
    if s.endswith("_PV"):
        s = s[:-3]
    return s.replace(" ", "").replace("-", "").replace("_", "")

# 2. Extract HMI tag names from tag table
print(f"Loading HMI tags from {HMI_TAGS_XML}...")
tag_tree = ET.parse(HMI_TAGS_XML)
tag_root = tag_tree.getroot()

tags_map = {} # normalized_name -> actual_tag_name
for tag in tag_root.findall(".//{http://www.siemens.com/automation/Openness/Attributes}Tag") or tag_root.findall(".//Hmi.Tag.Tag"):
    name_el = tag.find(".//Name") or tag.find("./AttributeList/Name")
    if name_el is not None and name_el.text:
        tag_name = name_el.text.strip()
        norm_name = normalize_name(tag_name)
        tags_map[norm_name] = tag_name
        print(f"  Mapped Tag: {tag_name} -> normalized: {norm_name}")

# Special mappings in case user uses simpler/custom names
tags_map[normalize_name("1400 1-02")] = "1400_1_02_PV"
tags_map[normalize_name("1400_1_02")] = "1400_1_02_PV"
tags_map[normalize_name("1406 TX35")] = "1406_TX35_PV"
tags_map[normalize_name("1406_TX35")] = "1406_TX35_PV"
tags_map[normalize_name("1400LGFE01")] = "1400_LGFE01_PV"

print(f"Total HMI tags indexed: {len(tags_map)}")

# 3. Load screen XML and determine max ID to prevent collisions
ET.register_namespace('', '')
screen_tree = ET.parse(INPUT_SCREEN_XML)
screen_root = screen_tree.getroot()

max_id = 0
for elem in screen_root.iter():
    id_attr = elem.get("ID")
    if id_attr:
        try:
            val = int(id_attr, 16)
            if val > max_id:
                max_id = val
        except ValueError:
            pass

id_counter = max_id + 1000
print(f"Max existing ID in hex is {hex(max_id)}, starting counter at {hex(id_counter)}")

def get_next_id():
    global id_counter
    res = hex(id_counter)[2:].upper()
    id_counter += 1
    return res

# 4. Find the Screen Layer containing ScreenItems
layer = screen_root.find(".//Hmi.Screen.ScreenLayer")
if layer is None:
    print("[ERROR] Hmi.Screen.ScreenLayer not found in Screen XML!")
    exit(1)

object_list = layer.find("ObjectList")
if object_list is None:
    print("[ERROR] ObjectList of Layer not found!")
    exit(1)

# Helper function to find coordinates
def get_coords(elem):
    left_el = elem.find("AttributeList/Left")
    top_el = elem.find("AttributeList/Top")
    width_el = elem.find("AttributeList/Width")
    height_el = elem.find("AttributeList/Height")
    
    left = int(left_el.text) if (left_el is not None and left_el.text) else 0
    top = int(top_el.text) if (top_el is not None and top_el.text) else 0
    width = int(width_el.text) if (width_el is not None and width_el.text) else 0
    height = int(height_el.text) if (height_el is not None and height_el.text) else 0
    return left, top, width, height

# 5. Extract all tag label TextFields from screen XML
print("\nScanning screen TextFields for tag name labels...")
tag_labels = [] # list of dict: {element, text, tag_name, left, top, cx, cy}
for elem in object_list:
    if elem.tag.endswith("TextField"):
        name_el = elem.find("AttributeList/ObjectName")
        obj_name = name_el.text if name_el is not None else ""
        if obj_name.startswith("Text_field_Unit_") or obj_name in ("Header_Title", "Header_Operator_Label"):
            continue
            
        # Get text content
        text_el = elem.find(".//Text")
        if text_el is not None:
            text_val = "".join(text_el.itertext()).strip()
            norm_text = normalize_name(text_val)
            if norm_text in tags_map:
                left, top, w, h = get_coords(elem)
                cx = left + w / 2
                cy = top + h / 2
                tag_labels.append({
                    "element": elem,
                    "text": text_val,
                    "tag_name": tags_map[norm_text],
                    "left": left,
                    "top": top,
                    "cx": cx,
                    "cy": cy
                })
                print(f"  Found Tag Label: '{text_val}' -> binds to '{tags_map[norm_text]}' at position ({left}, {top})")

# 6. Map IOFields to closest tag label TextFields
print("\nMapping IOFields to closest tag labels...")
mapped_io_fields = {} # io_name -> tag_name
io_fields_list = []

for elem in object_list:
    if elem.tag.endswith("IOField"):
        name_el = elem.find("AttributeList/ObjectName")
        io_name = name_el.text if name_el is not None else ""
        if io_name == "Header_Operator_Field":
            continue
            
        left, top, w, h = get_coords(elem)
        cx = left + w / 2
        cy = top + h / 2
        io_fields_list.append((elem, io_name, left, top, w, h, cx, cy))

for elem, io_name, io_left, io_top, io_w, io_h, io_cx, io_cy in io_fields_list:
    if not tag_labels:
        print("[WARNING] No tag labels found on Screen. Check if you added TextFields for tag names!")
        break
        
    # Find closest tag label by center-to-center Euclidean distance
    min_dist = float('inf')
    best_label = None
    for label in tag_labels:
        dist = math.sqrt((io_cx - label["cx"])**2 + (io_cy - label["cy"])**2)
        if dist < min_dist:
            min_dist = dist
            best_label = label
            
    if best_label and min_dist < 180: # Max radius threshold of 180 pixels
        target_tag = best_label["tag_name"]
        mapped_io_fields[io_name] = target_tag
        print(f"  Mapped IOField '{io_name}' at ({io_left}, {io_top}) to Label '{best_label['text']}' (Tag: {target_tag}) [dist={min_dist:.1f}px]")
        
        # A. Bind Tag to IOField ProcessValue property
        # Look for Property CompositionName="Properties" with Name="ProcessValue"
        props_list = elem.find("ObjectList")
        if props_list is None:
            props_list = ET.SubElement(elem, "ObjectList")
            
        prop_val = None
        for prop in props_list:
            if prop.tag.endswith("Property"):
                name_el = prop.find("AttributeList/Name")
                if name_el is not None and name_el.text == "ProcessValue":
                    prop_val = prop
                    break
                    
        if prop_val is None:
            # Create ProcessValue property
            prop_val = ET.SubElement(props_list, "Hmi.Screen.Property", {
                "ID": get_next_id(),
                "CompositionName": "Properties"
            })
            prop_attrs = ET.SubElement(prop_val, "AttributeList")
            ET.SubElement(prop_attrs, "Name").text = "ProcessValue"
            
        prop_objs = prop_val.find("ObjectList")
        if prop_objs is None:
            prop_objs = ET.SubElement(prop_val, "ObjectList")
            
        tag_conn = prop_objs.find(".//{http://www.siemens.com/automation/Openness/Attributes}TagConnectionDynamic") or prop_objs.find(".//TagConnectionDynamic") or prop_objs.find(".//Hmi.Dynamic.TagConnectionDynamic")
        if tag_conn is None:
            tag_conn = ET.SubElement(prop_objs, "Hmi.Dynamic.TagConnectionDynamic", {
                "ID": get_next_id(),
                "CompositionName": "Dynamic"
            })
            conn_attrs = ET.SubElement(tag_conn, "AttributeList")
            ET.SubElement(conn_attrs, "Indirect").text = "false"
            link_list = ET.SubElement(tag_conn, "LinkList")
            tag_el = ET.SubElement(link_list, "Tag", {"TargetID": "@OpenLink"})
            ET.SubElement(tag_el, "Name").text = target_tag
        else:
            tag_el = tag_conn.find(".//Tag")
            if tag_el is not None:
                name_el = tag_el.find("Name")
                if name_el is not None:
                    name_el.text = target_tag
                else:
                    ET.SubElement(tag_el, "Name").text = target_tag
            else:
                link_list = tag_conn.find("LinkList") or ET.SubElement(tag_conn, "LinkList")
                tag_el = ET.SubElement(link_list, "Tag", {"TargetID": "@OpenLink"})
                ET.SubElement(tag_el, "Name").text = target_tag
                
        # B. Style and Format IOField based on Tag type
        attr_list = elem.find("AttributeList")
        if attr_list is not None:
            # Set alignment Center/Middle
            ha = attr_list.find("HorizontalAlignment")
            if ha is not None: ha.text = "Center"
            else: ET.SubElement(attr_list, "HorizontalAlignment").text = "Center"
            
            va = attr_list.find("VerticalAlignment")
            if va is not None: va.text = "Middle"
            else: ET.SubElement(attr_list, "VerticalAlignment").text = "Middle"
            
            # Determine unit and formatting
            unit_val = ""
            format_pat = "99.9"
            
            if "TT" in target_tag or "1_02" in target_tag or "TT101" in target_tag:
                unit_val = "°C"
                format_pat = "99.9"
            elif "PT" in target_tag or "TX" in target_tag:
                unit_val = "bar"
                format_pat = "99.9"
            elif "FS" in target_tag:
                unit_val = "Hz"
                format_pat = "99.9"
            elif "FT" in target_tag or "FTT" in target_tag:
                unit_val = "L/h"
                format_pat = "999.9"
            elif "LGFE" in target_tag or "FY" in target_tag:
                unit_val = "%"
                format_pat = "999.9"
                
            fp_el = attr_list.find("FormatPattern")
            if fp_el is not None: fp_el.text = format_pat
            else: ET.SubElement(attr_list, "FormatPattern").text = format_pat
            
            # C. Handle Unit Label TextField
            unit_obj_name = f"Text_field_Unit_{io_name}"
            unit_tf = None
            
            # Search for existing unit text field
            for sub_el in object_list:
                if sub_el.tag.endswith("TextField"):
                    sub_name = sub_el.find("AttributeList/ObjectName")
                    if sub_name is not None and sub_name.text == unit_obj_name:
                        unit_tf = sub_el
                        break
            
            tf_left = io_left + io_w + 8
            tf_top = io_top
            tf_width = 50
            tf_height = io_h
            
            if unit_tf is None:
                # Create a new unit TextField
                print(f"    Creating unit label '{unit_val}' for '{io_name}'...")
                unit_tf = ET.SubElement(object_list, "Hmi.Screen.TextField", {
                    "ID": get_next_id(),
                    "CompositionName": "ScreenItems"
                })
                
                ut_attrs = ET.SubElement(unit_tf, "AttributeList")
                ET.SubElement(ut_attrs, "BackColor").text = "255, 255, 255"
                ET.SubElement(ut_attrs, "BackFillStyle").text = "Transparent"
                ET.SubElement(ut_attrs, "BorderWidth").text = "0"
                ET.SubElement(ut_attrs, "ForeColor").text = "0, 0, 0"
                ET.SubElement(ut_attrs, "Height").text = str(tf_height)
                ET.SubElement(ut_attrs, "HorizontalAlignment").text = "Left"
                ET.SubElement(ut_attrs, "Left").text = str(tf_left)
                ET.SubElement(ut_attrs, "ObjectName").text = unit_obj_name
                ET.SubElement(ut_attrs, "Top").text = str(tf_top)
                ET.SubElement(ut_attrs, "VerticalAlignment").text = "Middle"
                ET.SubElement(ut_attrs, "Width").text = str(tf_width)
                
                link_list = ET.SubElement(unit_tf, "LinkList")
                ET.SubElement(link_list, "StyleItem", {"TargetID": "@OpenLink"}).text = "Text field"
                
                ut_objs = ET.SubElement(unit_tf, "ObjectList")
                
                # MultiLingualFont
                font = ET.SubElement(ut_objs, "Hmi.Globalization.MultiLingualFont", {
                    "ID": get_next_id(),
                    "CompositionName": "Font"
                })
                font_objs = ET.SubElement(font, "ObjectList")
                font_item = ET.SubElement(font_objs, "Hmi.Globalization.FontItem", {
                    "ID": get_next_id(),
                    "CompositionName": "Items"
                })
                fi_attrs = ET.SubElement(font_item, "AttributeList")
                ET.SubElement(fi_attrs, "Culture").text = "en-US"
                ET.SubElement(fi_attrs, "FontFamily").text = "Arial"
                ET.SubElement(fi_attrs, "FontSize").text = "13"
                ET.SubElement(fi_attrs, "FontStyle").text = "Bold"
                
                # MultilingualText
                ml_text = ET.SubElement(ut_objs, "MultilingualText", {
                    "ID": get_next_id(),
                    "CompositionName": "Text"
                })
                ml_objs = ET.SubElement(ml_text, "ObjectList")
                ml_item = ET.SubElement(ml_objs, "MultilingualTextItem", {
                    "ID": get_next_id(),
                    "CompositionName": "Items"
                })
                item_attrs = ET.SubElement(ml_item, "AttributeList")
                ET.SubElement(item_attrs, "Culture").text = "en-US"
                ET.SubElement(item_attrs, "Text").text = f"<body><p>{unit_val}</p></body>"
            else:
                # Update existing unit TextField
                print(f"    Updating existing unit label to '{unit_val}' and positioning at left={tf_left}...")
                ut_attrs = unit_tf.find("AttributeList")
                if ut_attrs is not None:
                    left_el = ut_attrs.find("Left")
                    if left_el is not None: left_el.text = str(tf_left)
                    else: ET.SubElement(ut_attrs, "Left").text = str(tf_left)
                    
                    top_el = ut_attrs.find("Top")
                    if top_el is not None: top_el.text = str(tf_top)
                    else: ET.SubElement(ut_attrs, "Top").text = str(tf_top)
                    
                    height_el = ut_attrs.find("Height")
                    if height_el is not None: height_el.text = str(tf_height)
                    else: ET.SubElement(ut_attrs, "Height").text = str(tf_height)
                    
                    width_el = ut_attrs.find("Width")
                    if width_el is not None: width_el.text = str(tf_width)
                    else: ET.SubElement(ut_attrs, "Width").text = str(tf_width)
                    
                    ha_el = ut_attrs.find("HorizontalAlignment")
                    if ha_el is not None: ha_el.text = "Left"
                    else: ET.SubElement(ut_attrs, "HorizontalAlignment").text = "Left"
                    
                    va_el = ut_attrs.find("VerticalAlignment")
                    if va_el is not None: va_el.text = "Middle"
                    else: ET.SubElement(ut_attrs, "VerticalAlignment").text = "Middle"
                    
                    fs_el = ut_attrs.find("BackFillStyle")
                    if fs_el is not None: fs_el.text = "Transparent"
                    
                    bw_el = ut_attrs.find("BorderWidth")
                    if bw_el is not None: bw_el.text = "0"
                    
                # Update text value
                text_item = unit_tf.find(".//MultilingualTextItem/AttributeList")
                if text_item is not None:
                    txt_el = text_item.find("Text")
                    if txt_el is not None:
                        txt_el.text = f"<body><p>{unit_val}</p></body>"
                        
                # Update font to 13 Bold Arial
                font_item_attrs = unit_tf.find(".//Hmi.Globalization.FontItem/AttributeList")
                if font_item_attrs is not None:
                    ff = font_item_attrs.find("FontFamily")
                    if ff is not None: ff.text = "Arial"
                    else: ET.SubElement(font_item_attrs, "FontFamily").text = "Arial"
                    
                    fs = font_item_attrs.find("FontSize")
                    if fs is not None: fs.text = "13"
                    else: ET.SubElement(font_item_attrs, "FontSize").text = "13"
                    
                    fsty = font_item_attrs.find("FontStyle")
                    if fsty is not None: fsty.text = "Bold"
                    else: ET.SubElement(font_item_attrs, "FontStyle").text = "Bold"

# 7. Apply warning/limit alarms dynamically to IOFields that bound to TT32 and TX35
def add_appearance_animation(element, tag_name, limits_ranges):
    objs = element.find("ObjectList")
    if objs is None:
        objs = ET.SubElement(element, "ObjectList")
    
    # Remove existing RangeAppearanceAnimation if any
    to_remove = []
    for item in objs:
        if item.tag.endswith("RangeAppearanceAnimation"):
            to_remove.append(item)
    for item in to_remove:
        objs.remove(item)
        
    anim = ET.SubElement(objs, "Hmi.Dynamic.RangeAppearanceAnimation", {
        "ID": get_next_id(),
        "CompositionName": "Animations"
    })
    attrs = ET.SubElement(anim, "AttributeList")
    ET.SubElement(attrs, "Name").text = "RangeAppearanceAnimation"
    
    anim_objs = ET.SubElement(anim, "ObjectList")
    trigger = ET.SubElement(anim_objs, "Hmi.Dynamic.TagElementTrigger", {
        "ID": get_next_id(),
        "CompositionName": "RangeTag"
    })
    trigger_links = ET.SubElement(trigger, "LinkList")
    val_tag = ET.SubElement(trigger_links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(val_tag, "Name").text = tag_name
    
    for item in limits_ranges:
        low, high, bg_color, fg_color, flashing = item
        r = ET.SubElement(anim_objs, "Hmi.Dynamic.Range", {
            "ID": get_next_id(),
            "CompositionName": "RangeValues"
        })
        r_attrs = ET.SubElement(r, "AttributeList")
        ET.SubElement(r_attrs, "BackColor").text = bg_color
        ET.SubElement(r_attrs, "FlashingType").text = flashing
        ET.SubElement(r_attrs, "ForeColor").text = fg_color
        ET.SubElement(r_attrs, "LowerLimit").text = str(int(low))
        ET.SubElement(r_attrs, "UpperLimit").text = str(int(high))

print("\nApplying RangeAppearanceAnimations for critical tags...")
for elem, io_name, io_left, io_top, io_w, io_h, io_cx, io_cy in io_fields_list:
    if io_name in mapped_io_fields:
        tag_bound = mapped_io_fields[io_name]
        if tag_bound == "1400_TT32_PV":
            print(f"  Applying high temp alarm blinking to '{io_name}'...")
            add_appearance_animation(elem, "1400_TT32_PV", [
                (0, 74, "255, 255, 255", "0, 0, 0", "No"),
                (75, 77, "245, 158, 11", "0, 0, 0", "No"),
                (78, 150, "220, 38, 38", "255, 255, 255", "Fast")
            ])
        elif tag_bound == "1406_TX35_PV":
            print(f"  Applying high pressure alarm blinking to '{io_name}'...")
            add_appearance_animation(elem, "1406_TX35_PV", [
                (0, 6, "255, 255, 255", "0, 0, 0", "No"),
                (7, 7, "245, 158, 11", "0, 0, 0", "No"),
                (8, 15, "220, 38, 38", "255, 255, 255", "Fast")
            ])

# Save output screen XML
screen_tree.write(OUTPUT_SCREEN_XML, encoding="utf-8", xml_declaration=True)
print(f"\n[SUCCESS] Patched Hmi.Screen.Screen_2.xml written to: {OUTPUT_SCREEN_XML}")
