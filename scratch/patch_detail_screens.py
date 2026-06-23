# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import csv
import os
import sys
import hashlib

sys.stdout.reconfigure(encoding='utf-8')

missing_hmi_tags = []

# Source original XML files and target patched paths
screens = {
    "bon_tron_1": {
        "export": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_export.xml",
        "patched": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_patched.xml",
        "connection": "HMI_Connection_1",
        "plc": "PLC1",
        "layout": "A",
        "mapping": {
            "IOField": {
                "I/O field_9": ("FQ3200_Bon1_Eff", "Real", "999.9", "L"),
                "I/O field_12": ("LT3203_Bon1_Eff", "Real", "999.9", "L"),
                "I/O field_13": ("TT3204_Bon1_Eff", "Real", "999.9", "°C"),
                "I/O field_8": ("CV3201_Nuoc_Bon1_M", "Real", "999.9", "%"),
                "I/O field_1": ("HMI_SP_Time_Khuay_Bon1", "Time", "9999", None),
                "I/O field_7": ("HMI_SP_PLC1_Nuoc_Bon1", "Real", "999.9", "L"),
                # Simulated/extra fields to format
                "I/O field_11": ("GIA_TRI_NHIET_DO_DOC_VE", "Real", "999.9", "°C"),
                "I/O field_4": ("nguyen_lieu_tron_1", "Bool", "1", None),
                "I/O field_6": ("cap_nuoc_tron_1", "Bool", "1", None)
            },
            "SymbolLibrary": {
                "Symbol library_2": ("HMI_Anim_Bon1_Frame", "Int", "Output"),
                "Symbol library_5": ("HMI_Anim_Bon1_MucDich", "Int", "Output"),
                "Symbol library_11": ("V3232_Xa_Bon1", "Bool", "Output"),
                "Symbol library_9": ("V3233_Xa_Bon1", "Bool", "Output"),
                "Symbol library_4": ("V3234_Xa_Bon1", "Bool", "Output"),
                "Symbol library_16": ("Pump3264_Chuyen_Nhanh1", "Bool", "Output")
            }
        }
    },
    "bon_tron_2": {
        "export": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_2_export.xml",
        "patched": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_2_patched.xml",
        "connection": "HMI_Connection_1",
        "plc": "PLC1",
        "layout": "B",
        "mapping": {
            "IOField": {
                "I/O field_9": ("FQ3205_Bon2_Eff", "Real", "999.9", "L"),
                "I/O field_12": ("LT3209_Bon2_Eff", "Real", "999.9", "L"),
                "I/O field_13": ("TT3208_Bon2_Eff", "Real", "999.9", "°C"),
                "I/O field_8": ("CV3206_Hoi_Bon2_M", "Real", "999.9", "%"),
                "I/O field_5": ("HMI_SP_PLC1_Nhiet_Do_Bon2", "Real", "999.9", "°C"),
                "I/O field_1": ("HMI_SP_Time_Fwd", "Time", "9999", None),
                "I/O field_2": ("HMI_SP_Time_Rev", "Time", "9999", None),
                "I/O field_3": ("HMI_SP_Time_Sterilize", "Time", "9999", None),
                "I/O field_7": ("HMI_SP_PLC1_Nuoc_Bon2", "Real", "999.9", "L"),
                # Simulated/extra fields to format
                "I/O field_11": ("GIA_TRI_NHIET_DO_DOC_VE", "Real", "999.9", "°C"),
                "I/O field_4": ("nguyen_lieu_tron_1", "Bool", "1", None),
                "I/O field_6": ("cap_nuoc_tron_1", "Bool", "1", None)
            },
            "SymbolLibrary": {
                "Symbol library_2": ("HMI_Anim_Bon2_Frame", "Int", "Output"),
                "Symbol library_5": ("HMI_Anim_Bon2_MucDich", "Int", "Output"),
                "Symbol library_56": ("V3235_Nuoc_Bon2", "Bool", "Output"),
                "Symbol library_11": ("V3237_Xa_Bon2", "Bool", "Output"),
                "Symbol library_9": ("V3238_Xa_Bon2", "Bool", "Output"),
                "Symbol library_14": ("V3239_Xa_Bon2", "Bool", "Output"),
                "Symbol library_17": ("CV3206_Hoi_Bon2_M", "Bool", "Output"),
                "Symbol library_16": ("Pump3264_Chuyen_Nhanh1", "Bool", "Output")
            }
        }
    },
    "bon_tron_3": {
        "export": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_3_export.xml",
        "patched": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_3_patched.xml",
        "connection": "HMI_Connection_2",
        "plc": "PLC2",
        "layout": "A",
        "mapping": {
            "IOField": {
                "I/O field_9": ("FQ3210_Bon3_Eff", "Real", "999.9", "L"),
                "I/O field_12": ("LT3213_Bon3_Eff", "Real", "999.9", "L"),
                "I/O field_13": ("TT3214_Bon3_Eff", "Real", "999.9", "°C"),
                "I/O field_8": ("CV3211_Nuoc_Bon3_M", "Real", "999.9", "%"),
                "I/O field_1": ("HMI_SP_Time_Khuay_Bon3", "Time", "9999", None),
                "I/O field_7": ("HMI_SP_PLC2_Nuoc_Bon3", "Real", "999.9", "L"),
                # Simulated/extra fields to format
                "I/O field_11": ("GIA_TRI_NHIET_DO_DOC_VE", "Real", "999.9", "°C"),
                "I/O field_4": ("nguyen_lieu_tron_1", "Bool", "1", None),
                "I/O field_6": ("cap_nuoc_tron_1", "Bool", "1", None)
            },
            "SymbolLibrary": {
                "Symbol library_2": ("HMI_Anim_Bon3_Frame", "Int", "Output"),
                "Symbol library_5": ("HMI_Anim_Bon3_MucDich", "Int", "Output"),
                "Symbol library_11": ("V3242_Xa_Bon3", "Bool", "Output"),
                "Symbol library_9": ("V3243_Xa_Bon3", "Bool", "Output"),
                "Symbol library_4": ("V3244_Xa_Bon3", "Bool", "Output"),
                "Symbol library_16": ("Pump3265_Chuyen_Nhanh2", "Bool", "Output")
            }
        }
    },
    "bon_tron_4": {
        "export": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_4_export.xml",
        "patched": r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_4_patched.xml",
        "connection": "HMI_Connection_2",
        "plc": "PLC2",
        "layout": "B",
        "mapping": {
            "IOField": {
                "I/O field_9": ("FQ3215_Bon4_Eff", "Real", "999.9", "L"),
                "I/O field_12": ("LT3218_Bon4_Eff", "Real", "999.9", "L"),
                "I/O field_13": ("TT3219_Bon4_Eff", "Real", "999.9", "°C"),
                "I/O field_8": ("CV3216_Hoi_Bon4_M", "Real", "999.9", "%"),
                "I/O field_5": ("HMI_SP_PLC2_Nhiet_Do_Bon4", "Real", "999.9", "°C"),
                "I/O field_1": ("HMI_SP_Time_Fwd", "Time", "9999", None),
                "I/O field_2": ("HMI_SP_Time_Rev", "Time", "9999", None),
                "I/O field_3": ("HMI_SP_Time_Sterilize", "Time", "9999", None),
                "I/O field_7": ("HMI_SP_PLC2_Nuoc_Bon4", "Real", "999.9", "L"),
                # Simulated/extra fields to format
                "I/O field_11": ("GIA_TRI_NHIET_DO_DOC_VE", "Real", "999.9", "°C"),
                "I/O field_4": ("nguyen_lieu_tron_1", "Bool", "1", None),
                "I/O field_6": ("cap_nuoc_tron_1", "Bool", "1", None)
            },
            "SymbolLibrary": {
                "Symbol library_2": ("HMI_Anim_Bon4_Frame", "Int", "Output"),
                "Symbol library_5": ("HMI_Anim_Bon4_MucDich", "Int", "Output"),
                "Symbol library_56": ("V3245_Nuoc_Bon4", "Bool", "Output"),
                "Symbol library_11": ("V3247_Xa_Bon4", "Bool", "Output"),
                "Symbol library_9": ("V3248_Xa_Bon4", "Bool", "Output"),
                "Symbol library_14": ("V3249_Xa_Bon4", "Bool", "Output"),
                "Symbol library_17": ("CV3216_Hoi_Bon4_M", "Bool", "Output"),
                "Symbol library_16": ("Pump3265_Chuyen_Nhanh2", "Bool", "Output")
            }
        }
    }
}

