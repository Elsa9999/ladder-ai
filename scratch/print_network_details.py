import xml.etree.ElementTree as ET

path = r'd:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export\PLC_2\Blocks\FC_PLC2_Mixing.xml'

it = ET.iterparse(path)
for _, el in it:
    prefix, has_namespace, postfix = el.tag.partition('}')
    if has_namespace:
        el.tag = postfix
root = it.root

compile_units = root.findall('.//SW.Blocks.CompileUnit')
cu = compile_units[158]

with open(r'd:\AI_Agent_PLC_LADDER_ONLY\scratch\network_158.xml', 'w', encoding='utf-8') as f:
    f.write(ET.tostring(cu, encoding='utf-8').decode('utf-8'))
print("Done")
