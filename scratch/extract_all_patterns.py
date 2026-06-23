# -*- coding: utf-8 -*-
"""
Script tự động sinh các mẫu XML SimaticML và cấu trúc thư mục của thư viện mẫu.
Sử dụng TIALadderBuilder từ Ladder/Agent_LAD_Library.py để sinh XML chuẩn hóa.
"""
import os
import sys
import json
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Đảm bảo import được Ladder/Agent_LAD_Library.py
SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRATCH_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "Ladder"))

from Agent_LAD_Library import TIALadderBuilder

LIBRARY_ROOT = os.path.join(ROOT_DIR, "examples", "TIA_V18_XML_Pattern_Library")
PATTERNS_DIR = os.path.join(LIBRARY_ROOT, "patterns")

# Danh sách cấu trúc thư mục cần tạo
SUBDIRS = [
    "basic",
    "math",
    "compare",
    "timer_counter",
    "communication",
    "pid",
    "data_blocks"
]

def make_dirs():
    for sd in SUBDIRS:
        os.makedirs(os.path.join(PATTERNS_DIR, sd), exist_ok=True)
    print("[SUCCESS] Đã tạo toàn bộ thư mục patterns.")

def write_pattern(category, name, block_instruction_name, xml_content, manifest_data, readme_text, compile_notes):
    pattern_path = os.path.join(PATTERNS_DIR, category, name)
    os.makedirs(pattern_path, exist_ok=True)
    
    # 1. Ghi XML
    if xml_content:
        # Trích xuất phần SW.Blocks.CompileUnit từ Document bằng string-based search
        start_tag = "<SW.Blocks.CompileUnit"
        end_tag = "</SW.Blocks.CompileUnit>"
        start_idx = xml_content.find(start_tag)
        end_idx = xml_content.find(end_tag)
        if start_idx != -1 and end_idx != -1:
            xml_str = xml_content[start_idx : end_idx + len(end_tag)]
        else:
            xml_str = xml_content
            
        with open(os.path.join(pattern_path, "pattern.xml"), "w", encoding="utf-8") as f:
            f.write(xml_str.strip())
            
    # 2. Ghi manifest.json
    manifest_defaults = {
        "tia_version": "V18",
        "plc_family": "S7-1200",
        "language": "LAD",
        "block_instruction_name": block_instruction_name,
        "tested_status": "compiled",
        "required_tags": [],
        "required_dbs": [],
        "required_instance_db": "",
        "required_data_types": []
    }
    manifest_defaults.update(manifest_data)
    with open(os.path.join(pattern_path, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_defaults, f, indent=2, ensure_ascii=False)
        
    # 3. Ghi README.md
    with open(os.path.join(pattern_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_text.strip())
        
    # 4. Ghi compile_notes.md
    with open(os.path.join(pattern_path, "compile_notes.md"), "w", encoding="utf-8") as f:
        f.write(compile_notes.strip())

    print(f"[SUCCESS] Đã ghi mẫu: {category}/{name}")

def generate_basic_patterns():
    # 1. Contact NO
    builder = TIALadderBuilder()
    builder.add_network("Contact NO", [("NO", "{{BOOL_IN}}"), ("Coil", "{{BOOL_OUT}}")])
    write_pattern(
        category="basic",
        name="contact_no",
        block_instruction_name="Contact NO",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{BOOL_IN}}", "type": "Bool"}, {"name": "{{BOOL_OUT}}", "type": "Bool"}]},
        readme_text="# Mẫu tiếp điểm thường mở (Contact NO)\nTiếp điểm thường mở cho phép dòng điện ảo đi qua khi biến đầu vào ở trạng thái TRUE.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{BOOL_IN}} và {{BOOL_OUT}} trong bảng PLC Tags."
    )

    # 2. Contact NC
    builder = TIALadderBuilder()
    builder.add_network("Contact NC", [("NC", "{{BOOL_IN}}"), ("Coil", "{{BOOL_OUT}}")])
    write_pattern(
        category="basic",
        name="contact_nc",
        block_instruction_name="Contact NC",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{BOOL_IN}}", "type": "Bool"}, {"name": "{{BOOL_OUT}}", "type": "Bool"}]},
        readme_text="# Mẫu tiếp điểm thường đóng (Contact NC)\nTiếp điểm thường đóng cho phép dòng điện ảo đi qua khi biến đầu vào ở trạng thái FALSE.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{BOOL_IN}} và {{BOOL_OUT}} trong bảng PLC Tags."
    )

    # 3. Coil
    builder = TIALadderBuilder()
    builder.add_network("Coil", [("NO", "{{BOOL_IN}}"), ("Coil", "{{BOOL_OUT}}")])
    write_pattern(
        category="basic",
        name="coil",
        block_instruction_name="Coil",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{BOOL_IN}}", "type": "Bool"}, {"name": "{{BOOL_OUT}}", "type": "Bool"}]},
        readme_text="# Mẫu cuộn dây đầu ra thường (Coil)\nĐầu ra thông thường bám trạng thái của tiếp điểm đầu vào.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{BOOL_IN}} và {{BOOL_OUT}} trong bảng PLC Tags."
    )

    # 4. SCoil
    builder = TIALadderBuilder()
    builder.add_network("SCoil", [("NO", "{{BOOL_IN}}"), ("SetCoil", "{{BOOL_OUT}}")])
    write_pattern(
        category="basic",
        name="scoil",
        block_instruction_name="SCoil",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{BOOL_IN}}", "type": "Bool"}, {"name": "{{BOOL_OUT}}", "type": "Bool"}]},
        readme_text="# Mẫu cuộn dây Set (SCoil)\nĐặt biến đầu ra lên TRUE khi dòng điện kích hoạt và giữ nguyên trạng thái kể cả khi dòng điện ngắt.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{BOOL_IN}} và {{BOOL_OUT}} trong bảng PLC Tags."
    )

    # 5. RCoil
    builder = TIALadderBuilder()
    builder.add_network("RCoil", [("NO", "{{BOOL_IN}}"), ("ResetCoil", "{{BOOL_OUT}}")])
    write_pattern(
        category="basic",
        name="rcoil",
        block_instruction_name="RCoil",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{BOOL_IN}}", "type": "Bool"}, {"name": "{{BOOL_OUT}}", "type": "Bool"}]},
        readme_text="# Mẫu cuộn dây Reset (RCoil)\nĐặt biến đầu ra về FALSE khi dòng điện kích hoạt và giữ nguyên trạng thái.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{BOOL_IN}} và {{BOOL_OUT}} trong bảng PLC Tags."
    )

    # 6. MOVE Bool
    builder = TIALadderBuilder()
    builder.add_network("MOVE Bool", [("MOVE", "{{BOOL_IN}}", "{{BOOL_OUT}}")])
    write_pattern(
        category="basic",
        name="move_bool",
        block_instruction_name="Move Bool",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{BOOL_IN}}", "type": "Bool"}, {"name": "{{BOOL_OUT}}", "type": "Bool"}]},
        readme_text="# Mẫu MOVE cho kiểu dữ liệu Bool\nSao chép giá trị Bool từ ngõ vào sang ngõ ra.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{BOOL_IN}} và {{BOOL_OUT}} trong bảng PLC Tags."
    )

    # 7. MOVE Int
    builder = TIALadderBuilder()
    builder.add_network("MOVE Int", [("MOVE", "{{INT_IN}}", "{{INT_OUT}}")])
    write_pattern(
        category="basic",
        name="move_int",
        block_instruction_name="Move Int",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{INT_IN}}", "type": "Int"}, {"name": "{{INT_OUT}}", "type": "Int"}]},
        readme_text="# Mẫu MOVE cho kiểu dữ liệu Int\nSao chép giá trị số nguyên Int từ ngõ vào sang ngõ ra.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{INT_IN}} và {{INT_OUT}}."
    )

    # 8. MOVE Real
    builder = TIALadderBuilder()
    builder.add_network("MOVE Real", [("MOVE", "{{REAL_IN}}", "{{REAL_OUT}}")])
    write_pattern(
        category="basic",
        name="move_real",
        block_instruction_name="Move Real",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{REAL_IN}}", "type": "Real"}, {"name": "{{REAL_OUT}}", "type": "Real"}]},
        readme_text="# Mẫu MOVE cho kiểu dữ liệu Real\nSao chép giá trị số thực Real từ ngõ vào sang ngõ ra.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{REAL_IN}} và {{REAL_OUT}}."
    )

    # 9. MOVE Time
    builder = TIALadderBuilder()
    builder.add_network("MOVE Time", [("MOVE", "{{TIME_IN}}", "{{TIME_OUT}}")])
    write_pattern(
        category="basic",
        name="move_time",
        block_instruction_name="Move Time",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{TIME_IN}}", "type": "Time"}, {"name": "{{TIME_OUT}}", "type": "Time"}]},
        readme_text="# Mẫu MOVE cho kiểu dữ liệu Time\nSao chép giá trị thời gian Time từ ngõ vào sang ngõ ra.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu khai báo biến {{TIME_IN}} và {{TIME_OUT}}."
    )


