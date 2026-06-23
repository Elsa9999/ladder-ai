import xml.etree.ElementTree as ET
import os

xml_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_export.xml"

if not os.path.exists(xml_path):
    print("Exported XML does not exist:", xml_path)
    exit(1)

tree = ET.parse(xml_path)
root = tree.getroot()

def print_element_details(elem, tag_type):
    attrs = elem.find("AttributeList")
    obj_name = ""
    if attrs is not None:
        name_el = attrs.find("ObjectName")
        if name_el is not None:
            obj_name = name_el.text
    
    print(f"\n=== Found {tag_type}: {obj_name} (ID: {elem.get('ID')}) ===")
    
    # Print some properties
    if attrs is not None:
        mode_el = attrs.find("Mode")
        if mode_el is not None:
            print(f"  Mode: {mode_el.text}")
            
    # Print events or property dynamics
    for child in elem.iter():
        child_tag = child.tag.split('}')[-1]
        
        # Check property bindings (like ProcessValue)
        if "Property" in child_tag:
            pname = child.find("AttributeList/Name")
            if pname is not None:
                pname_text = pname.text
                print(f"  Property: {pname_text}")
                # Print tag binding if dynamic
                dyn = child.find(".//Hmi.Dynamic.TagConnectionDynamic") or child.find(".//TagConnectionDynamic")
                if dyn is not None:
                    tag_el = dyn.find(".//Tag")
                    if tag_el is not None:
                        tag_name_el = tag_el.find("Name")
                        if tag_name_el is not None:
                            print(f"    Dynamic Tag Binding -> Name: {tag_name_el.text}")
                            
        # Check events (like Activate on Button)
        if "Event" in child_tag:
            ename = child.find("AttributeList/Name")
            if ename is not None:
                ename_text = ename.text
                print(f"  Event: {ename_text}")
                # Print event action/function call details
                actions = child.find("ObjectList")
                if actions is not None:
                    for action in actions:
                        act_tag = action.tag.split('}')[-1]
                        print(f"    Action Type: {act_tag}")
                        act_attrs = action.find("AttributeList")
                        if act_attrs is not None:
                            # Print any interesting attributes of the action
                            for attr in act_attrs:
                                print(f"      {attr.tag.split('}')[-1]}: {attr.text}")
                        # Print link parameters (like screen names, etc.)
                        act_links = action.find("LinkList")
                        if act_links is not None:
                            for link in act_links:
                                link_name = link.find("Name")
                                if link_name is not None:
                                    print(f"      Link Parameter ({link.tag.split('}')[-1]}): {link_name.text}")

# Iterate over all elements
for elem in root.iter():
    tag_local = elem.tag.split('}')[-1]
    attrs = elem.find("AttributeList")
    if attrs is not None:
        name_el = attrs.find("ObjectName")
        if name_el is not None and name_el.text in ["Button_10", "I/O field_6", "I/O field_4", "I/O field_11"]:
            print_element_details(elem, tag_local)
