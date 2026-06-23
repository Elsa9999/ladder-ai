# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml"

if not os.path.exists(xml_path):
    print(f"File not found: {xml_path}")
    sys.exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

found = 0
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    # Check if this element is a screen item (e.g. Button, GraphicIOField, IOField, GraphicView)
    # Screen items usually have AttributeList and ObjectName
    attrs = elem.find("AttributeList")
    if attrs is not None:
        obj_name = attrs.find("ObjectName")
        if obj_name is not None:
            left = attrs.find("Left").text if attrs.find("Left") is not None else "N/A"
            top = attrs.find("Top").text if attrs.find("Top") is not None else "N/A"
            width = attrs.find("Width").text if attrs.find("Width") is not None else "N/A"
            height = attrs.find("Height").text if attrs.find("Height") is not None else "N/A"
            
            # Now let's traverse this element's ObjectList and find any property bindings
            objs = elem.find("ObjectList")
            if objs is not None:
                # Find all Property nodes
                for prop in objs.findall(".//Hmi.Screen.Property") + objs.findall(".//Property"):
                    pname = prop.find("AttributeList/Name")
                    pname_text = pname.text if pname is not None else "UnknownProperty"
                    
                    # Look for TagConnectionDynamic or TagElementTrigger or similar
                    for tag_conn in prop.findall(".//Hmi.Dynamic.TagConnectionDynamic") + prop.findall(".//TagConnectionDynamic"):
                        tag_el = tag_conn.find(".//Tag")
                        if tag_el is not None:
                            name_el = tag_el.find("Name")
                            if name_el is not None:
                                print(f"Item: {obj_name.text} ({tag_local}) at ({left}, {top}), Size: {width}x{height}")
                                print(f"  Prop: {pname_text} -> Bound Tag: {name_el.text}")
                                found += 1
                                
                    # Also check for visibility animations or other animations
                    for vis in prop.findall(".//Hmi.Dynamic.VisibilityAnimation") + prop.findall(".//VisibilityAnimation"):
                        # Check Tag
                        tag_el = vis.find(".//Tag")
                        if tag_el is not None:
                            name_el = tag_el.find("Name")
                            if name_el is not None:
                                print(f"Item: {obj_name.text} ({tag_local}) at ({left}, {top}), Size: {width}x{height}")
                                print(f"  Prop: VisibilityAnimation -> Tag: {name_el.text}")
                                found += 1
                                
                # Also check animations at the element level (e.g. Animations composition)
                for anim in objs.findall(".//Hmi.Dynamic.RangeAppearanceAnimation") + objs.findall(".//RangeAppearanceAnimation") + objs.findall(".//Hmi.Dynamic.VisibilityAnimation") + objs.findall(".//VisibilityAnimation"):
                    tag_el = anim.find(".//Tag")
                    if tag_el is not None:
                        name_el = tag_el.find("Name")
                        if name_el is not None:
                            print(f"Item: {obj_name.text} ({tag_local}) at ({left}, {top}), Size: {width}x{height}")
                            print(f"  Animation: {anim.tag.split('}')[-1]} -> Tag: {name_el.text}")
                            found += 1

print(f"Total bindings found: {found}")