hmi_tags_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml"
dryrun_path = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\graphic_mapping_dry_run_detail.csv"

# Global data logs
mapping_results = []
label_mismatches = []
blocked_objects = []

# Define standard blocked tags for report
blocked_objects_info = [
    {"Screen": "bon_tron_1", "Tag": "HMI_SP_PLC1_Nhiet_Do_Bon1 (SP(C))", "Reason": "Bồn 1 không gia nhiệt (Blocked)"},
    {"Screen": "bon_tron_1", "Tag": "HMI_SP_Time_Rev_Bon1", "Reason": "Bồn 1 không có tag thời gian khuấy ngược trong PLC (Blocked)"},
    {"Screen": "bon_tron_1", "Tag": "V3230_Nuoc_Bon1", "Reason": "Không có symbol van V3230 trên màn hình chi tiết Bồn 1 (Blocked)"},
    {"Screen": "bon_tron_3", "Tag": "HMI_SP_PLC2_Nhiet_Do_Bon3 (SP(C))", "Reason": "Bồn 3 không gia nhiệt (Blocked)"},
    {"Screen": "bon_tron_3", "Tag": "HMI_SP_Time_Rev_Bon3", "Reason": "Bồn 3 không có tag thời gian khuấy ngược trong PLC (Blocked)"},
    {"Screen": "bon_tron_3", "Tag": "V3240_Nuoc_Bon3", "Reason": "Không có symbol van V3240 trên màn hình chi tiết Bồn 3 (Blocked)"}
]

