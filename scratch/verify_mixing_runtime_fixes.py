# -*- coding: utf-8 -*-
"""
verify_mixing_runtime_fixes.py
Independent verification script to check XML blocks for P0/P1 fixes.
"""
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.join(ROOT, "projects", "Mixing_Nuoc_Tuong_Maggi_2026")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
IMPORT_DIR = os.path.join(PROJECT_DIR, "tia_import")

plc1_import_dir = os.path.join(IMPORT_DIR, "PLC_1_Mixing_Import")
plc2_import_dir = os.path.join(IMPORT_DIR, "PLC_2_Mixing_Import")

errors = []

def log_error(msg):
    errors.append(msg)
    print(f"[FAIL] {msg}")

def log_pass(msg):
    print(f"[PASS] {msg}")

def check_xml_exists(path):
    if not os.path.exists(path):
        log_error(f"File not found: {path}")
        return None
    try:
        return ET.parse(path).getroot()
    except Exception as e:
        log_error(f"Error parsing XML {path}: {str(e)}")
        return None

def get_title_text(net):
    for mt in net.findall(".//{*}MultilingualText"):
        if mt.attrib.get("CompositionName") == "Title":
            text_el = mt.find(".//{*}Text")
            if text_el is not None:
                return text_el.text or ""
    return ""

def get_component_names(elem):
    return [c.attrib.get("Name", "") for c in elem.findall(".//{*}Component")]

