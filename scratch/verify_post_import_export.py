import os
import re
import xml.etree.ElementTree as ET

EXPORT_DIR = r'd:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export'

print("=========================================================")
print(" POST IMPORT EXPORT LADDER XML LOGIC VERIFIER")
print("=========================================================")

errors = []

# Helper to load XML and strip namespaces for easier XPath
def load_xml(path):
    it = ET.iterparse(path)
    for _, el in it:
        prefix, has_namespace, postfix = el.tag.partition('}')
        if has_namespace:
            el.tag = postfix  # strip namespace
    return it.root

# 1. Verify PLC1 OB30_PID_PLC1_Bon2
ob30_path = os.path.join(EXPORT_DIR, 'PLC_1', 'Blocks', 'OB30_PID_PLC1_Bon2.xml')
if not os.path.exists(ob30_path):
    errors.append(f"OB30 file not found at: {ob30_path}")
else:
    print(f"Reading {ob30_path}...")
    with open(ob30_path, 'r', encoding='utf-8') as f:
        ob30_content = f.read()

    # Criteria: when PID_Bon2_Enable is TRUE, PID_Bon2_CV must MOVE to CV3206_Hoi_Bon2
    # Check if "Move PID Bon 2 CV to VFD" network title is gone
    if "Move PID Bon 2 CV to VFD" in ob30_content:
        errors.append("Stale network title 'Move PID Bon 2 CV to VFD' found in OB30!")
    else:
        print("[PASS] Network 'Move PID Bon 2 CV to VFD' has been removed.")

    # Check if MOVE 100.0 into CV3206_Hoi_Bon2 is gone
    # Search for ConstantValue 100.0 and CV3206_Hoi_Bon2 inside the same network
    # We can do this by dividing into networks / SW.Blocks.CompileUnit
    root = load_xml(ob30_path)
    compile_units = root.findall('.//SW.Blocks.CompileUnit')
    print(f"Found {len(compile_units)} compile units (networks) in OB30.")

    move_cv_found = False
    move_speed_found = False
    hardcoded_100_found = False

    for idx, cu in enumerate(compile_units):
        title_elem = cu.find('.//MultilingualText[@CompositionName="Title"]//MultilingualTextItem/Text')
        title = title_elem.text if title_elem is not None else ""
        
        # Check variables and constants
        variables = [c.attrib.get('Name') for c in cu.findall('.//Component')]
        constants = [c.text for c in cu.findall('.//ConstantValue')]
        contacts = [p.attrib.get('Name') for p in cu.findall('.//Part') if p.attrib.get('Name') == 'Contact']
        moves = [p.attrib.get('Name') for p in cu.findall('.//Part') if p.attrib.get('Name') == 'Move']
        
        cu_str = ET.tostring(cu, encoding='utf-8').decode('utf-8')

        # Check for Move PID CV to Steam Valve
        # Variables should contain PID_Bon2_Enable, PID_Bon2_CV, CV3206_Hoi_Bon2
        if 'PID_Bon2_Enable' in variables and 'PID_Bon2_CV' in variables and 'CV3206_Hoi_Bon2' in variables:
            if 'Move' in cu_str:
                move_cv_found = True
                print(f"[PASS] Found PID CV to Steam Valve mapping in network index {idx}.")

        # Check for Move Speed to VFD
        # Variables should contain PID_Bon2_Enable, HMI_SP_PLC1_Toc_Do_Bon2_Main, VFD_Bon2_Toc_Do_AO
        if 'PID_Bon2_Enable' in variables and 'HMI_SP_PLC1_Toc_Do_Bon2_Main' in variables and 'VFD_Bon2_Toc_Do_AO' in variables:
            if 'Move' in cu_str:
                move_speed_found = True
                print(f"[PASS] Found HMI Agitator Speed to VFD mapping in network index {idx}.")

        # Check if MOVE 100.0 to CV3206_Hoi_Bon2 exists
        if '100.0' in constants and 'CV3206_Hoi_Bon2' in variables and 'Move' in cu_str:
            hardcoded_100_found = True
            errors.append(f"Stale hardcoded MOVE 100.0 to CV3206_Hoi_Bon2 found in network index {idx}!")

    if not move_cv_found:
        errors.append("Could not find network moving PID_Bon2_CV to CV3206_Hoi_Bon2 under PID_Bon2_Enable!")
    if not move_speed_found:
        errors.append("Could not find network moving HMI_SP_PLC1_Toc_Do_Bon2_Main to VFD_Bon2_Toc_Do_AO under PID_Bon2_Enable!")
    if not hardcoded_100_found:
        print("[PASS] No hardcoded MOVE 100.0 to CV3206_Hoi_Bon2 when PID is running.")

# 2. Verify FC_PLC1_Mixing discharge valves open according to Pump3264_Chuyen_Nhanh1
fc1_path = os.path.join(EXPORT_DIR, 'PLC_1', 'Blocks', 'FC_PLC1_Mixing.xml')
if not os.path.exists(fc1_path):
    errors.append(f"FC_PLC1_Mixing file not found at: {fc1_path}")
