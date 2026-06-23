# -*- coding: utf-8 -*-
"""
generate_watch_tables.py
Script to generate TIA Portal CSV and Markdown watch tables for offline testing.
"""
import os

PROJECT_DIR = r"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026"
WATCH_DIR = os.path.join(PROJECT_DIR, "watch_tables")
os.makedirs(WATCH_DIR, exist_ok=True)

# Helper function to generate CSV and Markdown representations
def write_table(filename_base, title, tags_with_comments):
    # 1. Write CSV for TIA Portal (simple copy-paste friendly format)
    csv_path = os.path.join(WATCH_DIR, f"{filename_base}.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Name,Comment\n")
        for tag, comment in tags_with_comments:
            # Escape double quotes for CSV
            escaped_tag = tag.replace('"', '""')
            f.write(f'"{escaped_tag}","{comment}"\n')
            
    # 2. Write Markdown for quick view
    md_path = os.path.join(WATCH_DIR, f"{filename_base}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write("| Tên Biến (Tag Name) | Mô Tả / Chú Thích (Comment) |\n")
        f.write("| --- | --- |\n")
        for tag, comment in tags_with_comments:
            f.write(f"| `{tag}` | {comment} |\n")

# --- PLC1 Bảng 1: Main Sequence ---
plc1_main_tags = [
    ("AI_HMI_Sim_Mode", "Cho phép toàn bộ tín hiệu mô phỏng HMI tác động vào input hiệu dụng"),
    ("AI_HMI_Run_Enable", "Cho phép vận hành từ HMI ở chế độ thật"),
    ("AI_HMI_Use_Sim_Input_PLC1", "Cho phép sử dụng đầu vào mô phỏng PLC1"),
    ("AI_HMI_Use_Sim_Input_BonChua", "Cho phép sử dụng đầu vào mô phỏng Bồn chứa"),
    ("AI_Gia_Lap_Mat_Ket_Noi_HMI", "Nút giả lập mất kết nối PLC"),
    ("AI_HMI_Load_Default_Recipe", "Yêu cầu nạp lại Recipe mặc định từ HMI"),
    ("AI_Nut_Khoi_Dong_HMI", "Nút khởi động ảo từ HMI"),
    ("AI_Nut_Dung_HMI", "Nút dừng ảo từ HMI"),
    ("AI_Nut_Reset_HMI", "Nút reset lỗi ảo từ HMI"),
    ("AI_Nut_EStop_HMI", "Nút dừng khẩn ảo từ HMI"),

    ("AI_PLC1_State", "Mã bước chu trình Nhánh 1 Bồn 1-2"),
    ("AI_BonChua_State", "Mã bước cụm bồn chứa và lọc thành phẩm"),
    ("AI_PLC1_Loi_Tong", "Lỗi tổng khóa Auto Nhánh 1"),

    ("AI_FQ3200_Bon1_HMI", "Giá trị mô phỏng lưu lượng tích lũy Bồn 1 (lít)"),
    ("AI_LT3203_Bon1_HMI", "Giá trị mô phỏng mức liên tục Bồn 1 (m)"),
    ("AI_FQ3205_Bon2_HMI", "Giá trị mô phỏng lưu lượng tích lũy Bồn 2 (lít)"),
    ("AI_LT3209_Bon2_HMI", "Giá trị mô phỏng mức liên tục Bồn 2 (m)"),
    ("AI_TT3208_Bon2_HMI", "Giá trị mô phỏng nhiệt độ Bồn 2 (°C)"),
    ("AI_LT3302_BonChua1_HMI", "Giá trị mô phỏng mức liên tục Bồn chứa 01 (m)"),
    ("AI_TT3301_BonChua1_HMI", "Giá trị mô phỏng nhiệt độ Bồn chứa 01 (°C)"),
    ("AI_LT3307_BonChua2_HMI", "Giá trị mô phỏng mức liên tục Bồn chứa 02 (m)"),
    ("AI_PI3308_Truoc_Filter_HMI", "Giá trị mô phỏng áp suất trước màng lọc (bar)"),
    ("AI_FT3309_Xa_Thanh_Pham_HMI", "Giá trị mô phỏng lưu lượng xả thành phẩm (L/h)"),

    ("AI_V3230_Nuoc_Bon1", "Van on/off cấp nước Bồn 1"),
    ("AI_AGTR3260_Khuay_Bon1", "Động cơ khuấy Bồn 1"),
    ("AI_V3235_Nuoc_Bon2", "Van on/off cấp nước Bồn 2"),
    ("AI_CV3206_Hoi_Bon2", "Van hơi/nhiệt Bồn 2 (độ mở 0-100%)"),
    ("AI_VFD_Bon2_Run", "Lệnh chạy VFD động cơ Bồn 2"),
    ("AI_VFD_Bon2_Dao_Chieu", "Lệnh đảo chiều VFD động cơ Bồn 2"),
    ("AI_Pump3264_Chuyen_Nhanh1", "Bơm chuyển dung dịch Nhánh 1 xuống bồn chứa"),
    ("AI_Pump3364_Filter", "Bơm qua màng lọc CCP số 1"),
    ("AI_CV_Filler_Cap_Dich", "Van tuyến tính cấp dịch xuống phễu chiết rót")
]
write_table("PLC1_Watch_Main_Sequence", "PLC1 Watch Table - Chu Trình Tự Động & Mô Phỏng Cảm Biến", plc1_main_tags)

# --- PLC1 Bảng 2: PID & VFD ---
plc1_pid_vfd_tags = [
    ("AI_HMI_Sim_Mode", "Cho phép toàn bộ tín hiệu mô phỏng HMI tác động vào input hiệu dụng"),
    ("AI_PLC1_Loi_Tong", "Lỗi tổng khóa Auto Nhánh 1"),
    ("AI_PLC1_EStop_Latch", "Chốt dừng khẩn HMI/SCADA Nhánh 1"),
    ("AI_PLC1_Loi_Dry_Run", "Lỗi chạy khô bơm Nhánh 1"),
    ("AI_PLC1_Loi_Dosing", "Lỗi quá thời gian dosing Nhánh 1"),
    ("AI_PLC1_Loi_Truyen_Thong", "Lỗi truyền thông mô phỏng Nhánh 1"),
    ("AI_PLC1_Loi_Setpoint", "Lỗi Setpoint PLC1"),
    ("AI_BonChua_Loi_Setpoint", "Lỗi Setpoint Bồn chứa"),
    ("AI_PID_Bon2_Error", "Lỗi khối PID Bồn 2"),
    ("AI_PID_Bon2_ErrorBits", "Mã lỗi DWORD PID Bồn 2"),
    ("AI_VFD_Bon2_MB_Error", "Lỗi Modbus Master VFD Bồn 2"),
    ("AI_Gia_Lap_Mat_Ket_Noi_HMI", "Nút giả lập mất kết nối PLC")
]
write_table("PLC1_Watch_PID_VFD", "PLC1 Watch Table - Bảng Debug Lỗi Hệ Thống", plc1_pid_vfd_tags)

# --- PLC1 Bảng 3: Fake PLC2 Modbus Return ---
plc1_fake_plc2_tags = [
    ('"DB_PLC1_Recv_From_PLC2_DB".AckSeq', "Sequence nhận phản hồi từ PLC2"),
    ('"DB_PLC1_Recv_From_PLC2_DB".Done_Branch2', "Nhánh 2 Bồn 3-4 hoàn thành mẻ"),
    ('"DB_PLC1_Recv_From_PLC2_DB".Done_Discharge2', "Bồn 4 đã xả xong hoàn toàn"),
    ('"DB_PLC1_Recv_From_PLC2_DB".Done_Recipe', "PLC2 báo đã nạp xong Recipe mặc định"),
    ('"DB_PLC1_Recv_From_PLC2_DB".Alarm', "Cảnh báo lỗi tổng từ PLC2"),
    ('"DB_PLC1_Recv_From_PLC2_DB".State', "Mã trạng thái bước hiện tại của PLC2"),
    ('"DB_PLC1_Recv_From_PLC2_DB".PID_Bon4_SP', "Setpoint PID Bồn 4 gửi từ PLC2"),
    ('"DB_PLC1_Recv_From_PLC2_DB".PID_Bon4_PV', "Process Value PID Bồn 4 gửi từ PLC2"),
    ('"DB_PLC1_Recv_From_PLC2_DB".PID_Bon4_CV', "Control Value PID Bồn 4 gửi từ PLC2"),
    ('"DB_PLC1_Recv_From_PLC2_DB".Heartbeat', "Tín hiệu Heartbeat từ PLC2 để giám sát kết nối")
]
write_table("PLC1_Watch_Fake_PLC2_Modbus_Return", "PLC1 Watch Table - Giả Lập Dữ Liệu Modbus TCP Nhận Từ PLC2", plc1_fake_plc2_tags)

# --- PLC2 Bảng 1: Main Sequence ---
plc2_main_tags = [
    ("AI_HMI_Sim_Mode", "Cho phép toàn bộ tín hiệu mô phỏng HMI tác động vào input hiệu dụng"),
    ("AI_HMI_Use_Sim_Input_PLC2", "Cho phép sử dụng đầu vào mô phỏng PLC2"),
    ("AI_PLC2_State", "Mã bước chu trình Nhánh 2 Bồn 3-4"),
    ("AI_PLC2_Loi_Tong", "Lỗi tổng khóa Auto Nhánh 2"),

    ("AI_FQ3210_Bon3_HMI", "Giá trị mô phỏng lưu lượng tích lũy Bồn 3 (lít)"),
    ("AI_LT3213_Bon3_HMI", "Giá trị mô phỏng mức liên tục Bồn 3 (m)"),
    ("AI_FQ3215_Bon4_HMI", "Giá trị mô phỏng lưu lượng tích lũy Bồn 4 (lít)"),
    ("AI_LT3218_Bon4_HMI", "Giá trị mô phỏng mức liên tục Bồn 4 (m)"),
    ("AI_TT3219_Bon4_HMI", "Giá trị mô phỏng nhiệt độ Bồn 4 (°C)"),

    ("AI_V3240_Nuoc_Bon3", "Van on/off cấp nước Bồn 3"),
    ("AI_AGTR3262_Khuay_Bon3", "Động cơ khuấy Bồn 3"),
    ("AI_V3245_Nuoc_Bon4", "Van on/off cấp nước Bồn 4"),
    ("AI_CV3216_Hoi_Bon4", "Van tuyến tính gia nhiệt mô phỏng Bồn 4"),
    ("AI_AGTR3263_Khuay_Bon4", "Động cơ khuấy Bồn 4"),
    ("AI_AGTR3263_Dao_Chieu", "Lệnh đảo chiều động cơ khuấy Bồn 4"),
    ("AI_Pump3265_Chuyen_Nhanh2", "Bơm chuyển dung dịch Nhánh 2 xuống bồn chứa"),
    ("AI_PLC2_Me_Nhanh2_Hoan_Thanh", "Cờ hoàn thành Nhánh 2 gửi sang PLC1"),
    ("AI_PLC2_Xa_Bon4_Xong", "Bồn 4 đã xả xong hoàn toàn")
]
write_table("PLC2_Watch_Main_Sequence", "PLC2 Watch Table - Chu Trình Tự Động & Mô Phỏng Cảm Biến", plc2_main_tags)

# --- PLC2 Bảng 2: PID Sim ---
plc2_pid_sim_tags = [
    ("AI_PID_Bon4_Enable", "Cho phép PID Bồn 4 hoạt động"),
    ("AI_PID_Bon4_SP", "Setpoint nhiệt độ đưa vào PID Bồn 4"),
    ("AI_TT3219_Bon4_Sim", "Nhiệt độ mô phỏng nội bộ cho PID Bồn 4"),
    ("AI_TT3219_Bon4_Target", "Nhiệt độ đích mô phỏng Bồn 4"),
    ("AI_PID_Bon4_CV", "Giá trị điều khiển van hơi gia nhiệt Bồn 4 từ PID"),
    ("AI_PID_Bon4_Error", "Lỗi khối PID Bồn 4")
]
write_table("PLC2_Watch_PID_Sim", "PLC2 Watch Table - Khối PID Mô Phỏng Bồn 4", plc2_pid_sim_tags)

# --- PLC2 Bảng 3: Fake PLC1 Modbus Command ---
plc2_fake_plc1_tags = [
    ('"DB_Modbus_Holding_Register_DB".CmdSeq', "Sequence lệnh gửi từ PLC1"),
    ('"DB_Modbus_Holding_Register_DB".Cmd_Start', "Lệnh Start từ PLC1"),
    ('"DB_Modbus_Holding_Register_DB".Cmd_Stop', "Lệnh Stop từ PLC1"),
    ('"DB_Modbus_Holding_Register_DB".Cmd_Reset', "Lệnh Reset từ PLC1"),
    ('"DB_Modbus_Holding_Register_DB".Cmd_EStop', "Lệnh EStop từ PLC1"),
    ('"DB_Modbus_Holding_Register_DB".Cmd_Load_Recipe', "Lệnh yêu cầu nạp Recipe mặc định từ PLC1"),
    ('"DB_Modbus_Holding_Register_DB".Heartbeat_Client', "Heartbeat gửi từ PLC1"),
    ('"DB_Modbus_Holding_Register_DB".AckSeq', "Sequence phản hồi báo nhận lệnh của PLC2"),
    ('"DB_Modbus_Holding_Register_DB".Done_Branch2', "Nhánh 2 hoàn thành mẻ"),
    ('"DB_Modbus_Holding_Register_DB".Done_Discharge2', "Bồn 4 đã xả xong"),
    ('"DB_Modbus_Holding_Register_DB".Alarm', "Cảnh báo lỗi tổng từ PLC2"),
    ('"DB_Modbus_Holding_Register_DB".State', "Trạng thái bước chu trình PLC2")
]
write_table("PLC2_Watch_Fake_PLC1_Modbus_Command", "PLC2 Watch Table - Nhận Lệnh & Phản Hồi Modbus TCP Với PLC1", plc2_fake_plc1_tags)

print(f"Successfully generated all CSV and MD Watch Tables under {WATCH_DIR}!")
