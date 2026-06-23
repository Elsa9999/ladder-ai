with open(r'd:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export\PLC_2\Blocks\FC_PLC2_Mixing.xml', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.findall(r'AI_PID_Bon4_Enable', content)
print("AI_PID_Bon4_Enable occurrences in exported block:", len(matches))
