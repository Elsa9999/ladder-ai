# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import subprocess

# Output directory for importer
output_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens"
os.makedirs(output_dir, exist_ok=True)

def generate_probe_xml(tag_name, file_name, screen_number="99"):
    root = ET.Element("Document")
    eng = ET.SubElement(root, "Engineering", {"version": "V18"})
    doc_info = ET.SubElement(root, "DocumentInfo")
    ET.SubElement(doc_info, "Created").text = "2026-06-11T12:00:00Z"
    ET.SubElement(doc_info, "ExportSetting").text = "WithDefaults"
    
    screen = ET.SubElement(root, "Hmi.Screen.Screen", {"ID": "0"})
    attrs = ET.SubElement(screen, "AttributeList")
    ET.SubElement(attrs, "ActiveLayer").text = "0"
    ET.SubElement(attrs, "BackColor").text = "30, 30, 30"
    ET.SubElement(attrs, "Height").text = "1080"
    ET.SubElement(attrs, "Name").text = file_name
    ET.SubElement(attrs, "Number").text = screen_number
    ET.SubElement(attrs, "Visible").text = "true"
    ET.SubElement(attrs, "Width").text = "1920"
    
    objs = ET.SubElement(screen, "ObjectList")
    
    # Layer
    layer = ET.SubElement(objs, "Hmi.Screen.ScreenLayer", {"ID": "3", "CompositionName": "Layers"})
    layer_attrs = ET.SubElement(layer, "AttributeList")
    ET.SubElement(layer_attrs, "Index").text = "0"
    ET.SubElement(layer_attrs, "VisibleES").text = "true"
    
    layer_objs = ET.SubElement(layer, "ObjectList")
    
    # Probe element
    probe = ET.SubElement(layer_objs, tag_name, {"ID": "4", "CompositionName": "ScreenItems"})
    probe_attrs = ET.SubElement(probe, "AttributeList")
    ET.SubElement(probe_attrs, "Left").text = "100"
    ET.SubElement(probe_attrs, "Top").text = "150"
    ET.SubElement(probe_attrs, "Width").text = "1720"
    ET.SubElement(probe_attrs, "Height").text = "800"
    ET.SubElement(probe_attrs, "ObjectName").text = "Test_Alarm_Control"
    
    tree = ET.ElementTree(root)
    file_path = os.path.join(output_dir, f"Hmi.Screen.{file_name}.xml")
    
    ET.register_namespace('', '')
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    print(f"Generated {file_path} with tag <{tag_name}>")
    return file_path

# Clean output dir first
for f in os.listdir(output_dir):
    if f.endswith(".xml"):
        os.remove(os.path.join(output_dir, f))

# We will probe Hmi.Screen.AlarmView
generate_probe_xml("Hmi.Screen.AlarmView", "Probe_AlarmView", "96")
# Generate a dummy Login_out.xml to pass the importer's check
generate_probe_xml("Hmi.Screen.TextField", "Login_out", "97")

# Run import screen only executable
print("\nRunning import_screen_only.exe...")
result = subprocess.run([r"D:\AI_Agent_PLC_LADDER_ONLY\Ladder\import_screen_only.exe"], capture_output=True, text=True, encoding="utf-8")
print("--- STDOUT ---")
print(result.stdout.encode('ascii', errors='replace').decode('ascii'))
print("--- STDERR ---")
print(result.stderr)
