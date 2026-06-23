import re
import os

scratch_dir = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch"
screens = ["scadabai3", "scadabai4", "scadabai5", "scadabai6", "scadabai7"]

for screen_name in screens:
    path = os.path.join(scratch_dir, f"{screen_name}_export.xml")
    if not os.path.exists(path):
        print(f"{screen_name}: File not found.")
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = re.compile(r'<Hmi\.Screen\.Bar\b.*?>(.*?)</Hmi\.Screen\.Bar>', re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(content)
    
    if matches:
        print(f"\n=== {screen_name} (Found {len(matches)} Bar elements) ===")
        for i, block in enumerate(matches):
            obj_name = re.search(r'<ObjectName>(.*?)</ObjectName>', block)
            auto_scale = re.search(r'<UseAutoScaling>(.*?)</UseAutoScaling>', block)
            int_digits = re.search(r'<IntegerDigits>(.*?)</IntegerDigits>', block)
            
            print(f"  Bar {i+1}: Name={obj_name.group(1) if obj_name else 'N/A'}, UseAutoScaling={auto_scale.group(1) if auto_scale else 'N/A'}, IntegerDigits={int_digits.group(1) if int_digits else 'N/A'}")
    else:
        print(f"\n=== {screen_name} (No Bar elements found) ===")
