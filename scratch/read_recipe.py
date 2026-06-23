import re

with open('d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026/output/FC_Init_Default_Recipe_PLC1.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Find compile units
units = re.findall(r'<SW\.Blocks\.CompileUnit.*?>.*?</SW\.Blocks\.CompileUnit>', content, re.DOTALL)
for u in units:
    name_m = re.search(r'<AttributeList>.*?<Name>(.*?)</Name>', u, re.DOTALL)
    name = name_m.group(1) if name_m else "Unknown"
    print('=== NETWORK:', name)
    
    # We want to find each Part Contact and check if it is negated
    # SimaticML representation of a contact:
    # <Part Name="Contact" UId="174" />
    # Negated info is in the wires, or in the Part attributes?
    # Actually, in SimaticML, negation is represented by a template value or in the Part attributes.
    # Let's print the entire SW.Blocks.CompileUnit text of the last network to see!
    if 'AI_PLC1_Load_Default_Done_Nhan_Eff' in u:
        print(u)
