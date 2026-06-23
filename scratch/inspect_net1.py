import xml.etree.ElementTree as ET
import os

path = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC\FC_SCADA_Sim_B3to7.xml"

tree = ET.parse(path)
root = tree.getroot()

first_net = root.find(".//SW.Blocks.CompileUnit")
if first_net is not None:
    # Print the XML structure of this network
    # Convert element to string
    xml_str = ET.tostring(first_net, encoding='utf-8').decode('utf-8')
    print(xml_str[:1500])
