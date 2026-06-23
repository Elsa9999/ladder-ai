import xml.etree.ElementTree as ET
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

path_bai1 = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai1\PLC\FC_SCADA_Simulation.xml"
path_sim = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\FC_SCADA_Sim_B3to7.xml"

def print_net1(path, label):
    if not os.path.exists(path):
        print(f"{label}: File not found.")
        return
    tree = ET.parse(path)
    root = tree.getroot()
    net = root.find(".//SW.Blocks.CompileUnit")
    if net is not None:
        title_el = net.find(".//MultilingualText[@CompositionName='Title']//Text")
        title = title_el.text if title_el is not None else "No Title"
        print(f"=== {label} Network 1: {title} ===")
        # Print parts and wires
        parts = net.find(".//ns0:Parts", {"ns0": "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"})
        if parts is None:
            parts = net.find(".//Parts")
        if parts is not None:
            for part in parts:
                name = part.attrib.get("Name", "")
                uid = part.attrib.get("UId", "")
                print(f"  Part: {name} (UId {uid})")
                instance = part.find(".//ns0:Instance", {"ns0": "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"})
                if instance is None:
                    instance = part.find(".//Instance")
                if instance is not None:
                    scope = instance.attrib.get("Scope", "")
                    uid_inst = instance.attrib.get("UId", "")
                    component_name = instance.find(".//ns0:Component", {"ns0": "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"})
                    if component_name is None:
                        component_name = instance.find(".//Component")
                    comp_name = component_name.attrib.get("Name", "") if component_name is not None else "N/A"
                    print(f"    Instance: Scope={scope}, UId={uid_inst}, Name={comp_name}")
                
                # Check for operands
                operand_els = part.findall(".//ns0:Access", {"ns0": "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"})
                if not operand_els:
                    operand_els = part.findall(".//Access")
                for op in operand_els:
                    scope = op.attrib.get("Scope", "")
                    uid_op = op.attrib.get("UId", "")
                    comp_name_el = op.find(".//ns0:Component", {"ns0": "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4"})
                    if comp_name_el is None:
                        comp_name_el = op.find(".//Component")
                    comp_name = comp_name_el.attrib.get("Name", "") if comp_name_el is not None else "N/A"
                    print(f"    Access: Scope={scope}, UId={uid_op}, Name={comp_name}")
        else:
            print("  No parts found.")
    else:
        print(f"{label}: No network found.")

print_net1(path_bai1, "scadabai1")
print_net1(path_sim, "scadabai_sim")