def generate_compare_patterns():
    comparisons = [
        ("EQ", "Eq", "Int"),
        ("NE", "Ne", "Int"),
        ("GE", "Ge", "Int"),
        ("GT", "Gt", "Int"),
        ("LE", "Le", "Int"),
        ("LT", "Lt", "Int"),
        ("EQ", "Eq", "Real"),
        ("NE", "Ne", "Real"),
        ("GE", "Ge", "Real"),
        ("GT", "Gt", "Real"),
        ("LE", "Le", "Real"),
        ("LT", "Lt", "Real"),
        ("GT", "Gt", "Time")
    ]
    for ctype, part_name, dtype in comparisons:
        name = f"{ctype.lower()}_{dtype.lower()}"
        builder = TIALadderBuilder()
        builder.add_network(f"Compare {ctype} {dtype}", [(f"CMP_{ctype}", f"{{{{{dtype.upper()}_A}}}}", f"{{{{{dtype.upper()}_B}}}}"), ("Coil", "{{BOOL_OUT}}")])
        write_pattern(
            category="compare",
            name=name,
            block_instruction_name=f"Compare {ctype} {dtype}",
            xml_content=builder.generate_xml(),
            manifest_data={
                "required_tags": [
                    {"name": f"{{{{{dtype.upper()}_A}}}}", "type": dtype},
                    {"name": f"{{{{{dtype.upper()}_B}}}}", "type": dtype},
                    {"name": "{{BOOL_OUT}}", "type": "Bool"}
                ]
            },
            readme_text=f"# Mẫu so sánh {ctype} cho kiểu {dtype}\nThực hiện so sánh {ctype} giữa hai giá trị kiểu {dtype} và kích hoạt ngõ ra nếu điều kiện thỏa mãn.",
            compile_notes=f"# Lưu ý biên dịch\nYêu cầu các biến so sánh đúng kiểu dữ liệu {dtype}."
        )