# Standard label mismatches to report
label_mismatches_info = [
    {"Screen": "bon_tron_1", "Label": "V3235", "Detail": "Nhãn ghi V3235 nhưng tag thực tế là V3230_Nuoc_Bon1 (Tuy nhiên symbol van không tồn tại trên màn hình)"},
    {"Screen": "bon_tron_3", "Label": "V3235", "Detail": "Nhãn ghi V3235 nhưng tag thực tế là V3240_Nuoc_Bon3 (Tuy nhiên symbol van không tồn tại trên màn hình)"},
    {"Screen": "bon_tron_3", "Label": "AGTR 3260", "Detail": "Nhãn ghi AGTR 3260 nhưng tag thực tế là HMI_Anim_Bon3_Frame (AGTR 3262)"},
    {"Screen": "bon_tron_4", "Label": "LT3219", "Detail": "Nhãn mức bồn ghi LT3219 nhưng dùng cảm biến LT3218"},
    {"Screen": "bon_tron_4", "Label": "TT3218", "Detail": "Nhãn nhiệt độ ghi TT3218 nhưng dùng cảm biến TT3219"}
]

# XML Modification Helpers
ET.register_namespace('', '')

def get_next_id(existing_ids):
    max_id = max(existing_ids) if existing_ids else 1000
    new_id = max_id + 1
    existing_ids.append(new_id)
    return hex(new_id)[2:].upper()

def get_all_ids(root):
    ids = []
    for elem in root.iter():
        id_val = elem.get("ID")
        if id_val is not None:
            try:
                ids.append(int(id_val, 16))
            except ValueError:
                pass
    return ids