def verify_pid_compact_simulation_fixes(root_ob30, root_ob31):
    print("--- Checking PID_Compact Simulation Fixes (OB30 & OB31) ---")
    
    # Check OB30
    if root_ob30 is not None:
        compile_units = root_ob30.findall(".//{*}SW.Blocks.CompileUnit")
        pid_net_idx = -1
        pid_uid = None
        for idx, net in enumerate(compile_units):
            pid_part = net.find(".//{*}Part[@Name='PID_Compact']")
            if pid_part is not None:
                pid_net_idx = idx
                pid_uid = pid_part.attrib.get("UId")
                version = pid_part.attrib.get("Version")
                if version != "1.2":
                    log_error(f"OB30: PID_Compact version is '{version}', expected '1.2'")
                else:
                    log_pass("OB30: PID_Compact is Version 1.2")
                break
                
        if pid_net_idx == -1:
            log_error("OB30: PID_Compact call not found in compile units!")
        else:
            # Check Reset pin wiring
            reset_wire_found = False
            for wire in compile_units[pid_net_idx].findall(".//{*}Wire"):
                name_con = wire.find(".//{*}NameCon")
                if name_con is not None and name_con.attrib.get("UId") == pid_uid and name_con.attrib.get("Name") == "Reset":
                    ident_con = wire.find(".//{*}IdentCon")
                    if ident_con is not None:
                        target_uid = ident_con.attrib.get("UId")
                        for access in compile_units[pid_net_idx].findall(".//{*}Access"):
                            if access.attrib.get("UId") == target_uid:
                                tag_name = ".".join(get_component_names(access))
                                if tag_name == "PID_Bon2_Reset_Eff":
                                    reset_wire_found = True
                                    log_pass(f"OB30: PID_Compact Reset pin connected to '{tag_name}'")
                                else:
                                    log_error(f"OB30: PID_Compact Reset pin connected to '{tag_name}', expected 'PID_Bon2_Reset_Eff'")
            if not reset_wire_found:
                log_error("OB30: PID_Compact Reset pin connection wire not found!")

            # Check 3 networks before it
            estimation_found = False
            monitoring_found = False
            rcycle_found = False
            
            for idx in range(pid_net_idx):
                net = compile_units[idx]
                components = get_component_names(net)
                title = get_title_text(net)
                
                # Check for sb_EnCyclEstimation
                if "PID_Compact_1.sb_EnCyclEstimation" in title or "sb_EnCyclEstimation" in components:
                    has_nc_sim = False
                    for part in net.findall(".//{*}Part[@Name='Contact']"):
                        negated = part.find(".//{*}Negated[@Name='operand']")
                        if negated is not None:
                            part_uid = part.attrib.get("UId")
                            for wire in net.findall(".//{*}Wire"):
                                name_con = wire.find(".//{*}NameCon")
                                if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                    ident = wire.find(".//{*}IdentCon")
                                    if ident is not None:
                                        target_uid = ident.attrib.get("UId")
                                        for access in net.findall(".//{*}Access"):
                                            if access.attrib.get("UId") == target_uid:
                                                if "HMI_Sim_Mode" in get_component_names(access):
                                                    has_nc_sim = True
                    has_coil_est = False
                    for part in net.findall(".//{*}Part[@Name='Coil']"):
                        part_uid = part.attrib.get("UId")
                        for wire in net.findall(".//{*}Wire"):
                            name_con = wire.find(".//{*}NameCon")
                            if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                ident = wire.find(".//{*}IdentCon")
                                if ident is not None:
                                    target_uid = ident.attrib.get("UId")
                                    for access in net.findall(".//{*}Access"):
                                        if access.attrib.get("UId") == target_uid:
                                            if "PID_Compact_1.sb_EnCyclEstimation" in ".".join(get_component_names(access)):
                                                has_coil_est = True
                    if has_nc_sim and has_coil_est:
                        estimation_found = True
                        log_pass("OB30: sb_EnCyclEstimation network correctly configured before PID block")
                
                # Check for sb_EnCyclMonitoring
                if "PID_Compact_1.sb_EnCyclMonitoring" in title or "sb_EnCyclMonitoring" in components:
                    has_nc_sim = False
                    for part in net.findall(".//{*}Part[@Name='Contact']"):
                        negated = part.find(".//{*}Negated[@Name='operand']")
                        if negated is not None:
                            part_uid = part.attrib.get("UId")
                            for wire in net.findall(".//{*}Wire"):
                                name_con = wire.find(".//{*}NameCon")
                                if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                    ident = wire.find(".//{*}IdentCon")
                                    if ident is not None:
                                        target_uid = ident.attrib.get("UId")
                                        for access in net.findall(".//{*}Access"):
                                            if access.attrib.get("UId") == target_uid:
                                                if "HMI_Sim_Mode" in get_component_names(access):
                                                    has_nc_sim = True
                    has_coil_mon = False
                    for part in net.findall(".//{*}Part[@Name='Coil']"):
                        part_uid = part.attrib.get("UId")
                        for wire in net.findall(".//{*}Wire"):
                            name_con = wire.find(".//{*}NameCon")
                            if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                ident = wire.find(".//{*}IdentCon")
                                if ident is not None:
                                    target_uid = ident.attrib.get("UId")
                                    for access in net.findall(".//{*}Access"):
                                        if access.attrib.get("UId") == target_uid:
                                            if "PID_Compact_1.sb_EnCyclMonitoring" in ".".join(get_component_names(access)):
                                                has_coil_mon = True
                    if has_nc_sim and has_coil_mon:
                        monitoring_found = True
                        log_pass("OB30: sb_EnCyclMonitoring network correctly configured before PID block")

                # Check for r_Cycle Move
                if "PID_Compact_1.sPid_Calc.r_Cycle" in title or "r_Cycle" in components:
                    has_no_sim = False
                    for part in net.findall(".//{*}Part[@Name='Contact']"):
                        negated = part.find(".//{*}Negated[@Name='operand']")
                        if negated is None: # NO contact
                            part_uid = part.attrib.get("UId")
                            for wire in net.findall(".//{*}Wire"):
                                name_con = wire.find(".//{*}NameCon")
                                if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                    ident = wire.find(".//{*}IdentCon")
                                    if ident is not None:
                                        target_uid = ident.attrib.get("UId")
                                        for access in net.findall(".//{*}Access"):
                                            if access.attrib.get("UId") == target_uid:
                                                if "HMI_Sim_Mode" in get_component_names(access):
                                                    has_no_sim = True
                    has_move_01 = False
                    for part in net.findall(".//{*}Part[@Name='Move']"):
                        part_uid = part.attrib.get("UId")
                        for wire in net.findall(".//{*}Wire"):
                            name_con = wire.find(".//{*}NameCon")
                            if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "in":
                                ident = wire.find(".//{*}IdentCon")
                                if ident is not None:
                                    target_uid = ident.attrib.get("UId")
                                    for access in net.findall(".//{*}Access"):
                                        if access.attrib.get("UId") == target_uid:
                                            const_val = access.find(".//{*}ConstantValue")
                                            if const_val is not None and const_val.text == "0.1":
                                                has_move_01 = True
                    if has_no_sim and has_move_01:
                        rcycle_found = True
                        log_pass("OB30: r_Cycle MOVE 0.1 network correctly configured before PID block")

            if not estimation_found:
                log_error("OB30: Missing sb_EnCyclEstimation configuration network before PID block!")
            if not monitoring_found:
                log_error("OB30: Missing sb_EnCyclMonitoring configuration network before PID block!")
            if not rcycle_found:
                log_error("OB30: Missing r_Cycle MOVE 0.1 configuration network before PID block!")

    # Check OB31
    if root_ob31 is not None:
        compile_units = root_ob31.findall(".//{*}SW.Blocks.CompileUnit")
        pid_net_idx = -1
        pid_uid = None
        for idx, net in enumerate(compile_units):
            pid_part = net.find(".//{*}Part[@Name='PID_Compact']")
            if pid_part is not None:
                pid_net_idx = idx
                pid_uid = pid_part.attrib.get("UId")
                version = pid_part.attrib.get("Version")
                if version != "1.2":
                    log_error(f"OB31: PID_Compact version is '{version}', expected '1.2'")
                else:
                    log_pass("OB31: PID_Compact is Version 1.2")
                break
                
        if pid_net_idx == -1:
            log_error("OB31: PID_Compact call not found in compile units!")
        else:
            # Check Reset pin wiring
            reset_wire_found = False
            for wire in compile_units[pid_net_idx].findall(".//{*}Wire"):
                name_con = wire.find(".//{*}NameCon")
                if name_con is not None and name_con.attrib.get("UId") == pid_uid and name_con.attrib.get("Name") == "Reset":
                    ident_con = wire.find(".//{*}IdentCon")
                    if ident_con is not None:
                        target_uid = ident_con.attrib.get("UId")
                        for access in compile_units[pid_net_idx].findall(".//{*}Access"):
                            if access.attrib.get("UId") == target_uid:
                                tag_name = ".".join(get_component_names(access))
                                if tag_name == "PID_Bon4_Reset_Eff":
                                    reset_wire_found = True
                                    log_pass(f"OB31: PID_Compact Reset pin connected to '{tag_name}'")
                                else:
                                    log_error(f"OB31: PID_Compact Reset pin connected to '{tag_name}', expected 'PID_Bon4_Reset_Eff'")
            if not reset_wire_found:
                log_error("OB31: PID_Compact Reset pin connection wire not found!")

            # Check 3 networks before it
            estimation_found = False
            monitoring_found = False
            rcycle_found = False
            
            for idx in range(pid_net_idx):
                net = compile_units[idx]
                components = get_component_names(net)
                title = get_title_text(net)
                
                # Check for sb_EnCyclEstimation
                if "PID_Compact_2.sb_EnCyclEstimation" in title or "sb_EnCyclEstimation" in components:
                    has_nc_sim = False
                    for part in net.findall(".//{*}Part[@Name='Contact']"):
                        negated = part.find(".//{*}Negated[@Name='operand']")
                        if negated is not None:
                            part_uid = part.attrib.get("UId")
                            for wire in net.findall(".//{*}Wire"):
                                name_con = wire.find(".//{*}NameCon")
                                if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                    ident = wire.find(".//{*}IdentCon")
                                    if ident is not None:
                                        target_uid = ident.attrib.get("UId")
                                        for access in net.findall(".//{*}Access"):
                                            if access.attrib.get("UId") == target_uid:
                                                if "HMI_Sim_Mode" in get_component_names(access):
                                                    has_nc_sim = True
                    has_coil_est = False
                    for part in net.findall(".//{*}Part[@Name='Coil']"):
                        part_uid = part.attrib.get("UId")
                        for wire in net.findall(".//{*}Wire"):
                            name_con = wire.find(".//{*}NameCon")
                            if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                ident = wire.find(".//{*}IdentCon")
                                if ident is not None:
                                    target_uid = ident.attrib.get("UId")
                                    for access in net.findall(".//{*}Access"):
                                        if access.attrib.get("UId") == target_uid:
                                            if "PID_Compact_2.sb_EnCyclEstimation" in ".".join(get_component_names(access)):
                                                has_coil_est = True
                    if has_nc_sim and has_coil_est:
                        estimation_found = True
                        log_pass("OB31: sb_EnCyclEstimation network correctly configured before PID block")
                
                # Check for sb_EnCyclMonitoring
                if "PID_Compact_2.sb_EnCyclMonitoring" in title or "sb_EnCyclMonitoring" in components:
                    has_nc_sim = False
                    for part in net.findall(".//{*}Part[@Name='Contact']"):
                        negated = part.find(".//{*}Negated[@Name='operand']")
                        if negated is not None:
                            part_uid = part.attrib.get("UId")
                            for wire in net.findall(".//{*}Wire"):
                                name_con = wire.find(".//{*}NameCon")
                                if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                    ident = wire.find(".//{*}IdentCon")
                                    if ident is not None:
                                        target_uid = ident.attrib.get("UId")
                                        for access in net.findall(".//{*}Access"):
                                            if access.attrib.get("UId") == target_uid:
                                                if "HMI_Sim_Mode" in get_component_names(access):
                                                    has_nc_sim = True
                    has_coil_mon = False
                    for part in net.findall(".//{*}Part[@Name='Coil']"):
                        part_uid = part.attrib.get("UId")
                        for wire in net.findall(".//{*}Wire"):
                            name_con = wire.find(".//{*}NameCon")
                            if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                ident = wire.find(".//{*}IdentCon")
                                if ident is not None:
                                    target_uid = ident.attrib.get("UId")
                                    for access in net.findall(".//{*}Access"):
                                        if access.attrib.get("UId") == target_uid:
                                            if "PID_Compact_2.sb_EnCyclMonitoring" in ".".join(get_component_names(access)):
                                                has_coil_mon = True
                    if has_nc_sim and has_coil_mon:
                        monitoring_found = True
                        log_pass("OB31: sb_EnCyclMonitoring network correctly configured before PID block")

                # Check for r_Cycle Move
                if "PID_Compact_2.sPid_Calc.r_Cycle" in title or "r_Cycle" in components:
                    has_no_sim = False
                    for part in net.findall(".//{*}Part[@Name='Contact']"):
                        negated = part.find(".//{*}Negated[@Name='operand']")
                        if negated is None:
                            part_uid = part.attrib.get("UId")
                            for wire in net.findall(".//{*}Wire"):
                                name_con = wire.find(".//{*}NameCon")
                                if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "operand":
                                    ident = wire.find(".//{*}IdentCon")
                                    if ident is not None:
                                        target_uid = ident.attrib.get("UId")
                                        for access in net.findall(".//{*}Access"):
                                            if access.attrib.get("UId") == target_uid:
                                                if "HMI_Sim_Mode" in get_component_names(access):
                                                    has_no_sim = True
                    has_move_01 = False
                    for part in net.findall(".//{*}Part[@Name='Move']"):
                        part_uid = part.attrib.get("UId")
                        for wire in net.findall(".//{*}Wire"):
                            name_con = wire.find(".//{*}NameCon")
                            if name_con is not None and name_con.attrib.get("UId") == part_uid and name_con.attrib.get("Name") == "in":
                                ident = wire.find(".//{*}IdentCon")
                                if ident is not None:
                                    target_uid = ident.attrib.get("UId")
                                    for access in net.findall(".//{*}Access"):
                                        if access.attrib.get("UId") == target_uid:
                                            const_val = access.find(".//{*}ConstantValue")
                                            if const_val is not None and const_val.text == "0.1":
                                                has_move_01 = True
                    if has_no_sim and has_move_01:
                        rcycle_found = True
                        log_pass("OB31: r_Cycle MOVE 0.1 network correctly configured before PID block")

            if not estimation_found:
                log_error("OB31: Missing sb_EnCyclEstimation configuration network before PID block!")
            if not monitoring_found:
                log_error("OB31: Missing sb_EnCyclMonitoring configuration network before PID block!")
            if not rcycle_found:
                log_error("OB31: Missing r_Cycle MOVE 0.1 configuration network before PID block!")

