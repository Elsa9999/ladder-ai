# -*- coding: utf-8 -*-
import re
from pathlib import Path

gen_path = Path(r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py")
content = gen_path.read_text(encoding="utf-8")

# 2. Add GET/PUT status and PLC2 button tags to define_tags()
insert_marker = "    # Modbus RTU tags for VFD Bon 2 (PLC1)"
tags_to_insert = """    # S7 Connection (GET/PUT) Status and Recv tags for PLC1
    add_tag("AI_GET_NDR", "Bool", internal_bool.next(), "GET Done/NDR status", "PLC1", "Comm")
    add_tag("AI_GET_Error", "Bool", internal_bool.next(), "GET Error status", "PLC1", "Comm")
    add_tag("AI_GET_Status", "Word", internal_int.next(), "GET Status code", "PLC1", "Comm")
    add_tag("AI_PUT_Done", "Bool", internal_bool.next(), "PUT Done status", "PLC1", "Comm")
    add_tag("AI_PUT_Error", "Bool", internal_bool.next(), "PUT Error status", "PLC1", "Comm")
    add_tag("AI_PUT_Status", "Word", internal_int.next(), "PUT Status code", "PLC1", "Comm")

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

if insert_marker in content and "AI_GET_NDR" not in content:
    content = content.replace(insert_marker, tags_to_insert + insert_marker)
    print("Inserted S7 Comm and PLC2 received tags.")
else:
    print("Tags already present or marker not found.")

gen_path.write_text(content, encoding="utf-8")
print("Done.")