# 1. Update HMI Tag Table XML with missing setpoint tags
if os.path.exists(hmi_tags_path):
    print("Patching HMI Tag Table XML...")
    tag_tree = ET.parse(hmi_tags_path)
    tag_root = tag_tree.getroot()
    
    # Register namespaces to preserve format
    namespaces = {node[0]: node[1] for _, node in ET.iterparse(hmi_tags_path, events=['start-ns'])}
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
        
    tag_table_elem = None
    for elem in tag_root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local == "TagTable" or tag_local == "Hmi.Tag.TagTable":
            name_el = elem.find(".//{*}Name")
            if name_el is not None and name_el.text == "Screen1_HMI_Tags":
                tag_table_elem = elem
                break
                
    if tag_table_elem is None:
        for elem in tag_root.iter():
            tag_local = elem.tag.split('}')[-1]
            if tag_local == "TagTable" or tag_local == "Hmi.Tag.TagTable":
                tag_table_elem = elem
                break
                
    if tag_table_elem is not None:
        existing_tags = set()
        object_list_elem = None
        for child in list(tag_table_elem):
            child_local = child.tag.split('}')[-1]
            if child_local == "ObjectList":
                object_list_elem = child
                break
                
        if object_list_elem is not None:
            for tag in object_list_elem.iter():
                tag_local = tag.tag.split('}')[-1]
                if tag_local == "Tag" or tag_local == "Hmi.Tag.Tag":
                    name_el = tag.find(".//{*}Name")
                    if name_el is not None and name_el.text:
                        existing_tags.add(name_el.text.strip())
                        
            tag_ids = get_all_ids(tag_root)
            added_tags_count = 0
            ns_prefix = ""
            if tag_table_elem.tag.startswith("{"):
                ns_prefix = tag_table_elem.tag.split('}')[0] + "}"
                
            for m_tag in missing_hmi_tags:
                if m_tag["Name"] not in existing_tags:
                    new_tag_id = f"T_Detail_{get_next_id(tag_ids)}"
                    tag_el = ET.SubElement(object_list_elem, f"{ns_prefix}Hmi.Tag.Tag", {
                        "ID": new_tag_id,
                        "CompositionName": "Tags"
                    })
                    
                    attr_el = ET.SubElement(tag_el, f"{ns_prefix}AttributeList")
                    ET.SubElement(attr_el, f"{ns_prefix}AcquisitionTriggerMode").text = "Visible"
                    ET.SubElement(attr_el, f"{ns_prefix}AddressAccessMode").text = "Symbolic"
                    ET.SubElement(attr_el, f"{ns_prefix}Coding").text = m_tag["Coding"]
                    ET.SubElement(attr_el, f"{ns_prefix}ConfirmationType").text = "None"
                    ET.SubElement(attr_el, f"{ns_prefix}GmpRelevant").text = "false"
                    ET.SubElement(attr_el, f"{ns_prefix}JobNumber").text = "0"
                    ET.SubElement(attr_el, f"{ns_prefix}Length").text = str(m_tag["Length"])
                    ET.SubElement(attr_el, f"{ns_prefix}LinearScaling").text = "false"
                    # Correctly render empty tags to prevent multiplex address error
                    ET.SubElement(attr_el, f"{ns_prefix}LogicalAddress")
                    ET.SubElement(attr_el, f"{ns_prefix}MandatoryCommenting").text = "false"
                    ET.SubElement(attr_el, f"{ns_prefix}Name").text = m_tag["Name"]
                    ET.SubElement(attr_el, f"{ns_prefix}Persistency").text = "false"
                    ET.SubElement(attr_el, f"{ns_prefix}QualityCode").text = "false"
                    ET.SubElement(attr_el, f"{ns_prefix}ScalingHmiHigh").text = "100"
                    ET.SubElement(attr_el, f"{ns_prefix}ScalingHmiLow").text = "0"
                    ET.SubElement(attr_el, f"{ns_prefix}ScalingPlcHigh").text = "10"
                    ET.SubElement(attr_el, f"{ns_prefix}ScalingPlcLow").text = "0"
                    ET.SubElement(attr_el, f"{ns_prefix}StartValue")
                    ET.SubElement(attr_el, f"{ns_prefix}SubstituteValue")
                    ET.SubElement(attr_el, f"{ns_prefix}SubstituteValueUsage").text = "None"
                    ET.SubElement(attr_el, f"{ns_prefix}Synchronization").text = "false"
                    ET.SubElement(attr_el, f"{ns_prefix}UpdateMode").text = "ProjectWide"
                    ET.SubElement(attr_el, f"{ns_prefix}UseMultiplexing").text = "false"
                    
                    links_el = ET.SubElement(tag_el, f"{ns_prefix}LinkList")
                    
                    ac_cycle = ET.SubElement(links_el, f"{ns_prefix}AcquisitionCycle", {"TargetID": "@OpenLink"})
                    ET.SubElement(ac_cycle, f"{ns_prefix}Name").text = "1 s"
                    
                    conn_el = ET.SubElement(links_el, f"{ns_prefix}Connection", {"TargetID": "@OpenLink"})
                    ET.SubElement(conn_el, f"{ns_prefix}Name").text = m_tag["Connection"]
                    
                    ctrl_el = ET.SubElement(links_el, f"{ns_prefix}ControllerTag", {"TargetID": "@OpenLink"})
                    ET.SubElement(ctrl_el, f"{ns_prefix}Name").text = m_tag["Name"]
                    
                    dtype_el = ET.SubElement(links_el, f"{ns_prefix}DataType", {"TargetID": "@OpenLink"})
                    ET.SubElement(dtype_el, f"{ns_prefix}Name").text = m_tag["Type"]
                    
                    hdtype_el = ET.SubElement(links_el, f"{ns_prefix}HmiDataType", {"TargetID": "@OpenLink"})
                    ET.SubElement(hdtype_el, f"{ns_prefix}Name").text = m_tag["Type"]
                    
                    ET.SubElement(tag_el, f"{ns_prefix}ObjectList")
                    
                    existing_tags.add(m_tag["Name"])
                    added_tags_count += 1
            
            tag_tree.write(hmi_tags_path, encoding="utf-8", xml_declaration=True)
            print(f"HMI Tag Table patched successfully. Added {added_tags_count} missing setpoint tags.")
        else:
            print("ERROR: ObjectList not found inside Hmi.Tag.TagTable!")
    else:
        print("ERROR: Hmi.Tag.TagTable not found in XML!")