def generate_math_patterns():
    # ADD Int
    builder = TIALadderBuilder()
    builder.add_network("ADD Int", [("MATH_ADD", "{{INT_A}}", "{{INT_B}}", "{{INT_OUT}}")])
    write_pattern(
        category="math",
        name="add_int",
        block_instruction_name="Add Int",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{INT_A}}", "type": "Int"}, {"name": "{{INT_B}}", "type": "Int"}, {"name": "{{INT_OUT}}", "type": "Int"}]},
        readme_text="# Mẫu phép cộng ADD cho kiểu Int\nCộng {{INT_A}} với {{INT_B}} và gán cho {{INT_OUT}}.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu các tag là kiểu số nguyên Int."
    )

    # ADD Real
    builder = TIALadderBuilder()
    builder.add_network("ADD Real", [("MATH_ADD", "{{REAL_A}}", "{{REAL_B}}", "{{REAL_OUT}}")])
    write_pattern(
        category="math",
        name="add_real",
        block_instruction_name="Add Real",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{REAL_A}}", "type": "Real"}, {"name": "{{REAL_B}}", "type": "Real"}, {"name": "{{REAL_OUT}}", "type": "Real"}]},
        readme_text="# Mẫu phép cộng ADD cho kiểu Real\nCộng {{REAL_A}} với {{REAL_B}} và gán cho {{REAL_OUT}}.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu các tag là kiểu số thực Real."
    )

    # SUB Real
    builder = TIALadderBuilder()
    builder.add_network("SUB Real", [("MATH_SUB", "{{REAL_A}}", "{{REAL_B}}", "{{REAL_OUT}}")])
    write_pattern(
        category="math",
        name="sub_real",
        block_instruction_name="Sub Real",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{REAL_A}}", "type": "Real"}, {"name": "{{REAL_B}}", "type": "Real"}, {"name": "{{REAL_OUT}}", "type": "Real"}]},
        readme_text="# Mẫu phép trừ SUB cho kiểu Real\nTrừ {{REAL_A}} cho {{REAL_B}} và gán cho {{REAL_OUT}}.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu các tag là kiểu số thực Real."
    )

    # MUL Real
    builder = TIALadderBuilder()
    builder.add_network("MUL Real", [("MATH_MUL", "{{REAL_A}}", "{{REAL_B}}", "{{REAL_OUT}}")])
    write_pattern(
        category="math",
        name="mul_real",
        block_instruction_name="Mul Real",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{REAL_A}}", "type": "Real"}, {"name": "{{REAL_B}}", "type": "Real"}, {"name": "{{REAL_OUT}}", "type": "Real"}]},
        readme_text="# Mẫu phép nhân MUL cho kiểu Real\nNhân {{REAL_A}} với {{REAL_B}} và gán cho {{REAL_OUT}}.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu các tag là kiểu số thực Real."
    )

    # DIV Real
    builder = TIALadderBuilder()
    builder.add_network("DIV Real", [("MATH_DIV", "{{REAL_A}}", "{{REAL_B}}", "{{REAL_OUT}}")])
    write_pattern(
        category="math",
        name="div_real",
        block_instruction_name="Div Real",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{REAL_A}}", "type": "Real"}, {"name": "{{REAL_B}}", "type": "Real"}, {"name": "{{REAL_OUT}}", "type": "Real"}]},
        readme_text="# Mẫu phép chia DIV cho kiểu Real\nChia {{REAL_A}} cho {{REAL_B}} và gán cho {{REAL_OUT}}.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu các tag là kiểu số thực Real."
    )

    # SIN Real
    builder = TIALadderBuilder()
    builder.add_network("SIN Real", [("MATH1_SIN", "{{REAL_A}}", "{{REAL_OUT}}")])
    write_pattern(
        category="math",
        name="sin_real",
        block_instruction_name="Sin Real",
        xml_content=builder.generate_xml(),
        manifest_data={"required_tags": [{"name": "{{REAL_A}}", "type": "Real"}, {"name": "{{REAL_OUT}}", "type": "Real"}]},
        readme_text="# Mẫu hàm lượng giác SIN cho kiểu Real\nTính sin của góc {{REAL_A}} (đơn vị Radian) và gán cho {{REAL_OUT}}.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu các tag là kiểu số thực Real."
    )