def verify_state_12_and_15_sim_parameters():
    print("--- Checking State 12 & 15 Recipe Defaults & Sim Rates ---")
    
    # 1. Check Default Recipe for PLC1
    fc_init_plc1 = os.path.join(OUTPUT_DIR, "FC_Init_Default_Recipe_PLC1.xml")
    root_init_plc1 = check_xml_exists(fc_init_plc1)
    if root_init_plc1 is not None:
        found_t15s = False
        for net in root_init_plc1.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "recipe mặc định PLC1" in title or "Recipe" in title or "recipe" in title:
                components = get_component_names(net)
                if "HMI_SP_Time_Khuay_Bon1" in components:
                    for access in net.findall(".//{*}Access"):
                        const_val = access.find(".//{*}ConstantValue")
                        if const_val is not None and const_val.text == "T#15S":
                            found_t15s = True
        if found_t15s:
            log_pass("FC_Init_Default_Recipe_PLC1: HMI_SP_Time_Khuay_Bon1 is set to T#15S by default.")
        else:
            log_error("FC_Init_Default_Recipe_PLC1: HMI_SP_Time_Khuay_Bon1 is NOT set to T#15S by default!")

    # 2. Check Default Recipe for PLC2
    fc_init_plc2 = os.path.join(OUTPUT_DIR, "FC_Init_Default_Recipe_PLC2.xml")
    root_init_plc2 = check_xml_exists(fc_init_plc2)
    if root_init_plc2 is not None:
        found_t15s = False
        for net in root_init_plc2.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "recipe mặc định PLC2" in title or "Recipe" in title or "recipe" in title:
                components = get_component_names(net)
                if "HMI_SP_Time_Khuay_Bon3" in components:
                    for access in net.findall(".//{*}Access"):
                        const_val = access.find(".//{*}ConstantValue")
                        if const_val is not None and const_val.text == "T#15S":
                            found_t15s = True
        if found_t15s:
            log_pass("FC_Init_Default_Recipe_PLC2: HMI_SP_Time_Khuay_Bon3 is set to T#15S by default.")
        else:
            log_error("FC_Init_Default_Recipe_PLC2: HMI_SP_Time_Khuay_Bon3 is NOT set to T#15S by default!")

    # 3. Check OB30 Sim Bồn 1 level decrease rate
    fc_ob30 = os.path.join(OUTPUT_DIR, "OB30_PID_PLC1_Bon2.xml")
    root_ob30 = check_xml_exists(fc_ob30)
    if root_ob30 is not None:
        found_rate = False
        for net in root_ob30.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Sim Bồn 1: Giảm LT khi xả đáy" in title:
                components = get_component_names(net)
                if "LT3203_Bon1_HMI" in components:
                    for access in net.findall(".//{*}Access"):
                        const_val = access.find(".//{*}ConstantValue")
                        if const_val is not None and const_val.text == "0.4":
                            found_rate = True
        if found_rate:
            log_pass("OB30: Sim Bồn 1 Level decrease rate is 0.4 per 100ms.")
        else:
            log_error("OB30: Sim Bồn 1 Level decrease rate is NOT 0.4!")

    # 4. Check OB31 Sim Bồn 3 level decrease rate
    fc_ob31 = os.path.join(OUTPUT_DIR, "OB31_PID_PLC2_Bon4.xml")
    root_ob31 = check_xml_exists(fc_ob31)
    if root_ob31 is not None:
        found_rate = False
        for net in root_ob31.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Sim Bồn 3: Giảm LT khi xả đáy" in title:
                components = get_component_names(net)
                if "LT3213_Bon3_HMI" in components:
                    for access in net.findall(".//{*}Access"):
                        const_val = access.find(".//{*}ConstantValue")
                        if const_val is not None and const_val.text == "0.4":
                            found_rate = True
        if found_rate:
            log_pass("OB31: Sim Bồn 3 Level decrease rate is 0.4 per 100ms.")
        else:
            log_error("OB31: Sim Bồn 3 Level decrease rate is NOT 0.4!")

    # 5. Check FC_PLC1_Mixing transition State 15 -> State 20 condition
    fc_plc1 = os.path.join(OUTPUT_DIR, "FC_PLC1_Mixing.xml")
    root_plc1 = check_xml_exists(fc_plc1)
    if root_plc1 is not None:
        found_cond = False
        for net in root_plc1.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Xả Bồn 1 xong - Chuyển sang State 20" in title:
                components = get_component_names(net)
                if "LT3203_Bon1_Eff" in components:
                    for access in net.findall(".//{*}Access"):
                        const_val = access.find(".//{*}ConstantValue")
                        if const_val is not None and const_val.text == "0.5":
                            found_cond = True
        if found_cond:
            log_pass("FC_PLC1_Mixing: State 15 -> State 20 transition condition is Level <= 0.5.")
        else:
            log_error("FC_PLC1_Mixing: State 15 -> State 20 transition condition is NOT Level <= 0.5!")

    # 6. Check FC_PLC2_Mixing transition State 15 -> State 20 condition
    fc_plc2 = os.path.join(OUTPUT_DIR, "FC_PLC2_Mixing.xml")
    root_plc2 = check_xml_exists(fc_plc2)
    if root_plc2 is not None:
        found_cond = False
        for net in root_plc2.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Xả Bồn 3 xong - Chuyển sang State 20" in title:
                components = get_component_names(net)
                if "LT3213_Bon3_Eff" in components:
                    for access in net.findall(".//{*}Access"):
                        const_val = access.find(".//{*}ConstantValue")
                        if const_val is not None and const_val.text == "0.5":
                            found_cond = True
        if found_cond:
            log_pass("FC_PLC2_Mixing: State 15 -> State 20 transition condition is Level <= 0.5.")
        else:
            log_error("FC_PLC2_Mixing: State 15 -> State 20 transition condition is NOT Level <= 0.5!")

