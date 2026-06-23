import os
import re

main_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_exports\PLSP_export\PLC_1\Blocks\Main.xml"

if not os.path.exists(main_xml):
    print("Main.xml not found")
else:
    with open(main_xml, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Count networks
    compile_units = re.findall(r'<SW\.Blocks\.CompileUnit', content)
    print(f"Number of networks in Main.xml: {len(compile_units)}")
    
    # List unique parts
    part_names = re.findall(r'<Part\s+Name="([^"]+)"', content, re.IGNORECASE)
    # Also find block calls
    call_names = re.findall(r'<CallInfo\s+Name="([^"]+)"', content, re.IGNORECASE)
    
    print("Parts (Instructions) found:")
    for part in sorted(list(set(part_names))):
        print(f"  - {part}")
        
    print("Block calls found:")
    for call in sorted(list(set(call_names))):
        print(f"  - {call}")