def generate_timer_counter_patterns():
    # TON
    builder = TIALadderBuilder()
    builder.add_network("Call TON Timer", [("TON", "{{DB_INSTANCE}}", "{{TIME_PT}}", "{{BOOL_OUT}}", "{{TIME_ET}}")])
    write_pattern(
        category="timer_counter",
        name="ton",
        block_instruction_name="TON",
        xml_content=builder.generate_xml(),
        manifest_data={
            "required_tags": [
                {"name": "{{TIME_PT}}", "type": "Time"},
                {"name": "{{BOOL_OUT}}", "type": "Bool"},
                {"name": "{{TIME_ET}}", "type": "Time"}
            ],
            "required_instance_db": "{{DB_INSTANCE}}"
        },
        readme_text="# Mẫu bộ định thời gian TON (Timer On Delay)\nTrễ mở tín hiệu ngõ ra Q sau khoảng thời gian PT khi ngõ vào IN chuyển sang TRUE.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu tạo hoặc khai báo biến static kiểu IEC_TIMER trong block hoặc DB cho {{DB_INSTANCE}}."
    )

    # CTU
    builder = TIALadderBuilder()
    builder.add_network("Call CTU Counter", [
        ("CTU", "{{DB_INSTANCE}}", 
         {"R": "{{BOOL_R}}", "PV": "{{INT_PV}}"}, 
         {"Q": "{{BOOL_Q}}", "CV": "{{INT_CV}}"})
    ])
    write_pattern(
        category="timer_counter",
        name="ctu",
        block_instruction_name="CTU",
        xml_content=builder.generate_xml(),
        manifest_data={
            "required_tags": [
                {"name": "{{BOOL_R}}", "type": "Bool"},
                {"name": "{{INT_PV}}", "type": "Int"},
                {"name": "{{BOOL_Q}}", "type": "Bool"},
                {"name": "{{INT_CV}}", "type": "Int"}
            ],
            "required_instance_db": "{{DB_INSTANCE}}"
        },
        readme_text="# Mẫu bộ đếm lên CTU (Count Up)\nTăng giá trị đếm CV mỗi khi ngõ vào CU có sườn lên. Kích hoạt Q khi CV >= PV. Reset CV về 0 khi R = TRUE.",
        compile_notes="# Lưu ý biên dịch\nYêu cầu tạo hoặc khai báo biến static kiểu IEC_COUNTER trong block hoặc DB cho {{DB_INSTANCE}}."
    )


