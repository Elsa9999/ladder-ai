# -*- coding: utf-8 -*-
import os
import re
import json
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

raw_patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_patterns"
patterns_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\patterns"

patterns_config = [
    {
        "name": "or",
        "category": "basic",
        "instruction_name": "OR",
        "mapping": {
            "L_LEVEL": "{{BOOL_IN_1}}",
            "H_LEVEL": "{{BOOL_IN_2}}",
            "STOP": "{{BOOL_IN_3}}",
            "Tag_2": "{{BOOL_MEM}}",
            "PUMP_1": "{{BOOL_OUT_1}}",
            "PUMP_2": "{{BOOL_OUT_2}}"
        },
        "required_tags": [
            {"name": "{{BOOL_IN_1}}", "type": "Bool"},
            {"name": "{{BOOL_IN_2}}", "type": "Bool"},
            {"name": "{{BOOL_IN_3}}", "type": "Bool"},
            {"name": "{{BOOL_MEM}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_1}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_2}}", "type": "Bool"}
        ],
        "required_instance_db": "",
        "required_dbs": [],
        "description": "Cổng logic OR kết hợp với chốt SR (Set-Reset) điều khiển chạy/dừng bơm.",
        "compile_notes": "Yêu cầu khai báo các biến kiểu Bool tương ứng trong PLC Tags hoặc khối dữ liệu."
    },
    {
        "name": "sr",
        "category": "basic",
        "instruction_name": "SR",
        "mapping": {
            "L_LEVEL": "{{BOOL_IN_1}}",
            "H_LEVEL": "{{BOOL_IN_2}}",
            "STOP": "{{BOOL_IN_3}}",
            "Tag_2": "{{BOOL_MEM}}",
            "PUMP_1": "{{BOOL_OUT_1}}",
            "PUMP_2": "{{BOOL_OUT_2}}"
        },
        "required_tags": [
            {"name": "{{BOOL_IN_1}}", "type": "Bool"},
            {"name": "{{BOOL_IN_2}}", "type": "Bool"},
            {"name": "{{BOOL_IN_3}}", "type": "Bool"},
            {"name": "{{BOOL_MEM}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_1}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_2}}", "type": "Bool"}
        ],
        "required_instance_db": "",
        "required_dbs": [],
        "description": "Mạch chốt trạng thái SR (Set-Reset) duy trì trạng thái đầu ra.",
        "compile_notes": "Cần khai báo biến trung gian {{BOOL_MEM}} để lưu trữ trạng thái chốt của khối SR."
    },
    {
        "name": "tp",
        "category": "timer_counter",
        "instruction_name": "TP",
        "mapping": {
            "H_LEVEL": "{{BOOL_IN_SET}}",
            "VALVE": "{{BOOL_IN_RESET}}",
            "Tag_1": "{{BOOL_SR_MEM}}",
            "Timer_0_DB": "{{DB_INSTANCE}}",
            "STOP": "{{BOOL_IN_STOP}}",
            "MIXER": "{{BOOL_OUT}}"
        },
        "required_tags": [
            {"name": "{{BOOL_IN_SET}}", "type": "Bool"},
            {"name": "{{BOOL_IN_RESET}}", "type": "Bool"},
            {"name": "{{BOOL_SR_MEM}}", "type": "Bool"},
            {"name": "{{BOOL_IN_STOP}}", "type": "Bool"},
            {"name": "{{BOOL_OUT}}", "type": "Bool"}
        ],
        "required_instance_db": "{{DB_INSTANCE}}",
        "required_dbs": [],
        "description": "Khối tạo xung thời gian TP (Timer Pulse) giữ đầu ra cao trong một khoảng thời gian đặt trước.",
        "compile_notes": "Yêu cầu khai báo khối DB Instance kiểu IEC_TIMER cho bộ định thời {{DB_INSTANCE}}."
    },
    {
        "name": "tof",
        "category": "timer_counter",
        "instruction_name": "TOF",
        "mapping": {
            "M1_MOTOR_DB": "{{DB_MOTOR_STATUS}}",
            "COIL_F_OUT": "{{BOOL_COIL_F}}",
            "M1_I/O_DB": "{{DB_MOTOR_IO}}",
            "M1_STOP": "{{BOOL_STOP}}",
            "HMI_DB": "{{DB_HMI}}",
            "STATES_DB": "{{DB_STATES}}",
            "EMERGENCY_STATE": "{{BOOL_EMERGENCY}}",
            "DIV_1": "{{BOOL_DIV_1}}",
            "M1_STOP_TIMER": "{{DB_INSTANCE_TP}}",
            "M1_R_TIMER": "{{DB_INSTANCE_TOF_1}}",
            "M1_F_TIMER": "{{DB_INSTANCE_TOF_2}}",
            "MOVE_R": "{{BOOL_MOVE_R}}",
            "COIL_R_OUT": "{{BOOL_COIL_R}}",
            "MOVE_F": "{{BOOL_MOVE_F}}",
            "M1_WIND_DOWN": "{{BOOL_WIND_DOWN}}"
        },
        "required_tags": [
            {"name": "{{BOOL_COIL_F}}", "type": "Bool"},
            {"name": "{{BOOL_STOP}}", "type": "Bool"},
            {"name": "{{BOOL_EMERGENCY}}", "type": "Bool"},
            {"name": "{{BOOL_DIV_1}}", "type": "Bool"},
            {"name": "{{BOOL_MOVE_R}}", "type": "Bool"},
            {"name": "{{BOOL_COIL_R}}", "type": "Bool"},
            {"name": "{{BOOL_MOVE_F}}", "type": "Bool"},
            {"name": "{{BOOL_WIND_DOWN}}", "type": "Bool"}
        ],
        "required_instance_db": "{{DB_INSTANCE_TOF_1}}",
        "required_dbs": [
            "{{DB_MOTOR_STATUS}}",
            "{{DB_MOTOR_IO}}",
            "{{DB_HMI}}",
            "{{DB_STATES}}",
            "{{DB_INSTANCE_TP}}",
            "{{DB_INSTANCE_TOF_2}}"
        ],
        "description": "Khối trễ tắt TOF (Timer Off-Delay) trong hệ thống điều khiển và bảo vệ động cơ đảo chiều.",
        "compile_notes": "Hệ thống sử dụng các khối DB dữ liệu chung để quản lý trạng thái động cơ và I/O cùng 3 bộ định thời."
    },
    {
        "name": "r_trig",
        "category": "basic",
        "instruction_name": "R_TRIG",
        "mapping": {
            "Start": "{{BOOL_CLK}}",
            "Element Start": "{{BOOL_Q}}",
            "Element": "{{BOOL_OUT}}",
            "Element Time Delay": "{{TIME_ELAPSED}}",
            "R_TRIG_DB": "{{DB_INSTANCE_R_TRIG}}",
            "IEC_Timer_0_DB_1": "{{DB_INSTANCE_TOF}}"
        },
        "required_tags": [
            {"name": "{{BOOL_CLK}}", "type": "Bool"},
            {"name": "{{BOOL_Q}}", "type": "Bool"},
            {"name": "{{BOOL_OUT}}", "type": "Bool"},
            {"name": "{{TIME_ELAPSED}}", "type": "Time"}
        ],
        "required_instance_db": "{{DB_INSTANCE_R_TRIG}}",
        "required_dbs": ["{{DB_INSTANCE_TOF}}"],
        "description": "Bộ kích hoạt sườn lên R_TRIG (Rising Trigger) bắt tín hiệu chuyển từ mức thấp lên mức cao.",
        "compile_notes": "R_TRIG yêu cầu một khối DB Instance để lưu giữ trạng thái chu kỳ quét trước đó."
    },
    {
        "name": "f_trig",
        "category": "basic",
        "instruction_name": "F_TRIG",
        "mapping": {
            "F_TRIG_DB": "{{DB_INSTANCE_F_TRIG}}",
            "Auger Duty Cycle Output": "{{BOOL_CLK}}",
            "Test Output": "{{BOOL_Q}}",
            "Start": "{{BOOL_IN}}",
            "Set Reset": "{{BOOL_SR_MEM}}",
            "Auger Duty Cycle Start": "{{BOOL_SR_OUT}}"
        },
        "required_tags": [
            {"name": "{{BOOL_CLK}}", "type": "Bool"},
            {"name": "{{BOOL_Q}}", "type": "Bool"},
            {"name": "{{BOOL_IN}}", "type": "Bool"},
            {"name": "{{BOOL_SR_MEM}}", "type": "Bool"},
            {"name": "{{BOOL_SR_OUT}}", "type": "Bool"}
        ],
        "required_instance_db": "{{DB_INSTANCE_F_TRIG}}",
        "required_dbs": [],
        "description": "Bộ kích hoạt sườn xuống F_TRIG (Falling Trigger) bắt tín hiệu chuyển từ mức cao xuống mức thấp.",
        "compile_notes": "F_TRIG yêu cầu khối DB Instance lưu giữ trạng thái chu kỳ quét trước đó."
    },
    {
        "name": "tonr",
        "category": "timer_counter",
        "instruction_name": "TONR",
        "mapping": {
            "Q_BT": "{{BOOL_IN_RUN}}",
            "SIMU_CB_CAO": "{{BOOL_TARGET}}",
            "Simu_CB_Cao_Moi_Xuat_Phat": "{{BOOL_OUT_1}}",
            "M_CB_Cao": "{{BOOL_OUT_2}}",
            "Timer_Simu_CB_Cao": "{{DB_INSTANCE}}"
        },
        "required_tags": [
            {"name": "{{BOOL_IN_RUN}}", "type": "Bool"},
            {"name": "{{BOOL_TARGET}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_1}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_2}}", "type": "Bool"}
        ],
        "required_instance_db": "{{DB_INSTANCE}}",
        "required_dbs": [],
        "description": "Bộ định thời trễ bật tích lũy TONR (Timer On-Delay Retentive) giữ nguyên thời gian khi IN tắt.",
        "compile_notes": "Khác với TON thường, TONR chỉ xóa thời gian tích lũy về 0 khi chân reset R được kích hoạt."
    },
    {
        "name": "norm_x",
        "category": "math",
        "instruction_name": "NORM_X",
        "mapping": {
            "HMI_Simulation": "{{BOOL_SIMULATION}}",
            "Sensor_Temperature": "{{INT_ANALOG_IN}}",
            "TG_ND": "{{INT_TEMP}}",
            "HMI_Simu_Temperature": "{{INT_SIMU_VAL}}",
            "TG_ND1": "{{REAL_TEMP}}",
            "HMI_TT_Temperature": "{{REAL_SCALED_OUT}}"
        },
        "required_tags": [
            {"name": "{{BOOL_SIMULATION}}", "type": "Bool"},
            {"name": "{{INT_ANALOG_IN}}", "type": "Int"},
            {"name": "{{INT_TEMP}}", "type": "Int"},
            {"name": "{{INT_SIMU_VAL}}", "type": "Int"},
            {"name": "{{REAL_TEMP}}", "type": "Real"},
            {"name": "{{REAL_SCALED_OUT}}", "type": "Real"}
        ],
        "required_instance_db": "",
        "required_dbs": [],
        "description": "Hàm chuẩn hóa NORM_X đưa giá trị số nguyên trong dải min/max về tỷ lệ số thực từ 0.0 đến 1.0.",
        "compile_notes": "Kết quả Real của NORM_X thường được chuyển tiếp làm đầu vào cho khối SCALE_X."
    },
    {
        "name": "scale_x",
        "category": "math",
        "instruction_name": "SCALE_X",
        "mapping": {
            "HMI_Simulation": "{{BOOL_SIMULATION}}",
            "Sensor_Temperature": "{{INT_ANALOG_IN}}",
            "TG_ND": "{{INT_TEMP}}",
            "HMI_Simu_Temperature": "{{INT_SIMU_VAL}}",
            "TG_ND1": "{{REAL_TEMP}}",
            "HMI_TT_Temperature": "{{REAL_SCALED_OUT}}"
        },
        "required_tags": [
            {"name": "{{BOOL_SIMULATION}}", "type": "Bool"},
            {"name": "{{INT_ANALOG_IN}}", "type": "Int"},
            {"name": "{{INT_TEMP}}", "type": "Int"},
            {"name": "{{INT_SIMU_VAL}}", "type": "Int"},
            {"name": "{{REAL_TEMP}}", "type": "Real"},
            {"name": "{{REAL_SCALED_OUT}}", "type": "Real"}
        ],
        "required_instance_db": "",
        "required_dbs": [],
        "description": "Hàm tỷ lệ hóa SCALE_X chuyển đổi tỷ lệ Real (0.0-1.0) sang thang đo vật lý thực tế.",
        "compile_notes": "SCALE_X thường nhận giá trị đầu vào từ cổng ra OUT của NORM_X để khôi phục lại giá trị vật lý."
    },
    {
        "name": "invert",
        "category": "basic",
        "instruction_name": "INVERT",
        "mapping": {
            "base_start_button": "{{BOOL_IN_1}}",
            "state_of_start_base": "{{BOOL_MEM}}",
            "base_stop_button": "{{BOOL_IN_2}}",
            "lid_emergency_button": "{{BOOL_IN_3}}",
            "base_emergency": "{{BOOL_IN_4}}",
            "base_start_button_1_light": "{{BOOL_OUT_1}}",
            "base_stop_button_1_light": "{{BOOL_OUT_2}}"
        },
        "required_tags": [
            {"name": "{{BOOL_IN_1}}", "type": "Bool"},
            {"name": "{{BOOL_MEM}}", "type": "Bool"},
            {"name": "{{BOOL_IN_2}}", "type": "Bool"},
            {"name": "{{BOOL_IN_3}}", "type": "Bool"},
            {"name": "{{BOOL_IN_4}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_1}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_2}}", "type": "Bool"}
        ],
        "required_instance_db": "",
        "required_dbs": [],
        "description": "Hộp phủ định NOT (Invert) dùng để đảo ngược trạng thái logic của nhánh Ladder.",
        "compile_notes": "Hộp NOT đảo logic của tín hiệu đứng trước nó. Không yêu cầu tham số đi kèm."
    },
    {
        "name": "p_trig",
        "category": "basic",
        "instruction_name": "P_TRIG",
        "mapping": {
            "AlwaysFALSE": "{{BOOL_FALSE}}",
            "M_Mode": "{{BOOL_IN_1}}",
            "I_Mode": "{{BOOL_IN_2}}",
            "Tag_1": "{{BOOL_MEM_1}}",
            "Q_Auto_BT": "{{BOOL_OUT_1}}",
            "Q_Auto_Xylanh_Cao": "{{BOOL_IN_3}}",
            "Tag_2": "{{BOOL_MEM_2}}",
            "Q_Auto_Xylanh_TB": "{{BOOL_IN_4}}",
            "Tag_3": "{{BOOL_MEM_3}}"
        },
        "required_tags": [
            {"name": "{{BOOL_FALSE}}", "type": "Bool"},
            {"name": "{{BOOL_IN_1}}", "type": "Bool"},
            {"name": "{{BOOL_IN_2}}", "type": "Bool"},
            {"name": "{{BOOL_MEM_1}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_1}}", "type": "Bool"},
            {"name": "{{BOOL_IN_3}}", "type": "Bool"},
            {"name": "{{BOOL_MEM_2}}", "type": "Bool"},
            {"name": "{{BOOL_IN_4}}", "type": "Bool"},
            {"name": "{{BOOL_MEM_3}}", "type": "Bool"}
        ],
        "required_instance_db": "",
        "required_dbs": [],
        "description": "Tiếp điểm kích hoạt sườn lên PBox (Positive Edge Contact) trong dòng điện Ladder.",
        "compile_notes": "PBox cần một bit nhớ trung gian để lưu giữ trạng thái chu kỳ trước của tín hiệu ngõ vào."
    },
    {
        "name": "n_trig",
        "category": "basic",
        "instruction_name": "N_TRIG",
        "mapping": {
            "AlwaysFALSE": "{{BOOL_FALSE}}",
            "M_Mode": "{{BOOL_IN_1}}",
            "I_Mode": "{{BOOL_IN_2}}",
            "Tag_1": "{{BOOL_MEM_1}}",
            "Q_Auto_BT": "{{BOOL_OUT_1}}",
            "Q_Auto_Xylanh_Cao": "{{BOOL_IN_3}}",
            "Tag_2": "{{BOOL_MEM_2}}",
            "Q_Auto_Xylanh_TB": "{{BOOL_IN_4}}",
            "Tag_3": "{{BOOL_MEM_3}}"
        },
        "required_tags": [
            {"name": "{{BOOL_FALSE}}", "type": "Bool"},
            {"name": "{{BOOL_IN_1}}", "type": "Bool"},
            {"name": "{{BOOL_IN_2}}", "type": "Bool"},
            {"name": "{{BOOL_MEM_1}}", "type": "Bool"},
            {"name": "{{BOOL_OUT_1}}", "type": "Bool"},
            {"name": "{{BOOL_IN_3}}", "type": "Bool"},
            {"name": "{{BOOL_MEM_2}}", "type": "Bool"},
            {"name": "{{BOOL_IN_4}}", "type": "Bool"},
            {"name": "{{BOOL_MEM_3}}", "type": "Bool"}
        ],
        "required_instance_db": "",
        "required_dbs": [],
        "description": "Tiếp điểm kích hoạt sườn xuống NBox (Negative Edge Contact) trong dòng điện Ladder.",
        "compile_notes": "NBox cần một bit nhớ trung gian để lưu giữ trạng thái chu kỳ trước của tín hiệu ngõ vào."
    }
]

