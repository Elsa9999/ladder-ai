import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/test_plc_logic.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_tick = False
in_section = False
for i, line in enumerate(lines[:1034]):
    if 'def tick(' in line:
        in_tick = True
    elif in_tick and 'def ' in line:
        in_tick = False
    
    if in_tick:
        if 'modbus tcp' in line.lower() or 'mb_tcp' in line.lower():
            in_section = True
            print(f"--- Modbus TCP Section Start (Line {i+1}) ---")
        if in_section:
            print(f"{i+1}: {line.rstrip()}")
            # Stop printing if we see next major component
            if 'agitator' in line.lower() or 'analog' in line.lower() or 'alarm' in line.lower() or 'step ' in line.lower() and 'transition' not in line.lower():
                # but only if it's not modbus step
                if 'mb_tcp_istep' not in line.lower():
                    in_section = False
                    print(f"--- Modbus TCP Section End (Line {i+1}) ---")