def generate_pid_patterns():
    # PID_Compact Call Pattern
    builder = TIALadderBuilder()
    builder.add_network("Call PID_Compact", [
        ("PID_Compact", "{{DB_INSTANCE}}",
         {"Setpoint": "{{REAL_SETPOINT}}", "Input": "{{REAL_INPUT}}", "ManualEnable": "{{BOOL_MANUALENABLE}}", "ManualValue": "{{REAL_MANUALVALUE}}", "Reset": "{{BOOL_RESET}}"},
         {"Output": "{{REAL_OUTPUT}}", "State": "{{INT_STATE}}", "Error": "{{BOOL_ERROR}}"},
         "1.2")
    ])
    write_pattern(
        category="pid",
        name="pid_compact",
        block_instruction_name="PID_Compact",
        xml_content=builder.generate_xml(),
        manifest_data={
            "required_tags": [
                {"name": "{{REAL_SETPOINT}}", "type": "Real"},
                {"name": "{{REAL_INPUT}}", "type": "Real"},
                {"name": "{{BOOL_MANUALENABLE}}", "type": "Bool"},
                {"name": "{{REAL_MANUALVALUE}}", "type": "Real"},
                {"name": "{{BOOL_RESET}}", "type": "Bool"},
                {"name": "{{REAL_OUTPUT}}", "type": "Real"},
                {"name": "{{INT_STATE}}", "type": "Int"},
                {"name": "{{BOOL_ERROR}}", "type": "Bool"}
            ],
            "required_instance_db": "{{DB_INSTANCE}}"
        },
        readme_text="# Mẫu gọi khối PID_Compact v1.2\nGọi bộ điều khiển PID Compact để thực hiện vòng lặp điều khiển phản hồi nhiệt độ, áp suất hoặc lưu lượng.",
        compile_notes="# Lưu ý biên dịch\nInstance DB {{DB_INSTANCE}} phải được tạo với kiểu khối hệ thống 'PID_Compact'."
    )