def verify_refactored_naming_and_integrity():
    print("--- Checking Refactored Naming & Integrity ---")
    
    # 1. Anti-AI_ Prefix Check on all XML files in OUTPUT_DIR
    if os.path.exists(OUTPUT_DIR):
        xml_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".xml")]
        has_ai_prefix_error = False
        for f in xml_files:
            path = os.path.join(OUTPUT_DIR, f)
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                # Walk all elements and check Name attribute
                for elem in root.iter():
                    name = elem.attrib.get("Name")
                    if name and name.startswith("AI_"):
                        log_error(f"{f}: Found identifier with 'AI_' prefix: '{name}' in element <{elem.tag.split('}')[-1]}>")
                        has_ai_prefix_error = True
            except Exception as e:
                log_error(f"Error parsing XML {f} for AI_ check: {str(e)}")
                has_ai_prefix_error = True
        if not has_ai_prefix_error:
            log_pass("Anti-AI_ Prefix Check: No identifiers starting with 'AI_' found in any generated XML files.")
            
    # 2. Modbus versions check (MB_CLIENT & MB_SERVER version 3.1)
    for plc_dir, filename in [(plc1_import_dir, "Main.xml"), (plc2_import_dir, "Main.xml")]:
        path = os.path.join(plc_dir, filename)
        if os.path.exists(path):
            try:
                root = ET.parse(path).getroot()
                for part in root.findall(".//{*}Part"):
                    name = part.attrib.get("Name")
                    if name in ["MB_CLIENT", "MB_SERVER"]:
                        version = part.attrib.get("Version")
                        if version != "3.1":
                            log_error(f"{filename}: Found {name} with version '{version}', expected '3.1'")
                        else:
                            log_pass(f"{filename}: {name} version is '3.1'")
            except Exception as e:
                log_error(f"Error parsing {filename} for Modbus version: {str(e)}")

    # 3. Tag Address Integrity Check
    def parse_tags(path):
        tag_map = {}
        if not os.path.exists(path):
            return tag_map
        try:
            root = ET.parse(path).getroot()
            for tag_el in root.iter():
                if tag_el.tag.endswith("SW.Tags.PlcTag"):
                    name_el = tag_el.find(".//{*}Name")
                    addr_el = tag_el.find(".//{*}LogicalAddress")
                    type_el = tag_el.find(".//{*}DataTypeName")
                    if name_el is not None and addr_el is not None and type_el is not None:
                        tag_map[name_el.text] = (addr_el.text, type_el.text)
        except Exception as e:
            log_error(f"Error parsing tag file {path}: {str(e)}")
        return tag_map

    backup_dir = os.path.join(ROOT, "scratch", "backup_tags")
    backup_plc1 = os.path.join(backup_dir, "AI_Tags_PLC1.xml")
    backup_plc2 = os.path.join(backup_dir, "AI_Tags_PLC2.xml")
    
    new_plc1 = os.path.join(OUTPUT_DIR, "PLC_Tags_PLC1.xml")
    new_plc2 = os.path.join(OUTPUT_DIR, "PLC_Tags_PLC2.xml")
    
    overrides = {
        "AI_Tags": "PLC_Tags",
        "AI_Tags_PLC1": "PLC_Tags_PLC1",
        "AI_Tags_PLC2": "PLC_Tags_PLC2",
        "AI_VFD_Bon2_MB_ActualSpeed": "VFD_Bon2_MB_FreqActual",
    }
    
    for old_path, new_path, plc_name in [(backup_plc1, new_plc1, "PLC1"), (backup_plc2, new_plc2, "PLC2")]:
        if os.path.exists(old_path) and os.path.exists(new_path):
            old_tags = parse_tags(old_path)
            new_tags = parse_tags(new_path)
            
            matched_count = 0
            mismatches = []
            
            for old_name, (old_addr, old_dtype) in old_tags.items():
                if old_name in overrides:
                    expected_new_name = overrides[old_name]
                elif old_name.startswith("AI_"):
                    expected_new_name = old_name[3:]
                else:
                    expected_new_name = old_name
                    
                if expected_new_name not in new_tags:
                    mismatches.append(f"Tag '{old_name}' (expected '{expected_new_name}') not found in refactored tags!")
                else:
                    new_addr, new_dtype = new_tags[expected_new_name]
                    
                    # Allow VFD Tank 2 connection modifications
                    allowed_override = False
                    if expected_new_name == "V3230_Nuoc_Bon1" and old_addr == "%Q0.0" and new_addr == "%M345.2":
                        allowed_override = True
                    elif expected_new_name == "V3230_Nuoc_Bon1_M" and old_addr == "%M220.0" and new_addr == "%M345.3":
                        allowed_override = True
                    elif expected_new_name == "VFD_Bon2_Run" and old_addr == "%Q0.6" and new_addr == "%M345.4":
                        allowed_override = True
                    elif expected_new_name == "VFD_Bon2_Run_M" and old_addr == "%M220.6" and new_addr == "%M345.5":
                        allowed_override = True
                    elif expected_new_name == "VFD_Bon2_Dao_Chieu" and old_addr == "%Q0.7" and new_addr == "%M345.6":
                        allowed_override = True
                    elif expected_new_name == "VFD_Bon2_Dao_Chieu_M" and old_addr == "%M220.7" and new_addr == "%M345.7":
                        allowed_override = True
                    elif expected_new_name == "VFD_Bon2_Toc_Do_AO" and old_addr == "%QD112" and new_addr == "%MD1080":
                        allowed_override = True
                    elif expected_new_name == "VFD_Bon2_Toc_Do_AO_M" and old_addr == "%MD1212" and new_addr == "%MD1084":
                        allowed_override = True
                    
                    if expected_new_name == "MB_TCP_STATUS" and old_addr == "%MW84" and new_addr == "%MW86" and old_dtype == "Word" and new_dtype == "Word":
                        # Allow migration of MB_TCP_STATUS from %MW84 to %MW86 to resolve PLC1 memory overlap with edge command bits
                        matched_count += 1
                    elif allowed_override:
                        matched_count += 1
                    elif new_addr != old_addr or new_dtype != old_dtype:
                        mismatches.append(f"Tag '{expected_new_name}' has mismatched address/datatype: expected ({old_addr}, {old_dtype}), got ({new_addr}, {new_dtype})")
                    else:
                        matched_count += 1
            
            if mismatches:
                log_error(f"{plc_name} Tag Integrity Check: FAILED with {len(mismatches)} mismatches:")
                for m in mismatches[:10]:
                    print(f"  - {m}")
            else:
                log_pass(f"{plc_name} Tag Integrity Check: PASSED. Successfully matched {matched_count} tags with identical addresses & datatypes.")
        else:
            print(f"Skipping {plc_name} Tag Integrity Check: backup or new tags file not found.")