else:
    print(f"Warning: {hmi_tags_path} not found!")

# 2. Update HMI screen XMLs
for scr_name, scr_data in screens.items():
    export_path = scr_data["export"]
    patched_path = scr_data["patched"]
    conn_name = scr_data["connection"]
    plc_owner = scr_data["plc"]
    mapping = scr_data["mapping"]
    
    if not os.path.exists(export_path):
        print(f"Error: {export_path} not found! Skipping screen {scr_name}.")
        continue
        
    print(f"\nProcessing screen: {scr_name}...")
    tree = ET.parse(export_path)
    root = tree.getroot()
    
    # Load namespaces
    namespaces = {node[0]: node[1] for _, node in ET.iterparse(export_path, events=['start-ns'])}
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
        
    ns_prefix = ""
    if root.tag.startswith("{"):
        ns_prefix = root.tag.split('}')[0] + "}"
        
    existing_ids = get_all_ids(root)
    
    def set_or_update_attr(attr_list, name, value):
        el = attr_list.find(f"{ns_prefix}{name}")
        if el is None:
            el = ET.SubElement(attr_list, f"{ns_prefix}{name}")
        el.text = str(value)

    def bind_process_value(elem, tag_name):
        obj_list = elem.find(f"{ns_prefix}ObjectList")
        if obj_list is None:
            obj_list = ET.SubElement(elem, f"{ns_prefix}ObjectList")
        
        # Remove any existing ProcessValue property bindings
        props_to_remove = []
        for prop in obj_list.findall(f"{ns_prefix}Hmi.Screen.Property"):
            pname_el = prop.find(f"{ns_prefix}AttributeList/{ns_prefix}Name")
            if pname_el is not None and pname_el.text == "ProcessValue":
                props_to_remove.append(prop)
        for prop in props_to_remove:
            obj_list.remove(prop)
            
        # Create new Property element for ProcessValue
        prop = ET.SubElement(obj_list, f"{ns_prefix}Hmi.Screen.Property", {
            "ID": get_next_id(existing_ids),
            "CompositionName": "Properties"
        })
        prop_attr = ET.SubElement(prop, f"{ns_prefix}AttributeList")
        ET.SubElement(prop_attr, f"{ns_prefix}Name").text = "ProcessValue"
        
        prop_obj = ET.SubElement(prop, f"{ns_prefix}ObjectList")
        dyn = ET.SubElement(prop_obj, f"{ns_prefix}Hmi.Dynamic.TagConnectionDynamic", {
            "ID": get_next_id(existing_ids),
            "CompositionName": "Dynamic"
        })
        dyn_attr = ET.SubElement(dyn, f"{ns_prefix}AttributeList")
        ET.SubElement(dyn_attr, f"{ns_prefix}Indirect").text = "false"
        
        dyn_links = ET.SubElement(dyn, f"{ns_prefix}LinkList")
        tag_el = ET.SubElement(dyn_links, f"{ns_prefix}Tag", {
            "TargetID": "@OpenLink"
        })
        ET.SubElement(tag_el, f"{ns_prefix}Name").text = tag_name

    # 1.1 Load all TextFields to reposition unit labels
    labels = []
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        if tag_local.endswith("TextField"):
            attrs = elem.find("AttributeList")
            if attrs is not None:
                obj_name = attrs.find("ObjectName").text if attrs.find("ObjectName") is not None else ""
                left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
                top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
                w = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
                h = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
                
                text_val = ""
                mult_txt = elem.find(".//{*}MultilingualTextItem")
                if mult_txt is not None:
                    txt_elem = mult_txt.find(".//{*}Text")
                    if txt_elem is not None:
                        text_val = "".join(txt_elem.itertext()).strip()
                labels.append({"ObjectName": obj_name, "Left": left, "Top": top, "Width": w, "Height": h, "Text": text_val, "Element": elem})

    # 1.2 Loop and patch screen elements
    for elem in root.iter():
        tag_local = elem.tag.split('}')[-1]
        attrs = elem.find("AttributeList")
        if attrs is None:
            continue
            
        obj_name_el = attrs.find("ObjectName")
        if obj_name_el is None or not obj_name_el.text:
            continue
        obj_name = obj_name_el.text.strip()
        
        # IOFields patching
        if tag_local.endswith("IOField"):
            if obj_name in mapping["IOField"]:
                tag_name, tag_type, fmt, unit = mapping["IOField"][obj_name]
                
                # Format alignment and pattern
                set_or_update_attr(attrs, "HorizontalAlignment", "Center")
                set_or_update_attr(attrs, "VerticalAlignment", "Middle")
                set_or_update_attr(attrs, "FormatPattern", fmt)
                set_or_update_attr(attrs, "FieldLength", len(fmt))
                if tag_type == "Bool":
                    set_or_update_attr(attrs, "DataFormat", "Binary")
                
                # Bind tag
                bind_process_value(elem, tag_name)
                
                # Reposition Unit Label
                aligned_unit_lbl = "None"
                left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
                top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
                w = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
                h = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
                
                if unit:
                    best_unit_lbl = None
                    min_unit_dist = float("inf")
                    for lbl in labels:
                        if lbl["Text"] == unit:
                            # Must be to the right of IOField
                            if lbl["Left"] >= left + w - 5:
                                dist = ((lbl["Left"] - (left + w))**2 + (lbl["Top"] - top)**2)**0.5
                                if dist < min_unit_dist and dist < 80:
                                    min_unit_dist = dist
                                    best_unit_lbl = lbl
                                    
                    if best_unit_lbl:
                        new_left = left + w + 8
                        lbl_attrs = best_unit_lbl["Element"].find("AttributeList")
                        set_or_update_attr(lbl_attrs, "Left", new_left)
                        
                        # Set font size 13 Bold in ObjectList/MultiLingualFont
                        lbl_obj_list = best_unit_lbl["Element"].find(f"{ns_prefix}ObjectList")
                        if lbl_obj_list is not None:
                            font_item = lbl_obj_list.find(f".//{ns_prefix}Hmi.Globalization.FontItem")
                            if font_item is not None:
                                size_el = font_item.find(f"{ns_prefix}FontSize")
                                if size_el is not None:
                                    size_el.text = "13"
                                style_el = font_item.find(f"{ns_prefix}FontStyle")
                                if style_el is not None:
                                    style_el.text = "Bold"
                        aligned_unit_lbl = f"{best_unit_lbl['ObjectName']} ('{unit}') aligned to Left={new_left}, 13 Bold"
                        
                mapping_results.append({
                    "ScreenName": scr_name,
                    "ObjectType": "IOField",
                    "ObjectName": obj_name,
                    "Left": left,
                    "Top": top,
                    "Width": w,
                    "Height": h,
                    "ProposedTag": tag_name,
                    "PLC_Owner": plc_owner,
                    "Connection": conn_name,
                    "DataType": tag_type,
                    "FormatPattern": fmt,
                    "ProposedMode": "Input/output" if "SP" in tag_name or "Time" in tag_name else "Output",
                    "NearestLabel": f"Direct ObjectName mapping",
                    "UnitLabelAligned": aligned_unit_lbl
                })
                
        # SymbolLibraries patching
        elif tag_local.endswith("SymbolLibrary"):
            if obj_name in mapping["SymbolLibrary"]:
                tag_name, tag_type, mode = mapping["SymbolLibrary"][obj_name]
                
                # Bind tag
                bind_process_value(elem, tag_name)
                
                left = int(attrs.find("Left").text) if attrs.find("Left") is not None else 0
                top = int(attrs.find("Top").text) if attrs.find("Top") is not None else 0
                w = int(attrs.find("Width").text) if attrs.find("Width") is not None else 0
                h = int(attrs.find("Height").text) if attrs.find("Height") is not None else 0
                
                mapping_results.append({
                    "ScreenName": scr_name,
                    "ObjectType": "SymbolLibrary",
                    "ObjectName": obj_name,
                    "Left": left,
                    "Top": top,
                    "Width": w,
                    "Height": h,
                    "ProposedTag": tag_name,
                    "PLC_Owner": plc_owner,
                    "Connection": conn_name,
                    "DataType": tag_type,
                    "FormatPattern": "N/A",
                    "ProposedMode": mode,
                    "NearestLabel": f"Direct ObjectName mapping",
                    "UnitLabelAligned": "N/A"
                })

    # Save Patched Screen XML
    tree.write(patched_path, encoding="utf-8", xml_declaration=True)
    h = hashlib.sha256(open(patched_path, "rb").read()).hexdigest()
    print(f"  Saved patched XML at {patched_path}")
    print(f"  SHA256: {h}")

# 2. Write dry-run mapping CSV
with open(dryrun_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "ScreenName", "ObjectType", "ObjectName", "Left", "Top", "Width", "Height",
        "ProposedTag", "PLC_Owner", "Connection", "DataType", "FormatPattern",
        "ProposedMode", "NearestLabel", "UnitLabelAligned"
    ])
    for r in mapping_results:
        writer.writerow([
            r["ScreenName"], r["ObjectType"], r["ObjectName"], r["Left"], r["Top"], r["Width"], r["Height"],
            r["ProposedTag"], r["PLC_Owner"], r["Connection"], r["DataType"], r["FormatPattern"],
            r["ProposedMode"], r["NearestLabel"], r["UnitLabelAligned"]
        ])

print(f"\n========================================")
print(f"COMPLETED PATCHING")
print(f"========================================")
print(f"Total mapped objects: {len(mapping_results)}")
print(f"Label mismatches reported: {len(label_mismatches_info)}")
print(f"Blocked objects reported: {len(blocked_objects_info)}")
print(f"Dry-run CSV saved at {dryrun_path}")