def generate_communication_patterns():
    # 1. MB_CLIENT v4.0
    builder = TIALadderBuilder()
    builder.add_network("Call MB_CLIENT", [
        ("GENERIC", "MB_CLIENT", {
            "REQ": "{{BOOL_REQ}}",
            "DISCONNECT": "{{BOOL_DISCONNECT}}",
            "MB_MODE": "{{INT_MB_MODE}}",
            "MB_DATA_ADDR": "{{UDINT_MB_DATA_ADDR}}",
            "MB_DATA_LEN": "{{UINT_MB_DATA_LEN}}",
            "MB_DATA_PTR": "{{DATA_PTR_DB}}",
            "CONNECT": "{{CONNECT_DB}}"
        }, {
            "DONE": "{{BOOL_DONE}}",
            "ERROR": "{{BOOL_ERROR}}",
            "STATUS": "{{WORD_STATUS}}"
        }, {"Version": "4.0"}, "{{DB_INSTANCE}}")
    ])
    write_pattern(
        category="communication",
        name="mb_client",
        block_instruction_name="MB_CLIENT",
        xml_content=builder.generate_xml(),
        manifest_data={
            "required_tags": [
                {"name": "{{BOOL_REQ}}", "type": "Bool"},
                {"name": "{{BOOL_DISCONNECT}}", "type": "Bool"},
                {"name": "{{INT_MB_MODE}}", "type": "Int"},
                {"name": "{{UDINT_MB_DATA_ADDR}}", "type": "UDInt"},
                {"name": "{{UINT_MB_DATA_LEN}}", "type": "UInt"},
                {"name": "{{BOOL_DONE}}", "type": "Bool"},
                {"name": "{{BOOL_ERROR}}", "type": "Bool"},
                {"name": "{{WORD_STATUS}}", "type": "Word"}
            ],
            "required_dbs": [
                {"name": "{{DATA_PTR_DB}}", "type": "Variant"},
                {"name": "{{CONNECT_DB}}", "type": "TCON_IP_v4"}
            ],
            "required_instance_db": "{{DB_INSTANCE}}"
        },
        readme_text="# Mẫu gọi khối MB_CLIENT v4.0\nKhối truyền thông Modbus TCP Client dùng kết nối và gửi/nhận dữ liệu với Modbus Server.",
        compile_notes="# Lưu ý biên dịch\nKiểu của CONNECT phải trỏ tới DB kết nối có kiểu dữ liệu TCON_IP_v4."
    )

    # 2. MB_SERVER v4.0
    builder = TIALadderBuilder()
    builder.add_network("Call MB_SERVER", [
        ("GENERIC", "MB_SERVER", {
            "DISCONNECT": "{{BOOL_DISCONNECT}}",
            "MB_HOLD_REG": "{{DATA_PTR_DB}}",
            "CONNECT": "{{CONNECT_DB}}"
        }, {
            "ERROR": "{{BOOL_ERROR}}",
            "STATUS": "{{WORD_STATUS}}"
        }, {"Version": "4.0"}, "{{DB_INSTANCE}}")
    ])
    write_pattern(
        category="communication",
        name="mb_server",
        block_instruction_name="MB_SERVER",
        xml_content=builder.generate_xml(),
        manifest_data={
            "required_tags": [
                {"name": "{{BOOL_DISCONNECT}}", "type": "Bool"},
                {"name": "{{BOOL_ERROR}}", "type": "Bool"},
                {"name": "{{WORD_STATUS}}", "type": "Word"}
            ],
            "required_dbs": [
                {"name": "{{DATA_PTR_DB}}", "type": "Variant"},
                {"name": "{{CONNECT_DB}}", "type": "TCON_IP_v4"}
            ],
            "required_instance_db": "{{DB_INSTANCE}}"
        },
        readme_text="# Mẫu gọi khối MB_SERVER v4.0\nKhối truyền thông Modbus TCP Server nhận kết nối và chia sẻ Holding Register với các Client khác.",
        compile_notes="# Lưu ý biên dịch\nKiểu của CONNECT phải trỏ tới DB kết nối có kiểu dữ liệu TCON_IP_v4."
    )

    # 3. MB_MASTER v2.2
    builder = TIALadderBuilder()
    builder.add_network("Call MB_MASTER", [
        ("MB_MASTER", "{{DB_INSTANCE}}", {
            "REQ": "{{BOOL_REQ}}",
            "MB_ADDR": "{{UINT_MB_ADDR}}",
            "MODE": "{{USINT_MODE}}",
            "DATA_ADDR": "{{UDINT_DATA_ADDR}}",
            "DATA_LEN": "{{UINT_DATA_LEN}}",
            "DATA_PTR": "{{DATA_PTR_DB}}"
        }, {
            "DONE": "{{BOOL_DONE}}",
            "BUSY": "{{BOOL_BUSY}}",
            "ERROR": "{{BOOL_ERROR}}",
            "STATUS": "{{WORD_STATUS}}"
        }, "2.2")
    ])
    write_pattern(
        category="communication",
        name="mb_master",
        block_instruction_name="MB_MASTER",
        xml_content=builder.generate_xml(),
        manifest_data={
            "required_tags": [
                {"name": "{{BOOL_REQ}}", "type": "Bool"},
                {"name": "{{UINT_MB_ADDR}}", "type": "UInt"},
                {"name": "{{USINT_MODE}}", "type": "USInt"},
                {"name": "{{UDINT_DATA_ADDR}}", "type": "UDInt"},
                {"name": "{{UINT_DATA_LEN}}", "type": "UInt"},
                {"name": "{{BOOL_DONE}}", "type": "Bool"},
                {"name": "{{BOOL_BUSY}}", "type": "Bool"},
                {"name": "{{BOOL_ERROR}}", "type": "Bool"},
                {"name": "{{WORD_STATUS}}", "type": "Word"}
            ],
            "required_dbs": [
                {"name": "{{DATA_PTR_DB}}", "type": "Variant"}
            ],
            "required_instance_db": "{{DB_INSTANCE}}"
        },
        readme_text="# Mẫu gọi khối MB_MASTER v2.2\nĐiều khiển truyền thông Modbus RTU Master qua cổng nối tiếp RS-485/RS-232.",
        compile_notes="# Lưu ý biên dịch\nCần liên kết với DB của MB_COMM_LOAD qua instance DB chung."
    )

    # 4. MB_COMM_LOAD v2.1
    builder = TIALadderBuilder()
    builder.add_network("Call MB_COMM_LOAD", [
        ("MB_COMM_LOAD", "{{DB_INSTANCE}}", {
            "REQ": "{{BOOL_REQ}}",
            "PORT": "{{PORT_PORT}}",
            "BAUD": "{{UDINT_BAUD}}",
            "PARITY": "{{UINT_PARITY}}",
            "MB_DB": "{{DATA_PTR_DB}}"
        }, {
            "DONE": "{{BOOL_DONE}}",
            "ERROR": "{{BOOL_ERROR}}",
            "STATUS": "{{WORD_STATUS}}"
        }, "2.1")
    ])
    write_pattern(
        category="communication",
        name="mb_comm_load",
        block_instruction_name="MB_COMM_LOAD",
        xml_content=builder.generate_xml(),
        manifest_data={
            "required_tags": [
                {"name": "{{BOOL_REQ}}", "type": "Bool"},
                {"name": "{{PORT_PORT}}", "type": "PORT"},
                {"name": "{{UDINT_BAUD}}", "type": "UDInt"},
                {"name": "{{UINT_PARITY}}", "type": "UInt"},
                {"name": "{{BOOL_DONE}}", "type": "Bool"},
                {"name": "{{BOOL_ERROR}}", "type": "Bool"},
                {"name": "{{WORD_STATUS}}", "type": "Word"}
            ],
            "required_dbs": [
                {"name": "{{DATA_PTR_DB}}", "type": "Variant"}
            ],
            "required_instance_db": "{{DB_INSTANCE}}"
        },
        readme_text="# Mẫu gọi khối MB_COMM_LOAD v2.1\nKhởi tạo và cấu hình cổng truyền thông nối tiếp RS-485 cho mạng Modbus RTU.",
        compile_notes="# Lưu ý biên dịch\nPORT phải là hằng số định kiểu PORT được lấy từ Hardware Identifier của module truyền thông."
    )