def main():
    print("==========================================================")
    print(" RUNNING DESKTOP RUNTIME FIXES VERIFIER (P0/P1)")
    print("==========================================================")

    # 1. MB_CLIENT DB duplicate check in PLC1 Main
    plc1_main = os.path.join(plc1_import_dir, "Main.xml")
    root_main = check_xml_exists(plc1_main)
    if root_main is not None:
        instances = []
        for part in root_main.findall(".//{*}Part"):
            if part.attrib.get("Name") == "MB_CLIENT":
                inst = part.find(".//{*}Instance")
                if inst is not None:
                    comp_names = get_component_names(inst)
                    if comp_names:
                        instances.append(".".join(comp_names))
        
        if len(instances) == 0:
            log_error("No MB_CLIENT call found in PLC1 Main.xml!")
        elif len(instances) > 1:
            duplicates = [x for x in set(instances) if instances.count(x) > 1]
            if duplicates:
                log_error(f"MB_CLIENT calls use duplicate instance DBs in Main.xml: {duplicates}")
            else:
                log_pass("MB_CLIENT calls use distinct instance DBs or single call.")
        else:
            log_pass(f"Single call to MB_CLIENT found in Main.xml using: {instances[0]}")

    # 2. FC_Bon_Chua_Loc references BonChua_Owner_Nhanh1 and BonChua_Owner_Nhanh2
    fc_storage = os.path.join(OUTPUT_DIR, "FC_Bon_Chua_Loc.xml")
    root_storage = check_xml_exists(fc_storage)
    if root_storage is not None:
        owner1_found = False
        owner2_found = False
        for comp in root_storage.findall(".//{*}Component"):
            name = comp.attrib.get("Name")
            if name == "BonChua_Owner_Nhanh1":
                owner1_found = True
            if name == "BonChua_Owner_Nhanh2":
                owner2_found = True
        
        if owner1_found and owner2_found:
            log_pass("FC_Bon_Chua_Loc.xml references both owner tags.")
        else:
            log_error(f"FC_Bon_Chua_Loc.xml missing owner tags reference (Owner1: {owner1_found}, Owner2: {owner2_found}).")

        # 3. Pump3264 and Pump3265 gated by owner
        pump1_gated = False
        pump2_gated = False
        for net in root_storage.findall(".//{*}SW.Blocks.CompileUnit"):
            title_text = get_title_text(net)
            if "Bật bơm chuyển Nhánh 1" in title_text or "Nhánh 1 khi có owner" in title_text:
                components = get_component_names(net)
                if "BonChua_Owner_Nhanh1" in components:
                    pump1_gated = True
            if "Bật bơm chuyển Nhánh 2" in title_text or "Nhánh 2 khi có owner" in title_text:
                components = get_component_names(net)
                if "BonChua_Owner_Nhanh2" in components:
                    pump2_gated = True
        
        if pump1_gated and pump2_gated:
            log_pass("Pumps are correctly gated by owner tags in FC_Bon_Chua_Loc.xml.")
        else:
            log_error(f"Pumps not correctly gated by owner tags in FC_Bon_Chua_Loc.xml (Pump1: {pump1_gated}, Pump2: {pump2_gated}).")

        # 4. PLC2_Xa_Bon4_Xong_Nhan mapped or used in FC_Bon_Chua_Loc
        xa_bon4_xong_found = False
        for comp in root_storage.findall(".//{*}Component"):
            if comp.attrib.get("Name") == "PLC2_Xa_Bon4_Xong_Nhan":
                xa_bon4_xong_found = True
        if xa_bon4_xong_found:
            log_pass("PLC2_Xa_Bon4_Xong_Nhan is referenced in FC_Bon_Chua_Loc.xml.")
        else:
            log_error("PLC2_Xa_Bon4_Xong_Nhan is missing from FC_Bon_Chua_Loc.xml.")

    # 5. FC_PLC1_Mixing dry run TON
    fc_plc1 = os.path.join(OUTPUT_DIR, "FC_PLC1_Mixing.xml")
    root_plc1 = check_xml_exists(fc_plc1)
    if root_plc1 is not None:
        dry_run_net = None
        for net in root_plc1.findall(".//{*}SW.Blocks.CompileUnit"):
            title_text = get_title_text(net)
            if "Dry Run" in title_text:
                dry_run_net = net
                break
        if dry_run_net is not None:
            has_ton = any(part.attrib.get("Name") == "TON" for part in dry_run_net.findall(".//{*}Part"))
            components = get_component_names(dry_run_net)
            has_fault_tag = "PLC1_Loi_Dry_Run" in components
            if not has_ton and has_fault_tag:
                log_pass("Instant Dry Run protection (no TON, direct PLC1_Loi_Dry_Run) verified in FC_PLC1_Mixing.xml.")
            else:
                log_error(f"Dry Run check failed in PLC1 mixing. Has TON: {has_ton}, Has Fault Tag: {has_fault_tag}")
        else:
            log_error("Dry Run network not found in FC_PLC1_Mixing.xml.")

    # 6. FC_PLC2_Mixing dry run instant protection (no TON)
    fc_plc2 = os.path.join(OUTPUT_DIR, "FC_PLC2_Mixing.xml")
    root_plc2 = check_xml_exists(fc_plc2)
    if root_plc2 is not None:
        dry_run_net = None
        for net in root_plc2.findall(".//{*}SW.Blocks.CompileUnit"):
            title_text = get_title_text(net)
            if "Dry Run" in title_text:
                dry_run_net = net
                break
        if dry_run_net is not None:
            has_ton = any(part.attrib.get("Name") == "TON" for part in dry_run_net.findall(".//{*}Part"))
            components = get_component_names(dry_run_net)
            has_fault_tag = "PLC2_Loi_Dry_Run" in components
            if not has_ton and has_fault_tag:
                log_pass("Instant Dry Run protection (no TON, direct PLC2_Loi_Dry_Run) verified in FC_PLC2_Mixing.xml.")
            else:
                log_error(f"Dry Run check failed in PLC2 mixing. Has TON: {has_ton}, Has Fault Tag: {has_fault_tag}")
        else:
            log_error("Dry Run network not found in FC_PLC2_Mixing.xml.")

        # 7. PID Bồn 4 CV cleanup uses PID_Bon4_Enable instead of Step
        cv4_cleanup_enable = False
        for net in root_plc2.findall(".//{*}SW.Blocks.CompileUnit"):
            title_text = get_title_text(net)
            if "Reset CV hơi Bồn 4" in title_text or "Reset van hơi Bồn 4" in title_text or "CV hơi Bồn 4" in title_text:
                components = get_component_names(net)
                if "PID_Bon4_Enable" in components:
                    cv4_cleanup_enable = True
        if cv4_cleanup_enable:
            log_pass("Bồn 4 CV cleanup uses PID_Bon4_Enable.")
        else:
            log_error("Bồn 4 CV cleanup does not use PID_Bon4_Enable.")

        # 8. PID_Bon4_Error in Loi_Tong list
        pid4_error_in_fault = False
        for net in root_plc2.findall(".//{*}SW.Blocks.CompileUnit"):
            title_text = get_title_text(net)
            if "Tổng hợp lỗi PLC2" in title_text or "lỗi PLC2" in title_text:
                components = get_component_names(net)
                if "PID_Bon4_Error" in components:
                    pid4_error_in_fault = True
        if pid4_error_in_fault:
            log_pass("PID_Bon4_Error is in PLC2 fault aggregation list.")
        else:
            log_error("PID_Bon4_Error missing from PLC2 fault aggregation list.")

    # 9. No MOVE to FQ* (physical inputs)
    physical_fq_write = False
    physical_fq_tags = {"FQ3200_Bon1", "FQ3205_Bon2", "FQ3210_Bon3", "FQ3215_Bon4"}
    
    for root_obj, filename in [(root_plc1, "FC_PLC1_Mixing.xml"), (root_plc2, "FC_PLC2_Mixing.xml"), (root_storage, "FC_Bon_Chua_Loc.xml")]:
        if root_obj is None:
            continue
        for net in root_obj.findall(".//{*}SW.Blocks.CompileUnit"):
            # Find any Move parts in this network
            moves = [p for p in net.findall(".//{*}Part") if p.attrib.get("Name") == "Move"]
            if not moves:
                continue
            
            # For each move part, check what is connected to its out1 pin
            for move in moves:
                move_uid = move.attrib.get("UId")
                # Look for wire connecting Move out1
                for wire in net.findall(".//{*}Wire"):
                    name_con = wire.find(".//{*}NameCon")
                    if name_con is not None and name_con.attrib.get("UId") == move_uid and name_con.attrib.get("Name") == "out1":
                        # Find IdentCon
                        ident_con = wire.find(".//{*}IdentCon")
                        if ident_con is not None:
                            target_uid = ident_con.attrib.get("UId")
                            # Find the corresponding Access
                            for access in net.findall(".//{*}Access"):
                                if access.attrib.get("UId") == target_uid:
                                    target_name = ".".join(get_component_names(access))
                                    if target_name in physical_fq_tags:
                                        log_error(f"Illegal write to physical totalizer tag {target_name} in {filename}!")
                                        physical_fq_write = True
                                        
    if not physical_fq_write:
        log_pass("No physical totalizer FQ tags are written to (MOVE) in program blocks.")

    # 10. FT_HMI set/reset checks for all 4 tanks
    ob30_path = os.path.join(OUTPUT_DIR, "OB30_PID_PLC1_Bon2.xml")
    root_ob30 = check_xml_exists(ob30_path)
    if root_ob30 is not None:
        ft1_set = False
        ft1_reset = False
        ft2_set = False
        ft2_reset = False
        for net in root_ob30.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Set FT khi dosing" in title or "MOVE" in title or "FT" in title:
                components = get_component_names(net)
                if "FT3200_Bon1_HMI" in components:
                    if any(p.attrib.get("Name") == "Move" for p in net.findall(".//{*}Part")):
                        for access in net.findall(".//{*}Access"):
                            const_val = access.find(".//{*}ConstantValue")
                            if const_val is not None and const_val.text == "10.0":
                                ft1_set = True
                            if const_val is not None and const_val.text == "0.0":
                                ft1_reset = True
                if "FT3205_Bon2_HMI" in components:
                    for access in net.findall(".//{*}Access"):
                        const_val = access.find(".//{*}ConstantValue")
                        if const_val is not None and const_val.text == "10.0":
                            ft2_set = True
                        if const_val is not None and const_val.text == "0.0":
                            ft2_reset = True
        if ft1_set and ft1_reset:
            log_pass("OB30 has correct Set/Reset FT logic for Bồn 1.")
        else:
            log_error(f"OB30 missing Set/Reset FT logic for Bồn 1 (Set: {ft1_set}, Reset: {ft1_reset}).")
        if ft2_set and ft2_reset:
            log_pass("OB30 has correct Set/Reset FT logic for Bồn 2.")
        else:
            log_error(f"OB30 missing Set/Reset FT logic for Bồn 2 (Set: {ft2_set}, Reset: {ft2_reset}).")

    ob31_path = os.path.join(OUTPUT_DIR, "OB31_PID_PLC2_Bon4.xml")
    root_ob31 = check_xml_exists(ob31_path)
    if root_ob31 is not None:
        ft3_set = False
        ft3_reset = False
        ft4_set = False
        ft4_reset = False
        for net in root_ob31.findall(".//{*}SW.Blocks.CompileUnit"):
            components = get_component_names(net)
            if "FT3210_Bon3_HMI" in components:
                for access in net.findall(".//{*}Access"):
                    const_val = access.find(".//{*}ConstantValue")
                    if const_val is not None and const_val.text == "10.0":
                        ft3_set = True
                    if const_val is not None and const_val.text == "0.0":
                        ft3_reset = True
            if "FT3215_Bon4_HMI" in components:
                for access in net.findall(".//{*}Access"):
                    const_val = access.find(".//{*}ConstantValue")
                    if const_val is not None and const_val.text == "10.0":
                        ft4_set = True
                    if const_val is not None and const_val.text == "0.0":
                        ft4_reset = True
        if ft3_set and ft3_reset:
            log_pass("OB31 has correct Set/Reset FT logic for Bồn 3.")
        else:
            log_error(f"OB31 missing Set/Reset FT logic for Bồn 3 (Set: {ft3_set}, Reset: {ft3_reset}).")
        if ft4_set and ft4_reset:
            log_pass("OB31 has correct Set/Reset FT logic for Bồn 4.")
        else:
            log_error(f"OB31 missing Set/Reset FT logic for Bồn 4 (Set: {ft4_set}, Reset: {ft4_reset}).")

    # 11. Bồn 2 Temp simulation tag check
    if root_ob30 is not None:
        bon2_temp_inc_used = False
        bon4_temp_val1_used = False
        for net in root_ob30.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Sim Bồn 2 Temp" in title:
                components = get_component_names(net)
                if "PID_Bon2_Temp_Inc" in components:
                    bon2_temp_inc_used = True
                if "PID_Bon4_Temp_Val_1" in components:
                    bon4_temp_val1_used = True
        if bon2_temp_inc_used and not bon4_temp_val1_used:
            log_pass("OB30 simulates Bồn 2 temperature using PID_Bon2_Temp_Inc and not Bồn 4 temp variable.")
        else:
            log_error(f"OB30 temp simulation validation failed (PID_Bon2_Temp_Inc: {bon2_temp_inc_used}, PID_Bon4_Temp_Val_1: {bon4_temp_val1_used}).")

    # 12. Modbus mapping for PID Bồn 4 PV
    plc2_main = os.path.join(plc2_import_dir, "Main.xml")
    root_plc2_main = check_xml_exists(plc2_main)
    if root_plc2_main is not None:
        correct_mapping_found = False
        incorrect_mapping_found = False
        for net in root_plc2_main.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Modbus TCP Server - Map Analog Status" in title:
                components = get_component_names(net)
                if "PID_Bon4_PV" in components:
                    if "TT3219_Bon4_Sim" in components:
                        correct_mapping_found = True
                    if "TT3219_Bon4_Eff" in components:
                        incorrect_mapping_found = True
        if correct_mapping_found and not incorrect_mapping_found:
            log_pass("PLC2 Main maps PID_Bon4_PV from TT3219_Bon4_Sim correctly.")
        else:
            log_error(f"PLC2 Main Modbus PV mapping validation failed (Correct: {correct_mapping_found}, Incorrect: {incorrect_mapping_found}).")

    # 13. Reset coil for BonChua_Chuyen_Bon2_Xong_HMI in OB30
    if root_ob30 is not None:
        chuyen_bon2_reset_found = False
        for net in root_ob30.findall(".//{*}SW.Blocks.CompileUnit"):
            if any(p.attrib.get("Name") == "RCoil" for p in net.findall(".//{*}Part")):
                components = get_component_names(net)
                if "BonChua_Chuyen_Bon2_Xong_HMI" in components:
                    chuyen_bon2_reset_found = True
        if chuyen_bon2_reset_found:
            log_pass("OB30 contains RCoil for BonChua_Chuyen_Bon2_Xong_HMI.")
        else:
            log_error("OB30 is missing RCoil for BonChua_Chuyen_Bon2_Xong_HMI.")

    # 14. Reset coils for Auto_Enable
    if root_plc1 is not None:
        auto_enable_reset = False
        for net in root_plc1.findall(".//{*}SW.Blocks.CompileUnit"):
            if any(p.attrib.get("Name") == "RCoil" for p in net.findall(".//{*}Part")):
                components = get_component_names(net)
                if "PLC1_Auto_Enable" in components:
                    title = get_title_text(net)
                    if "hoàn thành Nhánh 1" in title or "Hoàn thành Nhánh 1" in title or "Auto Enable" in title:
                        auto_enable_reset = True
        if auto_enable_reset:
            log_pass("FC_PLC1_Mixing resets PLC1_Auto_Enable on batch completion.")
        else:
            log_error("FC_PLC1_Mixing is missing reset coil for PLC1_Auto_Enable on batch completion.")

    if root_plc2 is not None:
        auto_enable_reset = False
        for net in root_plc2.findall(".//{*}SW.Blocks.CompileUnit"):
            if any(p.attrib.get("Name") == "RCoil" for p in net.findall(".//{*}Part")):
                components = get_component_names(net)
                if "PLC2_Auto_Enable" in components:
                    title = get_title_text(net)
                    if "hoàn thành Nhánh 2" in title or "Hoàn thành Nhánh 2" in title or "Auto Enable" in title:
                        auto_enable_reset = True
        if auto_enable_reset:
            log_pass("FC_PLC2_Mixing resets PLC2_Auto_Enable on batch completion.")
        else:
            log_error("FC_PLC2_Mixing is missing reset coil for PLC2_Auto_Enable on batch completion.")

    # 15. Idle state logic checking
    if root_plc1 is not None:
        plc1_idle_found = False
        for net in root_plc1.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Idle" in title or "state PLC1 về 0" in title:
                components = get_component_names(net)
                if "PLC1_State" in components:
                    if any(p.attrib.get("Name") == "Move" for p in net.findall(".//{*}Part")):
                        plc1_idle_found = True
        if plc1_idle_found:
            log_pass("FC_PLC1_Mixing contains idle state reset logic.")
        else:
            log_error("FC_PLC1_Mixing is missing idle state reset logic.")

    if root_plc2 is not None:
        plc2_idle_found = False
        for net in root_plc2.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Idle" in title or "state PLC2 về 0" in title:
                components = get_component_names(net)
                if "PLC2_State" in components:
                    if any(p.attrib.get("Name") == "Move" for p in net.findall(".//{*}Part")):
                        plc2_idle_found = True
        if plc2_idle_found:
            log_pass("FC_PLC2_Mixing contains idle state reset logic.")
        else:
            log_error("FC_PLC2_Mixing is missing idle state reset logic.")

    if root_storage is not None:
        storage_idle_found = False
        for net in root_storage.findall(".//{*}SW.Blocks.CompileUnit"):
            title = get_title_text(net)
            if "Idle" in title or "state Storage về 0" in title:
                components = get_component_names(net)
                if "BonChua_State" in components:
                    if any(p.attrib.get("Name") == "Move" for p in net.findall(".//{*}Part")):
                        storage_idle_found = True
        if storage_idle_found:
            log_pass("FC_Bon_Chua_Loc contains idle state reset logic.")
        else:
            log_error("FC_Bon_Chua_Loc is missing idle state reset logic.")

    # 16. Verify network execution order in PLC1 and PLC2
    def check_network_order(root, filename, plc_name, set_auto_sub, move_10_sub, reset_auto_sub, reset_pid_sub, move_40_sub):
        compile_units = root.findall(".//{*}SW.Blocks.CompileUnit")
        
        idx_set_auto = -1
        idx_move_10 = -1
        idx_reset_auto = -1
        idx_reset_pid = -1
        idx_move_40 = -1
        
        for idx, net in enumerate(compile_units):
            title = get_title_text(net)
            if set_auto_sub in title:
                idx_set_auto = idx
            if move_10_sub in title:
                idx_move_10 = idx
            if reset_auto_sub in title:
                idx_reset_auto = idx
            if reset_pid_sub in title:
                idx_reset_pid = idx
            if move_40_sub[0] in title or move_40_sub[1] in title:
                idx_move_40 = idx

        if idx_set_auto == -1:
            log_error(f"{filename}: Network for Set Auto Enable ('{set_auto_sub}') not found!")
        if idx_move_10 == -1:
            log_error(f"{filename}: Network for Move 10 ('{move_10_sub}') not found!")
        if idx_reset_auto == -1:
            log_error(f"{filename}: Network for Reset Auto Enable ('{reset_auto_sub}') not found!")
        if idx_reset_pid == -1:
            log_error(f"{filename}: Network for Reset PID Enable ('{reset_pid_sub}') not found!")
        if idx_move_40 == -1:
            log_error(f"{filename}: Network for Move 40 not found!")
            
        if idx_set_auto != -1 and idx_move_10 != -1:
            if idx_set_auto < idx_move_10:
                log_pass(f"{filename}: Set Auto Enable (index {idx_set_auto}) is BEFORE Move 10 (index {idx_move_10}).")
            else:
                log_error(f"{filename}: Set Auto Enable (index {idx_set_auto}) must be BEFORE Move 10 (index {idx_move_10})!")
                
        if idx_reset_auto != -1 and idx_move_40 != -1:
            if idx_reset_auto < idx_move_40:
                log_pass(f"{filename}: Reset Auto Enable (index {idx_reset_auto}) is BEFORE Move 40 (index {idx_move_40}).")
            else:
                log_error(f"{filename}: Reset Auto Enable (index {idx_reset_auto}) must be BEFORE Move 40 (index {idx_move_40})!")
                
        if idx_reset_pid != -1 and idx_move_40 != -1:
            if idx_reset_pid < idx_move_40:
                log_pass(f"{filename}: Reset PID Enable (index {idx_reset_pid}) is BEFORE Move 40 (index {idx_move_40}).")
            else:
                log_error(f"{filename}: Reset PID Enable (index {idx_reset_pid}) must be BEFORE Move 40 (index {idx_move_40})!")

    if root_plc1 is not None:
        check_network_order(root_plc1, "FC_PLC1_Mixing.xml", "PLC1",
                            "Set Auto Enable", "Chuyển sang State 10",
                            "Tắt Auto Enable", "Tắt PID Enable",
                            ["Chuyển sang State 40", "Reset Auto Enable và chuyển sang State 40"])

    if root_plc2 is not None:
        check_network_order(root_plc2, "FC_PLC2_Mixing.xml", "PLC2",
                            "Set Auto Enable", "Chuyển sang State 10",
                            "Tắt Auto Enable", "Tắt PID Enable",
                            ["Chuyển sang State 40", "Reset Auto Enable và chuyển sang State 40"])

    verify_pid_compact_simulation_fixes(root_ob30, root_ob31)
    verify_state_12_and_15_sim_parameters()
    verify_refactored_naming_and_integrity()
    verify_agitator_animation_logic()

    print("==========================================================")
    if errors:
        print(f"VERIFIER STATUS: FAILED ({len(errors)} errors)")
        print("==========================================================")
        sys.exit(1)
    else:
        print("VERIFIER STATUS: ALL P0/P1 DESKTOP FIXES PASSED SUCCESSFULLY!")
        print("==========================================================")
        sys.exit(0)