else:
    print(f"Reading {fc1_path}...")
    root1 = load_xml(fc1_path)
    compile_units = root1.findall('.//SW.Blocks.CompileUnit')
    
    valves = ['V3237_Xa_Bon2', 'V3238_Xa_Bon2', 'V3239_Xa_Bon2']
    valves_status = {v: False for v in valves}
    
    for cu in compile_units:
        variables = [c.attrib.get('Name') for c in cu.findall('.//Component')]
        cu_str = ET.tostring(cu, encoding='utf-8').decode('utf-8')
        
        for v in valves:
            if 'Pump3264_Chuyen_Nhanh1' in variables and v in variables:
                # Check if it has a contact for pump and coil/setcoil for valve
                if 'Coil' in cu_str or 'SetCoil' in cu_str:
                    valves_status[v] = True
                    
    for v, status in valves_status.items():
        if not status:
            errors.append(f"FC_PLC1_Mixing: {v} is not configured to open with Pump3264_Chuyen_Nhanh1!")
        else:
            print(f"[PASS] {v} opens with Pump3264_Chuyen_Nhanh1.")

# 3. Verify FC_PLC2_Mixing discharge valves open according to Pump3265_Chuyen_Nhanh2
fc2_path = os.path.join(EXPORT_DIR, 'PLC_2', 'Blocks', 'FC_PLC2_Mixing.xml')
if not os.path.exists(fc2_path):
    errors.append(f"FC_PLC2_Mixing file not found at: {fc2_path}")
else:
    print(f"Reading {fc2_path}...")
    root2 = load_xml(fc2_path)
    compile_units = root2.findall('.//SW.Blocks.CompileUnit')
    
    valves = ['V3247_Xa_Bon4', 'V3248_Xa_Bon4', 'V3249_Xa_Bon4']
    valves_status = {v: False for v in valves}
    
    for cu in compile_units:
        variables = [c.attrib.get('Name') for c in cu.findall('.//Component')]
        cu_str = ET.tostring(cu, encoding='utf-8').decode('utf-8')
        
        for v in valves:
            if 'Pump3265_Chuyen_Nhanh2' in variables and v in variables:
                if 'Coil' in cu_str or 'SetCoil' in cu_str:
                    valves_status[v] = True
                    
    for v, status in valves_status.items():
        if not status:
            errors.append(f"FC_PLC2_Mixing: {v} is not configured to open with Pump3265_Chuyen_Nhanh2!")
        else:
            print(f"[PASS] {v} opens with Pump3265_Chuyen_Nhanh2.")

# 4. Verify Agitator/VFD runs even when PID_Enable is TRUE
# For PLC_1: VFD Bồn 2 should run if PID_Bon2_Enable is TRUE
if os.path.exists(fc1_path):
    root1 = load_xml(fc1_path)
    compile_units = root1.findall('.//SW.Blocks.CompileUnit')
    
    vfd_runs_with_pid = False
    for cu in compile_units:
        variables = [c.attrib.get('Name') for c in cu.findall('.//Component')]
        cu_str = ET.tostring(cu, encoding='utf-8').decode('utf-8')
        # Check if PID_Bon2_Enable triggers VFD_Bon2_Should_Run or VFD_Bon2_Run
        if 'PID_Bon2_Enable' in variables and ('VFD_Bon2_Should_Run' in variables or 'VFD_Bon2_Run' in variables):
            vfd_runs_with_pid = True
            break
            
    if not vfd_runs_with_pid:
        errors.append("Agitator Bon 2 does not run when PID_Bon2_Enable is TRUE!")
    else:
        print("[PASS] Agitator Bon 2 VFD runs when PID_Bon2_Enable is TRUE.")

# For PLC_2: Agitator Bồn 4 should run if PID_Bon4_Enable is TRUE
if os.path.exists(fc2_path):
    root2 = load_xml(fc2_path)
    compile_units = root2.findall('.//SW.Blocks.CompileUnit')
    
    agitator_runs_with_pid = False
    for cu in compile_units:
        variables = [c.attrib.get('Name') for c in cu.findall('.//Component')]
        cu_str = ET.tostring(cu, encoding='utf-8').decode('utf-8')
        if 'PID_Bon4_Enable' in variables and ('AGTR3263_Khuay_Active' in variables or 'AGTR3263_Khuay_Bon4' in variables):
            agitator_runs_with_pid = True
            break
            
    if not agitator_runs_with_pid:
        errors.append("Agitator Bon 4 does not run when PID_Bon4_Enable is TRUE!")
    else:
        print("[PASS] Agitator Bon 4 runs when PID_Bon4_Enable is TRUE.")

# 5. Verify Dosing timer preset values
# Check in FC_PLC1_Mixing and FC_PLC2_Mixing for TON with T#5S
dosing_timers = {
    'Timer_Dosing_Bon1': False,
    'Timer_Dosing_Bon2': False,
    'Timer_Dosing_Bon3': False,
    'Timer_Dosing_Bon4': False
}

def check_dosing_timers_in_root(root):
    compile_units = root.findall('.//SW.Blocks.CompileUnit')
    for cu in compile_units:
        cu_str = ET.tostring(cu, encoding='utf-8').decode('utf-8')
        for t in dosing_timers.keys():
            if t in cu_str:
                # Find if there is a ConstantValue of T#5S associated with it
                # TON block typically has PT input
                if 'T#5S' in cu_str:
                    dosing_timers[t] = True

if os.path.exists(fc1_path):
    check_dosing_timers_in_root(load_xml(fc1_path))
if os.path.exists(fc2_path):
    check_dosing_timers_in_root(load_xml(fc2_path))

for t, status in dosing_timers.items():
    if not status:
        errors.append(f"Dosing timer {t} preset is not set to T#5S!")
    else:
        print(f"[PASS] {t} is set to T#5S.")

print("=========================================================")
if len(errors) > 0:
    print("VERIFICATION FAILED with errors:")
    for err in errors:
        print(f"  - {err}")
    exit(1)
else:
    print("VERIFICATION SUCCESS! All acceptance criteria met.")
    exit(0)
