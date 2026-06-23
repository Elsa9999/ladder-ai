# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys

def inspect_file(filepath, part_name):
    print(f"\n--- Inspecting {filepath} for {part_name} ---")
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return

    # Siemens Openness NetworkSource namespace
    ns = {'flg': 'http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4'}
    
    # Find the compile units
    compile_units = root.findall('.//SW.Blocks.CompileUnit')
    for cu in compile_units:
        # Check if this compile unit contains the target part
        parts = cu.findall('.//flg:Part', ns)
        has_part = False
        target_uid = None
        for p in parts:
            if p.attrib.get('Name') == part_name:
                has_part = True
                target_uid = p.attrib.get('UId')
                version = p.attrib.get('Version')
                print(f"Found {part_name} (UId {target_uid}, Version {version}) in CompileUnit:")
                # Print the title of compile unit if any
                title_item = cu.find('.//MultilingualTextItem')
                if title_item is not None:
                    title_text = title_item.find('Text')
                    if title_text is not None:
                        print(f"  Title: {title_text.text}")
                break
        
        if has_part:
            # Let's inspect the access/constants in this CompileUnit
            accesses = cu.findall('.//flg:Access', ns)
            access_map = {}
            for a in accesses:
                auid = a.attrib.get('UId')
                scope = a.attrib.get('Scope')
                if scope == 'GlobalVariable':
                    symbol = a.find('flg:Symbol', ns)
                    if symbol is not None:
                        components = [c.attrib.get('Name') for c in symbol.findall('flg:Component', ns)]
                        access_map[auid] = '.'.join(components)
                elif scope == 'LiteralConstant':
                    constant = a.find('flg:Constant', ns)
                    if constant is not None:
                        val = constant.find('flg:ConstantValue', ns)
                        if val is not None:
                            access_map[auid] = val.text
                elif scope == 'LocalVariable':
                    symbol = a.find('flg:Symbol', ns)
                    if symbol is not None:
                        components = [c.attrib.get('Name') for c in symbol.findall('flg:Component', ns)]
                        access_map[auid] = '#' + '.'.join(components)
            
            # Let's trace wires in this CompileUnit
            wires = cu.findall('.//flg:Wire', ns)
            connections = {} # pin -> source_node_value
            for w in wires:
                # Find if one of the wire's nodes is our target part
                nodes = w.findall('.//flg:NameCon', ns) + w.findall('.//flg:IdentCon', ns)
                target_pin = None
                source_uid = None
                for node in nodes:
                    nuid = node.attrib.get('UId')
                    npin = node.attrib.get('Name')
                    if nuid == target_uid:
                        target_pin = npin
                    else:
                        source_uid = nuid
                
                if target_pin and source_uid:
                    # Look up the source
                    val = access_map.get(source_uid)
                    if val is None:
                        # Maybe it is another part's output pin
                        other_part = None
                        for p in parts:
                            if p.attrib.get('UId') == source_uid:
                                other_part = p
                                break
                        if other_part is not None:
                            val = f"Block:{other_part.attrib.get('Name')} (UId {source_uid})"
                        else:
                            val = f"UId {source_uid}"
                    connections[target_pin] = val

            print("  Connections:")
            for pin in sorted(connections.keys()):
                print(f"    {pin} = {connections[pin]}")

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    inspect_file('projects/Mixing_Nuoc_Tuong_Maggi_2026/post_import_export_manual/PLC_1/Blocks/Main.xml', 'MB_CLIENT')
    inspect_file('projects/Mixing_Nuoc_Tuong_Maggi_2026/post_import_export_manual/PLC_2/Blocks/Main.xml', 'MB_SERVER')