def verify_agitator_animation_logic():
    print("--- Checking Agitator Animation Logic & Tags (FC60/FC61 refactor) ---")

    # 1. Check tags in PLC1 and PLC2 XMLs
    plc1_tags_path = os.path.join(OUTPUT_DIR, "PLC_Tags_PLC1.xml")
    plc2_tags_path = os.path.join(OUTPUT_DIR, "PLC_Tags_PLC2.xml")

    def parse_tags(path):
        tag_map = {}
        if not os.path.exists(path):
            return tag_map
        try:
            root = ET.parse(path).getroot()
            for tag_el in root.iter():
                if tag_el.tag.endswith("SW.Tags.PlcTag"):
                    name_el = tag_el.find(".//{*}Name")
                    addr_el = tag_el.find(".//{*}LogicalAddress")
                    type_el = tag_el.find(".//{*}DataTypeName")
                    if name_el is not None and addr_el is not None and type_el is not None:
                        tag_map[name_el.text] = (addr_el.text, type_el.text)
        except Exception as e:
            errors.append(f"Error parsing tag file {path}: {str(e)}")
        return tag_map

    plc1_tags = parse_tags(plc1_tags_path)
    plc2_tags = parse_tags(plc2_tags_path)

    # Verify Bon 1 & Bon 2 on PLC1
    for tag_name in ["HMI_Anim_Bon1_Frame", "HMI_Anim_Bon2_Frame", "HMI_Anim_Bon1_MucDich", "HMI_Anim_Bon2_MucDich", "HMI_Anim_BonChua1_MucDich", "HMI_Anim_BonChua2_MucDich"]:
        if tag_name not in plc1_tags:
            log_error(f"PLC1 Tag Check: Tag '{tag_name}' is missing from PLC_Tags_PLC1.xml!")
        else:
            addr, dtype = plc1_tags[tag_name]
            if not addr.startswith("%MW") or dtype != "Int":
                log_error(f"PLC1 Tag Check: Tag '{tag_name}' has incorrect address '{addr}' or type '{dtype}', expected %MW and Int!")
            else:
                log_pass(f"PLC1 Tag Check: Tag '{tag_name}' is correctly declared at '{addr}' as Int.")

    # Verify Bon 3 & Bon 4 on PLC2
    for tag_name in ["HMI_Anim_Bon3_Frame", "HMI_Anim_Bon4_Frame", "HMI_Anim_Bon3_MucDich", "HMI_Anim_Bon4_MucDich"]:
        if tag_name not in plc2_tags:
            log_error(f"PLC2 Tag Check: Tag '{tag_name}' is missing from PLC_Tags_PLC2.xml!")
        else:
            addr, dtype = plc2_tags[tag_name]
            if not addr.startswith("%MW") or dtype != "Int":
                log_error(f"PLC2 Tag Check: Tag '{tag_name}' has incorrect address '{addr}' or type '{dtype}', expected %MW and Int!")
            else:
                log_pass(f"PLC2 Tag Check: Tag '{tag_name}' is correctly declared at '{addr}' as Int.")

    # 2. Check FC60: FC_HMI_Animation_PLC1
    fc60_path = os.path.join(OUTPUT_DIR, "FC_HMI_Animation_PLC1.xml")
    root_fc60 = check_xml_exists(fc60_path)
    if root_fc60 is not None:
        titles_fc60 = [get_title_text(n) for n in root_fc60.findall(".//{*}SW.Blocks.CompileUnit")]
        # Use suffix "n 1:" and "n 2:" to match both "Bồn 1:" and "Bon 1:" regardless of diacritics for agitator
        agit_nets_1 = [t for t in titles_fc60 if "n 1:" in t and "khu" in t.lower()]
        agit_nets_2 = [t for t in titles_fc60 if "n 2:" in t and "khu" in t.lower()]
        agit_total = len(agit_nets_1) + len(agit_nets_2)
        if agit_total == 8:
            log_pass(f"FC60 (FC_HMI_Animation_PLC1): 8 agitator animation networks for Bon 1 & Bon 2 found.")
        else:
            log_error(f"FC60 (FC_HMI_Animation_PLC1): Expected 8 agitator networks, found {agit_total} (Bon1:{len(agit_nets_1)}, Bon2:{len(agit_nets_2)})")

        # Check level state animation networks in FC60
        tanks_p1 = [
            ("Bồn 1 Mức dịch", "Bon 1 Mức dịch"),
            ("Bồn 2 Mức dịch", "Bon 2 Mức dịch"),
            ("Bồn chứa 1 Mức dịch", "Bon chứa 1 Mức dịch"),
            ("Bồn chứa 2 Mức dịch", "Bon chứa 2 Mức dịch")
        ]
        for t_vi, t_en in tanks_p1:
            nets = [t for t in titles_fc60 if t_vi in t or t_en in t]
            if len(nets) == 3:
                log_pass(f"FC60 (FC_HMI_Animation_PLC1): 3 level state networks for '{t_vi}' found.")
            else:
                log_error(f"FC60 (FC_HMI_Animation_PLC1): Expected 3 level state networks for '{t_vi}', found {len(nets)}!")

    # 3. Check FC61: FC_HMI_Animation_PLC2
    fc61_path = os.path.join(OUTPUT_DIR, "FC_HMI_Animation_PLC2.xml")
    root_fc61 = check_xml_exists(fc61_path)
    if root_fc61 is not None:
        titles_fc61 = [get_title_text(n) for n in root_fc61.findall(".//{*}SW.Blocks.CompileUnit")]
        agit_nets_3 = [t for t in titles_fc61 if "n 3:" in t and "khu" in t.lower()]
        agit_nets_4 = [t for t in titles_fc61 if "n 4:" in t and "khu" in t.lower()]
        agit_total = len(agit_nets_3) + len(agit_nets_4)
        if agit_total == 8:
            log_pass(f"FC61 (FC_HMI_Animation_PLC2): 8 agitator animation networks for Bon 3 & Bon 4 found.")
        else:
            log_error(f"FC61 (FC_HMI_Animation_PLC2): Expected 8 agitator networks, found {agit_total} (Bon3:{len(agit_nets_3)}, Bon4:{len(agit_nets_4)})")

        # Check level state animation networks in FC61
        tanks_p2 = [
            ("Bồn 3 Mức dịch", "Bon 3 Mức dịch"),
            ("Bồn 4 Mức dịch", "Bon 4 Mức dịch")
        ]
        for t_vi, t_en in tanks_p2:
            nets = [t for t in titles_fc61 if t_vi in t or t_en in t]
            if len(nets) == 3:
                log_pass(f"FC61 (FC_HMI_Animation_PLC2): 3 level state networks for '{t_vi}' found.")
            else:
                log_error(f"FC61 (FC_HMI_Animation_PLC2): Expected 3 level state networks for '{t_vi}', found {len(nets)}!")

    # 4. OB30 must NOT contain frame logic directly, MUST have CALL_FC
    ob30_path = os.path.join(OUTPUT_DIR, "OB30_PID_PLC1_Bon2.xml")
    root_ob30 = check_xml_exists(ob30_path)
    if root_ob30 is not None:
        titles_ob30 = [get_title_text(n) for n in root_ob30.findall(".//{*}SW.Blocks.CompileUnit")]
        direct_anim = [t for t in titles_ob30 if ("n 1:" in t or "n 2:" in t) and "khu" in t.lower()]
        if direct_anim:
            log_error(f"OB30: Still contains direct animation networks (should be in FC60): {direct_anim}")
        else:
            log_pass("OB30: No direct animation networks (correctly removed).")
        call_fc_found = any("animation" in t.lower() or "FC_HMI_Animation" in t for t in titles_ob30)
        if call_fc_found:
            log_pass("OB30: CALL_FC network for FC_HMI_Animation_PLC1 found.")
        else:
            log_error("OB30: Missing CALL_FC network for FC_HMI_Animation_PLC1!")

    # 5. OB31 must NOT contain frame logic directly, MUST have CALL_FC
    ob31_path = os.path.join(OUTPUT_DIR, "OB31_PID_PLC2_Bon4.xml")
    root_ob31 = check_xml_exists(ob31_path)
    if root_ob31 is not None:
        titles_ob31 = [get_title_text(n) for n in root_ob31.findall(".//{*}SW.Blocks.CompileUnit")]
        direct_anim = [t for t in titles_ob31 if ("n 3:" in t or "n 4:" in t) and "khu" in t.lower()]
        if direct_anim:
            log_error(f"OB31: Still contains direct animation networks (should be in FC61): {direct_anim}")
        else:
            log_pass("OB31: No direct animation networks (correctly removed).")
        call_fc_found = any("animation" in t.lower() or "FC_HMI_Animation" in t for t in titles_ob31)
        if call_fc_found:
            log_pass("OB31: CALL_FC network for FC_HMI_Animation_PLC2 found.")
        else:
            log_error("OB31: Missing CALL_FC network for FC_HMI_Animation_PLC2!")

    # 6. Import sets must include FC60/FC61
    fc60_import = os.path.join(plc1_import_dir, "FC_HMI_Animation_PLC1.xml")
    fc61_import = os.path.join(plc2_import_dir, "FC_HMI_Animation_PLC2.xml")
    if os.path.exists(fc60_import):
        log_pass("Import PLC1: FC_HMI_Animation_PLC1.xml present in tia_import/PLC_1_Mixing_Import/")
    else:
        log_error("Import PLC1: FC_HMI_Animation_PLC1.xml MISSING from tia_import/PLC_1_Mixing_Import/")
    if os.path.exists(fc61_import):
        log_pass("Import PLC2: FC_HMI_Animation_PLC2.xml present in tia_import/PLC_2_Mixing_Import/")
    else:
        log_error("Import PLC2: FC_HMI_Animation_PLC2.xml MISSING from tia_import/PLC_2_Mixing_Import/")


if __name__ == "__main__":
    main()