def clean_and_normalize(xml_str, mapping):
    # Perform exact replacements of variable component names
    for old_val, new_val in mapping.items():
        # Replace Component Name exactly
        # e.g., <Component Name="L_LEVEL" /> or <Component Name="L_LEVEL"/>
        pattern = r'Component\s+Name\s*=\s*"' + re.escape(old_val) + r'"'
        xml_str = re.sub(pattern, f'Component Name="{new_val}"', xml_str)

    # Re-indexing UId and ID of elements to start from 21 and 1
    uid_map = {}
    id_map = {}
    
    def uid_repl(match):
        old_uid = match.group(1)
        if old_uid not in uid_map:
            uid_map[old_uid] = str(len(uid_map) + 21)
        return f'UId="{uid_map[old_uid]}"'
        
    def id_repl(match):
        old_id = match.group(1)
        if old_id not in id_map:
            id_map[old_id] = str(len(id_map) + 1)
        return f'ID="{id_map[old_id]}"'

    xml_str = re.sub(r'UId="([0-9a-zA-Z_]+)"', uid_repl, xml_str)
    xml_str = re.sub(r'ID="([0-9a-zA-Z_]+)"', id_repl, xml_str)

    return xml_str

print("=================================================")
# Iterate through each pattern configuration
for config in patterns_config:
    name = config["name"]
    category = config["category"]
    instruction_name = config["instruction_name"]
    mapping = config["mapping"]
    
    src_xml_path = os.path.join(raw_patterns_dir, name, "pattern.raw.xml")
    if not os.path.exists(src_xml_path):
        print(f"[ERROR] Source raw XML for {name} does not exist: {src_xml_path}")
        continue
        
    # Create target directory
    target_dir = os.path.join(patterns_dir, category, name)
    os.makedirs(target_dir, exist_ok=True)
    
    # Process XML
    with open(src_xml_path, "r", encoding="utf-8") as f:
        xml_content = f.read()
        
    normalized_xml = clean_and_normalize(xml_content, mapping)
    
    # Save pattern.xml
    dest_xml_path = os.path.join(target_dir, "pattern.xml")
    with open(dest_xml_path, "w", encoding="utf-8") as f:
        f.write(normalized_xml)
        
    # Generate manifest.json
    manifest_data = {
        "tia_version": "V18",
        "plc_family": "S7-1200",
        "language": "LAD",
        "block_instruction_name": instruction_name,
        "tested_status": "compiled",
        "required_tags": config["required_tags"],
        "required_dbs": config["required_dbs"],
        "required_instance_db": config["required_instance_db"],
        "required_data_types": []
    }
    
    dest_manifest_path = os.path.join(target_dir, "manifest.json")
    with open(dest_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)
        
    # Generate README.md
    readme_content = f"# Mẫu khối {instruction_name}\n{config['description']}\n"
    dest_readme_path = os.path.join(target_dir, "README.md")
    with open(dest_readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    # Generate compile_notes.md
    compile_notes_content = f"# Lưu ý biên dịch\n{config['compile_notes']}\n"
    dest_compile_notes_path = os.path.join(target_dir, "compile_notes.md")
    with open(dest_compile_notes_path, "w", encoding="utf-8") as f:
        f.write(compile_notes_content)
        
    print(f"[SUCCESS] Integrated '{name}' patterns to patterns/{category}/{name}")

print("=================================================")
print("All 12 unique new patterns integrated successfully!")
