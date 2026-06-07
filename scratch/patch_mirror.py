# -*- coding: utf-8 -*-
from pathlib import Path

gen_path = Path(r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py")
content = gen_path.read_text(encoding="utf-8")

# 1. Tách build_hmi_mirror thành build_hmi_mirror_plc1 và build_hmi_mirror_plc2
split_mirror_functions = """def build_hmi_mirror_plc1() -> str:
    fc = TIALadderBuilder(fb_name="FC_HMI_Mirror_PLC1", block_id="40", block_type="FC")
    # Lọc mirror ngõ ra của PLC1 và Bồn chứa/lọc
    for out_name, mirror_name, dtype in physical_outputs:
        # Tìm tag tương ứng để kiểm tra PLC
        tag_plc = "PLC1"
        for t in tags:
            if t.name == out_name:
                tag_plc = t.plc
                break
        if tag_plc in ("PLC1", "Shared"):
            if dtype == "Bool":
                fc.add_network(f"Mirror {out_name}", [("NO", out_name), ("Coil", mirror_name)])
            else:
                fc.add_network(f"Mirror {out_name}", [("MOVE", out_name, mirror_name)])

    fc.add_network("Quyền Operator", [("NO", "AI_HMI_Operator_Login"), ("MOVE", "1", "AI_HMI_User_Level")])
    fc.add_network("Quyền Engineer", [("NO", "AI_HMI_Engineer_Login"), ("MOVE", "2", "AI_HMI_User_Level")])
    fc.add_network("Quyền Admin", [("NO", "AI_HMI_Admin_Login"), ("MOVE", "3", "AI_HMI_User_Level")])
    fc.add_network("Cho phép sửa thông số Engineer", [("NO", "AI_HMI_Engineer_Login"), ("SetCoil", "AI_HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Cho phép sửa thông số Admin", [("NO", "AI_HMI_Admin_Login"), ("SetCoil", "AI_HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Operator không được sửa thông số", [("NO", "AI_HMI_Operator_Login"), ("ResetCoil", "AI_HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Mã an toàn mặc định", [("MOVE", "0", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã cảnh báo dosing PLC1", [("NO", "AI_PLC1_Loi_Dosing"), ("MOVE", "1", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã lỗi Setpoint PLC1 không hợp lệ", [("NO", "AI_PLC1_Loi_Setpoint"), ("MOVE", "2", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã lỗi Setpoint Bồn chứa không hợp lệ", [("NO", "AI_BonChua_Loi_Setpoint"), ("MOVE", "2", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã lỗi dry run PLC1", [("NO", "AI_PLC1_Loi_Dry_Run"), ("MOVE", "3", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã E-Stop ưu tiên cao PLC1", [("NO", "AI_PLC1_EStop_Latch"), ("MOVE", "4", "AI_HMI_AnToan_Status")])
    fc.add_network("Còi báo động khi lỗi hoặc mất truyền thông PLC1", [
        ("OR2", "AI_PLC1_Loi_Tong", "AI_PLC2_Loi_Tong_Recv"),
        ("SetCoil", "AI_Coi_Bao_Dong"),
    ])
    fc.add_network("Tắt còi khi Ack Alarm", [("NO", "AI_HMI_Ack_Alarm"), ("ResetCoil", "AI_Coi_Bao_Dong")])

    # --- Trạng thái hiển thị chế độ hệ thống ---
    fc.add_network("Trạng thái hiển thị chế độ chạy thật", [("NC", "AI_HMI_Sim_Mode"), ("Coil", "AI_System_Mode_Real")])
    fc.add_network("Trạng thái hiển thị chế độ mô phỏng", [("NO", "AI_HMI_Sim_Mode"), ("Coil", "AI_System_Mode_Sim")])
    fc.add_network("Cảnh báo chế độ mô phỏng HMI active", [("NO", "AI_HMI_Sim_Mode"), ("Coil", "AI_HMI_Sim_Active_Warning")])

    # --- Dọn dẹp tín hiệu mô phỏng khi ở chế độ chạy thật (Sim_Mode = FALSE) ---
    # Digital sensors PLC1:
    for tag in [
        "AI_LS3202_Bon1_Cao_HMI", "AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_HMI",
        "AI_LSH3310_Pheu_Cao_HMI", "AI_LSL3311_Pheu_Thap_HMI",
        "AI_PLC1_Load_Default_Done_Nhan_HMI"
    ]:
        fc.add_network(f"Reset {tag} khi ở chế độ chạy thật", [("NC", "AI_HMI_Sim_Mode"), ("ResetCoil", tag)])

    # Analog sensors PLC1:
    for tag in [
        "AI_FT3200_Bon1_HMI", "AI_FQ3200_Bon1_HMI", "AI_LT3203_Bon1_HMI", "AI_TT3204_Bon1_HMI",
        "AI_FT3205_Bon2_HMI", "AI_LT3209_Bon2_HMI", "AI_TT3208_Bon2_HMI",
        "AI_LT3302_BonChua1_HMI", "AI_TT3301_BonChua1_HMI", "AI_TT3303_TraoDoiNhiet_HMI",
        "AI_LT3307_BonChua2_HMI", "AI_TT3306_BonChua2_HMI", "AI_PI3308_Truoc_Filter_HMI",
        "AI_FT3309_Xa_Thanh_Pham_HMI"
    ]:
        fc.add_network(f"Reset {tag} về 0.0 khi ở chế độ chạy thật", [("NC", "AI_HMI_Sim_Mode"), ("MOVE", "0.0", tag)])

    # Mô phỏng truyền thông GET/PUT offline trên PLC1
    fc.add_network("Mô phỏng truyền thông GET/PUT: Link Done nạp recipe PLC2 sang PLC1_HMI", [
        ("NO", "AI_HMI_Sim_Mode"),
        ("NO", "AI_PLC1_Load_Default_Cmd"),
        ("Coil", "AI_PLC1_Load_Default_Done_Nhan_HMI"),
    ])

    return fc.generate_xml()


def build_hmi_mirror_plc2() -> str:
    fc = TIALadderBuilder(fb_name="FC_HMI_Mirror_PLC2", block_id="41", block_type="FC")
    # Lọc mirror ngõ ra của PLC2
    for out_name, mirror_name, dtype in physical_outputs:
        tag_plc = "PLC1"
        for t in tags:
            if t.name == out_name:
                tag_plc = t.plc
                break
        if tag_plc in ("PLC2", "Shared"):
            if dtype == "Bool":
                fc.add_network(f"Mirror {out_name}", [("NO", out_name), ("Coil", mirror_name)])
            else:
                fc.add_network(f"Mirror {out_name}", [("MOVE", out_name, mirror_name)])

    fc.add_network("Quyền Operator", [("NO", "AI_HMI_Operator_Login"), ("MOVE", "1", "AI_HMI_User_Level")])
    fc.add_network("Quyền Engineer", [("NO", "AI_HMI_Engineer_Login"), ("MOVE", "2", "AI_HMI_User_Level")])
    fc.add_network("Quyền Admin", [("NO", "AI_HMI_Admin_Login"), ("MOVE", "3", "AI_HMI_User_Level")])
    fc.add_network("Cho phép sửa thông số Engineer", [("NO", "AI_HMI_Engineer_Login"), ("SetCoil", "AI_HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Cho phép sửa thông số Admin", [("NO", "AI_HMI_Admin_Login"), ("SetCoil", "AI_HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Operator không được sửa thông số", [("NO", "AI_HMI_Operator_Login"), ("ResetCoil", "AI_HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Mã an toàn mặc định", [("MOVE", "0", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã cảnh báo dosing PLC2", [("NO", "AI_PLC2_Loi_Dosing"), ("MOVE", "1", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã lỗi Setpoint PLC2 không hợp lệ", [("NO", "AI_PLC2_Loi_Setpoint"), ("MOVE", "2", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã lỗi dry run PLC2", [("NO", "AI_PLC2_Loi_Dry_Run"), ("MOVE", "3", "AI_HMI_AnToan_Status")])
    fc.add_network("Mã E-Stop ưu tiên cao PLC2", [("NO", "AI_PLC2_EStop_Latch"), ("MOVE", "4", "AI_HMI_AnToan_Status")])

    # --- Trạng thái hiển thị chế độ hệ thống ---
    fc.add_network("Trạng thái hiển thị chế độ chạy thật", [("NC", "AI_HMI_Sim_Mode"), ("Coil", "AI_System_Mode_Real")])
    fc.add_network("Trạng thái hiển thị chế độ mô phỏng", [("NO", "AI_HMI_Sim_Mode"), ("Coil", "AI_System_Mode_Sim")])
    fc.add_network("Cảnh báo chế độ mô phỏng HMI active", [("NO", "AI_HMI_Sim_Mode"), ("Coil", "AI_HMI_Sim_Active_Warning")])

    # --- Dọn dẹp tín hiệu mô phỏng khi ở chế độ chạy thật (Sim_Mode = FALSE) ---
    # Digital sensors PLC2:
    for tag in [
        "AI_LS3217_Bon4_Cao_HMI", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan_HMI",
        "AI_PLC2_Load_Default_Cmd_Nhan_HMI"
    ]:
        fc.add_network(f"Reset {tag} khi ở chế độ chạy thật", [("NC", "AI_HMI_Sim_Mode"), ("ResetCoil", tag)])

    # Analog sensors PLC2:
    for tag in [
        "AI_FT3210_Bon3_HMI", "AI_LT3213_Bon3_HMI", "AI_TT3214_Bon3_HMI",
        "AI_FT3215_Bon4_HMI", "AI_FQ3215_Bon4_HMI", "AI_LT3218_Bon4_HMI", "AI_TT3219_Bon4_HMI"
    ]:
        fc.add_network(f"Reset {tag} về 0.0 khi ở chế độ chạy thật", [("NC", "AI_HMI_Sim_Mode"), ("MOVE", "0.0", tag)])

    # Mô phỏng truyền thông GET/PUT offline trên PLC2
    fc.add_network("Mô phỏng truyền thông GET/PUT: Link Cmd nạp recipe PLC1 sang PLC2_HMI", [
        ("NO", "AI_HMI_Sim_Mode"),
        ("NO", "AI_HMI_Load_Default_Recipe"),
        ("Coil", "AI_PLC2_Load_Default_Cmd_Nhan_HMI"),
    ])

    return fc.generate_xml()
"""

# Tìm hàm build_hmi_mirror và thay thế
start_idx = content.find("def build_hmi_mirror()")
end_idx = content.find("def hmi_text_lists()")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + split_mirror_functions + "\n\n" + content[end_idx:]
    print("Replaced build_hmi_mirror with split versions.")
else:
    print("Error: build_hmi_mirror bounds not found!")

# 2. Sửa dict files trong main()
old_dict_item = '"FC_HMI_Mirror.xml": build_hmi_mirror(),'
new_dict_item = '"FC_HMI_Mirror_PLC1.xml": build_hmi_mirror_plc1(),\n        "FC_HMI_Mirror_PLC2.xml": build_hmi_mirror_plc2(),'

if old_dict_item in content:
    content = content.replace(old_dict_item, new_dict_item)
    print("Updated files dict with split HMI Mirror blocks.")
else:
    # Try with different whitespace
    content = re.sub(
        r'"FC_HMI_Mirror.xml"\s*:\s*build_hmi_mirror\(\s*\)\s*,',
        new_dict_item,
        content
    )
    print("Updated files dict using regex.")

gen_path.write_text(content, encoding="utf-8")
print("Done mirror split.")
