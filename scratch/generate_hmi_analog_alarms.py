# -*- coding: utf-8 -*-
"""
generate_hmi_analog_alarms.py
Tạo file XML Analog Alarm (Limit Alarm) cho HMI WinCC Advanced TIA V18
Theo chuẩn SCADA: khi giá trị tag vượt ngưỡng → Alarm tự động hiển thị popup/banner

Các alarm được tạo:
  - 1400_TT32_PV (Nhiệt độ): HiHi > 78°C, Hi > 75°C
  - 1406_TX35_PV (Áp suất):  HiHi > 8 bar, Hi > 7 bar
"""
import xml.etree.ElementTree as ET
import os

output_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Alarms"
os.makedirs(output_dir, exist_ok=True)

id_counter = 1

def next_id():
    global id_counter
    val = id_counter
    id_counter += 1
    return str(val)

def mltext(parent, comp_name, text_val):
    """Create MultilingualText node"""
    ml = ET.SubElement(parent, "MultilingualText", {
        "ID": next_id(), "CompositionName": comp_name
    })
    items = ET.SubElement(ml, "ObjectList")
    item = ET.SubElement(items, "MultilingualTextItem", {
        "ID": next_id(), "CompositionName": "Items"
    })
    attrs = ET.SubElement(item, "AttributeList")
    ET.SubElement(attrs, "Culture").text = "en-US"
    ET.SubElement(attrs, "Text").text = f"<body><p>{text_val}</p></body>"
    return ml

def create_analog_alarm(parent, name, alarm_text, tag_name, limit_value, limit_mode, priority=1):
    """
    Create one Hmi.Alarm.AnalogAlarm entry
    limit_mode: "HighHigh" | "High" | "Low" | "LowLow"
    """
    alarm = ET.SubElement(parent, "Hmi.Alarm.AnalogAlarm", {
        "ID": next_id(),
        "CompositionName": "AnalogAlarms"
    })
    attrs = ET.SubElement(alarm, "AttributeList")
    ET.SubElement(attrs, "AcknowledgementRequired").text = "true"
    ET.SubElement(attrs, "Delay").text = "0"
    ET.SubElement(attrs, "DelayTimeUnit").text = "Seconds"
    ET.SubElement(attrs, "Enabled").text = "true"
    ET.SubElement(attrs, "LimitMode").text = limit_mode
    ET.SubElement(attrs, "LimitValue").text = str(limit_value)
    ET.SubElement(attrs, "Name").text = name
    ET.SubElement(attrs, "Priority").text = str(priority)

    objs = ET.SubElement(alarm, "ObjectList")

    # AlarmClass link
    ac = ET.SubElement(objs, "Hmi.Alarm.AlarmClass", {
        "ID": next_id(), "CompositionName": "AlarmClass"
    })
    ac_links = ET.SubElement(ac, "LinkList")
    ET.SubElement(ac_links, "AlarmClass", {"TargetID": "@OpenLink"}).append(
        ET.fromstring("<Name>Errors</Name>")
    )

    # Alarm text
    mltext(objs, "AlarmText", alarm_text)

    # Tag (process value to monitor)
    tag_el = ET.SubElement(objs, "Hmi.Alarm.AnalogAlarmTag", {
        "ID": next_id(), "CompositionName": "Tag"
    })
    tag_links = ET.SubElement(tag_el, "LinkList")
    t = ET.SubElement(tag_links, "Tag", {"TargetID": "@OpenLink"})
    ET.SubElement(t, "Name").text = tag_name

    return alarm

def generate_alarm_xml():
    root = ET.Element("Document")
    ET.SubElement(root, "Engineering", {"version": "V18"})
    doc_info = ET.SubElement(root, "DocumentInfo")
    ET.SubElement(doc_info, "Created").text = "2026-06-11T12:00:00Z"
    ET.SubElement(doc_info, "ExportSetting").text = "WithDefaults"

    # AlarmLogging container
    alarm_logging = ET.SubElement(root, "Hmi.Alarm.AlarmLogging", {"ID": next_id()})
    attrs = ET.SubElement(alarm_logging, "AttributeList")
    ET.SubElement(attrs, "Name").text = "AlarmLogging_1"

    objs = ET.SubElement(alarm_logging, "ObjectList")

    # AnalogAlarms list
    # --- Nhiệt độ TT32 ---
    create_analog_alarm(
        objs,
        name="AI_Alarm_TT32_HiHi",
        alarm_text="CANH BAO: Nhiet do TT32 qua cao! Gia tri = {0} oC (Nguong: 78oC)",
        tag_name="1400_TT32_PV",
        limit_value=78,
        limit_mode="Higher",
        priority=2
    )
    create_analog_alarm(
        objs,
        name="AI_Alarm_TT32_Hi",
        alarm_text="CANH BAO: Nhiet do TT32 cao! Gia tri = {0} oC (Nguong: 75oC)",
        tag_name="1400_TT32_PV",
        limit_value=75,
        limit_mode="Higher",
        priority=1
    )

    # --- Ap suat TX35 ---
    create_analog_alarm(
        objs,
        name="AI_Alarm_TX35_HiHi",
        alarm_text="CANH BAO: Ap suat TX35 qua cao! Gia tri = {0} bar (Nguong: 8 bar)",
        tag_name="1406_TX35_PV",
        limit_value=8.0,
        limit_mode="Higher",
        priority=2
    )
    create_analog_alarm(
        objs,
        name="AI_Alarm_TX35_Hi",
        alarm_text="CANH BAO: Ap suat TX35 cao! Gia tri = {0} bar (Nguong: 7 bar)",
        tag_name="1406_TX35_PV",
        limit_value=7.0,
        limit_mode="Higher",
        priority=1
    )

    out_path = os.path.join(output_dir, "Hmi.Alarm.AlarmLogging_1.xml")
    tree = ET.ElementTree(root)
    ET.register_namespace("", "")
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    print(f"[SUCCESS] Generated: {out_path}")
    print(f"  4 Analog Alarms:")
    print(f"  - AI_Alarm_TT32_HiHi (Nhiệt độ > 78°C, Priority 3)")
    print(f"  - AI_Alarm_TT32_Hi   (Nhiệt độ > 75°C, Priority 2)")
    print(f"  - AI_Alarm_TX35_HiHi (Áp suất  >  8 bar, Priority 3)")
    print(f"  - AI_Alarm_TX35_Hi   (Áp suất  >  7 bar, Priority 2)")

if __name__ == "__main__":
    generate_alarm_xml()
