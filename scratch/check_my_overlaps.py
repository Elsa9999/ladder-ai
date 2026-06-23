import sys
sys.path.append('scratch')
from validate_plc_overlaps import parse_tags_xml, check_overlaps_and_system_memory
sys.stdout.reconfigure(encoding='utf-8')

tags1 = parse_tags_xml(r'projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC1.xml')
overlaps1 = check_overlaps_and_system_memory(tags1, 'PLC1 Mới')
print('=== PLC1 Overlaps ===')
for o in overlaps1:
    print(f"{o['tag1']['name']} ({o['tag1']['address']}) vs {o['tag2']['name']} ({o['tag2']['address']})")

tags2 = parse_tags_xml(r'projects\Mixing_Nuoc_Tuong_Maggi_2026\output\PLC_Tags_PLC2.xml')
overlaps2 = check_overlaps_and_system_memory(tags2, 'PLC2 Mới')
print('=== PLC2 Overlaps ===')
for o in overlaps2:
    print(f"{o['tag1']['name']} ({o['tag1']['address']}) vs {o['tag2']['name']} ({o['tag2']['address']})")
