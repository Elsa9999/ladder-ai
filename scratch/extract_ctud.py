import os
import re

main_xml = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_exports\PLSP_export\PLC_1\Blocks\Main.xml"

if not os.path.exists(main_xml):
    print("Main.xml not found")
else:
    with open(main_xml, "r", encoding="utf-8") as f:
        content = f.read()
        
    compile_unit_re = re.compile(r'(<SW\.Blocks\.CompileUnit[^>]*>.*?</SW\.Blocks\.CompileUnit>)', re.DOTALL)
    compile_units = compile_unit_re.findall(content)
    
    # Print network 11 (index 10)
    print(compile_units[10])