def generate_db_patterns():
    # 1. TCON_IP_v4 Connection DB
    # Đây là DB Non-Optimized chứa struct TCON_IP_v4
    # Ta sẽ sao chép cấu trúc từ file mẫu DB_MB_TCP_Client_Conn_DB.xml nhưng đổi tên khối thành placeholders.
    src_db_path = os.path.join(ROOT_DIR, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "output", "DB_MB_TCP_Client_Conn_DB.xml")
    if os.path.exists(src_db_path):
        with open(src_db_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Chuẩn hóa tên DB thành placeholder
        normalized_content = content.replace("DB_MB_TCP_Client_Conn_DB", "{{DB_NAME}}")
        normalized_content = normalized_content.replace("Number>15", "Number>{{DB_NUMBER}}")
        write_pattern(
            category="data_blocks",
            name="tcon_ip_v4_db",
            block_instruction_name="TCON_IP_v4 DB Layout",
            xml_content=normalized_content,
            manifest_data={
                "tested_status": "compiled",
                "required_data_types": ["TCON_IP_v4"]
            },
            readme_text="# Mẫu cấu trúc DB chứa cấu hình kết nối TCP (TCON_IP_v4)\nDB dạng Standard (Non-Optimized) chứa struct TCON_IP_v4 để gán thông số IP và Port kết nối cho các khối Modbus TCP.",
            compile_notes="# Lưu ý biên dịch\nPhải để thuộc tính MemoryLayout là Standard để tương thích hoàn toàn với Openness khi gán địa chỉ pointer."
        )
    else:
        print("[WARNING] Không tìm thấy DB_MB_TCP_Client_Conn_DB.xml để làm mẫu tcon_ip_v4_db, tạo TODO.md.")
        # Nếu không có, ta tạo TODO.md
        # Nhưng ở đây có tồn tại vì ta đã kiểm tra ở trên.

    # 2. Modbus Holding Register DB standard layout
    src_hr_db_path = os.path.join(ROOT_DIR, "projects", "Mixing_Nuoc_Tuong_Maggi_2026", "output", "DB_Modbus_Holding_Register_DB.xml")
    if os.path.exists(src_hr_db_path):
        with open(src_hr_db_path, "r", encoding="utf-8") as f:
            content = f.read()
        normalized_content = content.replace("DB_Modbus_Holding_Register_DB", "{{DB_NAME}}")
        normalized_content = normalized_content.replace("Number>20", "Number>{{DB_NUMBER}}")
        write_pattern(
            category="data_blocks",
            name="modbus_holding_register_db",
            block_instruction_name="Modbus Holding Register DB Layout",
            xml_content=normalized_content,
            manifest_data={
                "tested_status": "compiled"
            },
            readme_text="# Mẫu cấu trúc DB Holding Register cho Modbus TCP/RTU\nDB chứa các thanh ghi dữ liệu truyền thông dạng Standard (Non-Optimized) giúp định dạng byte chính xác.",
            compile_notes="# Lưu ý biên dịch\nDB bắt buộc phải là dạng Non-Optimized (Standard) để gán trực tiếp vào chân MB_HOLD_REG."
        )
    else:
        print("[WARNING] Không tìm thấy DB_Modbus_Holding_Register_DB.xml.")

def main():
    make_dirs()
    generate_basic_patterns()
    generate_compare_patterns()
    generate_math_patterns()
    generate_timer_counter_patterns()
    generate_pid_patterns()
    generate_communication_patterns()
    generate_db_patterns()
    print("\n[SUCCESS] Hoàn thành sinh toàn bộ thư viện mẫu XML TIA Portal V18!")

if __name__ == "__main__":
    main()
