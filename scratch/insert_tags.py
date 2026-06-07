# -*- coding: utf-8 -*-
from pathlib import Path

gen_path = Path(r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py")
content = gen_path.read_text(encoding="utf-8")

insert_marker = "    # Modbus RTU tags for VFD Bon 2 (PLC1)"
tags_to_insert = """    # S7 Connection (GET/PUT) Status and Recv tags for PLC1
    add_tag("AI_PID_Bon4_SP_Recv", "Real", internal_real.next(), "PID Bồn 4 Setpoint nhận từ PLC2", "PLC1", "Comm")
    add_tag("AI_PID_Bon4_PV_Recv", "Real", internal_real.next(), "PID Bồn 4 Process Value nhận từ PLC2", "PLC1", "Comm")
    add_tag("AI_PID_Bon4_CV_Recv", "Real", internal_real.next(), "PID Bồn 4 Control Value nhận từ PLC2", "PLC1", "Comm")
    add_tag("AI_PLC2_State_Recv", "Int", internal_int.next(), "Trạng thái hoạt động PLC2 nhận từ PLC2", "PLC1", "Comm")
    add_tag("AI_PLC2_Loi_Tong_Recv", "Bool", internal_bool.next(), "Cờ lỗi tổng PLC2 nhận từ PLC2", "PLC1", "Comm")

    # Recv Button tags for PLC2 (received from PLC1)
    def add_recv_button(name_recv: str, comment_recv: str) -> None:
        add_tag(name_recv, "Bool", internal_bool.next(), comment_recv, "PLC2", "Comm")
        add_tag(name_recv + "_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI song song cho " + comment_recv, "PLC2", "Comm")
        add_tag(name_recv + "_HMI_Gated", "Bool", internal_bool.next(), "Tín hiệu HMI đã qua xử lý chế độ cho " + comment_recv, "PLC2", "Comm")
        add_tag(name_recv + "_Eff", "Bool", internal_bool.next(), "Tín hiệu thực tế/mô phỏng hiệu dụng cho " + comment_recv, "PLC2", "Comm")

    add_recv_button("AI_Nut_Khoi_Dong_Nhan", "nút khởi động nhận từ PLC1")
    add_recv_button("AI_Nut_Dung_Nhan", "nút dừng nhận từ PLC1")
    add_recv_button("AI_Nut_Reset_Nhan", "nút reset nhận từ PLC1")
    add_recv_button("AI_Nut_EStop_Nhan", "nút dừng khẩn nhận từ PLC1")

"""

if "AI_Nut_Khoi_Dong_Nhan" not in content or "add_recv_button" not in content:
    if insert_marker in content:
        content = content.replace(insert_marker, tags_to_insert + insert_marker)
        print("Successfully inserted received tags in define_tags().")
    else:
        print("Error: insert_marker not found in content!")
else:
    print("Tags already exist in define_tags().")

gen_path.write_text(content, encoding="utf-8")
