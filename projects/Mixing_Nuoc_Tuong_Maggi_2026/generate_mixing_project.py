# -*- coding: utf-8 -*-
"""
Sinh bộ file bàn giao cho đề sơ khảo:
Mô phỏng hệ thống Mixing nước tương Maggi 2026.

Python chỉ dùng làm công cụ sinh SimaticML XML. Logic PLC được xuất ra
100% Ladder XML bằng Agent_LAD_Library.py.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
sys.path.insert(0, str(ROOT / "Ladder"))

from Agent_LAD_Library import TIAHmiListBuilder, TIALadderBuilder  # noqa: E402


@dataclass(frozen=True)
class Tag:
    name: str
    dtype: str
    address: str
    comment: str
    plc: str
    group: str


class BitAllocator:
    def __init__(self, area: str, start_byte: int):
        self.area = area
        self.byte = start_byte
        self.bit = 0

    def next(self) -> str:
        address = f"%{self.area}{self.byte}.{self.bit}"
        self.bit += 1
        if self.bit >= 8:
            self.byte += 1
            self.bit = 0
        return address


class WordAllocator:
    def __init__(self, area: str, start: int, step: int):
        self.area = area
        self.value = start
        self.step = step

    def next(self) -> str:
        address = f"%{self.area}{self.value}"
        self.value += self.step
        return address


tags: list[Tag] = []
tag_names: set[str] = set()

di: BitAllocator
do: BitAllocator
ai: WordAllocator
ao: WordAllocator
hmi_di: BitAllocator
mirror_do: BitAllocator
internal_bool: BitAllocator
hmi_bool: BitAllocator
internal_int: WordAllocator
internal_real: WordAllocator
mirror_ao: WordAllocator
physical_outputs: list[tuple[str, str, str]] = []


def reset_generation_state() -> None:
    global tags, tag_names, physical_outputs
    global di, do, ai, ao, hmi_di, mirror_do, internal_bool, hmi_bool
    global internal_int, internal_real, mirror_ao

    tags = []
    tag_names = set()
    physical_outputs = []

    di = BitAllocator("I", 0)
    do = BitAllocator("Q", 0)
    ai = WordAllocator("ID", 100, 4)
    ao = WordAllocator("QD", 100, 4)
    hmi_di = BitAllocator("M", 110)
    mirror_do = BitAllocator("M", 220)
    internal_bool = BitAllocator("M", 320)
    hmi_bool = BitAllocator("M", 420)
    internal_int = WordAllocator("MW", 520, 2)
    internal_real = WordAllocator("MD", 700, 4)
    mirror_ao = WordAllocator("MD", 1200, 4)


reset_generation_state()


def add_tag(name: str, dtype: str, address: str, comment: str, plc: str, group: str) -> None:
    if name in tag_names:
        raise ValueError(f"Trùng tag: {name}")
    tag_names.add(name)
    tags.append(Tag(name, dtype, address, comment, plc, group))


def add_bool(name: str, comment: str, plc: str = "Shared", group: str = "Internal") -> None:
    add_tag(name, "Bool", internal_bool.next(), comment, plc, group)


def add_hmi_bool(name: str, comment: str, plc: str = "Shared", group: str = "HMI") -> None:
    add_tag(name, "Bool", hmi_bool.next(), comment, plc, group)


def add_int(name: str, comment: str, plc: str = "Shared", group: str = "Internal") -> None:
    add_tag(name, "Int", internal_int.next(), comment, plc, group)


def add_real(name: str, comment: str, plc: str = "Shared", group: str = "Internal") -> None:
    add_tag(name, "Real", internal_real.next(), comment, plc, group)


def add_time(name: str, comment: str, plc: str = "Shared", group: str = "Internal") -> None:
    add_tag(name, "Time", internal_real.next(), comment, plc, group)


def add_physical_input(
    name: str,
    dtype: str,
    comment: str,
    plc: str,
    group: str,
) -> None:
    if dtype == "Bool":
        add_tag(name, "Bool", di.next(), comment, plc, group)
        add_tag(name + "_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI song song cho " + comment, plc, group)
        add_tag(name + "_HMI_Gated", "Bool", internal_bool.next(), "Tín hiệu HMI đã qua xử lý chế độ cho " + comment, plc, group)
        add_tag(name + "_Eff", "Bool", internal_bool.next(), "Tín hiệu thực tế/mô phỏng hiệu dụng cho " + comment, plc, group)
    else:
        add_tag(name, dtype, ai.next(), comment, plc, group)
        add_tag(name + "_HMI", dtype, internal_real.next(), "Giá trị mô phỏng/HMI song song cho " + comment, plc, group)
        add_tag(name + "_Use_HMI", "Bool", hmi_bool.next(), "Chọn chế độ mô phỏng HMI cho " + comment, plc, group)
        add_tag(name + "_Sim_Req", "Bool", internal_bool.next(), "Yêu cầu mô phỏng cảm biến cho " + comment, plc, group)
        add_tag(name + "_Sim_Active", "Bool", internal_bool.next(), "Mô phỏng cảm biến đang hoạt động cho " + comment, plc, group)
        add_tag(name + "_Eff", dtype, internal_real.next(), "Giá trị thực tế/mô phỏng hiệu dụng cho " + comment, plc, group)


def add_physical_output(
    name: str,
    dtype: str,
    comment: str,
    plc: str,
    group: str,
) -> None:
    if dtype == "Bool":
        add_tag(name, "Bool", do.next(), comment, plc, group)
        add_tag(name + "_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho " + comment, plc, group)
    else:
        add_tag(name, dtype, ao.next(), comment, plc, group)
        add_tag(name + "_M", dtype, mirror_ao.next(), "Tag gương phản hồi HMI cho " + comment, plc, group)
    physical_outputs.append((name, name + "_M", dtype))


def define_tags() -> None:
    # Lệnh vật lý chung.
    add_physical_input("Nut_Khoi_Dong", "Bool", "Nút khởi động vật lý", "PLC1", "Lenh_Chung")
    add_physical_input("Nut_Dung", "Bool", "Nút dừng vật lý", "PLC1", "Lenh_Chung")
    add_physical_input("Nut_Reset", "Bool", "Nút reset lỗi vật lý", "PLC1", "Lenh_Chung")
    add_physical_input("Nut_EStop", "Bool", "Nút dừng khẩn vật lý", "PLC1", "Lenh_Chung")

    # PLC1: Bồn 1 và Bồn 2.
    for name, dtype, comment in [
        ("FT3200_Bon1", "Real", "Cảm biến lưu lượng nước dosing vào Bồn 1"),
        ("FQ3200_Bon1", "Real", "Bộ đếm lưu lượng tích lũy Bồn 1"),
        ("LS3202_Bon1_Cao", "Bool", "Cảm biến mức cao Bồn 1"),
        ("LT3203_Bon1", "Real", "Cảm biến mức liên tục Bồn 1"),
        ("TT3204_Bon1", "Real", "Cảm biến nhiệt độ Bồn 1"),
        ("FT3205_Bon2", "Real", "Cảm biến lưu lượng nước dosing vào Bồn 2"),
        ("FQ3205_Bon2", "Real", "Bộ đếm lưu lượng tích lũy Bồn 2"),
        ("LT3209_Bon2", "Real", "Cảm biến mức liên tục Bồn 2"),
        ("TT3208_Bon2", "Real", "Cảm biến nhiệt độ Bồn 2"),
    ]:
        add_physical_input(name, dtype, comment, "PLC1", "Bon_1_2")

    for name, dtype, comment in [
        ("VFD_Bon2_Contactor", "Bool", "Contactor cấp nguồn/cho phép VFD Bồn 2"),
        ("CV3201_Nuoc_Bon1", "Real", "Van tuyến tính cấp nước Bồn 1"),
        ("AGTR3260_Khuay_Bon1", "Bool", "Động cơ khuấy Bồn 1"),
        ("AGTR3260_Toc_Do_AO", "Real", "Tín hiệu tốc độ khuấy Bồn 1"),
        ("V3232_Xa_Bon1", "Bool", "Van xả đáy Bồn 1 số 1"),
        ("V3233_Xa_Bon1", "Bool", "Van xả đáy Bồn 1 số 2"),
        ("V3234_Xa_Bon1", "Bool", "Van xả đáy Bồn 1 số 3"),
        ("V3235_Nuoc_Bon2", "Bool", "Van on/off cấp nước Bồn 2"),
        ("CV3206_Hoi_Bon2", "Real", "Van hơi/nhiệt Bồn 2 ở chế độ cho phép"),
        ("VFD_Bon2_Dummy_Run_Physical", "Bool", "Dummy RUN physical output VFD Bồn 2"),
        ("VFD_Bon2_Dummy_Reverse_Physical", "Bool", "Dummy Reverse physical output VFD Bồn 2"),
        ("VFD_Bon2_Dummy_Speed_Physical", "Real", "Dummy Speed physical output VFD Bồn 2"),
        ("V3237_Xa_Bon2", "Bool", "Van xả đáy Bồn 2 số 1"),
        ("V3238_Xa_Bon2", "Bool", "Van xả đáy Bồn 2 số 2"),
        ("V3239_Xa_Bon2", "Bool", "Van xả đáy Bồn 2 số 3"),
        ("Pump3264_Chuyen_Nhanh1", "Bool", "Bơm chuyển dung dịch Nhánh 1 xuống bồn chứa"),
    ]:
        add_physical_output(name, dtype, comment, "PLC1", "Bon_1_2")

    # PLC2: Bồn 3 và Bồn 4.
    for name, dtype, comment in [
        ("FT3210_Bon3", "Real", "Cảm biến lưu lượng nước dosing vào Bồn 3"),
        ("FQ3210_Bon3", "Real", "Bộ đếm lưu lượng tích lũy Bồn 3"),
        ("LT3213_Bon3", "Real", "Cảm biến mức liên tục Bồn 3"),
        ("TT3214_Bon3", "Real", "Cảm biến nhiệt độ Bồn 3"),
        ("FT3215_Bon4", "Real", "Cảm biến lưu lượng nước dosing vào Bồn 4"),
        ("FQ3215_Bon4", "Real", "Bộ đếm lưu lượng tích lũy Bồn 4"),
        ("LS3217_Bon4_Cao", "Bool", "Cảm biến mức cao Bồn 4"),
        ("LT3218_Bon4", "Real", "Cảm biến mức liên tục Bồn 4"),
        ("TT3219_Bon4", "Real", "Cảm biến nhiệt độ Bồn 4"),
    ]:
        add_physical_input(name, dtype, comment, "PLC2", "Bon_3_4")

    for name, dtype, comment in [
        ("V3240_Nuoc_Bon3", "Bool", "Van on/off cấp nước Bồn 3"),
        ("CV3211_Nuoc_Bon3", "Real", "Van tuyến tính cấp nước Bồn 3"),
        ("AGTR3262_Khuay_Bon3", "Bool", "Động cơ khuấy Bồn 3"),
        ("AGTR3262_Toc_Do_AO", "Real", "Tín hiệu tốc độ khuấy Bồn 3"),
        ("V3242_Xa_Bon3", "Bool", "Van xả đáy Bồn 3 số 1"),
        ("V3243_Xa_Bon3", "Bool", "Van xả đáy Bồn 3 số 2"),
        ("V3244_Xa_Bon3", "Bool", "Van xả đáy Bồn 3 số 3"),
        ("V3245_Nuoc_Bon4", "Bool", "Van on/off cấp nước Bồn 4"),
        ("CV3216_Hoi_Bon4", "Real", "Van tuyến tính gia nhiệt mô phỏng Bồn 4"),
        ("AGTR3263_Khuay_Bon4", "Bool", "Động cơ khuấy Bồn 4"),
        ("AGTR3263_Dao_Chieu", "Bool", "Lệnh đảo chiều động cơ khuấy Bồn 4"),
        ("AGTR3263_Toc_Do_AO", "Real", "Tốc độ đặt động cơ khuấy Bồn 4"),
        ("V3247_Xa_Bon4", "Bool", "Van xả đáy Bồn 4 số 1"),
        ("V3248_Xa_Bon4", "Bool", "Van xả đáy Bồn 4 số 2"),
        ("V3249_Xa_Bon4", "Bool", "Van xả đáy Bồn 4 số 3"),
        ("Pump3265_Chuyen_Nhanh2", "Bool", "Bơm chuyển dung dịch Nhánh 2 xuống bồn chứa"),
    ]:
        add_physical_output(name, dtype, comment, "PLC2", "Bon_3_4")

    # Bồn chứa và lọc thành phẩm gom về PLC1 để hiển thị kết quả chung.
    for name, dtype, comment in [
        ("LT3302_BonChua1", "Real", "Cảm biến mức liên tục Bồn chứa 01"),
        ("TT3301_BonChua1", "Real", "Cảm biến nhiệt độ Bồn chứa 01"),
        ("TT3303_TraoDoiNhiet", "Real", "Cảm biến nhiệt độ bộ trao đổi nhiệt"),
        ("LT3307_BonChua2", "Real", "Cảm biến mức liên tục Bồn chứa 02"),
        ("TT3306_BonChua2", "Real", "Cảm biến nhiệt độ Bồn chứa 02"),
        ("PI3308_Truoc_Filter", "Real", "Cảm biến áp suất trước màng lọc"),
        ("FT3309_Xa_Thanh_Pham", "Real", "Cảm biến lưu lượng xả thành phẩm"),
        ("LSH3310_Pheu_Cao", "Bool", "Cảm biến mức cao phễu chiết rót"),
        ("LSL3311_Pheu_Thap", "Bool", "Cảm biến mức thấp phễu chiết rót"),
    ]:
        add_physical_input(name, dtype, comment, "PLC1", "Bon_Chua_Loc")

    for name, dtype, comment in [
        ("V3331_Xa_BonChua1", "Bool", "Van xả đáy Bồn chứa 01 số 1"),
        ("V3332_Xa_BonChua1", "Bool", "Van xả đáy Bồn chứa 01 số 2"),
        ("Pump3361_LuanChuyen_BonChua1", "Bool", "Bơm luân chuyển Bồn chứa 01"),
        ("Pump3362_Xa_BonChua1", "Bool", "Bơm xả Bồn chứa 01"),
        ("V3333_DieuHuong_BonChua1", "Bool", "Van điều hướng Bồn chứa 01 số 1"),
        ("V3334_DieuHuong_BonChua1", "Bool", "Van điều hướng Bồn chứa 01 số 2"),
        ("V3335_DieuHuong_BonChua1", "Bool", "Van điều hướng Bồn chứa 01 số 3"),
        ("CV3304_Nuoc_Lam_Mat", "Real", "Van tuyến tính nước làm mát"),
        ("V3338_Xa_BonChua2", "Bool", "Van xả đáy Bồn chứa 02 số 1"),
        ("V3339_Xa_BonChua2", "Bool", "Van xả đáy Bồn chứa 02 số 2"),
        ("Pump3364_Filter", "Bool", "Bơm qua màng lọc CCP số 1"),
        ("Pump3365_Filter", "Bool", "Bơm qua màng lọc CCP số 2"),
        ("V3340_Duong_Filter", "Bool", "Van đường ống Filter số 1"),
        ("V3341_Duong_Filter", "Bool", "Van đường ống Filter số 2"),
        ("CV_Filler_Cap_Dich", "Real", "Van tuyến tính cấp dịch xuống phễu chiết rót"),
        ("Coi_Bao_Dong", "Bool", "Còi báo động chung"),
    ]:
        add_physical_output(name, dtype, comment, "PLC1", "Bon_Chua_Loc")

    # HMI setpoint, quyền, bước, alarm và cờ mô phỏng.
    for name, comment in [
        ("HMI_Operator_Login", "Đăng nhập quyền Operator"),
        ("HMI_Engineer_Login", "Đăng nhập quyền Engineer"),
        ("HMI_Admin_Login", "Đăng nhập quyền Admin"),
        ("HMI_Che_Do_Manual", "Cho phép điều khiển tay từng thiết bị"),
        ("HMI_Ack_Alarm", "Xác nhận cảnh báo"),
        ("HMI_Reset_Alarm", "Reset alarm bằng HMI"),
        ("Gia_Lap_Mat_Ket_Noi_HMI", "Nút giả lập mất kết nối PLC"),
    ]:
        add_hmi_bool(name, comment, "Shared", "HMI_Security")

    add_int("HMI_User_Level", "Mức quyền hiện tại: 1 Operator, 2 Engineer, 3 Admin", "Shared", "HMI_Security")
    add_bool("HMI_Cho_Phep_Sua_Thong_So", "Cờ cho phép sửa công thức và PID", "Shared", "HMI_Security")
    add_int("HMI_Alarm_Status", "Mã cảnh báo tổng hợp cho WinCC TextList", "Shared", "Alarm")
    add_int("HMI_AnToan_Status", "Mã chẩn đoán an toàn ưu tiên", "Shared", "Alarm")

    for plc, prefix, comment in [
        ("PLC1", "PLC1", "Nhánh 1 Bồn 1-2"),
        ("PLC2", "PLC2", "Nhánh 2 Bồn 3-4"),
    ]:
        add_bool(prefix + "_Auto_Enable", "Cho phép chạy Auto " + comment, plc, "Sequence")
        add_bool(prefix + "_EStop_Latch", "Chốt dừng khẩn HMI/SCADA " + comment, plc, "Safety")
        add_bool(prefix + "_Loi_Tong", "Lỗi tổng khóa Auto " + comment, plc, "Alarm")
        add_bool(prefix + "_Loi_Dry_Run", "Lỗi chạy khô bơm " + comment, plc, "Alarm")
        add_bool(prefix + "_Loi_Dosing", "Lỗi quá thời gian dosing " + comment, plc, "Alarm")
        add_bool(prefix + "_Loi_Truyen_Thong", "Lỗi truyền thông mô phỏng " + comment, plc, "Alarm")
        add_int(prefix + "_State", "Mã bước chu trình " + comment, plc, "Sequence")

    for name, comment in [
        ("PLC1_Step_Bon1_Dosing", "Bồn 1 đang dosing nước"),
        ("PLC1_Step_Bon1_Tip", "Bồn 1 đang mô phỏng tip cốt tương Nhật Bản"),
        ("PLC1_Step_Bon1_Khuay", "Bồn 1 đang khuấy ban đầu"),
        ("PLC1_Step_Bon1_Xa", "Bồn 1 đang xả sang Bồn 2"),
        ("PLC1_Step_Bon2_Dosing", "Bồn 2 đang dosing bổ sung"),
        ("PLC1_Step_Bon2_Tip", "Bồn 2 đang tip phụ gia"),
        ("PLC1_Step_Bon2_Khuay_Thuan", "Bồn 2 khuấy chiều thuận"),
        ("PLC1_Step_Bon2_Khuay_Nghich", "Bồn 2 khuấy chiều ngược"),
        ("PLC1_Step_Bon2_PID", "Bồn 2 gia nhiệt PID"),
        ("PLC1_Step_Bon2_Thanh_Trung", "Bồn 2 giữ thời gian thanh trùng"),
        ("PLC1_Me_Nhanh1_Hoan_Thanh", "Nhánh 1 hoàn thành và sẵn sàng xả xuống bồn chứa"),
        ("PLC1_Xa_Bon1_Xong", "Bồn 1 đã xả hết"),
        ("PLC1_Xa_Bon2_Xong", "Bồn 2 đã xả hết"),
    ]:
        add_bool(name, comment, "PLC1", "Sequence")

    for name, comment in [
        ("PLC2_Step_Bon3_Dosing", "Bồn 3 đang dosing nước"),
        ("PLC2_Step_Bon3_Tip", "Bồn 3 đang mô phỏng tip cốt tương đậu đậm đặc"),
        ("PLC2_Step_Bon3_Khuay", "Bồn 3 đang khuấy ban đầu"),
        ("PLC2_Step_Bon3_Xa", "Bồn 3 đang xả sang Bồn 4"),
        ("PLC2_Step_Bon4_Dosing", "Bồn 4 đang dosing bổ sung"),
        ("PLC2_Step_Bon4_Tip", "Bồn 4 đang tip phụ gia"),
        ("PLC2_Step_Bon4_Khuay_Thuan", "Bồn 4 khuấy chiều thuận"),
        ("PLC2_Step_Bon4_Khuay_Nghich", "Bồn 4 khuấy chiều ngược"),
        ("PLC2_Step_Bon4_PID_Mo_Phong", "Bồn 4 chạy PID mô phỏng"),
        ("PLC2_Step_Bon4_Thanh_Trung", "Bồn 4 giữ thời gian thanh trùng"),
        ("PLC2_Xa_Bon3_Xong", "Bồn 3 đã xả hết"),
        ("PLC2_Xa_Bon4_Xong", "Bồn 4 đã xả hết"),
    ]:
        add_bool(name, comment, "PLC2", "Sequence")

    for name, comment in [
        ("BonChua_Step_Nhan_Dich", "Bồn chứa 01 đang nhận dịch từ nhánh hoàn thành"),
        ("BonChua_Step_Giai_Nhiet", "Bồn chứa 01 đang giải nhiệt xuống 45 độ C"),
        ("BonChua_Step_Chuyen_Bon2", "Đang chuyển từ Bồn chứa 01 sang Bồn chứa 02"),
        ("BonChua_Step_Loc_Chiet", "Đang lọc CCP và chiết rót"),
        ("BonChua_Me_Hoan_Thanh", "Hoàn thành một mẻ sản xuất chung"),
    ]:
        add_bool(name, comment, "PLC1", "Bon_Chua_Loc")
    add_int("BonChua_State", "Mã bước cụm bồn chứa và lọc thành phẩm", "PLC1", "Bon_Chua_Loc")
    add_bool("BonChua_Owner_Nhanh1", "Mức ưu tiên Nhánh 1 sở hữu bồn chứa", "PLC1", "Bon_Chua_Loc")
    add_bool("BonChua_Owner_Nhanh2", "Mức ưu tiên Nhánh 2 sở hữu bồn chứa", "PLC1", "Bon_Chua_Loc")

    # Communication tags (PLC1 - PLC2)
    # PLC2 -> PLC1
    add_tag("PLC2_Me_Nhanh2_Hoan_Thanh", "Bool", internal_bool.next(), "Cờ hoàn thành Nhánh 2 gửi sang PLC1", "PLC2", "Comm")
    add_tag("PLC2_Me_Nhanh2_Hoan_Thanh_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho cờ hoàn thành Nhánh 2 gửi sang PLC1", "PLC2", "Comm")
    physical_outputs.append(("PLC2_Me_Nhanh2_Hoan_Thanh", "PLC2_Me_Nhanh2_Hoan_Thanh_M", "Bool"))
    add_tag("PLC2_Me_Nhanh2_Hoan_Thanh_Nhan", "Bool", internal_bool.next(), "Cờ PLC1 nhận trạng thái hoàn thành từ PLC2", "PLC1", "Comm")
    add_tag("PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI song song cho cờ PLC1 nhận trạng thái hoàn thành từ PLC2", "PLC1", "Comm")
    add_tag("PLC2_Xa_Bon4_Xong_Nhan", "Bool", internal_bool.next(), "Cờ PLC1 nhận trạng thái xả xong Bồn 4 từ PLC2", "PLC1", "Comm")
    # PLC1 -> PLC2
    add_tag("Pump3265_Chuyen_Nhanh2_Cmd", "Bool", internal_bool.next(), "Lệnh chạy bơm chuyển Nhánh 2 gửi sang PLC2", "PLC1", "Comm")
    add_tag("Pump3265_Chuyen_Nhanh2_Cmd_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho lệnh chạy bơm chuyển Nhánh 2 gửi sang PLC2", "PLC1", "Comm")
    physical_outputs.append(("Pump3265_Chuyen_Nhanh2_Cmd", "Pump3265_Chuyen_Nhanh2_Cmd_M", "Bool"))
    add_tag("Pump3265_Chuyen_Nhanh2_Cmd_Nhan", "Bool", internal_bool.next(), "Nhận lệnh chạy bơm chuyển Nhánh 2 từ PLC1", "PLC2", "Comm")
    add_tag("Pump3265_Chuyen_Nhanh2_Cmd_Nhan_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI song song cho lệnh chạy bơm chuyển Nhánh 2 từ PLC1", "PLC2", "Comm")

    # S7 Connection (Modbus TCP) Status and Recv tags for PLC1
    add_tag("PID_Bon4_SP_Recv", "Real", internal_real.next(), "PID Bồn 4 Setpoint nhận từ PLC2", "PLC1", "Comm")
    add_tag("PID_Bon4_PV_Recv", "Real", internal_real.next(), "PID Bồn 4 Process Value nhận từ PLC2", "PLC1", "Comm")
    add_tag("PID_Bon4_CV_Recv", "Real", internal_real.next(), "PID Bồn 4 Control Value nhận từ PLC2", "PLC1", "Comm")
    add_tag("PLC2_State_Recv", "Int", internal_int.next(), "Trạng thái hoạt động PLC2 nhận từ PLC2", "PLC1", "Comm")
    add_tag("PLC2_Loi_Tong_Recv", "Bool", internal_bool.next(), "Cờ lỗi tổng PLC2 nhận từ PLC2", "PLC1", "Comm")

    # Recv Button tags for PLC2 (received from PLC1)
    def add_recv_button(name_recv: str, comment_recv: str) -> None:
        add_tag(name_recv, "Bool", internal_bool.next(), comment_recv, "PLC2", "Comm")
        add_tag(name_recv + "_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI song song cho " + comment_recv, "PLC2", "Comm")
        add_tag(name_recv + "_HMI_Gated", "Bool", internal_bool.next(), "Tín hiệu HMI đã qua xử lý chế độ cho " + comment_recv, "PLC2", "Comm")
        add_tag(name_recv + "_Eff", "Bool", internal_bool.next(), "Tín hiệu thực tế/mô phỏng hiệu dụng cho " + comment_recv, "PLC2", "Comm")

    add_recv_button("Nut_Khoi_Dong_Nhan", "nút khởi động nhận từ PLC1")
    add_recv_button("Nut_Dung_Nhan", "nút dừng nhận từ PLC1")
    add_recv_button("Nut_Reset_Nhan", "nút reset nhận từ PLC1")
    add_recv_button("Nut_EStop_Nhan", "nút dừng khẩn nhận từ PLC1")

    # Modbus RTU tags for VFD Bon 2 (PLC1)
    add_tag("VFD_Bon2_iStep", "Int", "%MW60", "Bước quét tuần tự Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_iStep_Reset", "Bool", internal_bool.next(), "Cờ reset bộ đếm bước Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_Step0_Req", "Bool", internal_bool.next(), "Yêu cầu bước 0 Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_Step1_Req", "Bool", internal_bool.next(), "Yêu cầu bước 1 Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_Step2_Req", "Bool", internal_bool.next(), "Yêu cầu bước 2 Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_Step3_Req", "Bool", internal_bool.next(), "Yêu cầu bước 3 Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_ControlWord", "Word", "%MW40", "Control Word gửi VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_FreqSetpoint", "Int", "%MW42", "Frequency Setpoint gửi VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_StatusWord", "Word", "%MW44", "Status Word đọc từ VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_FreqActual", "Int", "%MW46", "Actual Speed đọc từ VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_Error", "Bool", "%M50.0", "Lỗi Modbus Master VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_Busy", "Bool", "%M50.1", "Modbus Master Busy VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_Done", "Bool", "%M50.2", "Modbus Master Done VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_Status", "Word", "%MW52", "Trạng thái Modbus Master VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MBCL_Done", "Bool", "%M51.0", "Modbus Comm Load Done VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MBCL_Error", "Bool", "%M51.1", "Modbus Comm Load Error VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MBCL_Status", "Word", "%MW54", "Trạng thái Modbus Comm Load VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_Freq_Temp", "Real", "%MD70", "Biến tạm tần số VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_Actual_Speed_Feedback", "Real", "%MD74", "Phản hồi tốc độ thực tế VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_Actual_Speed_Feedback_M", "Real", mirror_ao.next(), "Tag gương phản hồi HMI tốc độ thực tế VFD Bồn 2", "PLC1", "VFD")
    physical_outputs.append(("VFD_Bon2_Actual_Speed_Feedback", "VFD_Bon2_Actual_Speed_Feedback_M", "Real"))

    # System and Comm tags
    add_tag("Clock_1Hz", "Bool", "%M100.5", "Clock 1Hz system memory bit", "Shared", "System")
    add_tag("FirstScan", "Bool", "%M101.0", "First Scan system memory bit", "Shared", "System")
    # Modbus TCP Client tags (PLC1)
    add_tag("MB_TCP_iStep", "Int", "%MW80", "Modbus TCP Client step", "PLC1", "Comm")
    add_tag("MB_TCP_REQ", "Bool", "%M82.0", "Modbus TCP Client Request", "PLC1", "Comm")
    add_tag("MB_TCP_DONE", "Bool", "%M82.2", "Modbus TCP Client Transaction Done", "PLC1", "Comm")
    add_tag("MB_TCP_ERROR", "Bool", "%M82.3", "Modbus TCP Client Transaction Error", "PLC1", "Comm")
    add_tag("MB_TCP_BUSY", "Bool", "%M82.6", "Modbus TCP Client Transaction Busy", "PLC1", "Comm")
    add_tag("MB_TCP_STATUS", "Word", "%MW86", "Modbus TCP Client Status", "PLC1", "Comm")
    add_tag("MB_TCP_Mode", "USInt", "%MB88", "Modbus TCP Client Mode", "PLC1", "Comm")
    add_tag("MB_TCP_DataAddr", "UDInt", "%MD90", "Modbus TCP Client Data Address", "PLC1", "Comm")
    add_tag("MB_TCP_DataLen", "UInt", "%MW94", "Modbus TCP Client Data Length", "PLC1", "Comm")

    # Lưu ý: Real→Word conversion không dùng M-area overlap nữa.
    # SP/PV/CV truyền dưới dạng Int (x10) trong Word buffer DB để tránh overlap validator.

    # Edge detection and latch tags for handshake (PLC1)
    add_tag("Nut_Khoi_Dong_Eff_Old", "Bool", "%M83.0", "Old value of Start button", "PLC1", "Comm")
    add_tag("Nut_Khoi_Dong_Eff_Edge", "Bool", "%M83.6", "Start command edge detected", "PLC1", "Comm")
    add_tag("Nut_Dung_Eff_Old", "Bool", "%M83.1", "Old value of Stop button", "PLC1", "Comm")
    add_tag("Nut_Dung_Eff_Edge", "Bool", "%M83.7", "Stop command edge detected", "PLC1", "Comm")
    add_tag("Nut_Reset_Eff_Old", "Bool", "%M83.2", "Old value of Reset button", "PLC1", "Comm")
    add_tag("Nut_Reset_Eff_Edge", "Bool", "%M84.0", "Reset command edge detected", "PLC1", "Comm")
    add_tag("Nut_EStop_Eff_Old", "Bool", "%M83.3", "Old value of EStop button", "PLC1", "Comm")
    add_tag("Nut_EStop_Eff_Edge", "Bool", "%M84.1", "EStop command edge detected", "PLC1", "Comm")
    add_tag("Pump3265_Chuyen_Nhanh2_Cmd_Old", "Bool", "%M83.4", "Old value of Transfer command", "PLC1", "Comm")
    add_tag("Pump3265_Chuyen_Nhanh2_Cmd_Edge", "Bool", "%M84.2", "Transfer command edge detected", "PLC1", "Comm")
    add_tag("PLC1_Load_Default_Cmd_Old", "Bool", "%M83.5", "Old value of Load Recipe command", "PLC1", "Comm")
    add_tag("PLC1_Load_Default_Cmd_Edge", "Bool", "%M84.3", "Load Recipe command edge detected", "PLC1", "Comm")
    add_tag("MB_TCP_Any_Cmd_Edge", "Bool", "%M84.4", "Any handshake command edge detected", "PLC1", "Comm")

    # Modbus TCP Server tags (PLC2)
    add_tag("PLC2_Last_CmdSeq", "Int", "%MW80", "Last processed command sequence", "PLC2", "Comm")
    add_tag("PLC2_CmdSeq_New", "Bool", "%M82.0", "New command sequence received", "PLC2", "Comm")
    add_tag("MB_TCP_Server_Error", "Bool", "%M82.1", "Modbus TCP Server Error", "PLC2", "Comm")
    add_tag("MB_TCP_Server_Status", "Word", "%MW84", "Modbus TCP Server Status", "PLC2", "Comm")
    # NDR/DR moved below with AI_ prefix to avoid duplicate name


    # NDR/DR tags cho MB_SERVER output (PLC2)
    add_tag("MB_TCP_Server_NDR", "Bool", "%M82.2", "Modbus TCP Server New Data Received flag", "PLC2", "Comm")
    add_tag("MB_TCP_Server_DR", "Bool", "%M82.3", "Modbus TCP Server Data Read flag", "PLC2", "Comm")

    for name, comment in [
        ("PLC1_Tip_Bon1_Xong_HMI", "Nút mô phỏng tip Bồn 1 đã hoàn tất"),
        ("PLC1_Khuay_Bon1_Xong_HMI", "Nút mô phỏng hết thời gian khuấy Bồn 1"),
        ("PLC1_Tip_Bon2_Xong_HMI", "Nút mô phỏng tip Bồn 2 đã hoàn tất"),
        ("PLC1_Khuay_Thuan_Bon2_Xong_HMI", "Nút mô phỏng hết thời gian khuấy thuận Bồn 2"),
        ("PLC1_Khuay_Nghich_Bon2_Xong_HMI", "Nút mô phỏng hết thời gian khuấy ngược Bồn 2"),
        ("PLC1_Thanh_Trung_Bon2_Xong_HMI", "Nút mô phỏng hết thời gian thanh trùng Bồn 2"),
        ("PLC2_Tip_Bon3_Xong_HMI", "Nút mô phỏng tip Bồn 3 đã hoàn tất"),
        ("PLC2_Khuay_Bon3_Xong_HMI", "Nút mô phỏng hết thời gian khuấy Bồn 3"),
        ("PLC2_Tip_Bon4_Xong_HMI", "Nút mô phỏng tip Bồn 4 đã hoàn tất"),
        ("PLC2_Khuay_Thuan_Bon4_Xong_HMI", "Nút mô phỏng hết thời gian khuấy thuận Bồn 4"),
        ("PLC2_Khuay_Nghich_Bon4_Xong_HMI", "Nút mô phỏng hết thời gian khuấy ngược Bồn 4"),
        ("PLC2_Thanh_Trung_Bon4_Xong_HMI", "Nút mô phỏng hết thời gian thanh trùng Bồn 4"),
        ("BonChua_Nhan_Dich_Xong_HMI", "Nút mô phỏng nhận dịch vào Bồn chứa 01 xong"),
        ("BonChua_Chuyen_Bon2_Xong_HMI", "Nút mô phỏng chuyển sang Bồn chứa 02 xong"),
    ]:
        add_hmi_bool(name, comment, "Shared", "HMI_Simulation")

    for name, comment in [
        ("HMI_SP_PLC1_Nuoc_Bon1", "Lượng nước dosing Bồn 1"),
        ("HMI_SP_PLC1_Nuoc_Bon2", "Lượng nước dosing bổ sung Bồn 2"),
        ("HMI_SP_PLC1_Toc_Do_Bon1", "Tốc độ khuấy Bồn 1"),
        ("HMI_SP_PLC1_Toc_Do_Bon2_Main", "Tốc độ khuấy chính Bồn 2"),
        ("HMI_SP_PLC1_Nhiet_Do_Bon2", "Setpoint nhiệt/PID Bồn 2"),
        ("HMI_SP_PLC2_Nuoc_Bon3", "Lượng nước dosing Bồn 3"),
        ("HMI_SP_PLC2_Nuoc_Bon4", "Lượng nước dosing bổ sung Bồn 4"),
        ("HMI_SP_PLC2_Toc_Do_Bon3", "Tốc độ khuấy Bồn 3"),
        ("HMI_SP_PLC2_Toc_Do_Bon4_Main", "Tốc độ khuấy chính Bồn 4"),
        ("HMI_SP_PLC2_Nhiet_Do_Bon4", "Setpoint nhiệt/PID mô phỏng Bồn 4"),
        ("HMI_SP_BonChua1_Nhiet_Giai_Nhiet", "Nhiệt độ giải nhiệt đích Bồn chứa 01"),
        ("HMI_SP_Loc_Ap_Suat_Max", "Ngưỡng áp suất cao trước màng lọc"),
    ]:
        add_real(name, comment, "Shared", "HMI_Setpoint")

    for name, comment in [
        ("HMI_SP_Time_Khuay_Bon1", "Thời gian khuấy Bồn 1"),
        ("HMI_SP_Time_Khuay_Bon3", "Thời gian khuấy Bồn 3"),
        ("HMI_SP_Time_Fwd", "Thời gian khuấy chiều thuận"),
        ("HMI_SP_Time_Rev", "Thời gian khuấy chiều ngược"),
        ("HMI_SP_Time_Sterilize", "Thời gian giữ nhiệt thanh trùng"),
    ]:
        add_time(name, comment, "Shared", "HMI_Setpoint")

    for name, comment in [
        ("PLC1_Khuay_Bon1_Xong", "Trạng thái tự động xong khuấy Bồn 1"),
        ("PLC1_Khuay_Thuan_Bon2_Xong", "Trạng thái tự động xong khuấy thuận Bồn 2"),
        ("PLC1_Khuay_Nghich_Bon2_Xong", "Trạng thái tự động xong khuấy ngược Bồn 2"),
        ("PLC1_Thanh_Trung_Bon2_Xong", "Trạng thái tự động xong thanh trùng Bồn 2"),
        ("PLC2_Khuay_Bon3_Xong", "Trạng thái tự động xong khuấy Bồn 3"),
        ("PLC2_Khuay_Thuan_Bon4_Xong", "Trạng thái tự động xong khuấy thuận Bồn 4"),
        ("PLC2_Khuay_Nghich_Bon4_Xong", "Trạng thái tự động xong khuấy ngược Bồn 4"),
        ("PLC2_Thanh_Trung_Bon4_Xong", "Trạng thái tự động xong thanh trùng Bồn 4"),
        ("PLC1_Tip_Bon1_Auto_Done", "Trạng thái tự động xong tip Bồn 1"),
        ("PLC1_Tip_Bon2_Auto_Done", "Trạng thái tự động xong tip Bồn 2"),
        ("PLC2_Tip_Bon3_Auto_Done", "Trạng thái tự động xong tip Bồn 3"),
        ("PLC2_Tip_Bon4_Auto_Done", "Trạng thái tự động xong tip Bồn 4"),
        ("PLC1_Start_Edge_Old", "Cờ nhớ cạnh lên nút Start PLC1"),
        ("PLC1_Start_Edge_Edge", "Xung cạnh lên nút Start PLC1"),
        ("PLC2_Start_Edge_Old", "Cờ nhớ cạnh lên nút Start PLC2"),
        ("PLC2_Start_Edge_Edge", "Xung cạnh lên nút Start PLC2"),
    ]:
        add_bool(name, comment, "Shared", "Internal_Status")

    for name, comment in [
        ("PID_Bon2_Enable", "Cho phép PID Bồn 2"),
        ("PID_Bon2_ManualEnable", "Chế độ manual PID Bồn 2"),
        ("PID_Bon2_Error", "Lỗi khối PID Bồn 2"),
        ("PID_Bon2_Reset_Eff", "Reset hiệu dụng PID Bồn 2"),
        ("PID_Bon4_Enable", "Cho phép PID mô phỏng Bồn 4"),
        ("PID_Bon4_ManualEnable", "Chế độ manual PID Bồn 4"),
        ("PID_Bon4_Error", "Lỗi khối PID Bồn 4"),
        ("PID_Bon4_Reset_Eff", "Reset hiệu dụng PID Bồn 4"),
    ]:
        add_bool(name, comment, "Shared", "PID")

    for name, comment in [
        ("PID_Bon2_ErrorBits", "Mã lỗi DWORD PID Bồn 2"),
        ("PID_Bon4_ErrorBits", "Mã lỗi DWORD PID Bồn 4"),
    ]:
        add_tag(name, "DWord", internal_real.next(), comment, "Shared", "PID")

    for name, comment in [
        ("PID_Bon2_SP", "Setpoint đưa vào PID Bồn 2"),
        ("PID_Bon2_Err", "Sai lệch PID Bồn 2 = SP - PV"),
        ("PID_Bon2_CV", "Giá trị điều khiển PID Bồn 2"),
        ("PID_Bon2_ManualValue", "Giá trị manual PID Bồn 2"),
        ("PID_Bon4_SP", "Setpoint đưa vào PID mô phỏng Bồn 4"),
        ("PID_Bon4_Err", "Sai lệch PID mô phỏng Bồn 4 = SP - PV"),
        ("PID_Bon4_CV", "Giá trị điều khiển PID mô phỏng Bồn 4"),
        ("PID_Bon4_ManualValue", "Giá trị manual PID Bồn 4"),
        ("TT3219_Bon4_Sim", "Nhiệt độ mô phỏng nội bộ cho PID Bồn 4"),
        ("PID_Bon2_Temp_Inc", "Mức tăng nhiệt mô phỏng Bồn 2"),
        ("PID_Bon4_Tang_Nhiet_Buoc", "Mức tăng nhiệt mô phỏng mỗi chu kỳ OB31"),
        ("TT3219_Bon4_Target", "Nhiệt độ đích mô phỏng bồn 4"),
        ("TT3219_Bon4_Sim_Pure", "Nhiệt độ mô phỏng chưa có nhiễu bồn 4"),
        ("PID_Bon4_Temp_Val_1", "Biến tạm mô phỏng nhiệt độ 1"),
        ("PID_Bon4_Temp_Val_2", "Biến tạm mô phỏng nhiệt độ 2"),
        ("PID_Bon4_Sim_Counter", "Đồng hồ chu kỳ mô phỏng"),
        ("PID_Bon4_Sim_Angle", "Góc lượng giác nhiễu"),
        ("PID_Bon4_Sim_Sin", "Giá trị hình sin nhiễu"),
        ("PID_Bon4_Sim_Noise", "Giá trị nhiễu nhiệt độ"),
        ("PLC1_Tip_Bon1_Timer", "Bộ đếm thời gian mô phỏng tip bồn 1"),
        ("PLC1_Tip_Bon2_Timer", "Bộ đếm thời gian mô phỏng tip bồn 2"),
        ("PLC2_Tip_Bon3_Timer", "Bộ đếm thời gian mô phỏng tip bồn 3"),
        ("PLC2_Tip_Bon4_Timer", "Bộ đếm thời gian mô phỏng tip bồn 4"),
    ]:
        add_real(name, comment, "Shared", "PID")
    add_int("PID_Bon2_State", "Trạng thái khối PID Bồn 2", "PLC1", "PID")
    add_int("PID_Bon4_State", "Trạng thái khối PID Bồn 4", "PLC2", "PID")

    add_bool("PLC1_Stop_Active", "Tín hiệu dừng active PLC1", "PLC1", "Sequence")
    add_bool("PLC2_Stop_Active", "Tín hiệu dừng active PLC2", "PLC2", "Sequence")
    add_bool("VFD_Bon2_Khuay_Active", "Trạng thái khuấy Bồn 2 active", "PLC1", "Sequence")
    add_bool("VFD_Bon2_Should_Run", "Yêu cầu chạy VFD Bồn 2", "PLC1", "Sequence")
    add_bool("AGTR3263_Khuay_Active", "Trạng thái khuấy Bồn 4 active", "PLC2", "Sequence")
    add_bool("AGTR3263_Should_Run", "Yêu cầu chạy động cơ Bồn 4", "PLC2", "Sequence")

    # Simulation selectors
    add_bool("HMI_Use_Sim_Input_PLC1", "Cho phép sử dụng đầu vào mô phỏng PLC1", "PLC1", "HMI_Security")
    add_bool("HMI_Use_Sim_Input_PLC2", "Cho phép sử dụng đầu vào mô phỏng PLC2", "PLC2", "HMI_Security")
    add_bool("HMI_Use_Sim_Input_BonChua", "Cho phép sử dụng đầu vào mô phỏng Bồn chứa", "PLC1", "HMI_Security")

    # truyền thông Modbus TCP effective tags
    # Communication effective tags
    add_bool("PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff", "Cờ nhận trạng thái hoàn thành Nhánh 2 hiệu dụng", "PLC1", "Comm")
    add_bool("Pump3265_Chuyen_Nhanh2_Cmd_Nhan_Eff", "Lệnh chạy bơm chuyển Nhánh 2 nhận được hiệu dụng", "PLC2", "Comm")
    add_bool("PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_HMI_Gated", "Cờ nhận trạng thái hoàn thành Nhánh 2 HMI gated", "PLC1", "Comm")
    add_bool("Pump3265_Chuyen_Nhanh2_Cmd_Nhan_HMI_Gated", "Lệnh chạy bơm chuyển Nhánh 2 HMI gated", "PLC2", "Comm")

    # Setpoint validation & Init tags
    add_bool("PLC1_SP_Valid", "Setpoint PLC1 hợp lệ", "PLC1", "Sequence")
    add_bool("PLC2_SP_Valid", "Setpoint PLC2 hợp lệ", "PLC2", "Sequence")
    add_bool("BonChua_SP_Valid", "Setpoint Bồn chứa hợp lệ", "PLC1", "Bon_Chua_Loc")
    add_bool("PLC1_Loi_Setpoint", "Lỗi Setpoint PLC1", "PLC1", "Alarm")
    add_bool("PLC2_Loi_Setpoint", "Lỗi Setpoint PLC2", "PLC2", "Alarm")
    add_bool("BonChua_Loi_Setpoint", "Lỗi Setpoint Bồn chứa", "PLC1", "Alarm")
    add_bool("Init_Defaults_Done_PLC1", "Khởi tạo Setpoint mặc định PLC1 hoàn tất", "PLC1", "Sequence")
    add_bool("Init_Defaults_Done_PLC2", "Khởi tạo Setpoint mặc định PLC2 hoàn tất", "PLC2", "Sequence")
    add_bool("Init_Defaults_Done_BonChua", "Khởi tạo Setpoint mặc định Bồn chứa hoàn tất", "PLC1", "Bon_Chua_Loc")
    add_bool("Init_Trigger_PLC1", "Cờ kích hoạt nạp recipe mặc định PLC1", "PLC1", "Sequence")
    add_bool("Init_Trigger_PLC2", "Cờ kích hoạt nạp recipe mặc định PLC2", "PLC2", "Sequence")
    add_bool("Init_Trigger_BonChua", "Cờ kích hoạt nạp recipe mặc định Bồn chứa", "PLC1", "Bon_Chua_Loc")
    add_bool("HMI_Load_Default_Recipe", "Yêu cầu nạp lại Recipe mặc định từ HMI", "Shared", "PID")

    # Communication tags for Load Default handshake
    # PLC1 -> PLC2
    add_tag("PLC1_Load_Default_Cmd", "Bool", internal_bool.next(), "Lệnh nạp recipe mặc định gửi sang PLC2", "PLC1", "Comm")
    add_tag("PLC1_Load_Default_Cmd_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho lệnh nạp recipe mặc định PLC1", "PLC1", "Comm")
    physical_outputs.append(("PLC1_Load_Default_Cmd", "PLC1_Load_Default_Cmd_M", "Bool"))
    add_tag("PLC2_Load_Default_Cmd_Nhan", "Bool", internal_bool.next(), "Nhận lệnh nạp recipe mặc định từ PLC1", "PLC2", "Comm")
    add_tag("PLC2_Load_Default_Cmd_Nhan_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI cho nhận lệnh nạp recipe", "PLC2", "Comm")
    add_tag("PLC2_Load_Default_Cmd_Nhan_HMI_Gated", "Bool", internal_bool.next(), "Tín hiệu nhận lệnh nạp recipe HMI gated", "PLC2", "Comm")
    add_tag("PLC2_Load_Default_Cmd_Nhan_Eff", "Bool", internal_bool.next(), "Tín hiệu nhận lệnh nạp recipe hiệu dụng", "PLC2", "Comm")

    # PLC2 -> PLC1
    add_tag("PLC2_Load_Default_Done", "Bool", internal_bool.next(), "Báo nạp recipe mặc định xong gửi sang PLC1", "PLC2", "Comm")
    add_tag("PLC2_Load_Default_Done_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho báo nạp recipe xong PLC2", "PLC2", "Comm")
    physical_outputs.append(("PLC2_Load_Default_Done", "PLC2_Load_Default_Done_M", "Bool"))
    add_tag("PLC1_Load_Default_Done_Nhan", "Bool", internal_bool.next(), "Nhận báo nạp recipe xong từ PLC2", "PLC1", "Comm")
    add_tag("PLC1_Load_Default_Done_Nhan_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI cho nhận báo nạp recipe xong", "PLC1", "Comm")
    add_tag("PLC1_Load_Default_Done_Nhan_HMI_Gated", "Bool", internal_bool.next(), "Tín hiệu nhận báo nạp recipe xong HMI gated", "PLC1", "Comm")
    add_tag("PLC1_Load_Default_Done_Nhan_Eff", "Bool", internal_bool.next(), "Tín hiệu nhận báo nạp recipe xong hiệu dụng", "PLC1", "Comm")

    # Simulation mode and run enable tags
    add_bool("HMI_Sim_Mode", "Cho phép toàn bộ tín hiệu mô phỏng HMI tác động vào input hiệu dụng", "Shared", "HMI_Security")
    add_bool("HMI_Run_Enable", "Cho phép vận hành từ HMI ở chế độ thật", "Shared", "HMI_Security")
    add_bool("System_Mode_Real", "Hệ thống đang hoạt động ở chế độ thực tế", "Shared", "HMI_Security")
    add_bool("System_Mode_Sim", "Hệ thống đang hoạt động ở chế độ mô phỏng", "Shared", "HMI_Security")
    add_bool("HMI_Sim_Active_Warning", "Cảnh báo chế độ mô phỏng HMI đang hoạt động", "Shared", "HMI_Security")

    add_real("PID_Bon2_Kp_HMI", "HMI parameter for Kp PID Bồn 2", "PLC1", "PID")
    add_real("PID_Bon2_Ti_HMI", "HMI parameter for Ti PID Bồn 2", "PLC1", "PID")
    add_real("PID_Bon4_Kp_HMI", "HMI parameter for Kp PID Bồn 4", "PLC2", "PID")
    add_real("PID_Bon4_Ti_HMI", "HMI parameter for Ti PID Bồn 4", "PLC2", "PID")


    add_bool("BonChua_Nhan_Dich_Xong_Nhanh1", "Nhận dịch xong từ Nhánh 1", "PLC1", "Storage")
    add_bool("BonChua_Nhan_Dich_Xong_Nhanh2", "Nhận dịch xong từ Nhánh 2", "PLC1", "Storage")

    # Heartbeat edge detection tags
    add_bool("Clock_1Hz_Last", "Trạng thái Clock 1Hz chu kỳ trước", "Shared", "Comm")
    add_bool("Clock_1Hz_Edge", "Xung cạnh lên của Clock 1Hz", "Shared", "Comm")

    # Heartbeat timeout tags
    add_int("PLC1_Heartbeat_Last", "Heartbeat PLC1 chu kỳ trước", "PLC2", "Comm")
    add_bool("PLC1_Heartbeat_Changed", "Cờ heartbeat PLC1 thay đổi", "PLC2", "Comm")
    add_bool("PLC2_Heartbeat_Timeout", "Lỗi timeout heartbeat PLC1", "PLC2", "Comm")

    add_int("PLC2_Heartbeat_Last", "Heartbeat PLC2 chu kỳ trước", "PLC1", "Comm")
    add_bool("PLC2_Heartbeat_Changed", "Cờ heartbeat PLC2 thay đổi", "PLC1", "Comm")
    add_bool("PLC1_Heartbeat_Timeout", "Lỗi timeout heartbeat PLC2", "PLC1", "Comm")

    # VFD Modbus Single Call scheduler tags
    add_bool("VFD_Bon2_MB_Req", "REQ cho VFD Modbus", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_Mode", "USInt", "%MB500", "MODE cho VFD Modbus", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_DataAddr", "UDInt", "%MD504", "DATA_ADDR cho VFD Modbus", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_DataLen", "UInt", "%MW508", "DATA_LEN cho VFD Modbus", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_DataBuffer", "Word", "%MW510", "Buffer dữ liệu cho VFD Modbus", "PLC1", "VFD")

    # Agitator animation frame tags
    add_int("HMI_Anim_Bon1_Frame", "Khung hình animation cánh khuấy Bồn 1 (0..7)", "PLC1", "HMI")
    add_int("HMI_Anim_Bon2_Frame", "Khung hình animation cánh khuấy Bồn 2 (0..7)", "PLC1", "HMI")
    add_int("HMI_Anim_Bon3_Frame", "Khung hình animation cánh khuấy Bồn 3 (0..7)", "PLC2", "HMI")
    add_int("HMI_Anim_Bon4_Frame", "Khung hình animation cánh khuấy Bồn 4 (0..7)", "PLC2", "HMI")

    # Level state animation tags
    add_int("HMI_Anim_Bon1_MucDich", "Hình trạng thái mức dịch Bồn 1 (0..2)", "PLC1", "HMI")
    add_int("HMI_Anim_Bon2_MucDich", "Hình trạng thái mức dịch Bồn 2 (0..2)", "PLC1", "HMI")
    add_int("HMI_Anim_BonChua1_MucDich", "Hình trạng thái mức dịch Bồn chứa 1 (0..2)", "PLC1", "HMI")
    add_int("HMI_Anim_BonChua2_MucDich", "Hình trạng thái mức dịch Bồn chứa 2 (0..2)", "PLC1", "HMI")
    add_int("HMI_Anim_Bon3_MucDich", "Hình trạng thái mức dịch Bồn 3 (0..2)", "PLC2", "HMI")
    add_int("HMI_Anim_Bon4_MucDich", "Hình trạng thái mức dịch Bồn 4 (0..2)", "PLC2", "HMI")

    # Tag nội bộ ảo cho Bồn 1 & Bồn 2 và contactor VFD Bồn 2
    add_bool("V3230_Nuoc_Bon1", "Van nước Bồn 1 (virtual)", "PLC1", "Bon_1_2")
    add_bool("V3230_Nuoc_Bon1_M", "Tag gương phản hồi HMI cho Van nước Bồn 1", "PLC1", "Bon_1_2")
    add_bool("VFD_Bon2_Run", "Lệnh chạy VFD Bồn 2 (virtual)", "PLC1", "Bon_1_2")
    add_bool("VFD_Bon2_Run_M", "Tag gương phản hồi HMI cho Lệnh chạy VFD Bồn 2", "PLC1", "Bon_1_2")
    add_bool("VFD_Bon2_Dao_Chieu", "Lệnh đảo chiều VFD Bồn 2 (virtual)", "PLC1", "Bon_1_2")
    add_bool("VFD_Bon2_Dao_Chieu_M", "Tag gương phản hồi HMI cho Lệnh đảo chiều VFD Bồn 2", "PLC1", "Bon_1_2")
    add_real("VFD_Bon2_Toc_Do_AO", "Tốc độ đặt VFD Bồn 2 (virtual)", "PLC1", "Bon_1_2")
    add_real("VFD_Bon2_Toc_Do_AO_M", "Tag gương phản hồi HMI cho Tốc độ đặt VFD Bồn 2", "PLC1", "Bon_1_2")
    add_bool("VFD_Bon2_Contactor_Delay_Done", "Trễ đóng contactor VFD Bồn 2 hoàn tất", "PLC1", "VFD")

    # Tag điều khiển tay Manual PLC1
    add_bool("PLC1_Manual_Mode_Active", "Cờ báo chế độ điều khiển tay PLC1 hoạt động", "PLC1", "Manual")
    add_bool("BonChua1_Xa_Xong", "Cụm bồn chứa - Bồn chứa 01 đã xả hết hoàn toàn", "PLC1", "Sequence")
    add_bool("BonChua2_Xa_Xong", "Cụm bồn chứa - Bồn chứa 02 đã xả hết hoàn toàn", "PLC1", "Sequence")

    # Thiết bị Bồn 1-2 (PLC1)
    add_bool("V3230_Nuoc_Bon1_Man", "Lệnh điều khiển tay van nước Bồn 1", "PLC1", "Manual")
    add_real("CV3201_Nuoc_Bon1_Man", "Giá trị mở tay van tuyến tính nước Bồn 1", "PLC1", "Manual")
    add_bool("AGTR3260_Khuay_Bon1_Man", "Lệnh điều khiển tay động cơ khuấy Bồn 1", "PLC1", "Manual")
    add_real("AGTR3260_Toc_Do_AO_Man", "Giá trị đặt tốc độ tay động cơ khuấy Bồn 1", "PLC1", "Manual")
    add_bool("V3232_Xa_Bon1_Man", "Lệnh điều khiển tay van xả đáy Bồn 1 số 1", "PLC1", "Manual")
    add_bool("V3233_Xa_Bon1_Man", "Lệnh điều khiển tay van xả đáy Bồn 1 số 2", "PLC1", "Manual")
    add_bool("V3234_Xa_Bon1_Man", "Lệnh điều khiển tay van xả đáy Bồn 1 số 3", "PLC1", "Manual")
    add_bool("V3235_Nuoc_Bon2_Man", "Lệnh điều khiển tay van nước Bồn 2", "PLC1", "Manual")
    add_real("CV3206_Hoi_Bon2_Man", "Giá trị mở tay van tuyến tính hơi Bồn 2", "PLC1", "Manual")
    add_bool("VFD_Bon2_Run_Man", "Lệnh điều khiển tay chạy VFD Bồn 2", "PLC1", "Manual")
    add_bool("VFD_Bon2_Dao_Chieu_Man", "Lệnh điều khiển tay đảo chiều VFD Bồn 2", "PLC1", "Manual")
    add_real("VFD_Bon2_Toc_Do_AO_Man", "Giá trị đặt tốc độ tay VFD Bồn 2", "PLC1", "Manual")
    add_bool("V3237_Xa_Bon2_Man", "Lệnh điều khiển tay van xả đáy Bồn 2 số 1", "PLC1", "Manual")
    add_bool("V3238_Xa_Bon2_Man", "Lệnh điều khiển tay van xả đáy Bồn 2 số 2", "PLC1", "Manual")
    add_bool("V3239_Xa_Bon2_Man", "Lệnh điều khiển tay van xả đáy Bồn 2 số 3", "PLC1", "Manual")
    add_bool("Pump3264_Chuyen_Nhanh1_Man", "Lệnh điều khiển tay bơm chuyển Nhánh 1", "PLC1", "Manual")

    # Thiết bị Bồn chứa và Lọc (PLC1)
    add_bool("V3331_Xa_BonChua1_Man", "Lệnh điều khiển tay van xả đáy Bồn chứa 1 số 1", "PLC1", "Manual")
    add_bool("V3332_Xa_BonChua1_Man", "Lệnh điều khiển tay van xả đáy Bồn chứa 1 số 2", "PLC1", "Manual")
    add_bool("Pump3361_LuanChuyen_BonChua1_Man", "Lệnh điều khiển tay bơm luân chuyển Bồn chứa 1", "PLC1", "Manual")
    add_bool("Pump3362_Xa_BonChua1_Man", "Lệnh điều khiển tay bơm xả Bồn chứa 1", "PLC1", "Manual")
    add_bool("V3333_DieuHuong_BonChua1_Man", "Lệnh điều khiển tay van điều hướng Bồn chứa 1 số 1", "PLC1", "Manual")
    add_bool("V3334_DieuHuong_BonChua1_Man", "Lệnh điều khiển tay van điều hướng Bồn chứa 1 số 2", "PLC1", "Manual")
    add_bool("V3335_DieuHuong_BonChua1_Man", "Lệnh điều khiển tay van điều hướng Bồn chứa 1 số 3", "PLC1", "Manual")
    add_real("CV3304_Nuoc_Lam_Mat_Man", "Giá trị mở tay van nước làm mát", "PLC1", "Manual")
    add_bool("V3338_Xa_BonChua2_Man", "Lệnh điều khiển tay van xả đáy Bồn chứa 2 số 1", "PLC1", "Manual")
    add_bool("V3339_Xa_BonChua2_Man", "Lệnh điều khiển tay van xả đáy Bồn chứa 2 số 2", "PLC1", "Manual")
    add_bool("Pump3364_Filter_Man", "Lệnh điều khiển tay bơm qua lọc CCP 1", "PLC1", "Manual")
    add_bool("Pump3365_Filter_Man", "Lệnh điều khiển tay bơm qua lọc CCP 2", "PLC1", "Manual")
    add_bool("V3340_Duong_Filter_Man", "Lệnh điều khiển tay van đường Filter 1", "PLC1", "Manual")
    add_bool("V3341_Duong_Filter_Man", "Lệnh điều khiển tay van đường Filter 2", "PLC1", "Manual")
    add_real("CV_Filler_Cap_Dich_Man", "Giá trị mở tay van cấp dịch chiết rót", "PLC1", "Manual")

    # Tag điều khiển tay Manual PLC2
    add_bool("PLC2_Manual_Mode_Active", "Cờ báo chế độ điều khiển tay PLC2 hoạt động", "PLC2", "Manual")
    add_bool("V3240_Nuoc_Bon3_Man", "Lệnh điều khiển tay van nước Bồn 3", "PLC2", "Manual")
    add_real("CV3211_Nuoc_Bon3_Man", "Giá trị mở tay van tuyến tính nước Bồn 3", "PLC2", "Manual")
    add_bool("AGTR3262_Khuay_Bon3_Man", "Lệnh điều khiển tay động cơ khuấy Bồn 3", "PLC2", "Manual")
    add_real("AGTR3262_Toc_Do_AO_Man", "Giá trị đặt tốc độ tay động cơ khuấy Bồn 3", "PLC2", "Manual")
    add_bool("V3242_Xa_Bon3_Man", "Lệnh điều khiển tay van xả đáy Bồn 3 số 1", "PLC2", "Manual")
    add_bool("V3243_Xa_Bon3_Man", "Lệnh điều khiển tay van xả đáy Bồn 3 số 2", "PLC2", "Manual")
    add_bool("V3244_Xa_Bon3_Man", "Lệnh điều khiển tay van xả đáy Bồn 3 số 3", "PLC2", "Manual")
    add_bool("V3245_Nuoc_Bon4_Man", "Lệnh điều khiển tay van nước Bồn 4", "PLC2", "Manual")
    add_real("CV3216_Hoi_Bon4_Man", "Giá trị mở tay van tuyến tính hơi Bồn 4", "PLC2", "Manual")
    add_bool("AGTR3263_Khuay_Bon4_Man", "Lệnh điều khiển tay động cơ khuấy Bồn 4", "PLC2", "Manual")
    add_bool("AGTR3263_Dao_Chieu_Man", "Lệnh điều khiển tay đảo chiều động cơ khuấy Bồn 4", "PLC2", "Manual")
    add_real("AGTR3263_Toc_Do_AO_Man", "Giá trị đặt tốc độ tay động cơ khuấy Bồn 4", "PLC2", "Manual")
    add_bool("V3247_Xa_Bon4_Man", "Lệnh điều khiển tay van xả đáy Bồn 4 số 1", "PLC2", "Manual")
    add_bool("V3248_Xa_Bon4_Man", "Lệnh điều khiển tay van xả đáy Bồn 4 số 2", "PLC2", "Manual")
    add_bool("V3249_Xa_Bon4_Man", "Lệnh điều khiển tay van xả đáy Bồn 4 số 3", "PLC2", "Manual")
    add_bool("Pump3265_Chuyen_Nhanh2_Man", "Lệnh điều khiển tay bơm chuyển Nhánh 2", "PLC2", "Manual")

    # === DUAL-MODE THI ĐẤU: Chế độ Tự động hóa vs Đấu nối ===
    add_int("HMI_Che_Do_Thi", "Chế độ thi: 0=Tự động hóa (PID→Van hơi CV3206), 1=Đấu nối (PID→VFD Bồn 2 thật)", "Shared", "HMI_Security")

    # === HYBRID VFD/PID - COMMAND SEPARATION ===
    # PID routing
    add_real("PID_Bon2_PV_Eff", "PV hiệu dụng cho PID Bồn 2: nhiệt độ (Mode 0) hoặc tốc độ VFD (Mode 1)", "PLC1", "PID")
    add_bool("PID_Bon2_Enable_Eff", "Enable hiệu dụng cho PID Bồn 2: theo State (Mode 0) hoặc HMI độc lập (Mode 1)", "PLC1", "PID")
    add_bool("HMI_PID_Bon2_Dau_Noi_Enable", "HMI bật PID Bồn 2 khi Đấu nối - độc lập với State machine", "PLC1", "PID")
    # VFD command separation
    add_bool("VFD_Bon2_Run_Cmd", "Lệnh chạy VFD Bồn 2 nội bộ (chưa qua safety gate)", "PLC1", "VFD")
    add_bool("VFD_Bon2_Dao_Chieu_Cmd", "Lệnh đảo chiều VFD Bồn 2 nội bộ (chưa qua safety gate)", "PLC1", "VFD")
    add_real("VFD_Bon2_Toc_Do_Cmd", "Setpoint tốc độ VFD Bồn 2 nội bộ (chưa qua safety gate)", "PLC1", "VFD")
    add_bool("HMI_VFD_Bon2_Comm_Enable", "HMI cho phép giao tiếp Modbus RS-485 với VFD Bồn 2", "PLC1", "VFD")
    add_bool("HMI_VFD_Bon2_Real_Enable", "HMI xác nhận cho phép xuất lệnh ra VFD vật lý Bồn 2", "PLC1", "VFD")
    add_bool("VFD_Bon2_Comm_Active", "PLC tính: Modbus RS-485 VFD Bồn 2 đang active", "PLC1", "VFD")
    add_bool("VFD_Bon2_Real_Active", "PLC tính: đủ điều kiện an toàn để xuất physical outputs VFD Bồn 2", "PLC1", "VFD")
    add_bool("VFD_Bon2_Run_Safe", "Lệnh chạy VFD Bồn 2 đã qua safety gate", "PLC1", "VFD")
    add_bool("VFD_Bon2_Comm_Active_Last", "Trạng thái VFD_Bon2_Comm_Active chu kỳ trước (rising edge)", "PLC1", "VFD")
    add_bool("VFD_Bon2_MBCL_Trigger", "Trigger khởi tạo MB_COMM_LOAD khi Comm_Active cạnh lên", "PLC1", "VFD")
    add_bool("VFD_Bon2_Comm_Ready", "Truyền thông VFD Bồn 2 sẵn sàng (MB_COMM_LOAD done)", "PLC1", "VFD")
    add_bool("VFD_Bon2_Mode_Invalid", "Chế độ thi HMI_Che_Do_Thi không hợp lệ", "PLC1", "VFD")
    add_bool("VFD_Bon2_MB_Error_Confirmed", "Lỗi truyền thông Modbus VFD Bồn 2 đã xác nhận (sau 3 lần)", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_Error_Counter", "Int", "%MW512", "Bộ đếm lỗi truyền thông liên tiếp VFD Bồn 2", "PLC1", "VFD")
    add_tag("VFD_Bon2_MB_Last_Status", "Word", "%MW514", "Trạng thái lỗi Modbus VFD Bồn 2 cuối cùng", "PLC1", "VFD")
    add_bool("VFD_Bon2_MB_Retry_Active", "Cờ báo đang trong thời gian chờ 200ms để retry truyền thông", "PLC1", "VFD")
    add_bool("VFD_Bon2_MB_Retry_Timer_Q", "Tín hiệu ngõ ra Timer retry 200ms", "PLC1", "VFD")
    add_bool("VFD_Bon2_MBCL_Active", "Trạng thái đang thực thi khởi tạo MB_COMM_LOAD", "PLC1", "VFD")
    add_bool("VFD_Bon2_MB_Error_Last", "Trạng thái lỗi Modbus VFD Bồn 2 chu kỳ trước (phát hiện cạnh lên)", "PLC1", "VFD")
    add_bool("VFD_Bon2_MB_Error_Edge", "Xung canh len phat hien loi Modbus VFD Bon 2", "PLC1", "VFD")

    # === Tags trung gian cho conversion Real→Int×10 (them vao cuoi de khong shift counter) ===
    # PLC2 pack SP/PV/CV → Int x10 → Word
    add_tag("PID_Bon4_SP_x10_Real", "Real", internal_real.next(), "SP x10 Real temp PLC2", "PLC2", "Comm")
    add_tag("PID_Bon4_SP_x10_Int", "Int", internal_int.next(), "SP x10 Int temp PLC2", "PLC2", "Comm")
    add_tag("PID_Bon4_PV_x10_Real", "Real", internal_real.next(), "PV x10 Real temp PLC2", "PLC2", "Comm")
    add_tag("PID_Bon4_PV_x10_Int", "Int", internal_int.next(), "PV x10 Int temp PLC2", "PLC2", "Comm")
    add_tag("PID_Bon4_CV_x10_Real", "Real", internal_real.next(), "CV x10 Real temp PLC2", "PLC2", "Comm")
    add_tag("PID_Bon4_CV_x10_Int", "Int", internal_int.next(), "CV x10 Int temp PLC2", "PLC2", "Comm")
    # PLC1 unpack Word → Int → Real ÷ 10
    add_tag("PID_Bon4_SP_Recv_Int", "Int", internal_int.next(), "SP recv Int temp PLC1", "PLC1", "Comm")
    add_tag("PID_Bon4_PV_Recv_Int", "Int", internal_int.next(), "PV recv Int temp PLC1", "PLC1", "Comm")
    add_tag("PID_Bon4_CV_Recv_Int", "Int", internal_int.next(), "CV recv Int temp PLC1", "PLC1", "Comm")

    # === Tags trung gian để pack/unpack Modbus TCP (tránh lỗi slice access trên DB/Temp) ===
    add_tag("AI_Temp_Pack_Word", "Word", "%MW2000", "Biến tạm để pack dữ liệu", "Shared", "Comm")
    add_tag("AI_Temp_Unpack_Word", "Word", "%MW2002", "Biến tạm để unpack dữ liệu", "Shared", "Comm")




def tag_xml(plc_filter: str = None) -> str:
    blocks: list[str] = []
    next_id = 1
    filtered_tags = tags
    if plc_filter:
        filtered_tags = [t for t in tags if t.plc in (plc_filter, "Shared")]
        
    for tag in filtered_tags:
        tag_id = next_id
        text_id = next_id + 1
        text_item_id = next_id + 2
        next_id += 3
        blocks.append(
            f'''      <SW.Tags.PlcTag ID="{tag_id}" CompositionName="Tags">
        <AttributeList>
          <DataTypeName>{escape(tag.dtype)}</DataTypeName>
          <ExternalAccessible>true</ExternalAccessible>
          <ExternalVisible>true</ExternalVisible>
          <ExternalWritable>true</ExternalWritable>
          <LogicalAddress>{escape(tag.address)}</LogicalAddress>
          <Name>{escape(tag.name)}</Name>
        </AttributeList>
        <ObjectList>
          <MultilingualText ID="{text_id}" CompositionName="Comment">
            <ObjectList>
              <MultilingualTextItem ID="{text_item_id}" CompositionName="Items">
                <AttributeList>
                  <Culture>en-US</Culture>
                  <Text>{escape(tag.comment)}</Text>
                </AttributeList>
              </MultilingualTextItem>
            </ObjectList>
          </MultilingualText>
        </ObjectList>
      </SW.Tags.PlcTag>'''
        )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-06T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Tags.PlcTagTable ID="0">
    <AttributeList>
      <Name>PLC_Tags</Name>
    </AttributeList>
    <ObjectList>
{chr(10).join(blocks)}
    </ObjectList>
  </SW.Tags.PlcTagTable>
</Document>
'''


def reset_many(builder: TIALadderBuilder, trigger: str, bit_names: list[str], label: str) -> None:
    for bit in bit_names:
        builder.add_network(f"{label} - reset {bit}", [("NO", trigger), ("ResetCoil", bit)])


def cyclic_interrupt_xml(builder: TIALadderBuilder) -> str:
    return builder.generate_xml().replace(
        "<SecondaryType>ProgramCycle</SecondaryType>",
        "<SecondaryType>CyclicInterrupt</SecondaryType>",
    )


def build_manual_control_plc1() -> str:
    fc = TIALadderBuilder(fb_name="FC_Manual_Control_PLC1", block_id="62", block_type="FC")
    
    # 1. Xác định trạng thái Manual Mode Active
    fc.add_network("Xác định trạng thái Manual Mode Active PLC1", [
        ("NO", "HMI_Che_Do_Manual"),
        ("NO", "HMI_Cho_Phep_Sua_Thong_So"),
        ("CMP_GT_Int", "HMI_User_Level", "1"),
        ("Coil", "PLC1_Manual_Mode_Active")
    ])
    fc.add_network("Bypass Manual Mode Active PLC1", [
        ("NC", "HMI_Che_Do_Manual"),
        ("ResetCoil", "PLC1_Manual_Mode_Active")
    ])
    
    # 2. Reset Auto/PID/Sequence khi bật Manual
    fc.add_network("Reset Auto Enable khi bật Manual PLC1", [
        ("NO", "PLC1_Manual_Mode_Active"),
        ("ResetCoil", "PLC1_Auto_Enable")
    ])
    fc.add_network("Reset PID Enable khi bật Manual PLC1", [
        ("NO", "PLC1_Manual_Mode_Active"),
        ("ResetCoil", "PID_Bon2_Enable")
    ])
    fc.add_network("Reset State PLC1 khi bật Manual PLC1", [
        ("NO", "PLC1_Manual_Mode_Active"),
        ("MOVE", "0", "PLC1_State")
    ])
    fc.add_network("Reset State Bồn chứa khi bật Manual PLC1", [
        ("NO", "PLC1_Manual_Mode_Active"),
        ("MOVE", "0", "BonChua_State")
    ])

    # 3. Khi thoát Manual, reset toàn bộ tag _Man về 0
    man_bool_tags = [
        "V3230_Nuoc_Bon1_Man", "AGTR3260_Khuay_Bon1_Man", "V3232_Xa_Bon1_Man",
        "V3233_Xa_Bon1_Man", "V3234_Xa_Bon1_Man", "V3235_Nuoc_Bon2_Man",
        "VFD_Bon2_Run_Man", "VFD_Bon2_Dao_Chieu_Man", "V3237_Xa_Bon2_Man",
        "V3238_Xa_Bon2_Man", "V3239_Xa_Bon2_Man", "Pump3264_Chuyen_Nhanh1_Man",
        "V3331_Xa_BonChua1_Man", "V3332_Xa_BonChua1_Man", "Pump3361_LuanChuyen_BonChua1_Man",
        "Pump3362_Xa_BonChua1_Man", "V3333_DieuHuong_BonChua1_Man", "V3334_DieuHuong_BonChua1_Man",
        "V3335_DieuHuong_BonChua1_Man", "V3338_Xa_BonChua2_Man", "V3339_Xa_BonChua2_Man",
        "Pump3364_Filter_Man", "Pump3365_Filter_Man", "V3340_Duong_Filter_Man",
        "V3341_Duong_Filter_Man"
    ]
    for tag in man_bool_tags:
        fc.add_network(f"Reset {tag} khi thoát Manual", [
            ("NC", "PLC1_Manual_Mode_Active"),
            ("ResetCoil", tag)
        ])

    man_real_tags = [
        "CV3201_Nuoc_Bon1_Man", "AGTR3260_Toc_Do_AO_Man", "CV3206_Hoi_Bon2_Man",
        "VFD_Bon2_Toc_Do_AO_Man", "CV3304_Nuoc_Lam_Mat_Man", "CV_Filler_Cap_Dich_Man"
    ]
    for tag in man_real_tags:
        fc.add_network(f"Clear {tag} khi thoát Manual", [
            ("NC", "PLC1_Manual_Mode_Active"),
            ("MOVE", "0.0", tag)
        ])

    # 4. Clamp các giá trị AO Manual trước khi điều khiển
    for tag in man_real_tags:
        fc.add_network(f"Clamp dưới {tag} Manual", [
            ("CMP_LT", tag, "0.0"),
            ("MOVE", "0.0", tag)
        ])
        fc.add_network(f"Clamp trên {tag} Manual", [
            ("CMP_GT", tag, "100.0"),
            ("MOVE", "100.0", tag)
        ])

    # 5. Áp đặt điều khiển tay (DO và AO)
    # Van, motor thường (PLC1)
    regular_dos = [
        ("V3230_Nuoc_Bon1_Man", "V3230_Nuoc_Bon1"),
        ("AGTR3260_Khuay_Bon1_Man", "AGTR3260_Khuay_Bon1"),
        ("V3232_Xa_Bon1_Man", "V3232_Xa_Bon1"),
        ("V3233_Xa_Bon1_Man", "V3233_Xa_Bon1"),
        ("V3234_Xa_Bon1_Man", "V3234_Xa_Bon1"),
        ("V3235_Nuoc_Bon2_Man", "V3235_Nuoc_Bon2"),
        ("VFD_Bon2_Run_Man", "VFD_Bon2_Run_Cmd"),
        ("VFD_Bon2_Dao_Chieu_Man", "VFD_Bon2_Dao_Chieu_Cmd"),
        ("V3237_Xa_Bon2_Man", "V3237_Xa_Bon2"),
        ("V3238_Xa_Bon2_Man", "V3238_Xa_Bon2"),
        ("V3239_Xa_Bon2_Man", "V3239_Xa_Bon2"),
        ("V3331_Xa_BonChua1_Man", "V3331_Xa_BonChua1"),
        ("V3332_Xa_BonChua1_Man", "V3332_Xa_BonChua1"),
        ("V3333_DieuHuong_BonChua1_Man", "V3333_DieuHuong_BonChua1"),
        ("V3334_DieuHuong_BonChua1_Man", "V3334_DieuHuong_BonChua1"),
        ("V3335_DieuHuong_BonChua1_Man", "V3335_DieuHuong_BonChua1"),
        ("V3338_Xa_BonChua2_Man", "V3338_Xa_BonChua2"),
        ("V3339_Xa_BonChua2_Man", "V3339_Xa_BonChua2"),
        ("V3340_Duong_Filter_Man", "V3340_Duong_Filter"),
        ("V3341_Duong_Filter_Man", "V3341_Duong_Filter"),
    ]
    for man_tag, out_tag in regular_dos:
        fc.add_network(f"Manual {out_tag} - Set", [
            ("NO", "PLC1_Manual_Mode_Active"),
            ("NO", man_tag),
            ("SetCoil", out_tag)
        ])
        fc.add_network(f"Manual {out_tag} - Reset", [
            ("NO", "PLC1_Manual_Mode_Active"),
            ("NC", man_tag),
            ("ResetCoil", out_tag)
        ])

    # Van tuyến tính, tốc độ (AO)
    regular_aos = [
        ("CV3201_Nuoc_Bon1_Man", "CV3201_Nuoc_Bon1"),
        ("AGTR3260_Toc_Do_AO_Man", "AGTR3260_Toc_Do_AO"),
        ("CV3206_Hoi_Bon2_Man", "CV3206_Hoi_Bon2"),
        ("VFD_Bon2_Toc_Do_AO_Man", "VFD_Bon2_Toc_Do_Cmd"),
        ("CV3304_Nuoc_Lam_Mat_Man", "CV3304_Nuoc_Lam_Mat"),
        ("CV_Filler_Cap_Dich_Man", "CV_Filler_Cap_Dich"),
    ]
    for man_tag, ao_tag in regular_aos:
        fc.add_network(f"Manual {ao_tag}", [
            ("NO", "PLC1_Manual_Mode_Active"),
            ("MOVE", man_tag, ao_tag)
        ])

    # Các bơm có interlock dry-run (PLC1)
    pumps_with_interlocks = [
        ("Pump3264_Chuyen_Nhanh1_Man", "Pump3264_Chuyen_Nhanh1", "LT3209_Bon2_Eff", "Bơm chuyển Nhánh 1"),
        ("Pump3361_LuanChuyen_BonChua1_Man", "Pump3361_LuanChuyen_BonChua1", "LT3302_BonChua1_Eff", "Bơm luân chuyển Bồn chứa 1"),
        ("Pump3362_Xa_BonChua1_Man", "Pump3362_Xa_BonChua1", "LT3302_BonChua1_Eff", "Bơm xả Bồn chứa 1"),
        ("Pump3364_Filter_Man", "Pump3364_Filter", "LT3307_BonChua2_Eff", "Bơm lọc CCP 1"),
        ("Pump3365_Filter_Man", "Pump3365_Filter", "LT3307_BonChua2_Eff", "Bơm lọc CCP 2"),
    ]
    for man_tag, pump_tag, level_tag, comment in pumps_with_interlocks:
        fc.add_network(f"Manual {pump_tag} - Safe Reset", [
            ("NO", "PLC1_Manual_Mode_Active"),
            ("CMP_LE", level_tag, "0.5"),
            ("ResetCoil", man_tag)
        ])
        fc.add_network(f"Manual {pump_tag} - Output Reset", [
            ("NO", "PLC1_Manual_Mode_Active"),
            ("CMP_LE", level_tag, "0.5"),
            ("ResetCoil", pump_tag)
        ])
        fc.add_network(f"Manual {pump_tag} - Set", [
            ("NO", "PLC1_Manual_Mode_Active"),
            ("CMP_GT", level_tag, "0.5"),
            ("NO", man_tag),
            ("SetCoil", pump_tag)
        ])
        fc.add_network(f"Manual {pump_tag} - Reset", [
            ("NO", "PLC1_Manual_Mode_Active"),
            ("CMP_GT", level_tag, "0.5"),
            ("NC", man_tag),
            ("ResetCoil", pump_tag)
        ])

    # 6. Safety Overrides (Dừng khẩn / Dừng / Lỗi tổng)
    all_dos = [x[1] for x in regular_dos] + [x[1] for x in pumps_with_interlocks]
    for out_tag in all_dos:
        fc.add_network(f"Safety override - Reset {out_tag}", [
            ("OR3", "PLC1_EStop_Latch", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("ResetCoil", out_tag)
        ])
        if out_tag == "VFD_Bon2_Run_Cmd":
            man_tag = "VFD_Bon2_Run_Man"
        elif out_tag == "VFD_Bon2_Dao_Chieu_Cmd":
            man_tag = "VFD_Bon2_Dao_Chieu_Man"
        else:
            man_tag = out_tag + "_Man"
        fc.add_network(f"Safety override - Reset {man_tag}", [
            ("OR3", "PLC1_EStop_Latch", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("ResetCoil", man_tag)
        ])

    all_aos = [x[1] for x in regular_aos]
    for ao_tag in all_aos:
        fc.add_network(f"Safety override - Clear {ao_tag}", [
            ("OR3", "PLC1_EStop_Latch", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("MOVE", "0.0", ao_tag)
        ])
        if ao_tag == "VFD_Bon2_Toc_Do_Cmd":
            man_tag = "VFD_Bon2_Toc_Do_AO_Man"
        else:
            man_tag = ao_tag + "_Man"
        fc.add_network(f"Safety override - Clear {man_tag}", [
            ("OR3", "PLC1_EStop_Latch", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("MOVE", "0.0", man_tag)
        ])

    return fc.generate_xml()


def build_manual_control_plc2() -> str:
    fc = TIALadderBuilder(fb_name="FC_Manual_Control_PLC2", block_id="62", block_type="FC")
    
    # 1. Xác định trạng thái Manual Mode Active
    fc.add_network("Xác định trạng thái Manual Mode Active PLC2", [
        ("NO", "HMI_Che_Do_Manual"),
        ("NO", "HMI_Cho_Phep_Sua_Thong_So"),
        ("CMP_GT_Int", "HMI_User_Level", "1"),
        ("Coil", "PLC2_Manual_Mode_Active")
    ])
    fc.add_network("Bypass Manual Mode Active PLC2", [
        ("NC", "HMI_Che_Do_Manual"),
        ("ResetCoil", "PLC2_Manual_Mode_Active")
    ])
    
    # 2. Reset Auto/PID/Sequence khi bật Manual
    fc.add_network("Reset Auto Enable khi bật Manual PLC2", [
        ("NO", "PLC2_Manual_Mode_Active"),
        ("ResetCoil", "PLC2_Auto_Enable")
    ])
    fc.add_network("Reset PID Enable khi bật Manual PLC2", [
        ("NO", "PLC2_Manual_Mode_Active"),
        ("ResetCoil", "PID_Bon4_Enable")
    ])
    fc.add_network("Reset State PLC2 khi bật Manual PLC2", [
        ("NO", "PLC2_Manual_Mode_Active"),
        ("MOVE", "0", "PLC2_State")
    ])

    # 3. Khi thoát Manual, reset toàn bộ tag _Man về 0
    man_bool_tags = [
        "V3240_Nuoc_Bon3_Man", "AGTR3262_Khuay_Bon3_Man", "V3242_Xa_Bon3_Man",
        "V3243_Xa_Bon3_Man", "V3244_Xa_Bon3_Man", "V3245_Nuoc_Bon4_Man",
        "AGTR3263_Khuay_Bon4_Man", "AGTR3263_Dao_Chieu_Man", "V3247_Xa_Bon4_Man",
        "V3248_Xa_Bon4_Man", "V3249_Xa_Bon4_Man", "Pump3265_Chuyen_Nhanh2_Man"
    ]
    for tag in man_bool_tags:
        fc.add_network(f"Reset {tag} khi thoát Manual", [
            ("NC", "PLC2_Manual_Mode_Active"),
            ("ResetCoil", tag)
        ])

    man_real_tags = [
        "CV3211_Nuoc_Bon3_Man", "AGTR3262_Toc_Do_AO_Man", "CV3216_Hoi_Bon4_Man",
        "AGTR3263_Toc_Do_AO_Man"
    ]
    for tag in man_real_tags:
        fc.add_network(f"Clear {tag} khi thoát Manual", [
            ("NC", "PLC2_Manual_Mode_Active"),
            ("MOVE", "0.0", tag)
        ])

    # 4. Clamp các giá trị AO Manual trước khi điều khiển
    for tag in man_real_tags:
        fc.add_network(f"Clamp dưới {tag} Manual", [
            ("CMP_LT", tag, "0.0"),
            ("MOVE", "0.0", tag)
        ])
        fc.add_network(f"Clamp trên {tag} Manual", [
            ("CMP_GT", tag, "100.0"),
            ("MOVE", "100.0", tag)
        ])

    # 5. Áp đặt điều khiển tay (DO và AO)
    # Van, motor thường (PLC2)
    regular_dos = [
        ("V3240_Nuoc_Bon3_Man", "V3240_Nuoc_Bon3"),
        ("AGTR3262_Khuay_Bon3_Man", "AGTR3262_Khuay_Bon3"),
        ("V3242_Xa_Bon3_Man", "V3242_Xa_Bon3"),
        ("V3243_Xa_Bon3_Man", "V3243_Xa_Bon3"),
        ("V3244_Xa_Bon3_Man", "V3244_Xa_Bon3"),
        ("V3245_Nuoc_Bon4_Man", "V3245_Nuoc_Bon4"),
        ("AGTR3263_Khuay_Bon4_Man", "AGTR3263_Khuay_Bon4"),
        ("AGTR3263_Dao_Chieu_Man", "AGTR3263_Dao_Chieu"),
        ("V3247_Xa_Bon4_Man", "V3247_Xa_Bon4"),
        ("V3248_Xa_Bon4_Man", "V3248_Xa_Bon4"),
        ("V3249_Xa_Bon4_Man", "V3249_Xa_Bon4"),
    ]
    for man_tag, out_tag in regular_dos:
        fc.add_network(f"Manual {out_tag} - Set", [
            ("NO", "PLC2_Manual_Mode_Active"),
            ("NO", man_tag),
            ("SetCoil", out_tag)
        ])
        fc.add_network(f"Manual {out_tag} - Reset", [
            ("NO", "PLC2_Manual_Mode_Active"),
            ("NC", man_tag),
            ("ResetCoil", out_tag)
        ])

    # Van tuyến tính, tốc độ (AO)
    regular_aos = [
        ("CV3211_Nuoc_Bon3_Man", "CV3211_Nuoc_Bon3"),
        ("AGTR3262_Toc_Do_AO_Man", "AGTR3262_Toc_Do_AO"),
        ("CV3216_Hoi_Bon4_Man", "CV3216_Hoi_Bon4"),
        ("AGTR3263_Toc_Do_AO_Man", "AGTR3263_Toc_Do_AO"),
    ]
    for man_tag, ao_tag in regular_aos:
        fc.add_network(f"Manual {ao_tag}", [
            ("NO", "PLC2_Manual_Mode_Active"),
            ("MOVE", man_tag, ao_tag)
        ])

    # Bơm chuyển Nhánh 2 (PLC2)
    pumps_with_interlocks = [
        ("Pump3265_Chuyen_Nhanh2_Man", "Pump3265_Chuyen_Nhanh2", "LT3218_Bon4_Eff", "Bơm chuyển Nhánh 2"),
    ]
    for man_tag, pump_tag, level_tag, comment in pumps_with_interlocks:
        fc.add_network(f"Manual {pump_tag} - Safe Reset", [
            ("NO", "PLC2_Manual_Mode_Active"),
            ("CMP_LE", level_tag, "0.5"),
            ("ResetCoil", man_tag)
        ])
        fc.add_network(f"Manual {pump_tag} - Output Reset", [
            ("NO", "PLC2_Manual_Mode_Active"),
            ("CMP_LE", level_tag, "0.5"),
            ("ResetCoil", pump_tag)
        ])
        fc.add_network(f"Manual {pump_tag} - Set", [
            ("NO", "PLC2_Manual_Mode_Active"),
            ("CMP_GT", level_tag, "0.5"),
            ("NO", man_tag),
            ("SetCoil", pump_tag)
        ])
        fc.add_network(f"Manual {pump_tag} - Reset", [
            ("NO", "PLC2_Manual_Mode_Active"),
            ("CMP_GT", level_tag, "0.5"),
            ("NC", man_tag),
            ("ResetCoil", pump_tag)
        ])

    # 6. Safety Overrides (Dừng khẩn / Dừng / Lỗi tổng)
    all_dos = [x[1] for x in regular_dos] + [x[1] for x in pumps_with_interlocks]
    for out_tag in all_dos:
        fc.add_network(f"Safety override - Reset {out_tag}", [
            ("OR3", "PLC2_EStop_Latch", "PLC2_Stop_Active", "PLC2_Loi_Tong"),
            ("ResetCoil", out_tag)
        ])
        man_tag = out_tag + "_Man"
        fc.add_network(f"Safety override - Reset {man_tag}", [
            ("OR3", "PLC2_EStop_Latch", "PLC2_Stop_Active", "PLC2_Loi_Tong"),
            ("ResetCoil", man_tag)
        ])

    all_aos = [x[1] for x in regular_aos]
    for ao_tag in all_aos:
        fc.add_network(f"Safety override - Clear {ao_tag}", [
            ("OR3", "PLC2_EStop_Latch", "PLC2_Stop_Active", "PLC2_Loi_Tong"),
            ("MOVE", "0.0", ao_tag)
        ])
        man_tag = ao_tag + "_Man"
        fc.add_network(f"Safety override - Clear {man_tag}", [
            ("OR3", "PLC2_EStop_Latch", "PLC2_Stop_Active", "PLC2_Loi_Tong"),
            ("MOVE", "0.0", man_tag)
        ])

    return fc.generate_xml()


def build_init_default_recipe_plc1() -> str:
    fc = TIALadderBuilder(fb_name="FC_Init_Default_Recipe_PLC1", block_id="50", block_type="FC")
    
    # 1. Startup triggers
    fc.add_network("Kích hoạt nạp recipe mặc định lần đầu scan PLC1", [
        ("NC", "Init_Defaults_Done_PLC1"),
        ("SetCoil", "Init_Trigger_PLC1"),
    ])
    fc.add_network("Kích hoạt nạp recipe mặc định lần đầu scan Bồn chứa", [
        ("NC", "Init_Defaults_Done_BonChua"),
        ("SetCoil", "Init_Trigger_BonChua"),
    ])
    
    # 2. HMI triggers (sets PLC1, BonChua and triggers PLC2 via truyền thông Modbus TCP cmd)
    fc.add_network("Kích hoạt nạp recipe mặc định từ HMI", [
        ("NO", "HMI_Load_Default_Recipe"),
        ("SetCoil", "Init_Trigger_PLC1"),
    ])
    fc.add_network("Kích hoạt nạp recipe mặc định Bồn chứa từ HMI", [
        ("NO", "HMI_Load_Default_Recipe"),
        ("SetCoil", "Init_Trigger_BonChua"),
    ])
    fc.add_network("Gửi lệnh nạp recipe mặc định sang PLC2 từ HMI", [
        ("NO", "HMI_Load_Default_Recipe"),
        ("SetCoil", "PLC1_Load_Default_Cmd"),
    ])
    
    # 3. Nạp giá trị recipe mặc định PLC1
    fc.add_network("Nạp giá trị recipe mặc định PLC1", [
        ("NO", "Init_Trigger_PLC1"),
        ("MOVE", "100.0", "HMI_SP_PLC1_Nuoc_Bon1"),
        ("MOVE", "50.0", "HMI_SP_PLC1_Nuoc_Bon2"),
        ("MOVE", "60.0", "HMI_SP_PLC1_Toc_Do_Bon1"),
        ("MOVE", "80.0", "HMI_SP_PLC1_Toc_Do_Bon2_Main"),
        ("MOVE", "75.0", "HMI_SP_PLC1_Nhiet_Do_Bon2"),
        ("MOVE", "T#15S", "HMI_SP_Time_Khuay_Bon1"),
        ("MOVE", "T#10S", "HMI_SP_Time_Fwd"),
        ("MOVE", "T#10S", "HMI_SP_Time_Rev"),
        ("MOVE", "T#15S", "HMI_SP_Time_Sterilize"),
        ("SetCoil", "Init_Defaults_Done_PLC1"),
        ("ResetCoil", "Init_Trigger_PLC1"),
    ])
    
    # 4. Nạp giá trị recipe mặc định Bồn chứa
    fc.add_network("Nạp giá trị recipe mặc định Bồn chứa", [
        ("NO", "Init_Trigger_BonChua"),
        ("MOVE", "45.0", "HMI_SP_BonChua1_Nhiet_Giai_Nhiet"),
        ("MOVE", "2.5", "HMI_SP_Loc_Ap_Suat_Max"),
        ("SetCoil", "Init_Defaults_Done_BonChua"),
        ("ResetCoil", "Init_Trigger_BonChua"),
    ])
    
    # 5. PLC1 kết thúc quá trình nạp và reset lệnh HMI
    fc.add_network("PLC1 kết thúc nạp và reset lệnh HMI", [
        ("NO", "HMI_Load_Default_Recipe"),
        ("NC", "Init_Trigger_PLC1"),
        ("NC", "Init_Trigger_BonChua"),
        ("ResetCoil", "HMI_Load_Default_Recipe"),
    ])
    fc.add_network("PLC1 reset lệnh truyền thông nạp mặc định", [
        ("NO", "PLC1_Load_Default_Cmd"),
        ("NO", "PLC1_Load_Default_Done_Nhan_Eff"),
        ("ResetCoil", "PLC1_Load_Default_Cmd"),
    ])
    return fc.generate_xml()


def build_init_default_recipe_plc2() -> str:
    fc = TIALadderBuilder(fb_name="FC_Init_Default_Recipe_PLC2", block_id="51", block_type="FC")
    
    # 1. Startup triggers
    fc.add_network("Kích hoạt nạp recipe mặc định lần đầu scan PLC2", [
        ("NC", "Init_Defaults_Done_PLC2"),
        ("SetCoil", "Init_Trigger_PLC2"),
    ])
    
    # 2. PLC2 triggers when receiving command from PLC1
    fc.add_network("Kích hoạt nạp recipe mặc định PLC2 từ truyền thông Modbus TCP Cmd", [
        ("NO", "PLC2_Load_Default_Cmd_Nhan_Eff"),
        ("SetCoil", "Init_Trigger_PLC2"),
    ])
    
    # 3. Nạp giá trị recipe mặc định PLC2
    fc.add_network("Nạp giá trị recipe mặc định PLC2", [
        ("NO", "Init_Trigger_PLC2"),
        ("MOVE", "120.0", "HMI_SP_PLC2_Nuoc_Bon3"),
        ("MOVE", "60.0", "HMI_SP_PLC2_Nuoc_Bon4"),
        ("MOVE", "70.0", "HMI_SP_PLC2_Toc_Do_Bon3"),
        ("MOVE", "90.0", "HMI_SP_PLC2_Toc_Do_Bon4_Main"),
        ("MOVE", "95.0", "HMI_SP_PLC2_Nhiet_Do_Bon4"),
        ("MOVE", "T#15S", "HMI_SP_Time_Khuay_Bon3"),
        ("MOVE", "T#10S", "HMI_SP_Time_Fwd"),
        ("MOVE", "T#10S", "HMI_SP_Time_Rev"),
        ("MOVE", "T#15S", "HMI_SP_Time_Sterilize"),
        ("MOVE", "25.0", "TT3219_Bon4_Sim_Pure"),
        ("MOVE", "25.0", "TT3219_Bon4_Sim"),
        ("MOVE", "0.0", "PID_Bon4_Sim_Counter"),
        ("SetCoil", "Init_Defaults_Done_PLC2"),
        ("ResetCoil", "Init_Trigger_PLC2"),
    ])
    
    # 4. PLC2 báo nạp xong sang PLC1
    fc.add_network("PLC2 báo hoàn thành nạp recipe", [
        ("NO", "PLC2_Load_Default_Cmd_Nhan_Eff"),
        ("NC", "Init_Trigger_PLC2"),
        ("SetCoil", "PLC2_Load_Default_Done"),
    ])
    fc.add_network("PLC2 reset cờ hoàn thành nạp recipe", [
        ("NC", "PLC2_Load_Default_Cmd_Nhan_Eff"),
        ("ResetCoil", "PLC2_Load_Default_Done"),
    ])
    return fc.generate_xml()


def build_ob1() -> str:
    ob1 = TIALadderBuilder(fb_name="OB1_Main", block_id="1", block_type="OB")
    ob1.add_network("Gọi logic khởi tạo mặc định recipe PLC1", [("CALL_FC", "FC_Init_Default_Recipe_PLC1")])
    ob1.add_network("Gọi logic khởi tạo mặc định recipe PLC2", [("CALL_FC", "FC_Init_Default_Recipe_PLC2")])
    ob1.add_network("Gọi logic PLC1 Bồn 1-2", [("CALL_FC", "FC_PLC1_Mixing")])
    ob1.add_network("Gọi logic PLC2 Bồn 3-4", [("CALL_FC", "FC_PLC2_Mixing")])
    ob1.add_network("Gọi logic bồn chứa và lọc thành phẩm trên PLC1", [("CALL_FC", "FC_Bon_Chua_Loc")])
    ob1.add_network("Cập nhật mirror HMI cho PLC1", [("CALL_FC", "FC_HMI_Mirror_PLC1")])
    ob1.add_network("Cập nhật mirror HMI cho PLC2", [("CALL_FC", "FC_HMI_Mirror_PLC2")])
    return ob1.generate_xml()


def build_plc1() -> str:
    fc = TIALadderBuilder(fb_name="FC_PLC1_Mixing", block_id="10", block_type="FC")
    steps = [
        "PLC1_Step_Bon1_Dosing",
        "PLC1_Step_Bon1_Tip",
        "PLC1_Step_Bon1_Khuay",
        "PLC1_Step_Bon1_Xa",
        "PLC1_Step_Bon2_Dosing",
        "PLC1_Step_Bon2_Tip",
        "PLC1_Step_Bon2_Khuay_Thuan",
        "PLC1_Step_Bon2_Khuay_Nghich",
        "PLC1_Step_Bon2_PID",
        "PLC1_Step_Bon2_Thanh_Trung",
    ]

    # --- 1. Simulation Mapping (Digital & Analog) ---
    # Operator commands:
    fc.add_network("Khóa nút nhấn Start HMI qua Run Enable", [
        ("NO", "HMI_Run_Enable"),
        ("NO", "Nut_Khoi_Dong_HMI"),
        ("Coil", "Nut_Khoi_Dong_HMI_Gated"),
    ])
    fc.add_network("Tín hiệu khởi động hiệu dụng", [
        ("OR2", "Nut_Khoi_Dong", "Nut_Khoi_Dong_HMI_Gated"),
        ("Coil", "Nut_Khoi_Dong_Eff"),
    ])

    fc.add_network("Tín hiệu dừng hiệu dụng", [
        ("OR2", "Nut_Dung", "Nut_Dung_HMI"),
        ("Coil", "Nut_Dung_Eff"),
    ])

    fc.add_network("Tín hiệu reset hiệu dụng", [
        ("OR2", "Nut_Reset", "Nut_Reset_HMI"),
        ("Coil", "Nut_Reset_Eff"),
    ])
    fc.add_network("Tín hiệu reset hiệu dụng cho PID Bồn 2", [
        ("OR2", "Nut_Reset_Eff", "HMI_Reset_Alarm"),
        ("Coil", "PID_Bon2_Reset_Eff"),
    ])

    fc.add_network("Tín hiệu dừng khẩn hiệu dụng", [
        ("OR2", "Nut_EStop", "Nut_EStop_HMI"),
        ("Coil", "Nut_EStop_Eff"),
    ])

    # Sensors (digital):
    for tag in ["LS3202_Bon1_Cao", "PLC2_Me_Nhanh2_Hoan_Thanh_Nhan", "PLC1_Load_Default_Done_Nhan"]:
        fc.add_network(f"Gated HMI {tag} qua Sim Mode", [
            ("NO", "HMI_Sim_Mode"),
            ("NO", tag + "_HMI"),
            ("Coil", tag + "_HMI_Gated"),
        ])
        fc.add_network(f"Tín hiệu {tag} hiệu dụng", [
            ("OR2", tag, tag + "_HMI_Gated"),
            ("Coil", tag + "_Eff"),
        ])

    # Sensors (analog):
    for tag in ["FT3200_Bon1", "FQ3200_Bon1", "LT3203_Bon1", "TT3204_Bon1", "FT3205_Bon2", "FQ3205_Bon2", "LT3209_Bon2", "TT3208_Bon2"]:
        fc.add_network(f"Yêu cầu mô phỏng {tag} từ HMI", [
            ("OR2", "HMI_Use_Sim_Input_PLC1", tag + "_Use_HMI"),
            ("Coil", tag + "_Sim_Req"),
        ])
        fc.add_network(f"Kích hoạt mô phỏng {tag} khi ở chế độ Sim Mode", [
            ("NO", "HMI_Sim_Mode"),
            ("NO", tag + "_Sim_Req"),
            ("Coil", tag + "_Sim_Active"),
        ])
        fc.add_network(f"Đọc giá trị mô phỏng {tag} vào hiệu dụng", [
            ("NO", tag + "_Sim_Active"),
            ("MOVE", tag + "_HMI", tag + "_Eff"),
        ])
        fc.add_network(f"Đọc giá trị vật lý {tag} vào hiệu dụng", [
            ("NC", tag + "_Sim_Active"),
            ("MOVE", tag, tag + "_Eff"),
        ])

    # --- 1B. Setpoint Validation ---
    fc.add_network("Kiểm tra hợp lệ Setpoint PLC1", [
        ("CMP_GT", "HMI_SP_PLC1_Nuoc_Bon1", "0.0"),
        ("CMP_GT", "HMI_SP_PLC1_Nuoc_Bon2", "0.0"),
        ("CMP_GT", "HMI_SP_PLC1_Toc_Do_Bon1", "0.0"),
        ("CMP_GT", "HMI_SP_PLC1_Toc_Do_Bon2_Main", "0.0"),
        ("CMP_GT", "HMI_SP_PLC1_Nhiet_Do_Bon2", "0.0"),
        ("CMP_GT", "HMI_SP_Time_Khuay_Bon1", "T#0s"),
        ("CMP_GT", "HMI_SP_Time_Fwd", "T#0s"),
        ("CMP_GT", "HMI_SP_Time_Rev", "T#0s"),
        ("CMP_GT", "HMI_SP_Time_Sterilize", "T#0s"),
        ("Coil", "PLC1_SP_Valid"),
    ])
    # --- 2. Sequence Start / Auto Control (Rising Edge Start) ---
    fc.add_network("Nhận cạnh lên nút nhấn Start PLC1", [
        ("NO", "Nut_Khoi_Dong_Eff"),
        ("PBox", "PLC1_Start_Edge_Old"),
        ("Coil", "PLC1_Start_Edge_Edge"),
    ])
    fc.add_network("Khởi động chu trình PLC1 - Set Auto Enable", [
        ("CMP_EQ", "PLC1_State", "0"),
        ("NO", "PLC1_Start_Edge_Edge"),
        ("NC", "PLC1_Loi_Tong"),
        ("NO", "PLC1_SP_Valid"),
        ("SetCoil", "PLC1_Auto_Enable"),
    ])
    fc.add_network("Khởi động chu trình PLC1 - Chuyển sang State 10", [
        ("CMP_EQ", "PLC1_State", "0"),
        ("NO", "PLC1_Start_Edge_Edge"),
        ("NC", "PLC1_Loi_Tong"),
        ("NO", "PLC1_SP_Valid"),
        ("MOVE", "10", "PLC1_State"),
    ])
    fc.add_network("Báo lỗi setpoint PLC1 khi bấm Start", [
        ("NO", "PLC1_Start_Edge_Edge"),
        ("NC", "PLC1_Loi_Tong"),
        ("NC", "PLC1_SP_Valid"),
        ("SetCoil", "PLC1_Loi_Setpoint"),
    ])
    fc.add_network("Stop PLC1 từ nút vật lý hoặc HMI", [
        ("NO", "Nut_Dung_Eff"),
        ("MOVE", "0", "PLC1_State"),
    ])
    fc.add_network("Stop PLC1 - reset Auto Enable", [
        ("NO", "Nut_Dung_Eff"),
        ("ResetCoil", "PLC1_Auto_Enable"),
    ])

    # --- 3. Stop Active & Cleanup ---
    fc.add_network("Tạo tín hiệu Stop active PLC1", [
        ("NO", "Nut_Dung_Eff"),
        ("Coil", "PLC1_Stop_Active"),
    ])
    for out_tag in [
        "V3230_Nuoc_Bon1", "V3232_Xa_Bon1", "V3233_Xa_Bon1", "V3234_Xa_Bon1",
        "V3235_Nuoc_Bon2", "V3237_Xa_Bon2", "V3238_Xa_Bon2", "V3239_Xa_Bon2",
        "Pump3264_Chuyen_Nhanh1",
    ]:
        fc.add_network(f"Stop PLC1 - reset {out_tag}", [("NO", "PLC1_Stop_Active"), ("ResetCoil", out_tag)])
    fc.add_network("Stop PLC1 - reset PID Enable", [("NO", "PLC1_Stop_Active"), ("ResetCoil", "PID_Bon2_Enable")])
    for ao_tag in [
        "CV3201_Nuoc_Bon1", "AGTR3260_Toc_Do_AO", "CV3206_Hoi_Bon2",
    ]:
        fc.add_network(f"Stop PLC1 - clear {ao_tag}", [("NO", "PLC1_Stop_Active"), ("MOVE", "0.0", ao_tag)])
    
    # Dừng an toàn clear các VFD Cmds
    for cmd_tag in ["VFD_Bon2_Run_Cmd", "VFD_Bon2_Dao_Chieu_Cmd"]:
        fc.add_network(f"Stop PLC1 - reset {cmd_tag}", [("NO", "PLC1_Stop_Active"), ("ResetCoil", cmd_tag)])
    fc.add_network("Stop PLC1 - clear VFD_Bon2_Toc_Do_Cmd", [("NO", "PLC1_Stop_Active"), ("MOVE", "0.0", "VFD_Bon2_Toc_Do_Cmd")])

    # --- 4. Safety E-Stop & Alarm Logic ---
    fc.add_network("Chốt E-Stop PLC1", [
        ("NO", "Nut_EStop_Eff"),
        ("SetCoil", "PLC1_EStop_Latch"),
    ])
    # Reset E-Stop path 1 (Physical reset)
    fc.add_network("Reset chốt E-Stop PLC1 an toàn (Vật lý)", [
        ("NO", "Nut_Reset_Eff"),
        ("NC", "Nut_EStop_Eff"),
        ("ResetCoil", "PLC1_EStop_Latch"),
    ])
    # Reset E-Stop path 2 (HMI reset)
    fc.add_network("Reset chốt E-Stop PLC1 an toàn (HMI)", [
        ("NO", "HMI_Reset_Alarm"),
        ("NO", "HMI_Cho_Phep_Sua_Thong_So"),
        ("NC", "Nut_EStop_Eff"),
        ("ResetCoil", "PLC1_EStop_Latch"),
    ])

    fc.add_network("Mất truyền thông PLC1 - Giả lập HMI", [
        ("NO", "Gia_Lap_Mat_Ket_Noi_HMI"),
        ("NC", "HMI_Sim_Mode"),
        ("SetCoil", "PLC1_Loi_Truyen_Thong"),
    ])
    fc.add_network("Mất truyền thông PLC1 - Heartbeat Timeout", [
        ("NO", "PLC1_Heartbeat_Timeout"),
        ("NC", "HMI_Sim_Mode"),
        ("SetCoil", "PLC1_Loi_Truyen_Thong"),
    ])
    fc.add_network("Mất truyền thông PLC1 - Modbus TCP Error", [
        ("NO", "MB_TCP_ERROR"),
        ("NC", "HMI_Sim_Mode"),
        ("SetCoil", "PLC1_Loi_Truyen_Thong"),
    ])
    fc.add_network("Bản đồ trạng thái - Bồn 1 đã xả xong", [("CMP_EQ", "PLC1_State", "15"), ("CMP_LE", "LT3203_Bon1_Eff", "0.5"), ("Coil", "PLC1_Xa_Bon1_Xong")])
    fc.add_network("Bản đồ trạng thái - Bồn 2 đã xả xong", [("CMP_EQ", "PLC1_State", "40"), ("CMP_LE", "LT3209_Bon2_Eff", "0.5"), ("Coil", "PLC1_Xa_Bon2_Xong")])

    fc.add_network("Dry Run bơm Nhánh 1", [
        ("NO", "Pump3264_Chuyen_Nhanh1"),
        ("CMP_LE", "LT3209_Bon2_Eff", "0.5"),
        ("NC", "PLC1_Xa_Bon2_Xong"),
        ("SetCoil", "PLC1_Loi_Dry_Run"),
    ])
    fc.add_network("Dosing Bồn 1 lỗi quá 5 giây không có lưu lượng", [
        ("NO", "V3230_Nuoc_Bon1"),
        ("CMP_LE", "FT3200_Bon1_Eff", "0.01"),
        ("TON", "Timers_PLC1.Timer_Dosing_Bon1", "T#5S", "PLC1_Loi_Dosing"),
    ])
    fc.add_network("Dosing Bồn 2 lỗi quá 5 giây không có lưu lượng", [
        ("NO", "V3235_Nuoc_Bon2"),
        ("CMP_LE", "FT3205_Bon2_Eff", "0.01"),
        ("TON", "Timers_PLC1.Timer_Dosing_Bon2", "T#5S", "PLC1_Loi_Dosing"),
    ])
    for fault in ["PLC1_EStop_Latch", "PLC1_Loi_Dry_Run", "PLC1_Loi_Dosing", "PLC1_Loi_Truyen_Thong", "PLC1_Loi_Setpoint", "BonChua_Loi_Setpoint", "PID_Bon2_Error", "VFD_Bon2_MB_Error_Confirmed", "VFD_Bon2_MBCL_Error"]:
        ops = [("NO", fault)]
        if fault in ("VFD_Bon2_MB_Error_Confirmed", "VFD_Bon2_MBCL_Error"):
            ops.append(("NO", "VFD_Bon2_Comm_Active"))
        elif fault == "PID_Bon2_Error":
            ops.append(("NO", "PID_Bon2_Enable_Eff"))
        ops.append(("SetCoil", "PLC1_Loi_Tong"))
        fc.add_network(f"Tổng hợp lỗi PLC1 từ {fault}", ops)

    # Reset all alarms (Physical path)
    for alarm in ["PLC1_Loi_Tong", "PLC1_Loi_Dry_Run", "PLC1_Loi_Dosing", "PLC1_Loi_Truyen_Thong", "PID_Bon2_Error", "VFD_Bon2_MB_Error_Confirmed", "VFD_Bon2_MBCL_Error", "PLC1_Loi_Setpoint", "BonChua_Loi_Setpoint"]:
        fc.add_network(f"Reset {alarm} từ nút vật lý", [
            ("NO", "Nut_Reset_Eff"),
            ("NC", "PLC1_EStop_Latch"),
            ("NC", "Nut_EStop_Eff"),
            ("ResetCoil", alarm),
        ])
    # Reset all alarms (HMI path)
    for alarm in ["PLC1_Loi_Tong", "PLC1_Loi_Dry_Run", "PLC1_Loi_Dosing", "PLC1_Loi_Truyen_Thong", "PID_Bon2_Error", "VFD_Bon2_MB_Error_Confirmed", "VFD_Bon2_MBCL_Error", "PLC1_Loi_Setpoint", "BonChua_Loi_Setpoint"]:
        fc.add_network(f"Reset {alarm} từ HMI", [
            ("NO", "HMI_Reset_Alarm"),
            ("NO", "HMI_Cho_Phep_Sua_Thong_So"),
            ("NC", "PLC1_EStop_Latch"),
            ("NC", "Nut_EStop_Eff"),
            ("ResetCoil", alarm),
        ])

    fc.add_network("Lỗi PLC1 - Dừng State về 0", [
        ("NO", "PLC1_Loi_Tong"),
        ("MOVE", "0", "PLC1_State"),
    ])
    fc.add_network("Lỗi PLC1 - Reset Auto Enable", [
        ("NO", "PLC1_Loi_Tong"),
        ("ResetCoil", "PLC1_Auto_Enable"),
    ])
    fc.add_network("Lỗi PLC1 - Reset PID Enable", [
        ("NO", "PLC1_Loi_Tong"),
        ("ResetCoil", "PID_Bon2_Enable"),
    ])

    # --- 5. One-Hot State Mapping (CMP_EQ State to Boolean Step flags) ---
    fc.add_network("Bản đồ trạng thái - Dosing Bồn 1 (State 10)", [("CMP_EQ", "PLC1_State", "10"), ("Coil", "PLC1_Step_Bon1_Dosing")])
    fc.add_network("Bản đồ trạng thái - Tip Bồn 1 (State 11)", [("CMP_EQ", "PLC1_State", "11"), ("Coil", "PLC1_Step_Bon1_Tip")])
    fc.add_network("Bản đồ trạng thái - Khuấy Bồn 1 (State 12)", [("CMP_EQ", "PLC1_State", "12"), ("Coil", "PLC1_Step_Bon1_Khuay")])
    fc.add_network("Bản đồ trạng thái - Xả Bồn 1 (State 15)", [("CMP_EQ", "PLC1_State", "15"), ("Coil", "PLC1_Step_Bon1_Xa")])
    fc.add_network("Bản đồ trạng thái - Dosing Bồn 2 (State 20)", [("CMP_EQ", "PLC1_State", "20"), ("Coil", "PLC1_Step_Bon2_Dosing")])
    fc.add_network("Bản đồ trạng thái - Tip Bồn 2 (State 21)", [("CMP_EQ", "PLC1_State", "21"), ("Coil", "PLC1_Step_Bon2_Tip")])
    fc.add_network("Bản đồ trạng thái - Khuấy thuận Bồn 2 (State 22)", [("CMP_EQ", "PLC1_State", "22"), ("Coil", "PLC1_Step_Bon2_Khuay_Thuan")])
    fc.add_network("Bản đồ trạng thái - Khuấy nghịch Bồn 2 (State 23)", [("CMP_EQ", "PLC1_State", "23"), ("Coil", "PLC1_Step_Bon2_Khuay_Nghich")])
    fc.add_network("Bản đồ trạng thái - PID Bồn 2 (State 30)", [("CMP_EQ", "PLC1_State", "30"), ("Coil", "PLC1_Step_Bon2_PID")])
    fc.add_network("Bản đồ trạng thái - Thanh trùng Bồn 2 (State 31)", [("CMP_EQ", "PLC1_State", "31"), ("Coil", "PLC1_Step_Bon2_Thanh_Trung")])
    fc.add_network("Bản đồ trạng thái - Nhánh 1 Hoàn thành (State 40)", [("CMP_EQ", "PLC1_State", "40"), ("Coil", "PLC1_Me_Nhanh1_Hoan_Thanh")])

    # --- 6. Step Transitions in Reverse Scan Order ---
    fc.add_network("Chuyển về Idle - Reset Auto Enable PLC1 khi xả xong", [
        ("CMP_EQ", "PLC1_State", "40"),
        ("CMP_LE", "LT3209_Bon2_Eff", "0.5"),
        ("ResetCoil", "PLC1_Auto_Enable"),
    ])
    fc.add_network("Chuyển về Idle - Reset state PLC1 về 0 khi xả xong", [
        ("CMP_EQ", "PLC1_State", "40"),
        ("CMP_LE", "LT3209_Bon2_Eff", "0.5"),
        ("MOVE", "0", "PLC1_State"),
    ])
    
    fc.add_network("Hoàn thành Nhánh 1 - Tắt Auto Enable", [
        ("CMP_EQ", "PLC1_State", "31"),
        ("OR2", "PLC1_Thanh_Trung_Bon2_Xong", "PLC1_Thanh_Trung_Bon2_Xong_HMI"),
        ("ResetCoil", "PLC1_Auto_Enable"),
    ])
    fc.add_network("Hoàn thành Nhánh 1 - Tắt PID Enable", [
        ("CMP_EQ", "PLC1_State", "31"),
        ("OR2", "PLC1_Thanh_Trung_Bon2_Xong", "PLC1_Thanh_Trung_Bon2_Xong_HMI"),
        ("ResetCoil", "PID_Bon2_Enable"),
    ])
    fc.add_network("Hoàn thành Nhánh 1 - Chuyển sang State 40", [
        ("CMP_EQ", "PLC1_State", "31"),
        ("OR2", "PLC1_Thanh_Trung_Bon2_Xong", "PLC1_Thanh_Trung_Bon2_Xong_HMI"),
        ("MOVE", "40", "PLC1_State"),
    ])

    fc.add_network("Gia nhiệt Bồn 2 đạt SP - Chuyển sang State 31", [
        ("CMP_EQ", "PLC1_State", "30"),
        ("CMP_GE", "TT3208_Bon2_Eff", "HMI_SP_PLC1_Nhiet_Do_Bon2"),
        ("MOVE", "31", "PLC1_State"),
    ])

    fc.add_network("Hết khuấy ngược - Chuyển sang State 30", [
        ("CMP_EQ", "PLC1_State", "23"),
        ("OR2", "PLC1_Khuay_Nghich_Bon2_Xong", "PLC1_Khuay_Nghich_Bon2_Xong_HMI"),
        ("MOVE", "30", "PLC1_State"),
    ])

    fc.add_network("Hết khuấy thuận - Chuyển sang State 23", [
        ("CMP_EQ", "PLC1_State", "22"),
        ("OR2", "PLC1_Khuay_Thuan_Bon2_Xong", "PLC1_Khuay_Thuan_Bon2_Xong_HMI"),
        ("MOVE", "23", "PLC1_State"),
    ])

    fc.add_network("Tip Bồn 2 xong - Chuyển sang State 22", [
        ("CMP_EQ", "PLC1_State", "21"),
        ("OR2", "PLC1_Tip_Bon2_Auto_Done", "PLC1_Tip_Bon2_Xong_HMI"),
        ("MOVE", "22", "PLC1_State"),
    ])

    fc.add_network("Hoàn tất dosing Bồn 2 - Chuyển sang State 21", [
        ("CMP_EQ", "PLC1_State", "20"),
        ("CMP_GE", "FQ3205_Bon2_Eff", "HMI_SP_PLC1_Nuoc_Bon2"),
        ("MOVE", "21", "PLC1_State"),
    ])

    fc.add_network("Xả Bồn 1 xong - Chuyển sang State 20", [
        ("CMP_EQ", "PLC1_State", "15"),
        ("CMP_LE", "LT3203_Bon1_Eff", "0.5"),
        ("MOVE", "20", "PLC1_State"),
    ])

    fc.add_network("Khuấy Bồn 1 xong - Chuyển sang State 15", [
        ("CMP_EQ", "PLC1_State", "12"),
        ("OR2", "PLC1_Khuay_Bon1_Xong", "PLC1_Khuay_Bon1_Xong_HMI"),
        ("MOVE", "15", "PLC1_State"),
    ])

    fc.add_network("Tip Bồn 1 xong - Chuyển sang State 12", [
        ("CMP_EQ", "PLC1_State", "11"),
        ("OR2", "PLC1_Tip_Bon1_Auto_Done", "PLC1_Tip_Bon1_Xong_HMI"),
        ("MOVE", "12", "PLC1_State"),
    ])

    fc.add_network("Hoàn tất dosing Bồn 1 - Chuyển sang State 11", [
        ("CMP_EQ", "PLC1_State", "10"),
        ("CMP_GE", "FQ3200_Bon1_Eff", "HMI_SP_PLC1_Nuoc_Bon1"),
        ("MOVE", "11", "PLC1_State"),
    ])

    # --- 6B. TON Tip Timers & Agitator/Sterilize Timers ---
    fc.add_network("Timer đếm thời gian Tip Bồn 1", [
        ("NO", "PLC1_Step_Bon1_Tip"),
        ("TON", "Timers_PLC1.Timer_Tip_Bon1", "T#3S", "PLC1_Tip_Bon1_Auto_Done"),
    ])
    fc.add_network("Timer đếm thời gian Tip Bồn 2", [
        ("NO", "PLC1_Step_Bon2_Tip"),
        ("TON", "Timers_PLC1.Timer_Tip_Bon2", "T#3S", "PLC1_Tip_Bon2_Auto_Done"),
    ])

    fc.add_network("Reset FQ Bồn 1 khi không dosing", [("NC", "PLC1_Step_Bon1_Dosing"), ("MOVE", "0.0", "FQ3200_Bon1_HMI")])
    fc.add_network("Mở nước Bồn 1", [("NO", "PLC1_Step_Bon1_Dosing"), ("SetCoil", "V3230_Nuoc_Bon1")])
    fc.add_network("CV nước Bồn 1 mở 100 phần trăm", [("NO", "PLC1_Step_Bon1_Dosing"), ("MOVE", "100.0", "CV3201_Nuoc_Bon1")])
    fc.add_network("Đóng nước Bồn 1 sau dosing", [("NC", "PLC1_Step_Bon1_Dosing"), ("ResetCoil", "V3230_Nuoc_Bon1")])

    fc.add_network("Đặt tốc độ khuấy Bồn 1", [("NO", "PLC1_Step_Bon1_Khuay"), ("MOVE", "HMI_SP_PLC1_Toc_Do_Bon1", "AGTR3260_Toc_Do_AO")])
    fc.add_network("Timer đếm thời gian khuấy Bồn 1", [
        ("NO", "PLC1_Step_Bon1_Khuay"),
        ("TON", "Timers_PLC1.Timer_Khuay_Bon1", "HMI_SP_Time_Khuay_Bon1", "PLC1_Khuay_Bon1_Xong"),
    ])

    for valve in ["V3232_Xa_Bon1", "V3233_Xa_Bon1", "V3234_Xa_Bon1"]:
        fc.add_network(f"Mở {valve}", [("NO", "PLC1_Step_Bon1_Xa"), ("SetCoil", valve)])
    for valve in ["V3232_Xa_Bon1", "V3233_Xa_Bon1", "V3234_Xa_Bon1"]:
        fc.add_network(f"Đóng {valve}", [("NC", "PLC1_Step_Bon1_Xa"), ("ResetCoil", valve)])

    fc.add_network("Reset FQ Bồn 2 khi không dosing", [("NC", "PLC1_Step_Bon2_Dosing"), ("MOVE", "0.0", "FQ3205_Bon2_HMI")])
    fc.add_network("Mở nước Bồn 2", [("NO", "PLC1_Step_Bon2_Dosing"), ("SetCoil", "V3235_Nuoc_Bon2")])
    fc.add_network("Đóng nước Bồn 2", [("NC", "PLC1_Step_Bon2_Dosing"), ("ResetCoil", "V3235_Nuoc_Bon2")])

    fc.add_network("Tốc độ khuấy thuận Bồn 2 → VFD_Bon2_Toc_Do_Cmd (nội bộ)", [("NO", "PLC1_Step_Bon2_Khuay_Thuan"), ("MOVE", "HMI_SP_PLC1_Toc_Do_Bon2_Main", "VFD_Bon2_Toc_Do_Cmd")])
    fc.add_network("Timer đếm thời gian khuấy thuận Bồn 2", [
        ("NO", "PLC1_Step_Bon2_Khuay_Thuan"),
        ("TON", "Timers_PLC1.Timer_Khuay_Thuan_Bon2", "HMI_SP_Time_Fwd", "PLC1_Khuay_Thuan_Bon2_Xong"),
    ])

    fc.add_network("Timer đếm thời gian khuấy ngược Bồn 2", [
        ("NO", "PLC1_Step_Bon2_Khuay_Nghich"),
        ("TON", "Timers_PLC1.Timer_Khuay_Nghich_Bon2", "HMI_SP_Time_Rev", "PLC1_Khuay_Nghich_Bon2_Xong"),
    ])

    fc.add_network("Cho phép PID Bồn 2", [("NO", "PLC1_Step_Bon2_PID"), ("SetCoil", "PID_Bon2_Enable")])
    fc.add_network("Nạp SP PID Bồn 2", [("NO", "PLC1_Step_Bon2_PID"), ("MOVE", "HMI_SP_PLC1_Nhiet_Do_Bon2", "PID_Bon2_SP")])

    fc.add_network("Timer đếm thời gian thanh trùng Bồn 2", [
        ("NO", "PLC1_Step_Bon2_Thanh_Trung"),
        ("TON", "Timers_PLC1.Timer_Thanh_Trung_Bon2", "HMI_SP_Time_Sterilize", "PLC1_Thanh_Trung_Bon2_Xong"),
    ])

    # --- 6C. Reset stuck HMI Simulation done flags when leaving state ---
    fc.add_network("Reset HMI Tip Bồn 1 xong khi không ở State 11", [("CMP_NE", "PLC1_State", "11"), ("ResetCoil", "PLC1_Tip_Bon1_Xong_HMI")])
    fc.add_network("Reset HMI Khuấy Bồn 1 xong khi không ở State 12", [("CMP_NE", "PLC1_State", "12"), ("ResetCoil", "PLC1_Khuay_Bon1_Xong_HMI")])
    fc.add_network("Reset HMI Tip Bồn 2 xong khi không ở State 21", [("CMP_NE", "PLC1_State", "21"), ("ResetCoil", "PLC1_Tip_Bon2_Xong_HMI")])
    fc.add_network("Reset HMI Khuấy thuận Bồn 2 xong khi không ở State 22", [("CMP_NE", "PLC1_State", "22"), ("ResetCoil", "PLC1_Khuay_Thuan_Bon2_Xong_HMI")])
    fc.add_network("Reset HMI Khuấy ngược Bồn 2 xong khi không ở State 23", [("CMP_NE", "PLC1_State", "23"), ("ResetCoil", "PLC1_Khuay_Nghich_Bon2_Xong_HMI")])
    fc.add_network("Reset HMI Thanh trùng Bồn 2 xong khi không ở State 31", [("CMP_NE", "PLC1_State", "31"), ("ResetCoil", "PLC1_Thanh_Trung_Bon2_Xong_HMI")])

    # --- 7. Standard Coils for Motors & VFDs ---
    fc.add_network("Chạy cánh khuấy Bồn 1 (Coil thường)", [
        ("NO", "PLC1_Step_Bon1_Khuay"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "AGTR3260_Khuay_Bon1"),
    ])
    fc.add_network("Gom trạng thái khuấy thuận/ngược Bồn 2", [
        ("OR2", "PLC1_Step_Bon2_Khuay_Thuan", "PLC1_Step_Bon2_Khuay_Nghich"),
        ("Coil", "VFD_Bon2_Khuay_Active"),
    ])
    fc.add_network("Yêu cầu chạy VFD Bồn 2 bao gồm PID", [
        ("OR2", "VFD_Bon2_Khuay_Active", "PID_Bon2_Enable_Eff"),
        ("Coil", "VFD_Bon2_Should_Run"),
    ])
    # Sequence/Logic ghi _Cmd - KHÔNG ghi trực tiếp physical Q
    fc.add_network("Lệnh chạy VFD Bồn 2 → VFD_Bon2_Run_Cmd (nội bộ)", [
        ("NO", "VFD_Bon2_Should_Run"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "VFD_Bon2_Run_Cmd"),
    ])
    fc.add_network("Lệnh đảo chiều VFD Bồn 2 → VFD_Bon2_Dao_Chieu_Cmd (nội bộ)", [
        ("NO", "PLC1_Step_Bon2_Khuay_Nghich"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "VFD_Bon2_Dao_Chieu_Cmd"),
    ])

    fc.add_network("Mở van xả đáy Bồn 2 số 1 khi bơm chuyển Nhánh 1 chạy", [
        ("NO", "Pump3264_Chuyen_Nhanh1"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "V3237_Xa_Bon2"),
    ])
    fc.add_network("Mở van xả đáy Bồn 2 số 2 khi bơm chuyển Nhánh 1 chạy", [
        ("NO", "Pump3264_Chuyen_Nhanh1"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "V3238_Xa_Bon2"),
    ])
    fc.add_network("Mở van xả đáy Bồn 2 số 3 khi bơm chuyển Nhánh 1 chạy", [
        ("NO", "Pump3264_Chuyen_Nhanh1"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "V3239_Xa_Bon2"),
    ])

    # --- 8. AO Idle Cleanups, Safety Interlocks & Clamping ---
    # CV3201_Nuoc_Bon1
    fc.add_network("Reset CV nước Bồn 1 khi không dosing", [
        ("NC", "PLC1_Step_Bon1_Dosing"),
        ("MOVE", "0.0", "CV3201_Nuoc_Bon1"),
    ])
    fc.add_network("Reset CV nước Bồn 1 khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
        ("MOVE", "0.0", "CV3201_Nuoc_Bon1"),
    ])
    fc.add_network("Clamp CV nước Bồn 1 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "CV3201_Nuoc_Bon1", "0.0"),
        ("MOVE", "0.0", "CV3201_Nuoc_Bon1"),
    ])
    fc.add_network("Clamp CV nước Bồn 1 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "CV3201_Nuoc_Bon1", "100.0"),
        ("MOVE", "100.0", "CV3201_Nuoc_Bon1"),
    ])

    # AGTR3260_Toc_Do_AO
    fc.add_network("Reset tốc độ cánh khuấy Bồn 1 khi không khuấy", [
        ("NC", "PLC1_Step_Bon1_Khuay"),
        ("MOVE", "0.0", "AGTR3260_Toc_Do_AO"),
    ])
    fc.add_network("Reset tốc độ cánh khuấy Bồn 1 khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
        ("MOVE", "0.0", "AGTR3260_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ cánh khuấy Bồn 1 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AGTR3260_Toc_Do_AO", "0.0"),
        ("MOVE", "0.0", "AGTR3260_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ cánh khuấy Bồn 1 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AGTR3260_Toc_Do_AO", "100.0"),
        ("MOVE", "100.0", "AGTR3260_Toc_Do_AO"),
    ])

    # CV3206_Hoi_Bon2
    fc.add_network("Reset CV hơi Bồn 2 khi không chạy PID", [
        ("NC", "PID_Bon2_Enable_Eff"),
        ("MOVE", "0.0", "CV3206_Hoi_Bon2"),
    ])
    fc.add_network("Reset CV hơi Bồn 2 khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
        ("MOVE", "0.0", "CV3206_Hoi_Bon2"),
    ])
    fc.add_network("Clamp CV hơi Bồn 2 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "CV3206_Hoi_Bon2", "0.0"),
        ("MOVE", "0.0", "CV3206_Hoi_Bon2"),
    ])
    fc.add_network("Clamp CV hơi Bồn 2 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "CV3206_Hoi_Bon2", "100.0"),
        ("MOVE", "100.0", "CV3206_Hoi_Bon2"),
    ])

    # VFD_Bon2_Toc_Do_Cmd (lệnh nội bộ - FC_VFD_Bon2_Hybrid sẽ routing sang QD)
    fc.add_network("Reset VFD_Bon2_Toc_Do_Cmd khi không có lệnh chạy", [
        ("NC", "VFD_Bon2_Run_Cmd"),
        ("MOVE", "0.0", "VFD_Bon2_Toc_Do_Cmd"),
    ])
    fc.add_network("Reset VFD_Bon2_Toc_Do_Cmd khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
        ("MOVE", "0.0", "VFD_Bon2_Toc_Do_Cmd"),
    ])
    fc.add_network("Clamp VFD_Bon2_Toc_Do_Cmd trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "VFD_Bon2_Toc_Do_Cmd", "0.0"),
        ("MOVE", "0.0", "VFD_Bon2_Toc_Do_Cmd"),
    ])
    fc.add_network("Clamp VFD_Bon2_Toc_Do_Cmd trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "VFD_Bon2_Toc_Do_Cmd", "100.0"),
        ("MOVE", "100.0", "VFD_Bon2_Toc_Do_Cmd"),
    ])

    # Modbus RTU VFD Bon 2 Control Logic - đọc từ _Cmd tags, không từ physical Q
    fc.add_network("VFD Bon 2 Freq Scale: Cmd Speed x 5.0", [
        ("NO", "VFD_Bon2_Real_Active"),
        ("MOVE", "VFD_Bon2_Toc_Do_Cmd", "VFD_Bon2_Freq_Temp"),
        ("MATH_MUL_Real", "VFD_Bon2_Freq_Temp", "5.0", "VFD_Bon2_Freq_Temp")
    ])
    fc.add_network("VFD Bon 2 Freq Scale: Force 0.0 khi không Real_Active", [
        ("NC", "VFD_Bon2_Real_Active"),
        ("MOVE", "0.0", "VFD_Bon2_Freq_Temp")
    ])
    fc.add_network("VFD Bon 2 Freq Negate for Reverse Direction", [
        ("NO", "VFD_Bon2_Dao_Chieu_Cmd"),
        ("MATH_MUL_Real", "VFD_Bon2_Freq_Temp", "-1.0", "VFD_Bon2_Freq_Temp")
    ])
    fc.add_network("VFD Bon 2 Convert Freq Real to Int", [
        ("CONV_Convert", "VFD_Bon2_Freq_Temp", "VFD_Bon2_MB_FreqSetpoint", "Real", "Int")
    ])
    fc.add_network("VFD Bon 2 Control Word: Fault Reset (0x008F)", [
        ("OR2", "Nut_Reset_Eff", "HMI_Reset_Alarm"),
        ("MOVE", "143", "VFD_Bon2_MB_ControlWord")
    ])
    # Khi Real_Active: gửi Run command. Khi Comm_Active nhưng không Real_Active: gửi Stop Ready (speed=0)
    fc.add_network("VFD Bon 2 Control Word: Run Forward/Reverse (0x000F)", [
        ("NC", "Nut_Reset_Eff"),
        ("NC", "HMI_Reset_Alarm"),
        ("NO", "VFD_Bon2_Run_Cmd"),
        ("NO", "VFD_Bon2_Real_Active"),
        ("MOVE", "15", "VFD_Bon2_MB_ControlWord")
    ])
    fc.add_network("VFD Bon 2 Control Word: Stop Ready (0x0006) khi dừng hoặc chưa Real_Active", [
        ("NC", "Nut_Reset_Eff"),
        ("NC", "HMI_Reset_Alarm"),
        ("NO", "VFD_Bon2_Comm_Active"),
        ("NC", "VFD_Bon2_Run_Cmd"),
        ("MOVE", "6", "VFD_Bon2_MB_ControlWord")
    ])
    fc.add_network("VFD Bon 2 Control Word: Stop Ready khi Comm_Active nhưng không Real_Active", [
        ("NC", "Nut_Reset_Eff"),
        ("NC", "HMI_Reset_Alarm"),
        ("NO", "VFD_Bon2_Comm_Active"),
        ("NC", "VFD_Bon2_Real_Active"),
        ("MOVE", "6", "VFD_Bon2_MB_ControlWord")
    ])
    fc.add_network("VFD Bon 2 Actual Speed Convert Int to Real & Scale x 0.2", [
        ("CONV_Convert", "VFD_Bon2_MB_FreqActual", "VFD_Bon2_Actual_Speed_Feedback", "Int", "Real"),
        ("MATH_MUL_Real", "VFD_Bon2_Actual_Speed_Feedback", "0.2", "VFD_Bon2_Actual_Speed_Feedback")
    ])

    # Reset state to 0 when idle
    idle_conds = []
    for step in steps:
        idle_conds.append(("NC", step))
    idle_conds.append(("NC", "Pump3264_Chuyen_Nhanh1"))
    idle_conds.append(("NC", "PLC1_Me_Nhanh1_Hoan_Thanh"))
    idle_conds.append(("MOVE", "0", "PLC1_State"))
    fc.add_network("Reset state PLC1 về 0 khi ở chế độ Idle", idle_conds)

    # --- 9. Safety Outputs Reset ---
    for out_tag in [
        "V3230_Nuoc_Bon1", "V3232_Xa_Bon1", "V3233_Xa_Bon1",
        "V3234_Xa_Bon1", "V3235_Nuoc_Bon2",
        "V3237_Xa_Bon2", "V3238_Xa_Bon2", "V3239_Xa_Bon2", "Pump3264_Chuyen_Nhanh1",
    ]:
        fc.add_network(f"Dừng an toàn PLC1 reset {out_tag}", [("NO", "PLC1_Loi_Tong"), ("ResetCoil", out_tag)])

    # --- 10. VFD Bon 2 _Cmd Safety Clear khi lỗi tổng hoặc Stop active ---
    # Physical outputs được gating BỞI FC_VFD_Bon2_Hybrid (không ghi ở đây)
    # Chỉ clear _Cmd khi PLC1_Loi_Tong hoặc PLC1_Stop_Active để sequence không giữ stale command
    fc.add_network("Lỗi tổng hoặc Stop PLC1: Clear VFD_Bon2_Run_Cmd", [
        ("OR2", "PLC1_Loi_Tong", "PLC1_Stop_Active"),
        ("ResetCoil", "VFD_Bon2_Run_Cmd"),
    ])
    fc.add_network("Lỗi tổng hoặc Stop PLC1: Clear VFD_Bon2_Dao_Chieu_Cmd", [
        ("OR2", "PLC1_Loi_Tong", "PLC1_Stop_Active"),
        ("ResetCoil", "VFD_Bon2_Dao_Chieu_Cmd"),
    ])
    fc.add_network("Lỗi tổng hoặc Stop PLC1: Clear VFD_Bon2_Toc_Do_Cmd", [
        ("OR2", "PLC1_Loi_Tong", "PLC1_Stop_Active"),
        ("MOVE", "0.0", "VFD_Bon2_Toc_Do_Cmd"),
    ])

    # --- 11. Chế độ thi không hợp lệ (<0 hoặc >1) ---
    fc.add_network("Set VFD_Bon2_Mode_Invalid khi HMI_Che_Do_Thi < 0", [
        ("CMP_LT_Int", "HMI_Che_Do_Thi", "0"),
        ("SetCoil", "VFD_Bon2_Mode_Invalid"),
    ])
    fc.add_network("Set VFD_Bon2_Mode_Invalid khi HMI_Che_Do_Thi > 1", [
        ("CMP_GT_Int", "HMI_Che_Do_Thi", "1"),
        ("SetCoil", "VFD_Bon2_Mode_Invalid"),
    ])
    fc.add_network("Reset VFD_Bon2_Mode_Invalid khi HMI_Che_Do_Thi hợp lệ", [
        ("CMP_GE_Int", "HMI_Che_Do_Thi", "0"),
        ("CMP_LE_Int", "HMI_Che_Do_Thi", "1"),
        ("ResetCoil", "VFD_Bon2_Mode_Invalid"),
    ])
    fc.add_network("Reset PID_Bon2_Enable_Eff khi Mode không hợp lệ", [
        ("NO", "VFD_Bon2_Mode_Invalid"),
        ("ResetCoil", "PID_Bon2_Enable_Eff"),
    ])
    fc.add_network("Reset VFD_Bon2_Run_Cmd khi Mode không hợp lệ", [
        ("NO", "VFD_Bon2_Mode_Invalid"),
        ("ResetCoil", "VFD_Bon2_Run_Cmd"),
    ])
    fc.add_network("Reset VFD_Bon2_Dao_Chieu_Cmd khi Mode không hợp lệ", [
        ("NO", "VFD_Bon2_Mode_Invalid"),
        ("ResetCoil", "VFD_Bon2_Dao_Chieu_Cmd"),
    ])
    fc.add_network("Reset VFD_Bon2_Toc_Do_Cmd khi Mode không hợp lệ", [
        ("NO", "VFD_Bon2_Mode_Invalid"),
        ("MOVE", "0.0", "VFD_Bon2_Toc_Do_Cmd"),
    ])

    return fc.generate_xml()


def build_plc2() -> str:
    fc = TIALadderBuilder(fb_name="FC_PLC2_Mixing", block_id="20", block_type="FC")
    steps = [
        "PLC2_Step_Bon3_Dosing",
        "PLC2_Step_Bon3_Tip",
        "PLC2_Step_Bon3_Khuay",
        "PLC2_Step_Bon3_Xa",
        "PLC2_Step_Bon4_Dosing",
        "PLC2_Step_Bon4_Tip",
        "PLC2_Step_Bon4_Khuay_Thuan",
        "PLC2_Step_Bon4_Khuay_Nghich",
        "PLC2_Step_Bon4_PID_Mo_Phong",
        "PLC2_Step_Bon4_Thanh_Trung",
    ]

    # --- 1. Simulation Mapping (Digital & Analog) ---
    # Operator commands (received from PLC1):
    fc.add_network("Khóa nút nhấn Start HMI qua Run Enable PLC2", [
        ("NO", "HMI_Run_Enable"),
        ("NO", "Nut_Khoi_Dong_Nhan_HMI"),
        ("Coil", "Nut_Khoi_Dong_Nhan_HMI_Gated"),
    ])
    fc.add_network("Tín hiệu khởi động hiệu dụng PLC2", [
        ("OR2", "Nut_Khoi_Dong_Nhan", "Nut_Khoi_Dong_Nhan_HMI_Gated"),
        ("Coil", "Nut_Khoi_Dong_Nhan_Eff"),
    ])

    fc.add_network("Tín hiệu dừng hiệu dụng PLC2", [
        ("OR2", "Nut_Dung_Nhan", "Nut_Dung_Nhan_HMI"),
        ("Coil", "Nut_Dung_Nhan_Eff"),
    ])

    fc.add_network("Tín hiệu reset hiệu dụng PLC2", [
        ("OR2", "Nut_Reset_Nhan", "Nut_Reset_Nhan_HMI"),
        ("Coil", "Nut_Reset_Nhan_Eff"),
    ])
    fc.add_network("Tín hiệu reset hiệu dụng cho PID Bồn 4", [
        ("OR2", "Nut_Reset_Nhan_Eff", "HMI_Reset_Alarm"),
        ("Coil", "PID_Bon4_Reset_Eff"),
    ])

    fc.add_network("Tín hiệu dừng khẩn hiệu dụng PLC2", [
        ("OR2", "Nut_EStop_Nhan", "Nut_EStop_Nhan_HMI"),
        ("Coil", "Nut_EStop_Nhan_Eff"),
    ])

    # Sensors (digital):
    for tag in ["LS3217_Bon4_Cao", "Pump3265_Chuyen_Nhanh2_Cmd_Nhan", "PLC2_Load_Default_Cmd_Nhan"]:
        fc.add_network(f"Gated HMI {tag} qua Sim Mode", [
            ("NO", "HMI_Sim_Mode"),
            ("NO", tag + "_HMI"),
            ("Coil", tag + "_HMI_Gated"),
        ])
        fc.add_network(f"Tín hiệu {tag} hiệu dụng", [
            ("OR2", tag, tag + "_HMI_Gated"),
            ("Coil", tag + "_Eff"),
        ])

    # Sensors (analog):
    for tag in ["FT3210_Bon3", "FQ3210_Bon3", "LT3213_Bon3", "TT3214_Bon3", "FT3215_Bon4", "FQ3215_Bon4", "LT3218_Bon4", "TT3219_Bon4"]:
        fc.add_network(f"Yêu cầu mô phỏng {tag} từ HMI", [
            ("OR2", "HMI_Use_Sim_Input_PLC2", tag + "_Use_HMI"),
            ("Coil", tag + "_Sim_Req"),
        ])
        fc.add_network(f"Kích hoạt mô phỏng {tag} khi ở chế độ Sim Mode", [
            ("NO", "HMI_Sim_Mode"),
            ("NO", tag + "_Sim_Req"),
            ("Coil", tag + "_Sim_Active"),
        ])
        fc.add_network(f"Đọc giá trị mô phỏng {tag} vào hiệu dụng", [
            ("NO", tag + "_Sim_Active"),
            ("MOVE", tag + "_HMI", tag + "_Eff"),
        ])
        fc.add_network(f"Đọc giá trị vật lý {tag} vào hiệu dụng", [
            ("NC", tag + "_Sim_Active"),
            ("MOVE", tag, tag + "_Eff"),
        ])

    # --- 1B. Setpoint Validation ---
    fc.add_network("Kiểm tra hợp lệ Setpoint PLC2", [
        ("CMP_GT", "HMI_SP_PLC2_Nuoc_Bon3", "0.0"),
        ("CMP_GT", "HMI_SP_PLC2_Nuoc_Bon4", "0.0"),
        ("CMP_GT", "HMI_SP_PLC2_Toc_Do_Bon3", "0.0"),
        ("CMP_GT", "HMI_SP_PLC2_Toc_Do_Bon4_Main", "0.0"),
        ("CMP_GT", "HMI_SP_PLC2_Nhiet_Do_Bon4", "0.0"),
        ("CMP_GT", "HMI_SP_Time_Khuay_Bon3", "T#0s"),
        ("CMP_GT", "HMI_SP_Time_Fwd", "T#0s"),
        ("CMP_GT", "HMI_SP_Time_Rev", "T#0s"),
        ("CMP_GT", "HMI_SP_Time_Sterilize", "T#0s"),
        ("Coil", "PLC2_SP_Valid"),
    ])
    # --- 2. Sequence Start / Auto Control (Rising Edge Start) ---
    fc.add_network("Nhận cạnh lên nút nhấn Start PLC2", [
        ("NO", "Nut_Khoi_Dong_Nhan_Eff"),
        ("PBox", "PLC2_Start_Edge_Old"),
        ("Coil", "PLC2_Start_Edge_Edge"),
    ])
    fc.add_network("Khởi động chu trình PLC2 - Set Auto Enable", [
        ("CMP_EQ", "PLC2_State", "0"),
        ("NO", "PLC2_Start_Edge_Edge"),
        ("NC", "PLC2_Loi_Tong"),
        ("NO", "PLC2_SP_Valid"),
        ("SetCoil", "PLC2_Auto_Enable"),
    ])
    fc.add_network("Khởi động chu trình PLC2 - Chuyển sang State 10", [
        ("CMP_EQ", "PLC2_State", "0"),
        ("NO", "PLC2_Start_Edge_Edge"),
        ("NC", "PLC2_Loi_Tong"),
        ("NO", "PLC2_SP_Valid"),
        ("MOVE", "10", "PLC2_State"),
    ])
    fc.add_network("Báo lỗi setpoint PLC2 khi bấm Start", [
        ("NO", "PLC2_Start_Edge_Edge"),
        ("NC", "PLC2_Loi_Tong"),
        ("NC", "PLC2_SP_Valid"),
        ("SetCoil", "PLC2_Loi_Setpoint"),
    ])
    fc.add_network("Stop PLC2 từ HMI dùng chung", [
        ("NO", "Nut_Dung_Nhan_Eff"),
        ("MOVE", "0", "PLC2_State"),
    ])
    fc.add_network("Stop PLC2 - reset Auto Enable", [
        ("NO", "Nut_Dung_Nhan_Eff"),
        ("ResetCoil", "PLC2_Auto_Enable"),
    ])

    # --- 3. Stop Active & Cleanup ---
    fc.add_network("Tạo tín hiệu Stop active PLC2", [
        ("NO", "Nut_Dung_Nhan_Eff"),
        ("Coil", "PLC2_Stop_Active"),
    ])
    for out_tag in [
        "V3240_Nuoc_Bon3", "V3242_Xa_Bon3", "V3243_Xa_Bon3", "V3244_Xa_Bon3",
        "V3245_Nuoc_Bon4", "V3247_Xa_Bon4", "V3248_Xa_Bon4", "V3249_Xa_Bon4",
    ]:
        fc.add_network(f"Stop PLC2 - reset {out_tag}", [("NO", "PLC2_Stop_Active"), ("ResetCoil", out_tag)])
    fc.add_network("Stop PLC2 - reset PID Enable", [("NO", "PLC2_Stop_Active"), ("ResetCoil", "PID_Bon4_Enable")])
    for ao_tag in [
        "CV3211_Nuoc_Bon3", "AGTR3262_Toc_Do_AO", "CV3216_Hoi_Bon4", "AGTR3263_Toc_Do_AO",
    ]:
        fc.add_network(f"Stop PLC2 - clear {ao_tag}", [("NO", "PLC2_Stop_Active"), ("MOVE", "0.0", ao_tag)])

    # --- 4. Safety E-Stop & Alarm Logic ---
    fc.add_network("Chốt E-Stop PLC2", [
        ("NO", "Nut_EStop_Nhan_Eff"),
        ("SetCoil", "PLC2_EStop_Latch"),
    ])
    # Reset E-Stop path 1 (Physical reset)
    fc.add_network("Reset chốt E-Stop PLC2 an toàn (Vật lý)", [
        ("NO", "Nut_Reset_Nhan_Eff"),
        ("NC", "Nut_EStop_Nhan_Eff"),
        ("ResetCoil", "PLC2_EStop_Latch"),
    ])
    # Reset E-Stop path 2 (HMI reset)
    fc.add_network("Reset chốt E-Stop PLC2 an toàn (HMI)", [
        ("NO", "HMI_Reset_Alarm"),
        ("NO", "HMI_Cho_Phep_Sua_Thong_So"),
        ("NC", "Nut_EStop_Nhan_Eff"),
        ("ResetCoil", "PLC2_EStop_Latch"),
    ])

    fc.add_network("Mất truyền thông PLC2 - Giả lập HMI", [
        ("NO", "Gia_Lap_Mat_Ket_Noi_HMI"),
        ("NC", "HMI_Sim_Mode"),
        ("SetCoil", "PLC2_Loi_Truyen_Thong"),
    ])
    fc.add_network("Mất truyền thông PLC2 - Heartbeat Timeout", [
        ("NO", "PLC2_Heartbeat_Timeout"),
        ("NC", "HMI_Sim_Mode"),
        ("SetCoil", "PLC2_Loi_Truyen_Thong"),
    ])
    fc.add_network("Mất truyền thông PLC2 - Modbus TCP Server Error", [
        ("NO", "MB_TCP_Server_Error"),
        ("NC", "HMI_Sim_Mode"),
        ("SetCoil", "PLC2_Loi_Truyen_Thong"),
    ])
    fc.add_network("Bản đồ trạng thái - Bồn 3 đã xả xong", [("CMP_EQ", "PLC2_State", "15"), ("CMP_LE", "LT3213_Bon3_Eff", "0.5"), ("Coil", "PLC2_Xa_Bon3_Xong")])
    fc.add_network("Bản đồ trạng thái - Bồn 4 đã xả xong", [("CMP_EQ", "PLC2_State", "40"), ("CMP_LE", "LT3218_Bon4_Eff", "0.5"), ("Coil", "PLC2_Xa_Bon4_Xong")])

    fc.add_network("Dry Run bơm Nhánh 2", [
        ("NO", "Pump3265_Chuyen_Nhanh2"),
        ("CMP_LE", "LT3218_Bon4_Eff", "0.5"),
        ("NC", "PLC2_Xa_Bon4_Xong"),
        ("SetCoil", "PLC2_Loi_Dry_Run"),
    ])
    fc.add_network("Dosing Bồn 3 lỗi quá 5 giây không có lưu lượng", [
        ("NO", "V3240_Nuoc_Bon3"),
        ("CMP_LE", "FT3210_Bon3_Eff", "0.01"),
        ("TON", "Timers_PLC2.Timer_Dosing_Bon3", "T#5S", "PLC2_Loi_Dosing"),
    ])
    fc.add_network("Dosing Bồn 4 lỗi quá 5 giây không có lưu lượng", [
        ("NO", "V3245_Nuoc_Bon4"),
        ("CMP_LE", "FT3215_Bon4_Eff", "0.01"),
        ("TON", "Timers_PLC2.Timer_Dosing_Bon4", "T#5S", "PLC2_Loi_Dosing"),
    ])
    for fault in ["PLC2_EStop_Latch", "PLC2_Loi_Dry_Run", "PLC2_Loi_Dosing", "PLC2_Loi_Truyen_Thong", "PLC2_Loi_Setpoint", "PID_Bon4_Error"]:
        ops = [("NO", fault)]
        if fault == "PID_Bon4_Error":
            ops.append(("NO", "PID_Bon4_Enable"))
        ops.append(("SetCoil", "PLC2_Loi_Tong"))
        fc.add_network(f"Tổng hợp lỗi PLC2 từ {fault}", ops)

    # Reset all alarms (Physical path)
    for alarm in ["PLC2_Loi_Tong", "PLC2_Loi_Dry_Run", "PLC2_Loi_Dosing", "PLC2_Loi_Truyen_Thong", "PID_Bon4_Error", "PLC2_Loi_Setpoint"]:
        fc.add_network(f"Reset {alarm} từ nút vật lý", [
            ("NO", "Nut_Reset_Nhan_Eff"),
            ("NC", "PLC2_EStop_Latch"),
            ("NC", "Nut_EStop_Nhan_Eff"),
            ("ResetCoil", alarm),
        ])
    # Reset all alarms (HMI path)
    for alarm in ["PLC2_Loi_Tong", "PLC2_Loi_Dry_Run", "PLC2_Loi_Dosing", "PLC2_Loi_Truyen_Thong", "PID_Bon4_Error", "PLC2_Loi_Setpoint"]:
        fc.add_network(f"Reset {alarm} từ HMI", [
            ("NO", "HMI_Reset_Alarm"),
            ("NO", "HMI_Cho_Phep_Sua_Thong_So"),
            ("NC", "PLC2_EStop_Latch"),
            ("NC", "Nut_EStop_Nhan_Eff"),
            ("ResetCoil", alarm),
        ])

    fc.add_network("Lỗi PLC2 - Dừng State về 0", [
        ("NO", "PLC2_Loi_Tong"),
        ("MOVE", "0", "PLC2_State"),
    ])
    fc.add_network("Lỗi PLC2 - Reset Auto Enable", [
        ("NO", "PLC2_Loi_Tong"),
        ("ResetCoil", "PLC2_Auto_Enable"),
    ])
    fc.add_network("Lỗi PLC2 - Reset PID Enable", [
        ("NO", "PLC2_Loi_Tong"),
        ("ResetCoil", "PID_Bon4_Enable"),
    ])

    # --- 5. One-Hot State Mapping (CMP_EQ State to Boolean Step flags) ---
    fc.add_network("Bản đồ trạng thái - Dosing Bồn 3 (State 10)", [("CMP_EQ", "PLC2_State", "10"), ("Coil", "PLC2_Step_Bon3_Dosing")])
    fc.add_network("Bản đồ trạng thái - Tip Bồn 3 (State 11)", [("CMP_EQ", "PLC2_State", "11"), ("Coil", "PLC2_Step_Bon3_Tip")])
    fc.add_network("Bản đồ trạng thái - Khuấy Bồn 3 (State 12)", [("CMP_EQ", "PLC2_State", "12"), ("Coil", "PLC2_Step_Bon3_Khuay")])
    fc.add_network("Bản đồ trạng thái - Xả Bồn 3 (State 15)", [("CMP_EQ", "PLC2_State", "15"), ("Coil", "PLC2_Step_Bon3_Xa")])
    fc.add_network("Bản đồ trạng thái - Dosing Bồn 4 (State 20)", [("CMP_EQ", "PLC2_State", "20"), ("Coil", "PLC2_Step_Bon4_Dosing")])
    fc.add_network("Bản đồ trạng thái - Tip Bồn 4 (State 21)", [("CMP_EQ", "PLC2_State", "21"), ("Coil", "PLC2_Step_Bon4_Tip")])
    fc.add_network("Bản đồ trạng thái - Khuấy thuận Bồn 4 (State 22)", [("CMP_EQ", "PLC2_State", "22"), ("Coil", "PLC2_Step_Bon4_Khuay_Thuan")])
    fc.add_network("Bản đồ trạng thái - Khuấy nghịch Bồn 4 (State 23)", [("CMP_EQ", "PLC2_State", "23"), ("Coil", "PLC2_Step_Bon4_Khuay_Nghich")])
    fc.add_network("Bản đồ trạng thái - PID Bồn 4 (State 30)", [("CMP_EQ", "PLC2_State", "30"), ("Coil", "PLC2_Step_Bon4_PID_Mo_Phong")])
    fc.add_network("Bản đồ trạng thái - Thanh trùng Bồn 4 (State 31)", [("CMP_EQ", "PLC2_State", "31"), ("Coil", "PLC2_Step_Bon4_Thanh_Trung")])
    fc.add_network("Bản đồ trạng thái - Nhánh 2 Hoàn thành (State 40)", [("CMP_EQ", "PLC2_State", "40"), ("Coil", "PLC2_Me_Nhanh2_Hoan_Thanh")])

    # --- 6. Step Transitions in Reverse Scan Order ---
    fc.add_network("Chuyển về Idle - Reset Auto Enable PLC2 khi xả xong", [
        ("CMP_EQ", "PLC2_State", "40"),
        ("CMP_LE", "LT3218_Bon4_Eff", "0.5"),
        ("ResetCoil", "PLC2_Auto_Enable"),
    ])
    fc.add_network("Chuyển về Idle - Reset state PLC2 về 0 khi xả xong", [
        ("CMP_EQ", "PLC2_State", "40"),
        ("CMP_LE", "LT3218_Bon4_Eff", "0.5"),
        ("MOVE", "0", "PLC2_State"),
    ])
    
    fc.add_network("Hoàn thành Nhánh 2 - Tắt Auto Enable", [
        ("CMP_EQ", "PLC2_State", "31"),
        ("OR2", "PLC2_Thanh_Trung_Bon4_Xong", "PLC2_Thanh_Trung_Bon4_Xong_HMI"),
        ("ResetCoil", "PLC2_Auto_Enable"),
    ])
    fc.add_network("Hoàn thành Nhánh 2 - Tắt PID Enable", [
        ("CMP_EQ", "PLC2_State", "31"),
        ("OR2", "PLC2_Thanh_Trung_Bon4_Xong", "PLC2_Thanh_Trung_Bon4_Xong_HMI"),
        ("ResetCoil", "PID_Bon4_Enable"),
    ])
    fc.add_network("Hoàn thành Nhánh 2 - Chuyển sang State 40", [
        ("CMP_EQ", "PLC2_State", "31"),
        ("OR2", "PLC2_Thanh_Trung_Bon4_Xong", "PLC2_Thanh_Trung_Bon4_Xong_HMI"),
        ("MOVE", "40", "PLC2_State"),
    ])

    fc.add_network("Bồn 4 đạt nhiệt độ mô phỏng - Chuyển sang State 31", [
        ("CMP_EQ", "PLC2_State", "30"),
        ("CMP_GE", "TT3219_Bon4_Sim", "HMI_SP_PLC2_Nhiet_Do_Bon4"),
        ("MOVE", "31", "PLC2_State"),
    ])

    fc.add_network("Hết khuấy ngược Bồn 4 - Chuyển sang State 30", [
        ("CMP_EQ", "PLC2_State", "23"),
        ("OR2", "PLC2_Khuay_Nghich_Bon4_Xong", "PLC2_Khuay_Nghich_Bon4_Xong_HMI"),
        ("MOVE", "30", "PLC2_State"),
    ])

    fc.add_network("Hết khuấy thuận Bồn 4 - Chuyển sang State 23", [
        ("CMP_EQ", "PLC2_State", "22"),
        ("OR2", "PLC2_Khuay_Thuan_Bon4_Xong", "PLC2_Khuay_Thuan_Bon4_Xong_HMI"),
        ("MOVE", "23", "PLC2_State"),
    ])

    fc.add_network("Tip Bồn 4 xong - Chuyển sang State 22", [
        ("CMP_EQ", "PLC2_State", "21"),
        ("OR2", "PLC2_Tip_Bon4_Auto_Done", "PLC2_Tip_Bon4_Xong_HMI"),
        ("MOVE", "22", "PLC2_State"),
    ])

    fc.add_network("Hoàn tất dosing Bồn 4 - Chuyển sang State 21", [
        ("CMP_EQ", "PLC2_State", "20"),
        ("CMP_GE", "FQ3215_Bon4_Eff", "HMI_SP_PLC2_Nuoc_Bon4"),
        ("MOVE", "21", "PLC2_State"),
    ])

    fc.add_network("Xả Bồn 3 xong - Chuyển sang State 20", [
        ("CMP_EQ", "PLC2_State", "15"),
        ("CMP_LE", "LT3213_Bon3_Eff", "0.5"),
        ("MOVE", "20", "PLC2_State"),
    ])

    fc.add_network("Khuấy Bồn 3 xong - Chuyển sang State 15", [
        ("CMP_EQ", "PLC2_State", "12"),
        ("OR2", "PLC2_Khuay_Bon3_Xong", "PLC2_Khuay_Bon3_Xong_HMI"),
        ("MOVE", "15", "PLC2_State"),
    ])

    fc.add_network("Tip Bồn 3 xong - Chuyển sang State 12", [
        ("CMP_EQ", "PLC2_State", "11"),
        ("OR2", "PLC2_Tip_Bon3_Auto_Done", "PLC2_Tip_Bon3_Xong_HMI"),
        ("MOVE", "12", "PLC2_State"),
    ])

    fc.add_network("Hoàn tất dosing Bồn 3 - Chuyển sang State 11", [
        ("CMP_EQ", "PLC2_State", "10"),
        ("CMP_GE", "FQ3210_Bon3_Eff", "HMI_SP_PLC2_Nuoc_Bon3"),
        ("MOVE", "11", "PLC2_State"),
    ])

    # --- 6B. TON Tip Timers & Agitator/Sterilize Timers ---
    fc.add_network("Timer đếm thời gian Tip Bồn 3", [
        ("NO", "PLC2_Step_Bon3_Tip"),
        ("TON", "Timers_PLC2.Timer_Tip_Bon3", "T#3S", "PLC2_Tip_Bon3_Auto_Done"),
    ])
    fc.add_network("Timer đếm thời gian Tip Bồn 4", [
        ("NO", "PLC2_Step_Bon4_Tip"),
        ("TON", "Timers_PLC2.Timer_Tip_Bon4", "T#3S", "PLC2_Tip_Bon4_Auto_Done"),
    ])

    fc.add_network("Reset FQ Bồn 3 khi không dosing", [("NC", "PLC2_Step_Bon3_Dosing"), ("MOVE", "0.0", "FQ3210_Bon3_HMI")])
    fc.add_network("Mở nước Bồn 3", [("NO", "PLC2_Step_Bon3_Dosing"), ("SetCoil", "V3240_Nuoc_Bon3")])
    fc.add_network("CV nước Bồn 3 mở 100 phần trăm", [("NO", "PLC2_Step_Bon3_Dosing"), ("MOVE", "100.0", "CV3211_Nuoc_Bon3")])
    fc.add_network("Đóng nước Bồn 3 sau dosing", [("NC", "PLC2_Step_Bon3_Dosing"), ("ResetCoil", "V3240_Nuoc_Bon3")])

    fc.add_network("Đặt tốc độ khuấy Bồn 3", [("NO", "PLC2_Step_Bon3_Khuay"), ("MOVE", "HMI_SP_PLC2_Toc_Do_Bon3", "AGTR3262_Toc_Do_AO")])
    fc.add_network("Timer đếm thời gian khuấy Bồn 3", [
        ("NO", "PLC2_Step_Bon3_Khuay"),
        ("TON", "Timers_PLC2.Timer_Khuay_Bon3", "HMI_SP_Time_Khuay_Bon3", "PLC2_Khuay_Bon3_Xong"),
    ])

    for valve in ["V3242_Xa_Bon3", "V3243_Xa_Bon3", "V3244_Xa_Bon3"]:
        fc.add_network(f"Mở {valve}", [("NO", "PLC2_Step_Bon3_Xa"), ("SetCoil", valve)])
    for valve in ["V3242_Xa_Bon3", "V3243_Xa_Bon3", "V3244_Xa_Bon3"]:
        fc.add_network(f"Đóng {valve}", [("NC", "PLC2_Step_Bon3_Xa"), ("ResetCoil", valve)])

    fc.add_network("Reset FQ Bồn 4 khi không dosing", [("NC", "PLC2_Step_Bon4_Dosing"), ("MOVE", "0.0", "FQ3215_Bon4_HMI")])
    fc.add_network("Mở nước Bồn 4", [("NO", "PLC2_Step_Bon4_Dosing"), ("SetCoil", "V3245_Nuoc_Bon4")])
    fc.add_network("Đóng nước Bồn 4", [("NC", "PLC2_Step_Bon4_Dosing"), ("ResetCoil", "V3245_Nuoc_Bon4")])

    fc.add_network("Tốc độ khuấy thuận Bồn 4", [("NO", "PLC2_Step_Bon4_Khuay_Thuan"), ("MOVE", "HMI_SP_PLC2_Toc_Do_Bon4_Main", "AGTR3263_Toc_Do_AO")])
    fc.add_network("Timer đếm thời gian khuấy thuận Bồn 4", [
        ("NO", "PLC2_Step_Bon4_Khuay_Thuan"),
        ("TON", "Timers_PLC2.Timer_Khuay_Thuan_Bon4", "HMI_SP_Time_Fwd", "PLC2_Khuay_Thuan_Bon4_Xong"),
    ])

    fc.add_network("Timer đếm thời gian khuấy ngược Bồn 4", [
        ("NO", "PLC2_Step_Bon4_Khuay_Nghich"),
        ("TON", "Timers_PLC2.Timer_Khuay_Nghich_Bon4", "HMI_SP_Time_Rev", "PLC2_Khuay_Nghich_Bon4_Xong"),
    ])

    fc.add_network("Cho phép PID mô phỏng Bồn 4", [("NO", "PLC2_Step_Bon4_PID_Mo_Phong"), ("SetCoil", "PID_Bon4_Enable")])
    fc.add_network("Nạp SP PID Bồn 4", [("NO", "PLC2_Step_Bon4_PID_Mo_Phong"), ("MOVE", "HMI_SP_PLC2_Nhiet_Do_Bon4", "PID_Bon4_SP")])

    fc.add_network("Timer đếm thời gian thanh trùng Bồn 4", [
        ("NO", "PLC2_Step_Bon4_Thanh_Trung"),
        ("TON", "Timers_PLC2.Timer_Thanh_Trung_Bon4", "HMI_SP_Time_Sterilize", "PLC2_Thanh_Trung_Bon4_Xong"),
    ])

    # Transfer Pump is self-latched
    fc.add_network("Bơm chuyển Nhánh 2 chạy khi có lệnh", [
        ("CMP_EQ", "PLC2_State", "40"),
        ("OR2", "Pump3265_Chuyen_Nhanh2_Cmd_Nhan_Eff", "Pump3265_Chuyen_Nhanh2"),
        ("CMP_GT", "LT3218_Bon4_Eff", "0.5"),
        ("NC", "PLC2_Loi_Tong"),
        ("NC", "PLC2_Stop_Active"),
        ("NC", "PLC2_EStop_Latch"),
        ("Coil", "Pump3265_Chuyen_Nhanh2"),
    ])

    # --- 6C. Reset stuck HMI Simulation done flags when leaving state ---
    fc.add_network("Reset HMI Tip Bồn 3 xong khi không ở State 11", [("CMP_NE", "PLC2_State", "11"), ("ResetCoil", "PLC2_Tip_Bon3_Xong_HMI")])
    fc.add_network("Reset HMI Khuấy Bồn 3 xong khi không ở State 12", [("CMP_NE", "PLC2_State", "12"), ("ResetCoil", "PLC2_Khuay_Bon3_Xong_HMI")])
    fc.add_network("Reset HMI Tip Bồn 4 xong khi không ở State 21", [("CMP_NE", "PLC2_State", "21"), ("ResetCoil", "PLC2_Tip_Bon4_Xong_HMI")])
    fc.add_network("Reset HMI Khuấy thuận Bồn 4 xong khi không ở State 22", [("CMP_NE", "PLC2_State", "22"), ("ResetCoil", "PLC2_Khuay_Thuan_Bon4_Xong_HMI")])
    fc.add_network("Reset HMI Khuấy ngược Bồn 4 xong khi không ở State 23", [("CMP_NE", "PLC2_State", "23"), ("ResetCoil", "PLC2_Khuay_Nghich_Bon4_Xong_HMI")])
    fc.add_network("Reset HMI Thanh trùng Bồn 4 xong khi không ở State 31", [("CMP_NE", "PLC2_State", "31"), ("ResetCoil", "PLC2_Thanh_Trung_Bon4_Xong_HMI")])
    fc.add_network("Dừng PID khi hoàn thành Nhánh 2", [("NO", "PLC2_Me_Nhanh2_Hoan_Thanh"), ("ResetCoil", "PID_Bon4_Enable")])
    fc.add_network("Reset bước thanh trùng Bồn 4", [("NO", "PLC2_Me_Nhanh2_Hoan_Thanh"), ("ResetCoil", "PLC2_Step_Bon4_Thanh_Trung")])

    # --- 7. Standard Coils for Motors & VFDs ---
    fc.add_network("Chạy cánh khuấy Bồn 3 (Coil thường)", [
        ("NO", "PLC2_Step_Bon3_Khuay"),
        ("NC", "PLC2_Loi_Tong"),
        ("Coil", "AGTR3262_Khuay_Bon3"),
    ])
    fc.add_network("Gom trạng thái khuấy Bồn 4", [
        ("OR3", "PLC2_Step_Bon4_Khuay_Thuan", "PLC2_Step_Bon4_Khuay_Nghich", "PID_Bon4_Enable"),
        ("Coil", "AGTR3263_Khuay_Active"),
    ])
    fc.add_network("Yêu cầu chạy động cơ Bồn 4", [
        ("NO", "AGTR3263_Khuay_Active"),
        ("Coil", "AGTR3263_Should_Run"),
    ])
    fc.add_network("Lệnh chạy động cơ khuấy Bồn 4 (Coil thường)", [
        ("NO", "AGTR3263_Should_Run"),
        ("NC", "PLC2_Loi_Tong"),
        ("Coil", "AGTR3263_Khuay_Bon4"),
    ])
    fc.add_network("Lệnh đảo chiều động cơ khuấy Bồn 4 (Coil thường)", [
        ("NO", "PLC2_Step_Bon4_Khuay_Nghich"),
        ("NC", "PLC2_Loi_Tong"),
        ("Coil", "AGTR3263_Dao_Chieu"),
    ])

    fc.add_network("Mở van xả đáy Bồn 4 số 1 khi bơm chuyển Nhánh 2 chạy", [
        ("NO", "Pump3265_Chuyen_Nhanh2"),
        ("NC", "PLC2_Loi_Tong"),
        ("Coil", "V3247_Xa_Bon4"),
    ])
    fc.add_network("Mở van xả đáy Bồn 4 số 2 khi bơm chuyển Nhánh 2 chạy", [
        ("NO", "Pump3265_Chuyen_Nhanh2"),
        ("NC", "PLC2_Loi_Tong"),
        ("Coil", "V3248_Xa_Bon4"),
    ])
    fc.add_network("Mở van xả đáy Bồn 4 số 3 khi bơm chuyển Nhánh 2 chạy", [
        ("NO", "Pump3265_Chuyen_Nhanh2"),
        ("NC", "PLC2_Loi_Tong"),
        ("Coil", "V3249_Xa_Bon4"),
    ])

    # --- 8. AO Idle Cleanups, Safety Interlocks & Clamping ---
    # CV3211_Nuoc_Bon3
    fc.add_network("Reset CV nước Bồn 3 khi không dosing", [
        ("NC", "PLC2_Step_Bon3_Dosing"),
        ("MOVE", "0.0", "CV3211_Nuoc_Bon3"),
    ])
    fc.add_network("Reset CV nước Bồn 3 khi Stop hoặc Lỗi tổng PLC2", [
        ("OR2", "PLC2_Stop_Active", "PLC2_Loi_Tong"),
        ("MOVE", "0.0", "CV3211_Nuoc_Bon3"),
    ])
    fc.add_network("Clamp CV nước Bồn 3 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "CV3211_Nuoc_Bon3", "0.0"),
        ("MOVE", "0.0", "CV3211_Nuoc_Bon3"),
    ])
    fc.add_network("Clamp CV nước Bồn 3 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "CV3211_Nuoc_Bon3", "100.0"),
        ("MOVE", "100.0", "CV3211_Nuoc_Bon3"),
    ])

    # AGTR3262_Toc_Do_AO
    fc.add_network("Reset tốc độ cánh khuấy Bồn 3 khi không khuấy", [
        ("NC", "PLC2_Step_Bon3_Khuay"),
        ("MOVE", "0.0", "AGTR3262_Toc_Do_AO"),
    ])
    fc.add_network("Reset tốc độ cánh khuấy Bồn 3 khi Stop hoặc Lỗi tổng PLC2", [
        ("OR2", "PLC2_Stop_Active", "PLC2_Loi_Tong"),
        ("MOVE", "0.0", "AGTR3262_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ cánh khuấy Bồn 3 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AGTR3262_Toc_Do_AO", "0.0"),
        ("MOVE", "0.0", "AGTR3262_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ cánh khuấy Bồn 3 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AGTR3262_Toc_Do_AO", "100.0"),
        ("MOVE", "100.0", "AGTR3262_Toc_Do_AO"),
    ])

    # CV3216_Hoi_Bon4
    fc.add_network("Reset CV hơi Bồn 4 khi không chạy PID", [
        ("NC", "PID_Bon4_Enable"),
        ("MOVE", "0.0", "CV3216_Hoi_Bon4"),
    ])
    fc.add_network("Reset CV hơi Bồn 4 khi Stop hoặc Lỗi tổng PLC2", [
        ("OR2", "PLC2_Stop_Active", "PLC2_Loi_Tong"),
        ("MOVE", "0.0", "CV3216_Hoi_Bon4"),
    ])
    fc.add_network("Clamp CV hơi Bồn 4 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "CV3216_Hoi_Bon4", "0.0"),
        ("MOVE", "0.0", "CV3216_Hoi_Bon4"),
    ])
    fc.add_network("Clamp CV hơi Bồn 4 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "CV3216_Hoi_Bon4", "100.0"),
        ("MOVE", "100.0", "CV3216_Hoi_Bon4"),
    ])

    # AGTR3263_Toc_Do_AO
    fc.add_network("Reset tốc độ động cơ khuấy Bồn 4 khi không chạy", [
        ("NC", "AGTR3263_Khuay_Bon4"),
        ("MOVE", "0.0", "AGTR3263_Toc_Do_AO"),
    ])
    fc.add_network("Reset tốc độ động cơ khuấy Bồn 4 khi Stop hoặc Lỗi tổng PLC2", [
        ("OR2", "PLC2_Stop_Active", "PLC2_Loi_Tong"),
        ("MOVE", "0.0", "AGTR3263_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ động cơ khuấy Bồn 4 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AGTR3263_Toc_Do_AO", "0.0"),
        ("MOVE", "0.0", "AGTR3263_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ động cơ khuấy Bồn 4 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AGTR3263_Toc_Do_AO", "100.0"),
        ("MOVE", "100.0", "AGTR3263_Toc_Do_AO"),
    ])

    # Reset state to 0 when idle
    idle_conds = []
    for step in steps:
        idle_conds.append(("NC", step))
    idle_conds.append(("NC", "Pump3265_Chuyen_Nhanh2"))
    idle_conds.append(("NC", "PLC2_Me_Nhanh2_Hoan_Thanh"))
    idle_conds.append(("MOVE", "0", "PLC2_State"))
    fc.add_network("Reset state PLC2 về 0 khi ở chế độ Idle", idle_conds)

    # --- 9. Safety Outputs Reset ---
    for out_tag in [
        "V3240_Nuoc_Bon3", "V3242_Xa_Bon3", "V3243_Xa_Bon3",
        "V3244_Xa_Bon3", "V3245_Nuoc_Bon4",
        "V3247_Xa_Bon4", "V3248_Xa_Bon4", "V3249_Xa_Bon4",
    ]:
        fc.add_network(f"Dừng an toàn PLC2 reset {out_tag}", [("NO", "PLC2_Loi_Tong"), ("ResetCoil", out_tag)])
    return fc.generate_xml()


def build_storage() -> str:
    fc = TIALadderBuilder(fb_name="FC_Bon_Chua_Loc", block_id="30", block_type="FC")
    steps = [
        "BonChua_Step_Nhan_Dich",
        "BonChua_Step_Giai_Nhiet",
        "BonChua_Step_Chuyen_Bon2",
        "BonChua_Step_Loc_Chiet",
    ]

    # --- 1. Simulation Mapping (Digital & Analog) ---
    # Sensors (digital):
    for tag in ["LSH3310_Pheu_Cao", "LSL3311_Pheu_Thap"]:
        fc.add_network(f"Gated HMI {tag} qua Sim Mode", [
            ("NO", "HMI_Sim_Mode"),
            ("NO", tag + "_HMI"),
            ("Coil", tag + "_HMI_Gated"),
        ])
        fc.add_network(f"Tín hiệu {tag} hiệu dụng", [
            ("OR2", tag, tag + "_HMI_Gated"),
            ("Coil", tag + "_Eff"),
        ])

    # Sensors (analog):
    for tag in [
        "LT3302_BonChua1", "TT3301_BonChua1", "TT3303_TraoDoiNhiet",
        "LT3307_BonChua2", "TT3306_BonChua2", "PI3308_Truoc_Filter",
        "FT3309_Xa_Thanh_Pham"
    ]:
        fc.add_network(f"Yêu cầu mô phỏng {tag} từ HMI", [
            ("OR2", "HMI_Use_Sim_Input_BonChua", tag + "_Use_HMI"),
            ("Coil", tag + "_Sim_Req"),
        ])
        fc.add_network(f"Kích hoạt mô phỏng {tag} khi ở chế độ Sim Mode", [
            ("NO", "HMI_Sim_Mode"),
            ("NO", tag + "_Sim_Req"),
            ("Coil", tag + "_Sim_Active"),
        ])
        fc.add_network(f"Đọc giá trị mô phỏng {tag} vào hiệu dụng", [
            ("NO", tag + "_Sim_Active"),
            ("MOVE", tag + "_HMI", tag + "_Eff"),
        ])
        fc.add_network(f"Đọc giá trị vật lý {tag} vào hiệu dụng", [
            ("NC", tag + "_Sim_Active"),
            ("MOVE", tag, tag + "_Eff"),
        ])

    # --- 1A. Empty State Mapping and Dry Run for Storage ---
    fc.add_network("Bản đồ trạng thái - Bồn chứa 1 đã xả xong", [
        ("CMP_EQ", "BonChua_State", "70"),
        ("CMP_LE", "LT3302_BonChua1_Eff", "0.5"),
        ("Coil", "BonChua1_Xa_Xong")
    ])
    fc.add_network("Bản đồ trạng thái - Bồn chứa 2 đã xả xong", [
        ("CMP_EQ", "BonChua_State", "80"),
        ("CMP_LE", "LT3307_BonChua2_Eff", "0.5"),
        ("Coil", "BonChua2_Xa_Xong")
    ])

    fc.add_network("Dry Run bơm luân chuyển Bồn chứa 1", [
        ("NO", "Pump3361_LuanChuyen_BonChua1"),
        ("CMP_LE", "LT3302_BonChua1_Eff", "0.5"),
        ("NC", "BonChua1_Xa_Xong"),
        ("SetCoil", "PLC1_Loi_Dry_Run")
    ])
    fc.add_network("Dry Run bơm xả Bồn chứa 1", [
        ("NO", "Pump3362_Xa_BonChua1"),
        ("CMP_LE", "LT3302_BonChua1_Eff", "0.5"),
        ("NC", "BonChua1_Xa_Xong"),
        ("SetCoil", "PLC1_Loi_Dry_Run")
    ])
    fc.add_network("Dry Run bơm lọc CCP 1", [
        ("NO", "Pump3364_Filter"),
        ("CMP_LE", "LT3307_BonChua2_Eff", "0.5"),
        ("NC", "BonChua2_Xa_Xong"),
        ("SetCoil", "PLC1_Loi_Dry_Run")
    ])
    fc.add_network("Dry Run bơm lọc CCP 2", [
        ("NO", "Pump3365_Filter"),
        ("CMP_LE", "LT3307_BonChua2_Eff", "0.5"),
        ("NC", "BonChua2_Xa_Xong"),
        ("SetCoil", "PLC1_Loi_Dry_Run")
    ])

    # --- 1B. Setpoint Validation ---
    fc.add_network("Kiểm tra hợp lệ Setpoint Bồn chứa", [
        ("CMP_GT", "HMI_SP_BonChua1_Nhiet_Giai_Nhiet", "0.0"),
        ("CMP_GT", "HMI_SP_Loc_Ap_Suat_Max", "0.0"),
        ("Coil", "BonChua_SP_Valid"),
    ])

    # --- 2. Stop or Fault Logic ---
    # Reset all steps under Stop/Fault
    for step in steps + ["BonChua_Me_Hoan_Thanh"]:
        fc.add_network(f"Stop hoặc Lỗi tổng - reset {step}", [
            ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("ResetCoil", step)
        ])
    
    # Reset owners under Stop/Fault
    for owner in ["BonChua_Owner_Nhanh1", "BonChua_Owner_Nhanh2"]:
        fc.add_network(f"Stop hoặc Lỗi tổng - reset {owner}", [
            ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("ResetCoil", owner)
        ])

    # Reset all DOs under Stop/Fault
    for out_tag in [
        "V3331_Xa_BonChua1", "V3332_Xa_BonChua1", "Pump3361_LuanChuyen_BonChua1",
        "Pump3362_Xa_BonChua1", "V3333_DieuHuong_BonChua1", "V3334_DieuHuong_BonChua1",
        "V3335_DieuHuong_BonChua1", "V3338_Xa_BonChua2", "V3339_Xa_BonChua2",
        "Pump3364_Filter", "Pump3365_Filter", "V3340_Duong_Filter", "V3341_Duong_Filter",
        "Pump3264_Chuyen_Nhanh1", "Pump3265_Chuyen_Nhanh2_Cmd",
    ]:
        fc.add_network(f"Stop hoặc Lỗi tổng - reset {out_tag}", [
            ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("ResetCoil", out_tag)
        ])

    # Move 0.0 to all AOs under Stop/Fault
    for ao_tag in [
        "CV3304_Nuoc_Lam_Mat", "CV_Filler_Cap_Dich",
    ]:
        fc.add_network(f"Stop hoặc Lỗi tổng - clear {ao_tag}", [
            ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("MOVE", "0.0", ao_tag)
        ])

    # --- 2B. Owner Arbitration ---
    fc.add_network("Cấp quyền sở hữu Bồn chứa cho Nhánh 1 (Ưu tiên)", [
        ("NO", "PLC1_Me_Nhanh1_Hoan_Thanh"),
        ("NC", "BonChua_Owner_Nhanh1"),
        ("NC", "BonChua_Owner_Nhanh2"),
        ("NC", "PLC1_Stop_Active"),
        ("NC", "PLC1_Loi_Tong"),
        ("SetCoil", "BonChua_Owner_Nhanh1"),
    ])
    fc.add_network("Cấp quyền sở hữu Bồn chứa cho Nhánh 2", [
        ("NO", "PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff"),
        ("NC", "BonChua_Owner_Nhanh1"),
        ("NC", "BonChua_Owner_Nhanh2"),
        ("NC", "PLC1_Stop_Active"),
        ("NC", "PLC1_Loi_Tong"),
        ("SetCoil", "BonChua_Owner_Nhanh2"),
    ])

    # --- 3. Step Prevention Sequence Start ---
    # Derive step flags using CMP_EQ from State (One-hot mapping)
    fc.add_network("Bản đồ trạng thái Storage - Nhận dịch (State 50)", [("CMP_EQ", "BonChua_State", "50"), ("Coil", "BonChua_Step_Nhan_Dich")])
    fc.add_network("Bản đồ trạng thái Storage - Giải nhiệt (State 60)", [("CMP_EQ", "BonChua_State", "60"), ("Coil", "BonChua_Step_Giai_Nhiet")])
    fc.add_network("Bản đồ trạng thái Storage - Chuyển bồn 2 (State 70)", [("CMP_EQ", "BonChua_State", "70"), ("Coil", "BonChua_Step_Chuyen_Bon2")])
    fc.add_network("Bản đồ trạng thái Storage - Lọc CCP và chiết (State 80)", [("CMP_EQ", "BonChua_State", "80"), ("Coil", "BonChua_Step_Loc_Chiet")])

    fc.add_network("Nhận mẻ từ Nhánh 1 hoặc Nhánh 2 thành công - Chuyển sang State 50", [
        ("CMP_EQ", "BonChua_State", "0"),
        ("NC", "PLC1_Stop_Active"),
        ("NC", "PLC1_Loi_Tong"),
        ("OR2", "BonChua_Owner_Nhanh1", "BonChua_Owner_Nhanh2"),
        ("NO", "BonChua_SP_Valid"),
        ("MOVE", "50", "BonChua_State"),
    ])

    fc.add_network("Báo lỗi setpoint bồn chứa khi nhận mẻ", [
        ("OR2", "PLC1_Me_Nhanh1_Hoan_Thanh", "PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff"),
        ("NC", "BonChua_SP_Valid"),
        ("SetCoil", "BonChua_Loi_Setpoint"),
    ])

    # --- 4. Main Logic & Transitions (Reverse Scan Order) ---
    fc.add_network("Bồn chứa 02 cạn hoàn thành mẻ - Chuyển sang State 0", [
        ("CMP_EQ", "BonChua_State", "80"),
        ("CMP_LE", "LT3307_BonChua2_Eff", "0.5"),
        ("MOVE", "0", "BonChua_State"),
        ("SetCoil", "BonChua_Me_Hoan_Thanh"),
    ])

    fc.add_network("Chuyển sang Bồn chứa 02 xong - Chuyển sang State 80", [
        ("CMP_EQ", "BonChua_State", "70"),
        ("NO", "BonChua_Chuyen_Bon2_Xong_HMI"),
        ("MOVE", "80", "BonChua_State"),
    ])

    fc.add_network("Đạt 45 độ C chuyển Bồn chứa 02 - Chuyển sang State 70", [
        ("CMP_EQ", "BonChua_State", "60"),
        ("CMP_LE", "TT3301_BonChua1_Eff", "HMI_SP_BonChua1_Nhiet_Giai_Nhiet"),
        ("MOVE", "70", "BonChua_State"),
    ])

    fc.add_network("Nhận dịch xong chuyển giải nhiệt (Nhánh 1 auto-end) - Chuyển sang State 60", [
        ("CMP_EQ", "BonChua_State", "50"),
        ("NO", "BonChua_Owner_Nhanh1"),
        ("CMP_LE", "LT3209_Bon2_Eff", "0.5"),
        ("MOVE", "60", "BonChua_State"),
    ])
    fc.add_network("Nhận dịch xong chuyển giải nhiệt (Nhánh 2 auto-end) - Chuyển sang State 60", [
        ("CMP_EQ", "BonChua_State", "50"),
        ("NO", "BonChua_Owner_Nhanh2"),
        ("NO", "PLC2_Xa_Bon4_Xong_Nhan"),
        ("MOVE", "60", "BonChua_State"),
    ])
    fc.add_network("Nhận dịch xong chuyển giải nhiệt (HMI override) - Chuyển sang State 60", [
        ("CMP_EQ", "BonChua_State", "50"),
        ("NO", "BonChua_Nhan_Dich_Xong_HMI"),
        ("MOVE", "60", "BonChua_State"),
    ])

    fc.add_network("Reset cờ hoàn thành mẻ khi bắt đầu nhận dịch mới", [("CMP_EQ", "BonChua_State", "50"), ("ResetCoil", "BonChua_Me_Hoan_Thanh")])
    fc.add_network("Reset state Storage về 0 khi ở chế độ Idle hoặc Dừng khẩn hoặc Lỗi tổng", [
        ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
        ("MOVE", "0", "BonChua_State"),
    ])
    
    # Bơm gated by owner
    fc.add_network("Bật bơm chuyển Nhánh 1 khi có owner (Coil thường)", [
        ("CMP_EQ", "BonChua_State", "50"),
        ("NO", "BonChua_Owner_Nhanh1"),
        ("NO", "PLC1_Me_Nhanh1_Hoan_Thanh"),
        ("NC", "PLC1_Stop_Active"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "Pump3264_Chuyen_Nhanh1"),
    ])
    fc.add_network("Bật bơm chuyển Nhánh 2 khi có owner (Coil thường)", [
        ("CMP_EQ", "BonChua_State", "50"),
        ("NO", "BonChua_Owner_Nhanh2"),
        ("NO", "PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff"),
        ("NC", "PLC1_Stop_Active"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "Pump3265_Chuyen_Nhanh2_Cmd"),
    ])

    # Release owners when in State 60 (cooling)
    fc.add_network("Giải phóng owner Nhánh 1 khi ở State 60", [
        ("CMP_EQ", "BonChua_State", "60"),
        ("NO", "BonChua_Owner_Nhanh1"),
        ("ResetCoil", "BonChua_Owner_Nhanh1"),
    ])
    fc.add_network("Giải phóng owner Nhánh 2 khi ở State 60", [
        ("CMP_EQ", "BonChua_State", "60"),
        ("NO", "BonChua_Owner_Nhanh2"),
        ("ResetCoil", "BonChua_Owner_Nhanh2"),
    ])

    # Actuators logic
    fc.add_network("Mở nước làm mát 100 phần trăm", [("NO", "BonChua_Step_Giai_Nhiet"), ("MOVE", "100.0", "CV3304_Nuoc_Lam_Mat")])
    fc.add_network("Mở van xả đáy 01 để luân chuyển giải nhiệt", [("NO", "BonChua_Step_Giai_Nhiet"), ("SetCoil", "V3331_Xa_BonChua1")])
    fc.add_network("Bật bơm luân chuyển giải nhiệt", [("NO", "BonChua_Step_Giai_Nhiet"), ("SetCoil", "Pump3361_LuanChuyen_BonChua1")])

    fc.add_network("Đóng van hơi giải nhiệt", [("NO", "BonChua_Step_Chuyen_Bon2"), ("MOVE", "0.0", "CV3304_Nuoc_Lam_Mat")])
    fc.add_network("Đóng van xả đáy 01 sau giải nhiệt", [("NO", "BonChua_Step_Chuyen_Bon2"), ("ResetCoil", "V3331_Xa_BonChua1")])
    fc.add_network("Dừng bơm luân chuyển sau giải nhiệt", [("NO", "BonChua_Step_Chuyen_Bon2"), ("ResetCoil", "Pump3361_LuanChuyen_BonChua1")])
    fc.add_network("Mở van xả đáy 02 để chuyển bồn", [("NO", "BonChua_Step_Chuyen_Bon2"), ("SetCoil", "V3332_Xa_BonChua1")])
    for out_tag in ["Pump3362_Xa_BonChua1", "V3333_DieuHuong_BonChua1", "V3334_DieuHuong_BonChua1", "V3335_DieuHuong_BonChua1"]:
        fc.add_network(f"Mở {out_tag}", [("NO", "BonChua_Step_Chuyen_Bon2"), ("SetCoil", out_tag)])

    for out_tag in ["Pump3362_Xa_BonChua1", "V3332_Xa_BonChua1", "V3333_DieuHuong_BonChua1", "V3334_DieuHuong_BonChua1", "V3335_DieuHuong_BonChua1"]:
        fc.add_network(f"Đóng {out_tag} sau khi chuyển bồn", [("NO", "BonChua_Step_Loc_Chiet"), ("ResetCoil", out_tag)])
        
    for out_tag in ["Pump3364_Filter", "Pump3365_Filter", "V3340_Duong_Filter", "V3341_Duong_Filter"]:
        fc.add_network(f"Chạy {out_tag} (Coil thường)", [
            ("CMP_EQ", "BonChua_State", "80"),
            ("NC", "PLC1_Stop_Active"),
            ("NC", "PLC1_Loi_Tong"),
            ("Coil", out_tag)
        ])
        
    fc.add_network("Mở van filler theo lưu lượng", [
        ("CMP_EQ", "BonChua_State", "80"),
        ("NC", "PLC1_Stop_Active"),
        ("NC", "PLC1_Loi_Tong"),
        ("MOVE", "75.0", "CV_Filler_Cap_Dich"),
    ])
    
    fc.add_network("Áp suất filter cao báo lỗi", [
        ("NO", "BonChua_Step_Loc_Chiet"),
        ("CMP_GT", "PI3308_Truoc_Filter_Eff", "HMI_SP_Loc_Ap_Suat_Max"),
        ("SetCoil", "PLC1_Loi_Tong"),
    ])

    # --- 5. AO Idle Cleanups, Safety Interlocks & Clamping ---
    # CV3304_Nuoc_Lam_Mat
    fc.add_network("Reset CV nước làm mát khi không giải nhiệt", [
        ("NC", "BonChua_Step_Giai_Nhiet"),
        ("MOVE", "0.0", "CV3304_Nuoc_Lam_Mat"),
    ])
    fc.add_network("Reset CV nước làm mát khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
        ("MOVE", "0.0", "CV3304_Nuoc_Lam_Mat"),
    ])
    fc.add_network("Clamp CV nước làm mát trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "CV3304_Nuoc_Lam_Mat", "0.0"),
        ("MOVE", "0.0", "CV3304_Nuoc_Lam_Mat"),
    ])
    fc.add_network("Clamp CV nước làm mát trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "CV3304_Nuoc_Lam_Mat", "100.0"),
        ("MOVE", "100.0", "CV3304_Nuoc_Lam_Mat"),
    ])

    # CV_Filler_Cap_Dich
    fc.add_network("Reset CV cấp dịch khi không ở State 80", [
        ("CMP_NE", "BonChua_State", "80"),
        ("MOVE", "0.0", "CV_Filler_Cap_Dich"),
    ])
    fc.add_network("Reset CV cấp dịch khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
        ("MOVE", "0.0", "CV_Filler_Cap_Dich"),
    ])
    fc.add_network("Clamp CV cấp dịch trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "CV_Filler_Cap_Dich", "0.0"),
        ("MOVE", "0.0", "CV_Filler_Cap_Dich"),
    ])
    fc.add_network("Clamp CV cấp dịch trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "CV_Filler_Cap_Dich", "100.0"),
        ("MOVE", "100.0", "CV_Filler_Cap_Dich"),
    ])

    for bit in steps:
        fc.add_network(f"Reset {bit} khi Stop hoặc Lỗi tổng PLC1", [
            ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("ResetCoil", bit)
        ])
    for out_tag in [
        "Pump3264_Chuyen_Nhanh1", "Pump3265_Chuyen_Nhanh2_Cmd", "Pump3361_LuanChuyen_BonChua1",
        "Pump3362_Xa_BonChua1", "Pump3364_Filter", "Pump3365_Filter", "V3331_Xa_BonChua1",
        "V3332_Xa_BonChua1", "V3333_DieuHuong_BonChua1", "V3334_DieuHuong_BonChua1",
        "V3335_DieuHuong_BonChua1", "V3340_Duong_Filter", "V3341_Duong_Filter",
    ]:
        fc.add_network(f"Dừng an toàn bồn chứa reset {out_tag} khi Stop hoặc Lỗi tổng", [
            ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
            ("ResetCoil", out_tag)
        ])
    return fc.generate_xml()


def build_pid_plc1() -> str:
    ob = TIALadderBuilder(fb_name="OB30_PID_PLC1_Bon2", block_id="30", block_type="OB")
    ob.add_network("Initialize PID Bon 2 Kp parameter", [
        ("CMP_LE", "PID_Compact_1.sRet.r_Ctrl_Gain", "0.1"),
        ("MOVE", "2.0", "PID_Compact_1.sRet.r_Ctrl_Gain"),
    ])
    ob.add_network("Initialize PID Bon 2 Ti parameter", [
        ("CMP_LE", "PID_Compact_1.sRet.r_Ctrl_Ti", "1.0"),
        ("MOVE", "60.0", "PID_Compact_1.sRet.r_Ctrl_Ti"),
    ])
    ob.add_network("Sync Kp PID Bon 2 from HMI", [
        ("CMP_GT", "PID_Bon2_Kp_HMI", "0.1"),
        ("MOVE", "PID_Bon2_Kp_HMI", "PID_Compact_1.sRet.r_Ctrl_Gain"),
    ])
    ob.add_network("Sync Ti PID Bon 2 from HMI", [
        ("CMP_GT", "PID_Bon2_Ti_HMI", "1.0"),
        ("MOVE", "PID_Bon2_Ti_HMI", "PID_Compact_1.sRet.r_Ctrl_Ti"),
    ])
    ob.add_network("sb_EnCyclEstimation khi ở Sim Mode cho PID Bồn 2", [
        ("NC", "HMI_Sim_Mode"),
        ("Coil", "PID_Compact_1.sb_EnCyclEstimation"),
    ])
    ob.add_network("sb_EnCyclMonitoring khi ở Sim Mode cho PID Bồn 2", [
        ("NC", "HMI_Sim_Mode"),
        ("Coil", "PID_Compact_1.sb_EnCyclMonitoring"),
    ])
    ob.add_network("Gán cứng chu kỳ r_Cycle khi ở Sim Mode cho PID Bồn 2", [
        ("NO", "HMI_Sim_Mode"),
        ("MOVE", "0.1", "PID_Compact_1.sPid_Calc.r_Cycle"),
    ])

    # === DUAL-MODE PID ROUTING: SP / PV / Enable theo HMI_Che_Do_Thi ===
    # Mode 0 (TDH): PV = TT3208 (nhiệt độ), Enable = PID_Bon2_Enable (từ State)
    ob.add_network("Mode 0 TDH: PID_Bon2_PV_Eff = TT3208_Bon2_Eff", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "0"),
        ("MOVE", "TT3208_Bon2_Eff", "PID_Bon2_PV_Eff"),
    ])
    ob.add_network("Mode 0 TDH: Set PID_Bon2_Enable_Eff khi Enable", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "0"),
        ("NO", "PID_Bon2_Enable"),
        ("SetCoil", "PID_Bon2_Enable_Eff"),
    ])
    ob.add_network("Mode 0 TDH: Reset PID_Bon2_Enable_Eff khi không Enable", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "0"),
        ("NC", "PID_Bon2_Enable"),
        ("ResetCoil", "PID_Bon2_Enable_Eff"),
    ])
    # Mode 1 (DN): PV = VFD_Bon2_Actual_Speed_Feedback (tốc độ), Enable = HMI_PID_Bon2_Dau_Noi_Enable
    ob.add_network("Mode 1 DN: PID_Bon2_PV_Eff = VFD_Bon2_Actual_Speed_Feedback", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("MOVE", "VFD_Bon2_Actual_Speed_Feedback", "PID_Bon2_PV_Eff"),
    ])
    ob.add_network("Mode 1 DN: Set PID_Bon2_Enable_Eff khi Enable", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("NO", "HMI_PID_Bon2_Dau_Noi_Enable"),
        ("SetCoil", "PID_Bon2_Enable_Eff"),
    ])
    ob.add_network("Mode 1 DN: Reset PID_Bon2_Enable_Eff khi không Enable", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("NC", "HMI_PID_Bon2_Dau_Noi_Enable"),
        ("ResetCoil", "PID_Bon2_Enable_Eff"),
    ])
    ob.add_network("Reset PID_Bon2_Enable_Eff khi Mode không hợp lệ", [
        ("NO", "VFD_Bon2_Mode_Invalid"),
        ("ResetCoil", "PID_Bon2_Enable_Eff"),
    ])
    ob.add_network("Reset PID_Bon2_Enable_Eff khi Stop hoặc Lỗi tổng", [
        ("OR2", "PLC1_Stop_Active", "PLC1_Loi_Tong"),
        ("ResetCoil", "PID_Bon2_Enable_Eff"),
    ])
    # SP routing theo mode (OB30 cập nhật mỗi 100ms)
    ob.add_network("Mode 0 TDH: PID_Bon2_SP = HMI_SP_PLC1_Nhiet_Do_Bon2", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "0"),
        ("NO", "PID_Bon2_Enable_Eff"),
        ("MOVE", "HMI_SP_PLC1_Nhiet_Do_Bon2", "PID_Bon2_SP"),
    ])
    ob.add_network("Mode 1 DN: PID_Bon2_SP = HMI_SP_PLC1_Toc_Do_Bon2_Main", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("NO", "PID_Bon2_Enable_Eff"),
        ("MOVE", "HMI_SP_PLC1_Toc_Do_Bon2_Main", "PID_Bon2_SP"),
    ])

    ob.add_network("PID Compact Bon 2 - call technology block", [
        ("PID_Compact", "PID_Compact_1",
            {
                "Setpoint": "PID_Bon2_SP",
                "Input": "PID_Bon2_PV_Eff",
                "ManualEnable": "PID_Bon2_ManualEnable",
                "ManualValue": "PID_Bon2_ManualValue",
                "Reset": "PID_Bon2_Reset_Eff",
            },
            {
                "Output": "PID_Bon2_CV",
                "State": "PID_Bon2_State",
                "Error": "PID_Bon2_ErrorBits",
            },
            "1.2"),
    ])
    ob.add_network("Detect PID Bon 2 Error", [
        ("CMP_NE", "PID_Bon2_ErrorBits", "0"),
        ("Coil", "PID_Bon2_Error"),
    ])

    # PID_Compact dùng PID_Bon2_Enable_Eff và PID_Bon2_PV_Eff
    ob.add_pid_mode_network("PID Compact Bon 2 - Chế độ chạy", "PID_Bon2_Enable_Eff", "PID_Compact_1")

    # === PHÂN NHÁNH PID OUTPUT THEO CHẾ ĐỘ THI ===
    # Mode 0 (TDH): PID_CV → CV3206 (van hơi gia nhiệt)
    ob.add_network("Mode 0 TDH: PID_CV → CV3206_Hoi_Bon2", [
        ("NO", "PID_Bon2_Enable_Eff"),
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "0"),
        ("MOVE", "PID_Bon2_CV", "CV3206_Hoi_Bon2"),
    ])
    # Mode 0: Tốc độ khuấy cố định từ HMI SP → _Cmd
    ob.add_network("Mode 0 TDH: Tốc độ khuấy Bồn 2 từ HMI SP → VFD_Bon2_Toc_Do_Cmd", [
        ("NO", "PID_Bon2_Enable_Eff"),
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "0"),
        ("MOVE", "HMI_SP_PLC1_Toc_Do_Bon2_Main", "VFD_Bon2_Toc_Do_Cmd"),
    ])
    # Mode 1 (DN): PID_CV → VFD_Bon2_Toc_Do_Cmd (FC_VFD_Bon2_Hybrid routing ra QD)
    ob.add_network("Mode 1 DN: PID_CV → VFD_Bon2_Toc_Do_Cmd", [
        ("NO", "PID_Bon2_Enable_Eff"),
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("MOVE", "PID_Bon2_CV", "VFD_Bon2_Toc_Do_Cmd"),
    ])
    # Mode 1: Không gia nhiệt → CV3206 = 0
    ob.add_network("Mode 1 DN: Tắt van hơi CV3206_Hoi_Bon2 = 0", [
        ("NO", "PID_Bon2_Enable_Eff"),
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("MOVE", "0.0", "CV3206_Hoi_Bon2"),
    ])

    # === LOGIC MÔ PHỎNG TỰ ĐỘNG CHO PLC1 (OB30 - 100ms) ===
    # 1. Bồn 1 Level & Flow
    ob.add_network("Sim Bồn 1: Tăng FQ và LT khi dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "V3230_Nuoc_Bon1"),
        ("MATH_ADD_Real", "FQ3200_Bon1_HMI", "0.45", "FQ3200_Bon1_HMI"),
        ("MATH_ADD_Real", "LT3203_Bon1_HMI", "0.45", "LT3203_Bon1_HMI"),
    ])
    ob.add_network("Sim Bồn 1: Set FT khi dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "V3230_Nuoc_Bon1"),
        ("MOVE", "10.0", "FT3200_Bon1_HMI"),
    ])
    ob.add_network("Sim Bồn 1: Reset FT khi không dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NC", "V3230_Nuoc_Bon1"),
        ("MOVE", "0.0", "FT3200_Bon1_HMI"),
    ])
    ob.add_network("Sim Bồn 1: Giảm LT khi xả đáy", [
        ("NO", "HMI_Sim_Mode"),
        ("OR3", "V3232_Xa_Bon1", "V3233_Xa_Bon1", "V3234_Xa_Bon1"),
        ("MATH_SUB_Real", "LT3203_Bon1_HMI", "0.4", "LT3203_Bon1_HMI"),
    ])
    ob.add_network("Sim Bồn 1: Giới hạn mức nước tối đa", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_GT", "LT3203_Bon1_HMI", "100.0"),
        ("MOVE", "100.0", "LT3203_Bon1_HMI"),
    ])
    ob.add_network("Sim Bồn 1: Giới hạn mức nước tối thiểu", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_LT", "LT3203_Bon1_HMI", "0.0"),
        ("MOVE", "0.0", "LT3203_Bon1_HMI"),
    ])

    # 2. Bồn 2 Level & Flow
    ob.add_network("Sim Bồn 2: Tăng FQ và LT khi dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "V3235_Nuoc_Bon2"),
        ("MATH_ADD_Real", "FQ3205_Bon2_HMI", "0.3", "FQ3205_Bon2_HMI"),
        ("MATH_ADD_Real", "LT3209_Bon2_HMI", "0.3", "LT3209_Bon2_HMI"),
    ])
    ob.add_network("Sim Bồn 2: Set FT khi dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "V3235_Nuoc_Bon2"),
        ("MOVE", "10.0", "FT3205_Bon2_HMI"),
    ])
    ob.add_network("Sim Bồn 2: Reset FT khi không dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NC", "V3235_Nuoc_Bon2"),
        ("MOVE", "0.0", "FT3205_Bon2_HMI"),
    ])
    ob.add_network("Sim Bồn 2: Giảm LT khi bơm chuyển chạy", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "Pump3264_Chuyen_Nhanh1"),
        ("MATH_SUB_Real", "LT3209_Bon2_HMI", "0.3", "LT3209_Bon2_HMI"),
    ])
    ob.add_network("Sim Bồn 2: Giới hạn mức nước tối đa", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_GT", "LT3209_Bon2_HMI", "100.0"),
        ("MOVE", "100.0", "LT3209_Bon2_HMI"),
    ])
    ob.add_network("Sim Bồn 2: Giới hạn mức nước tối thiểu", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_LT", "LT3209_Bon2_HMI", "0.0"),
        ("MOVE", "0.0", "LT3209_Bon2_HMI"),
    ])

    # 2b. Bồn 2 Temp Simulation
    ob.add_network("Sim Bồn 2 Temp: Tăng nhiệt khi PID enabled", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "PID_Bon2_Enable"),
        ("MATH_MUL_Real", "PID_Bon2_CV", "0.001", "PID_Bon2_Temp_Inc"),
    ])
    ob.add_network("Sim Bồn 2 Temp: Cộng dồn vào HMI temp", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "PID_Bon2_Enable"),
        ("MATH_ADD_Real", "TT3208_Bon2_HMI", "PID_Bon2_Temp_Inc", "TT3208_Bon2_HMI"),
    ])
    ob.add_network("Sim Bồn 2 Temp: Giảm nhiệt khi PID disabled", [
        ("NO", "HMI_Sim_Mode"),
        ("NC", "PID_Bon2_Enable"),
        ("MATH_SUB_Real", "TT3208_Bon2_HMI", "0.05", "TT3208_Bon2_HMI"),
    ])
    ob.add_network("Sim Bồn 2 Temp: Giới hạn nhiệt độ tối đa 100", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_GT", "TT3208_Bon2_HMI", "100.0"),
        ("MOVE", "100.0", "TT3208_Bon2_HMI"),
    ])
    ob.add_network("Sim Bồn 2 Temp: Giới hạn nhiệt độ tối thiểu 25", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_LT", "TT3208_Bon2_HMI", "25.0"),
        ("MOVE", "25.0", "TT3208_Bon2_HMI"),
    ])

    # 3. Bồn Chứa 1 & 2 (Storage & Filter)
    ob.add_network("Sim Bồn Chứa 1: Tăng LT khi bơm chuyển Nhánh 1/2 chạy", [
        ("NO", "HMI_Sim_Mode"),
        ("OR2", "Pump3264_Chuyen_Nhanh1", "Pump3265_Chuyen_Nhanh2_Cmd"),
        ("MATH_ADD_Real", "LT3302_BonChua1_HMI", "0.4", "LT3302_BonChua1_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Khởi tạo nhiệt độ từ Bồn 2 (Nhánh 1) khi mới bắt đầu nhận dịch", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Owner_Nhanh1"),
        ("NO", "Pump3264_Chuyen_Nhanh1"),
        ("CMP_LT", "LT3302_BonChua1_HMI", "1.5"),
        ("MOVE", "TT3208_Bon2_Eff", "TT3301_BonChua1_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Khởi tạo nhiệt độ từ Bồn 4 (Nhánh 2) khi mới bắt đầu nhận dịch", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Owner_Nhanh2"),
        ("NO", "Pump3265_Chuyen_Nhanh2_Cmd"),
        ("CMP_LT", "LT3302_BonChua1_HMI", "1.5"),
        ("MOVE", "PID_Bon4_PV_Recv", "TT3301_BonChua1_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Giảm nhiệt độ khi bước giải nhiệt active", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Step_Giai_Nhiet"),
        ("MATH_SUB_Real", "TT3301_BonChua1_HMI", "0.15", "TT3301_BonChua1_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Giới hạn nhiệt độ giải nhiệt tối thiểu", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Step_Giai_Nhiet"),
        ("CMP_LT", "TT3301_BonChua1_HMI", "45.0"),
        ("MOVE", "45.0", "TT3301_BonChua1_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Giảm LT1 và Tăng LT2 khi chuyển bồn", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Step_Chuyen_Bon2"),
        ("MATH_SUB_Real", "LT3302_BonChua1_HMI", "0.4", "LT3302_BonChua1_HMI"),
        ("MATH_ADD_Real", "LT3307_BonChua2_HMI", "0.4", "LT3307_BonChua2_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Tự động kết thúc bước chuyển bồn", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Step_Chuyen_Bon2"),
        ("CMP_LE", "LT3302_BonChua1_HMI", "0.5"),
        ("Coil", "BonChua_Chuyen_Bon2_Xong_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Reset cờ chuyển bồn xong khi không ở bước chuyển bồn", [
        ("NO", "HMI_Sim_Mode"),
        ("NC", "BonChua_Step_Chuyen_Bon2"),
        ("ResetCoil", "BonChua_Chuyen_Bon2_Xong_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 2: Giảm LT2 khi chạy lọc và chiết", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Step_Loc_Chiet"),
        ("MATH_SUB_Real", "LT3307_BonChua2_HMI", "0.35", "LT3307_BonChua2_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 2: Mô phỏng áp suất lọc", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Step_Loc_Chiet"),
        ("MOVE", "1.5", "PI3308_Truoc_Filter_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 2: Mô phỏng lưu lượng xả", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "BonChua_Step_Loc_Chiet"),
        ("MOVE", "120.0", "FT3309_Xa_Thanh_Pham_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 2: Reset áp suất khi không chạy lọc", [
        ("NO", "HMI_Sim_Mode"),
        ("NC", "BonChua_Step_Loc_Chiet"),
        ("MOVE", "0.0", "PI3308_Truoc_Filter_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 2: Reset lưu lượng xả khi không chạy lọc", [
        ("NO", "HMI_Sim_Mode"),
        ("NC", "BonChua_Step_Loc_Chiet"),
        ("MOVE", "0.0", "FT3309_Xa_Thanh_Pham_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Giới hạn mức nước tối đa", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_GT", "LT3302_BonChua1_HMI", "100.0"),
        ("MOVE", "100.0", "LT3302_BonChua1_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 1: Giới hạn mức nước tối thiểu", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_LT", "LT3302_BonChua1_HMI", "0.0"),
        ("MOVE", "0.0", "LT3302_BonChua1_HMI"),
    ])
    ob.add_network("Sim Bồn Chứa 2: Giới hạn mức nước tối thiểu", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_LT", "LT3307_BonChua2_HMI", "0.0"),
        ("MOVE", "0.0", "LT3307_BonChua2_HMI"),
    ])

    # Gọi FC animation cánh khuấy Bồn 1 và Bồn 2 (100ms từ OB30)
    ob.add_network("Gọi FC animation cánh khuấy PLC1", [("CALL_FC", "FC_HMI_Animation_PLC1")])

    return cyclic_interrupt_xml(ob)



def build_hmi_animation_plc1() -> str:
    """FC_HMI_Animation_PLC1 (block ID 60) - Animation cánh khuấy Bồn 1 và Bồn 2."""
    fc = TIALadderBuilder(fb_name="FC_HMI_Animation_PLC1", block_id="60", block_type="FC")

    # === LOGIC ANIMATION CÁNH KHUẤY BỒN 1 ===
    fc.add_network("Cánh khuấy Bồn 1: Tăng khung hình khi chạy", [
        ("NO", "AGTR3260_Khuay_Bon1"),
        ("MATH_ADD_Int", "HMI_Anim_Bon1_Frame", "1", "HMI_Anim_Bon1_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 1: Reset khung hình về 0 khi vượt quá 7", [
        ("NO", "AGTR3260_Khuay_Bon1"),
        ("CMP_GT_Int", "HMI_Anim_Bon1_Frame", "7"),
        ("MOVE", "0", "HMI_Anim_Bon1_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 1: Reset khung hình về 0 khi dừng", [
        ("NC", "AGTR3260_Khuay_Bon1"),
        ("MOVE", "0", "HMI_Anim_Bon1_Frame"),
    ])

    # === LOGIC ANIMATION CÁNH KHUẤY BỒN 2 ===
    # Dùng _Cmd tags để animation chạy ở cả Mode 0 (mô phỏng) và Mode 1 (thật)
    fc.add_network("Cánh khuấy Bồn 2: Tăng khung hình khi quay thuận", [
        ("NO", "VFD_Bon2_Run_Cmd"),
        ("NC", "VFD_Bon2_Dao_Chieu_Cmd"),
        ("MATH_ADD_Int", "HMI_Anim_Bon2_Frame", "1", "HMI_Anim_Bon2_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 2: Giới hạn khung hình quay thuận", [
        ("NO", "VFD_Bon2_Run_Cmd"),
        ("NC", "VFD_Bon2_Dao_Chieu_Cmd"),
        ("CMP_GT_Int", "HMI_Anim_Bon2_Frame", "7"),
        ("MOVE", "0", "HMI_Anim_Bon2_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 2: Giảm khung hình khi quay nghịch", [
        ("NO", "VFD_Bon2_Run_Cmd"),
        ("NO", "VFD_Bon2_Dao_Chieu_Cmd"),
        ("MATH_SUB_Int", "HMI_Anim_Bon2_Frame", "1", "HMI_Anim_Bon2_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 2: Giới hạn khung hình quay nghịch", [
        ("NO", "VFD_Bon2_Run_Cmd"),
        ("NO", "VFD_Bon2_Dao_Chieu_Cmd"),
        ("CMP_LT_Int", "HMI_Anim_Bon2_Frame", "0"),
        ("MOVE", "7", "HMI_Anim_Bon2_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 2: Reset khung hình về 0 khi dừng", [
        ("NC", "VFD_Bon2_Run_Cmd"),
        ("MOVE", "0", "HMI_Anim_Bon2_Frame"),
    ])

    # === LOGIC ANIMATION MỨC DỊCH CỦA PLC1 ===
    # Bồn 1
    fc.add_network("Bồn 1 Mức dịch: Rỗng khi LT <= 0.5", [
        ("CMP_LE", "LT3203_Bon1_Eff", "0.5"),
        ("MOVE", "0", "HMI_Anim_Bon1_MucDich"),
    ])
    fc.add_network("Bồn 1 Mức dịch: Mức 40% khi 0.5 < LT < 50.0", [
        ("CMP_GT", "LT3203_Bon1_Eff", "0.5"),
        ("CMP_LT", "LT3203_Bon1_Eff", "50.0"),
        ("MOVE", "1", "HMI_Anim_Bon1_MucDich"),
    ])
    fc.add_network("Bồn 1 Mức dịch: Mức 60% khi LT >= 50.0", [
        ("CMP_GE", "LT3203_Bon1_Eff", "50.0"),
        ("MOVE", "2", "HMI_Anim_Bon1_MucDich"),
    ])

    # Bồn 2
    fc.add_network("Bồn 2 Mức dịch: Rỗng khi LT <= 0.5", [
        ("CMP_LE", "LT3209_Bon2_Eff", "0.5"),
        ("MOVE", "0", "HMI_Anim_Bon2_MucDich"),
    ])
    fc.add_network("Bồn 2 Mức dịch: Mức 40% khi 0.5 < LT < 50.0", [
        ("CMP_GT", "LT3209_Bon2_Eff", "0.5"),
        ("CMP_LT", "LT3209_Bon2_Eff", "50.0"),
        ("MOVE", "1", "HMI_Anim_Bon2_MucDich"),
    ])
    fc.add_network("Bồn 2 Mức dịch: Mức 60% khi LT >= 50.0", [
        ("CMP_GE", "LT3209_Bon2_Eff", "50.0"),
        ("MOVE", "2", "HMI_Anim_Bon2_MucDich"),
    ])

    # Bồn chứa 1
    fc.add_network("Bồn chứa 1 Mức dịch: Rỗng khi LT <= 0.5", [
        ("CMP_LE", "LT3302_BonChua1_Eff", "0.5"),
        ("MOVE", "0", "HMI_Anim_BonChua1_MucDich"),
    ])
    fc.add_network("Bồn chứa 1 Mức dịch: Mức 40% khi 0.5 < LT < 50.0", [
        ("CMP_GT", "LT3302_BonChua1_Eff", "0.5"),
        ("CMP_LT", "LT3302_BonChua1_Eff", "50.0"),
        ("MOVE", "1", "HMI_Anim_BonChua1_MucDich"),
    ])
    fc.add_network("Bồn chứa 1 Mức dịch: Mức 60% khi LT >= 50.0", [
        ("CMP_GE", "LT3302_BonChua1_Eff", "50.0"),
        ("MOVE", "2", "HMI_Anim_BonChua1_MucDich"),
    ])

    # Bồn chứa 2
    fc.add_network("Bồn chứa 2 Mức dịch: Rỗng khi LT <= 0.5", [
        ("CMP_LE", "LT3307_BonChua2_Eff", "0.5"),
        ("MOVE", "0", "HMI_Anim_BonChua2_MucDich"),
    ])
    fc.add_network("Bồn chứa 2 Mức dịch: Mức 40% khi 0.5 < LT < 50.0", [
        ("CMP_GT", "LT3307_BonChua2_Eff", "0.5"),
        ("CMP_LT", "LT3307_BonChua2_Eff", "50.0"),
        ("MOVE", "1", "HMI_Anim_BonChua2_MucDich"),
    ])
    fc.add_network("Bồn chứa 2 Mức dịch: Mức 60% khi LT >= 50.0", [
        ("CMP_GE", "LT3307_BonChua2_Eff", "50.0"),
        ("MOVE", "2", "HMI_Anim_BonChua2_MucDich"),
    ])

    return fc.generate_xml()



def build_vfd_bon2_hybrid() -> str:
    """FC_VFD_Bon2_Hybrid (block ID 70) - Physical output gating & command routing for VFD Bồn 2."""
    fc = TIALadderBuilder(fb_name="FC_VFD_Bon2_Hybrid", block_id="70", block_type="FC")

    # 0. Điều khiển contactor VFD Bồn 2 & trễ đóng nguồn
    fc.add_network("Điều khiển contactor VFD Bồn 2", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("NO", "HMI_Run_Enable"),
        ("NC", "PLC1_EStop_Latch"),
        ("NC", "PLC1_Stop_Active"),
        ("NC", "Nut_EStop_Eff"),
        ("NC", "Nut_Dung_Eff"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "VFD_Bon2_Contactor")
    ])

    fc.add_network("Timer trễ khởi động sau khi đóng contactor VFD Bồn 2", [
        ("NO", "VFD_Bon2_Contactor"),
        ("TON", "Timers_PLC1.Timer_VFD_Contactor", "T#3S", "VFD_Bon2_Contactor_Delay_Done")
    ])

    # 1. Tính VFD_Bon2_Comm_Active (gate bởi contactor delay)
    fc.add_network("Bật Comm_Active khi HMI_VFD_Bon2_Comm_Enable và Chế độ thi = 1 và trễ contactor xong", [
        ("NO", "HMI_VFD_Bon2_Comm_Enable"),
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("NO", "VFD_Bon2_Contactor_Delay_Done"),
        ("SetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi không cho phép truyền thông HMI", [
        ("NC", "HMI_VFD_Bon2_Comm_Enable"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi không ở chế độ đấu nối (Che_Do_Thi != 1)", [
        ("CMP_NE_Int", "HMI_Che_Do_Thi", "1"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi contactor nguồn VFD không đóng (NOT Contactor)", [
        ("NC", "VFD_Bon2_Contactor"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi trễ đóng contactor chưa hoàn tất (NOT Delay_Done)", [
        ("NC", "VFD_Bon2_Contactor_Delay_Done"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi Stop Active hệ thống", [
        ("NO", "PLC1_Stop_Active"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi có lỗi dừng khẩn (EStop Latch)", [
        ("NO", "PLC1_EStop_Latch"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi nút dừng khẩn EStop được nhấn", [
        ("NO", "Nut_EStop_Eff"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi nút dừng hệ thống Stop được nhấn", [
        ("NO", "Nut_Dung_Eff"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    fc.add_network("Tắt Comm_Active khi hệ thống báo lỗi tổng (Loi_Tong)", [
        ("NO", "PLC1_Loi_Tong"),
        ("ResetCoil", "VFD_Bon2_Comm_Active")
    ])
    # 3. Tính VFD_Bon2_Real_Active (tất cả điều kiện an toàn)
    fc.add_network("Kích hoạt Real_Active khi đủ mọi điều kiện an toàn", [
        ("CMP_EQ_Int", "HMI_Che_Do_Thi", "1"),
        ("NO", "HMI_VFD_Bon2_Comm_Enable"),
        ("NO", "HMI_VFD_Bon2_Real_Enable"),
        ("NO", "HMI_Run_Enable"),
        ("NO", "VFD_Bon2_Comm_Ready"),
        ("NC", "PLC1_EStop_Latch"),
        ("NC", "PLC1_Loi_Tong"),
        ("NC", "PLC1_Stop_Active"),
        ("SetCoil", "VFD_Bon2_Real_Active")
    ])
    fc.add_network("Reset Real_Active khi mất các điều kiện cho phép", [
        ("NC", "HMI_VFD_Bon2_Comm_Enable"),
        ("ResetCoil", "VFD_Bon2_Real_Active")
    ])
    fc.add_network("Reset Real_Active khi mất Real_Enable", [
        ("NC", "HMI_VFD_Bon2_Real_Enable"),
        ("ResetCoil", "VFD_Bon2_Real_Active")
    ])
    fc.add_network("Reset Real_Active khi mất Run_Enable", [
        ("NC", "HMI_Run_Enable"),
        ("ResetCoil", "VFD_Bon2_Real_Active")
    ])
    fc.add_network("Reset Real_Active khi có EStop", [
        ("NO", "PLC1_EStop_Latch"),
        ("ResetCoil", "VFD_Bon2_Real_Active")
    ])
    fc.add_network("Reset Real_Active khi có lỗi tổng", [
        ("NO", "PLC1_Loi_Tong"),
        ("ResetCoil", "VFD_Bon2_Real_Active")
    ])
    fc.add_network("Reset Real_Active khi có Stop active", [
        ("NO", "PLC1_Stop_Active"),
        ("ResetCoil", "VFD_Bon2_Real_Active")
    ])
    fc.add_network("Reset Real_Active khi mất truyền thông sẵn sàng", [
        ("NC", "VFD_Bon2_Comm_Ready"),
        ("ResetCoil", "VFD_Bon2_Real_Active")
    ])
    fc.add_network("Reset Real_Active khi không ở chế độ đấu nối", [
        ("CMP_NE_Int", "HMI_Che_Do_Thi", "1"),
        ("ResetCoil", "VFD_Bon2_Real_Active")
    ])

    # 4. Tính VFD_Bon2_Run_Safe
    fc.add_network("Safety gate kiểm soát lệnh chạy thực tế", [
        ("NO", "VFD_Bon2_Real_Active"),
        ("NO", "VFD_Bon2_Run_Cmd"),
        ("NC", "PLC1_Loi_Tong"),
        ("Coil", "VFD_Bon2_Run_Safe")
    ])

    # 5. Physical output routing — DUY NHẤT ghi physical Q/QD
    fc.add_network("Xuất lệnh chạy physical VFD_Bon2_Run khi Real_Active và an toàn", [
        ("NO", "VFD_Bon2_Real_Active"),
        ("NO", "VFD_Bon2_Run_Safe"),
        ("Coil", "VFD_Bon2_Run")
    ])
    fc.add_network("Xuất lệnh đảo chiều physical VFD_Bon2_Dao_Chieu khi Real_Active", [
        ("NO", "VFD_Bon2_Real_Active"),
        ("NO", "VFD_Bon2_Dao_Chieu_Cmd"),
        ("Coil", "VFD_Bon2_Dao_Chieu")
    ])
    fc.add_network("Xuất tốc độ physical VFD_Bon2_Toc_Do_AO khi Real_Active", [
        ("NO", "VFD_Bon2_Real_Active"),
        ("MOVE", "VFD_Bon2_Toc_Do_Cmd", "VFD_Bon2_Toc_Do_AO")
    ])

    # Khi không Real_Active: clear physical
    fc.add_network("Clear physical VFD_Bon2_Run khi không Real_Active", [
        ("NC", "VFD_Bon2_Real_Active"),
        ("ResetCoil", "VFD_Bon2_Run")
    ])
    fc.add_network("Clear physical VFD_Bon2_Dao_Chieu khi không Real_Active", [
        ("NC", "VFD_Bon2_Real_Active"),
        ("ResetCoil", "VFD_Bon2_Dao_Chieu")
    ])
    fc.add_network("Clear physical VFD_Bon2_Toc_Do_AO khi không Real_Active", [
        ("NC", "VFD_Bon2_Real_Active"),
        ("MOVE", "0.0", "VFD_Bon2_Toc_Do_AO")
    ])

    # Force các ngõ ra vật lý dummy về trạng thái an toàn (không đấu nối vật lý thực tế)
    fc.add_network("Force physical dummy run output to FALSE (Unconditional)", [
        ("CMP_EQ_Real", "VFD_Bon2_Dummy_Speed_Physical", "VFD_Bon2_Dummy_Speed_Physical"),
        ("ResetCoil", "VFD_Bon2_Dummy_Run_Physical")
    ])
    fc.add_network("Force physical dummy reverse output to FALSE (Unconditional)", [
        ("CMP_EQ_Real", "VFD_Bon2_Dummy_Speed_Physical", "VFD_Bon2_Dummy_Speed_Physical"),
        ("ResetCoil", "VFD_Bon2_Dummy_Reverse_Physical")
    ])
    fc.add_network("Force physical dummy speed output to 0.0 (Unconditional)", [
        ("CMP_EQ_Real", "VFD_Bon2_Dummy_Speed_Physical", "VFD_Bon2_Dummy_Speed_Physical"),
        ("MOVE", "0.0", "VFD_Bon2_Dummy_Speed_Physical")
    ])

    return fc.generate_xml()


def build_pid_plc2() -> str:
    ob = TIALadderBuilder(fb_name="OB31_PID_PLC2_Bon4", block_id="31", block_type="OB")
    ob.add_network("Initialize PID Bon 4 Kp parameter", [
        ("CMP_LE", "PID_Compact_2.sRet.r_Ctrl_Gain", "0.1"),
        ("MOVE", "2.0", "PID_Compact_2.sRet.r_Ctrl_Gain"),
    ])
    ob.add_network("Initialize PID Bon 4 Ti parameter", [
        ("CMP_LE", "PID_Compact_2.sRet.r_Ctrl_Ti", "1.0"),
        ("MOVE", "60.0", "PID_Compact_2.sRet.r_Ctrl_Ti"),
    ])
    ob.add_network("Sync Kp PID Bon 4 from HMI", [
        ("CMP_GT", "PID_Bon4_Kp_HMI", "0.1"),
        ("MOVE", "PID_Bon4_Kp_HMI", "PID_Compact_2.sRet.r_Ctrl_Gain"),
    ])
    ob.add_network("Sync Ti PID Bon 4 from HMI", [
        ("CMP_GT", "PID_Bon4_Ti_HMI", "1.0"),
        ("MOVE", "PID_Bon4_Ti_HMI", "PID_Compact_2.sRet.r_Ctrl_Ti"),
    ])
    ob.add_network("sb_EnCyclEstimation khi ở Sim Mode cho PID Bồn 4", [
        ("NC", "HMI_Sim_Mode"),
        ("Coil", "PID_Compact_2.sb_EnCyclEstimation"),
    ])
    ob.add_network("sb_EnCyclMonitoring khi ở Sim Mode cho PID Bồn 4", [
        ("NC", "HMI_Sim_Mode"),
        ("Coil", "PID_Compact_2.sb_EnCyclMonitoring"),
    ])
    ob.add_network("Gán cứng chu kỳ r_Cycle khi ở Sim Mode cho PID Bồn 4", [
        ("NO", "HMI_Sim_Mode"),
        ("MOVE", "0.1", "PID_Compact_2.sPid_Calc.r_Cycle"),
    ])
    ob.add_network("PID Compact Bon 4 - call technology block", [
        ("PID_Compact", "PID_Compact_2",
            {
                "Setpoint": "PID_Bon4_SP",
                "Input": "TT3219_Bon4_Sim",
                "ManualEnable": "PID_Bon4_ManualEnable",
                "ManualValue": "PID_Bon4_ManualValue",
                "Reset": "PID_Bon4_Reset_Eff",
            },
            {
                "Output": "PID_Bon4_CV",
                "State": "PID_Bon4_State",
                "Error": "PID_Bon4_ErrorBits",
            },
            "1.2"),
    ])
    ob.add_network("Detect PID Bon 4 Error", [
        ("CMP_NE", "PID_Bon4_ErrorBits", "0"),
        ("Coil", "PID_Bon4_Error"),
    ])
    ob.add_pid_mode_network("PID Compact Bon 4 - Chế độ chạy", "PID_Bon4_Enable", "PID_Compact_2")
    ob.add_network("Move PID Bon 4 CV to simulated heat valve", [
        ("NO", "PID_Bon4_Enable"),
        ("MOVE", "PID_Bon4_CV", "CV3216_Hoi_Bon4"),
    ])
    ob.add_network("Move Main Agitator Speed to VFD while PID runs PLC2", [
        ("NO", "PID_Bon4_Enable"),
        ("MOVE", "HMI_SP_PLC2_Toc_Do_Bon4_Main", "AGTR3263_Toc_Do_AO"),
    ])
    ob.add_network("If PID enabled, calculate heating target", [
        ("NO", "PID_Bon4_Enable"),
        ("MATH_MUL_Real", "PID_Bon4_CV", "0.95", "TT3219_Bon4_Target"),
    ])
    ob.add_network("If PID enabled, add ambient base to target", [
        ("NO", "PID_Bon4_Enable"),
        ("MATH_ADD_Real", "TT3219_Bon4_Target", "25.0", "TT3219_Bon4_Target"),
    ])
    ob.add_network("If PID disabled, set target to ambient", [
        ("NC", "PID_Bon4_Enable"),
        ("MOVE", "25.0", "TT3219_Bon4_Target"),
    ])
    ob.add_network("Calculate memory term: Pure * 0.995", [
        ("MATH_MUL_Real", "TT3219_Bon4_Sim_Pure", "0.995", "PID_Bon4_Temp_Val_1"),
    ])
    ob.add_network("Calculate target term: Target * 0.005", [
        ("MATH_MUL_Real", "TT3219_Bon4_Target", "0.005", "PID_Bon4_Temp_Val_2"),
    ])
    ob.add_network("Combine terms: Pure = Pure_prev * 0.995 + Target * 0.005", [
        ("MATH_ADD_Real", "PID_Bon4_Temp_Val_1", "PID_Bon4_Temp_Val_2", "TT3219_Bon4_Sim_Pure"),
    ])
    ob.add_network("Increment simulation counter", [
        ("MATH_ADD_Real", "PID_Bon4_Sim_Counter", "1.0", "PID_Bon4_Sim_Counter"),
    ])
    ob.add_network("Reset simulation counter at 1000", [
        ("CMP_GE_Real", "PID_Bon4_Sim_Counter", "1000.0"),
        ("MOVE", "0.0", "PID_Bon4_Sim_Counter"),
    ])
    ob.add_network("Calculate noise angle", [
        ("MATH_MUL_Real", "PID_Bon4_Sim_Counter", "0.05", "PID_Bon4_Sim_Angle"),
    ])
    ob.add_network("Calculate sine of noise angle", [
        ("MATH1_Sin", "PID_Bon4_Sim_Angle", "PID_Bon4_Sim_Sin"),
    ])
    ob.add_network("Calculate noise value (amplitude 0.2)", [
        ("MATH_MUL_Real", "PID_Bon4_Sim_Sin", "0.2", "PID_Bon4_Sim_Noise"),
    ])
    ob.add_network("Add noise to pure temperature to get noisy PV", [
        ("MATH_ADD_Real", "TT3219_Bon4_Sim_Pure", "PID_Bon4_Sim_Noise", "TT3219_Bon4_Sim"),
    ])
    ob.add_network("Đồng bộ giá trị mô phỏng sang tag HMI để truyền Modbus", [
        ("MOVE", "TT3219_Bon4_Sim", "TT3219_Bon4_HMI"),
    ])

    # === LOGIC MÔ PHỎNG TỰ ĐỘNG CHO PLC2 (OB31 - 100ms) ===
    # 1. Bồn 3 Level & Flow
    ob.add_network("Sim Bồn 3: Tăng FQ và LT khi dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "V3240_Nuoc_Bon3"),
        ("MATH_ADD_Real", "FQ3210_Bon3_HMI", "0.45", "FQ3210_Bon3_HMI"),
        ("MATH_ADD_Real", "LT3213_Bon3_HMI", "0.45", "LT3213_Bon3_HMI"),
    ])
    ob.add_network("Sim Bồn 3: Set FT khi dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "V3240_Nuoc_Bon3"),
        ("MOVE", "10.0", "FT3210_Bon3_HMI"),
    ])
    ob.add_network("Sim Bồn 3: Reset FT khi không dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NC", "V3240_Nuoc_Bon3"),
        ("MOVE", "0.0", "FT3210_Bon3_HMI"),
    ])
    ob.add_network("Sim Bồn 3: Giảm LT khi xả đáy", [
        ("NO", "HMI_Sim_Mode"),
        ("OR3", "V3242_Xa_Bon3", "V3243_Xa_Bon3", "V3244_Xa_Bon3"),
        ("MATH_SUB_Real", "LT3213_Bon3_HMI", "0.4", "LT3213_Bon3_HMI"),
    ])
    ob.add_network("Sim Bồn 3: Giới hạn mức nước tối đa", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_GT", "LT3213_Bon3_HMI", "100.0"),
        ("MOVE", "100.0", "LT3213_Bon3_HMI"),
    ])
    ob.add_network("Sim Bồn 3: Giới hạn mức nước tối thiểu", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_LT", "LT3213_Bon3_HMI", "0.0"),
        ("MOVE", "0.0", "LT3213_Bon3_HMI"),
    ])

    # 2. Bồn 4 Level & Flow
    ob.add_network("Sim Bồn 4: Tăng FQ và LT khi dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "V3245_Nuoc_Bon4"),
        ("MATH_ADD_Real", "FQ3215_Bon4_HMI", "0.3", "FQ3215_Bon4_HMI"),
        ("MATH_ADD_Real", "LT3218_Bon4_HMI", "0.3", "LT3218_Bon4_HMI"),
    ])
    ob.add_network("Sim Bồn 4: Set FT khi dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "V3245_Nuoc_Bon4"),
        ("MOVE", "10.0", "FT3215_Bon4_HMI"),
    ])
    ob.add_network("Sim Bồn 4: Reset FT khi không dosing", [
        ("NO", "HMI_Sim_Mode"),
        ("NC", "V3245_Nuoc_Bon4"),
        ("MOVE", "0.0", "FT3215_Bon4_HMI"),
    ])
    ob.add_network("Sim Bồn 4: Giảm LT khi bơm chuyển chạy", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "Pump3265_Chuyen_Nhanh2"),
        ("MATH_SUB_Real", "LT3218_Bon4_HMI", "0.3", "LT3218_Bon4_HMI"),
    ])
    ob.add_network("Sim Bồn 4: Giới hạn mức nước tối đa", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_GT", "LT3218_Bon4_HMI", "100.0"),
        ("MOVE", "100.0", "LT3218_Bon4_HMI"),
    ])
    ob.add_network("Sim Bồn 4: Giới hạn mức nước tối thiểu", [
        ("NO", "HMI_Sim_Mode"),
        ("CMP_LT", "LT3218_Bon4_HMI", "0.0"),
        ("MOVE", "0.0", "LT3218_Bon4_HMI"),
    ])

    # Gọi FC animation cánh khuấy Bồn 3 và Bồn 4 (100ms từ OB31)
    ob.add_network("Gọi FC animation cánh khuấy PLC2", [("CALL_FC", "FC_HMI_Animation_PLC2")])

    return cyclic_interrupt_xml(ob)



def build_hmi_animation_plc2() -> str:
    """FC_HMI_Animation_PLC2 (block ID 61) - Animation cánh khuấy Bồn 3 và Bồn 4."""
    fc = TIALadderBuilder(fb_name="FC_HMI_Animation_PLC2", block_id="61", block_type="FC")

    # === LOGIC ANIMATION CÁNH KHUẤY BỒN 3 ===
    fc.add_network("Cánh khuấy Bồn 3: Tăng khung hình khi chạy", [
        ("NO", "AGTR3262_Khuay_Bon3"),
        ("MATH_ADD_Int", "HMI_Anim_Bon3_Frame", "1", "HMI_Anim_Bon3_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 3: Reset khung hình về 0 khi vượt quá 7", [
        ("NO", "AGTR3262_Khuay_Bon3"),
        ("CMP_GT_Int", "HMI_Anim_Bon3_Frame", "7"),
        ("MOVE", "0", "HMI_Anim_Bon3_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 3: Reset khung hình về 0 khi dừng", [
        ("NC", "AGTR3262_Khuay_Bon3"),
        ("MOVE", "0", "HMI_Anim_Bon3_Frame"),
    ])

    # === LOGIC ANIMATION CÁNH KHUẤY BỒN 4 ===
    fc.add_network("Cánh khuấy Bồn 4: Tăng khung hình khi quay thuận", [
        ("NO", "AGTR3263_Khuay_Bon4"),
        ("NC", "AGTR3263_Dao_Chieu"),
        ("MATH_ADD_Int", "HMI_Anim_Bon4_Frame", "1", "HMI_Anim_Bon4_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 4: Giới hạn khung hình quay thuận", [
        ("NO", "AGTR3263_Khuay_Bon4"),
        ("NC", "AGTR3263_Dao_Chieu"),
        ("CMP_GT_Int", "HMI_Anim_Bon4_Frame", "7"),
        ("MOVE", "0", "HMI_Anim_Bon4_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 4: Giảm khung hình khi quay nghịch", [
        ("NO", "AGTR3263_Khuay_Bon4"),
        ("NO", "AGTR3263_Dao_Chieu"),
        ("MATH_SUB_Int", "HMI_Anim_Bon4_Frame", "1", "HMI_Anim_Bon4_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 4: Giới hạn khung hình quay nghịch", [
        ("NO", "AGTR3263_Khuay_Bon4"),
        ("NO", "AGTR3263_Dao_Chieu"),
        ("CMP_LT_Int", "HMI_Anim_Bon4_Frame", "0"),
        ("MOVE", "7", "HMI_Anim_Bon4_Frame"),
    ])
    fc.add_network("Cánh khuấy Bồn 4: Reset khung hình về 0 khi dừng", [
        ("NC", "AGTR3263_Khuay_Bon4"),
        ("MOVE", "0", "HMI_Anim_Bon4_Frame"),
    ])

    # === LOGIC ANIMATION MỨC DỊCH CỦA PLC2 ===
    # Bồn 3
    fc.add_network("Bồn 3 Mức dịch: Rỗng khi LT <= 0.5", [
        ("CMP_LE", "LT3213_Bon3_Eff", "0.5"),
        ("MOVE", "0", "HMI_Anim_Bon3_MucDich"),
    ])
    fc.add_network("Bồn 3 Mức dịch: Mức 40% khi 0.5 < LT < 50.0", [
        ("CMP_GT", "LT3213_Bon3_Eff", "0.5"),
        ("CMP_LT", "LT3213_Bon3_Eff", "50.0"),
        ("MOVE", "1", "HMI_Anim_Bon3_MucDich"),
    ])
    fc.add_network("Bồn 3 Mức dịch: Mức 60% khi LT >= 50.0", [
        ("CMP_GE", "LT3213_Bon3_Eff", "50.0"),
        ("MOVE", "2", "HMI_Anim_Bon3_MucDich"),
    ])

    # Bồn 4
    fc.add_network("Bồn 4 Mức dịch: Rỗng khi LT <= 0.5", [
        ("CMP_LE", "LT3218_Bon4_Eff", "0.5"),
        ("MOVE", "0", "HMI_Anim_Bon4_MucDich"),
    ])
    fc.add_network("Bồn 4 Mức dịch: Mức 40% khi 0.5 < LT < 50.0", [
        ("CMP_GT", "LT3218_Bon4_Eff", "0.5"),
        ("CMP_LT", "LT3218_Bon4_Eff", "50.0"),
        ("MOVE", "1", "HMI_Anim_Bon4_MucDich"),
    ])
    fc.add_network("Bồn 4 Mức dịch: Mức 60% khi LT >= 50.0", [
        ("CMP_GE", "LT3218_Bon4_Eff", "50.0"),
        ("MOVE", "2", "HMI_Anim_Bon4_MucDich"),
    ])

    return fc.generate_xml()



def build_hmi_mirror_plc1() -> str:
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

    fc.add_network("Quyền Operator", [("NO", "HMI_Operator_Login"), ("MOVE", "1", "HMI_User_Level")])
    fc.add_network("Quyền Engineer", [("NO", "HMI_Engineer_Login"), ("MOVE", "2", "HMI_User_Level")])
    fc.add_network("Quyền Admin", [("NO", "HMI_Admin_Login"), ("MOVE", "3", "HMI_User_Level")])
    fc.add_network("Cho phép sửa thông số Engineer", [("NO", "HMI_Engineer_Login"), ("SetCoil", "HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Cho phép sửa thông số Admin", [("NO", "HMI_Admin_Login"), ("SetCoil", "HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Operator không được sửa thông số", [("NO", "HMI_Operator_Login"), ("ResetCoil", "HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Mã an toàn mặc định", [("MOVE", "0", "HMI_AnToan_Status")])
    fc.add_network("Mã cảnh báo dosing PLC1", [("NO", "PLC1_Loi_Dosing"), ("MOVE", "1", "HMI_AnToan_Status")])
    fc.add_network("Mã lỗi Setpoint PLC1 không hợp lệ", [("NO", "PLC1_Loi_Setpoint"), ("MOVE", "2", "HMI_AnToan_Status")])
    fc.add_network("Mã lỗi Setpoint Bồn chứa không hợp lệ", [("NO", "BonChua_Loi_Setpoint"), ("MOVE", "2", "HMI_AnToan_Status")])
    fc.add_network("Mã lỗi dry run PLC1", [("NO", "PLC1_Loi_Dry_Run"), ("MOVE", "3", "HMI_AnToan_Status")])
    fc.add_network("Mã E-Stop ưu tiên cao PLC1", [("NO", "PLC1_EStop_Latch"), ("MOVE", "4", "HMI_AnToan_Status")])
    fc.add_network("Còi báo động khi lỗi hoặc mất truyền thông PLC1", [
        ("OR2", "PLC1_Loi_Tong", "PLC2_Loi_Tong_Recv"),
        ("SetCoil", "Coi_Bao_Dong"),
    ])
    fc.add_network("Tắt còi khi Ack Alarm", [("NO", "HMI_Ack_Alarm"), ("ResetCoil", "Coi_Bao_Dong")])

    # --- Trạng thái hiển thị chế độ hệ thống ---
    fc.add_network("Trạng thái hiển thị chế độ chạy thật", [("NC", "HMI_Sim_Mode"), ("Coil", "System_Mode_Real")])
    fc.add_network("Trạng thái hiển thị chế độ mô phỏng", [("NO", "HMI_Sim_Mode"), ("Coil", "System_Mode_Sim")])
    fc.add_network("Cảnh báo chế độ mô phỏng HMI active", [("NO", "HMI_Sim_Mode"), ("Coil", "HMI_Sim_Active_Warning")])

    # --- Dọn dẹp tín hiệu mô phỏng khi ở chế độ chạy thật (Sim_Mode = FALSE) ---
    # Digital sensors PLC1:
    for tag in [
        "LS3202_Bon1_Cao_HMI", "PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_HMI",
        "LSH3310_Pheu_Cao_HMI", "LSL3311_Pheu_Thap_HMI",
        "PLC1_Load_Default_Done_Nhan_HMI"
    ]:
        fc.add_network(f"Reset {tag} khi ở chế độ chạy thật", [("NC", "HMI_Sim_Mode"), ("ResetCoil", tag)])

    # Analog sensors PLC1:
    for tag in [
        "FT3200_Bon1_HMI", "FQ3200_Bon1_HMI", "LT3203_Bon1_HMI", "TT3204_Bon1_HMI",
        "FT3205_Bon2_HMI", "FQ3205_Bon2_HMI", "LT3209_Bon2_HMI", "TT3208_Bon2_HMI",
        "LT3302_BonChua1_HMI", "TT3301_BonChua1_HMI", "TT3303_TraoDoiNhiet_HMI",
        "LT3307_BonChua2_HMI", "TT3306_BonChua2_HMI", "PI3308_Truoc_Filter_HMI",
        "FT3309_Xa_Thanh_Pham_HMI"
    ]:
        fc.add_network(f"Reset {tag} về 0.0 khi ở chế độ chạy thật", [("NC", "HMI_Sim_Mode"), ("MOVE", "0.0", tag)])

    # Mô phỏng truyền thông Modbus TCP offline trên PLC1
    fc.add_network("Mô phỏng truyền thông Modbus TCP: Link Done nạp recipe PLC2 sang PLC1_HMI", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "PLC1_Load_Default_Cmd"),
        ("Coil", "PLC1_Load_Default_Done_Nhan_HMI"),
    ])

    # Mirror virtual/internal tags manually
    fc.add_network("Mirror virtual V3230_Nuoc_Bon1", [("NO", "V3230_Nuoc_Bon1"), ("Coil", "V3230_Nuoc_Bon1_M")])
    fc.add_network("Mirror virtual VFD_Bon2_Run", [("NO", "VFD_Bon2_Run"), ("Coil", "VFD_Bon2_Run_M")])
    fc.add_network("Mirror virtual VFD_Bon2_Dao_Chieu", [("NO", "VFD_Bon2_Dao_Chieu"), ("Coil", "VFD_Bon2_Dao_Chieu_M")])
    fc.add_network("Mirror virtual VFD_Bon2_Toc_Do_AO", [("MOVE", "VFD_Bon2_Toc_Do_AO", "VFD_Bon2_Toc_Do_AO_M")])

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

    fc.add_network("Quyền Operator", [("NO", "HMI_Operator_Login"), ("MOVE", "1", "HMI_User_Level")])
    fc.add_network("Quyền Engineer", [("NO", "HMI_Engineer_Login"), ("MOVE", "2", "HMI_User_Level")])
    fc.add_network("Quyền Admin", [("NO", "HMI_Admin_Login"), ("MOVE", "3", "HMI_User_Level")])
    fc.add_network("Cho phép sửa thông số Engineer", [("NO", "HMI_Engineer_Login"), ("SetCoil", "HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Cho phép sửa thông số Admin", [("NO", "HMI_Admin_Login"), ("SetCoil", "HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Operator không được sửa thông số", [("NO", "HMI_Operator_Login"), ("ResetCoil", "HMI_Cho_Phep_Sua_Thong_So")])
    fc.add_network("Mã an toàn mặc định", [("MOVE", "0", "HMI_AnToan_Status")])
    fc.add_network("Mã cảnh báo dosing PLC2", [("NO", "PLC2_Loi_Dosing"), ("MOVE", "1", "HMI_AnToan_Status")])
    fc.add_network("Mã lỗi Setpoint PLC2 không hợp lệ", [("NO", "PLC2_Loi_Setpoint"), ("MOVE", "2", "HMI_AnToan_Status")])
    fc.add_network("Mã lỗi dry run PLC2", [("NO", "PLC2_Loi_Dry_Run"), ("MOVE", "3", "HMI_AnToan_Status")])
    fc.add_network("Mã E-Stop ưu tiên cao PLC2", [("NO", "PLC2_EStop_Latch"), ("MOVE", "4", "HMI_AnToan_Status")])

    # --- Trạng thái hiển thị chế độ hệ thống ---
    fc.add_network("Trạng thái hiển thị chế độ chạy thật", [("NC", "HMI_Sim_Mode"), ("Coil", "System_Mode_Real")])
    fc.add_network("Trạng thái hiển thị chế độ mô phỏng", [("NO", "HMI_Sim_Mode"), ("Coil", "System_Mode_Sim")])
    fc.add_network("Cảnh báo chế độ mô phỏng HMI active", [("NO", "HMI_Sim_Mode"), ("Coil", "HMI_Sim_Active_Warning")])

    # --- Dọn dẹp tín hiệu mô phỏng khi ở chế độ chạy thật (Sim_Mode = FALSE) ---
    # Digital sensors PLC2:
    for tag in [
        "LS3217_Bon4_Cao_HMI", "Pump3265_Chuyen_Nhanh2_Cmd_Nhan_HMI",
        "PLC2_Load_Default_Cmd_Nhan_HMI"
    ]:
        fc.add_network(f"Reset {tag} khi ở chế độ chạy thật", [("NC", "HMI_Sim_Mode"), ("ResetCoil", tag)])

    # Analog sensors PLC2:
    for tag in [
        "FT3210_Bon3_HMI", "FQ3210_Bon3_HMI", "LT3213_Bon3_HMI", "TT3214_Bon3_HMI",
        "FT3215_Bon4_HMI", "FQ3215_Bon4_HMI", "LT3218_Bon4_HMI", "TT3219_Bon4_HMI"
    ]:
        fc.add_network(f"Reset {tag} về 0.0 khi ở chế độ chạy thật", [("NC", "HMI_Sim_Mode"), ("MOVE", "0.0", tag)])

    # Mô phỏng truyền thông Modbus TCP offline trên PLC2
    fc.add_network("Mô phỏng truyền thông Modbus TCP: Link Cmd nạp recipe PLC1 sang PLC2_HMI", [
        ("NO", "HMI_Sim_Mode"),
        ("NO", "HMI_Load_Default_Recipe"),
        ("Coil", "PLC2_Load_Default_Cmd_Nhan_HMI"),
    ])

    return fc.generate_xml()


def hmi_text_lists() -> dict[str, str]:
    step = TIAHmiListBuilder("TL_Mixing_Step", "TextList", "Mã bước chu trình Mixing")
    for value, text in [
        (0, "Chờ lệnh"),
        (10, "Dosing nước"),
        (11, "Tip nguyên liệu"),
        (12, "Khuấy ban đầu"),
        (15, "Xả sang bồn kế tiếp"),
        (20, "Dosing bổ sung"),
        (21, "Tip phụ gia"),
        (22, "Khuấy chiều thuận"),
        (23, "Khuấy chiều ngược"),
        (30, "PID gia nhiệt/điều khiển"),
        (31, "Giữ thanh trùng"),
        (50, "Bồn chứa 01 nhận dịch"),
        (60, "Giải nhiệt"),
        (70, "Chuyển sang Bồn chứa 02"),
        (80, "Lọc CCP và chiết rót"),
    ]:
        step.add_item(value, text)

    alarm = TIAHmiListBuilder("TL_Canh_Bao_Mixing", "TextList", "Cảnh báo Mixing")
    for value, text in [
        (0, "[AN TOÀN] Không có cảnh báo"),
        (1, "[DOSING] Van mở nhưng lưu lượng không tăng"),
        (2, "[SETPOINT] Giá trị setpoint không hợp lệ"),
        (3, "[KHÓA AN TOÀN] Dry run hoặc liên động bảo vệ"),
        (4, "[ESTOP ACTIVE] Dừng khẩn đang được chốt"),
    ]:
        alarm.add_item(value, text)

    role = TIAHmiListBuilder("TL_Phan_Quyen", "TextList", "Phân quyền vận hành")
    for value, text in [
        (0, "Chưa đăng nhập"),
        (1, "Operator - Start/Stop, Ack Alarm, xem màn hình"),
        (2, "Engineer - sửa thông số, manual, reset alarm"),
        (3, "Admin - toàn quyền"),
    ]:
        role.add_item(value, text)

    return {
        "Hmi.TextList.TL_Mixing_Step.xml": step.generate_xml(),
        "Hmi.TextList.TL_Canh_Bao_Mixing.xml": alarm.generate_xml(),
        "Hmi.TextList.TL_Phan_Quyen.xml": role.generate_xml(),
    }


def build_io_map() -> dict[str, object]:
    physical_inputs = [tag for tag in tags if tag.address.upper().startswith("%I")]
    physical_outputs_now = [tag for tag in tags if tag.address.upper().startswith("%Q")]
    input_hmi = [tag for tag in tags if tag.name.endswith("_HMI") and tag.address.upper().startswith("%M")]
    output_mirrors = [tag for tag in tags if tag.name.endswith("_M") and tag.address.upper().startswith("%M")]

    return {
        "project": {
            "name": "Mixing_Nuoc_Tuong_Maggi_2026",
            "source_pdf": r"C:\Users\lienb\Downloads\ĐỀ THI VÒNG SƠ KHẢO.pdf",
            "generator": "projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py",
            "generated_by": "coding/Antigravity branch",
            "language": "vi-VN",
            "ladder_xml_generated": True,
            "ladder_policy": "100% Ladder XML, không sinh SCL logic",
        },
        "architecture": [
            {
                "controller": "PLC1",
                "scope": "Điều khiển Bồn 1-2, PID Bồn 2 điều khiển van hơi CV3206; VFD chỉ giữ tốc độ khuấy từ HMI, và logic gom Bồn chứa/Lọc thành phẩm.",
                "blocks": ["FC_PLC1_Mixing.xml", "FC_Bon_Chua_Loc.xml", "OB30_PID_PLC1_Bon2.xml"],
            },
            {
                "controller": "PLC2",
                "scope": "Điều khiển Bồn 3-4 và PID mô phỏng Bồn 4.",
                "blocks": ["FC_PLC2_Mixing.xml", "OB31_PID_PLC2_Bon4.xml"],
            },
            {
                "controller": "Shared",
                "scope": "OB1 gọi các FC phẳng để QA import; khi tách CPU thực tế, import đúng block theo PLC và giữ tag mirror/HMI.",
                "blocks": ["OB1_Main.xml", "FC_HMI_Mirror_PLC1.xml", "FC_HMI_Mirror_PLC2.xml", "FC_Init_Default_Recipe_PLC1.xml", "FC_Init_Default_Recipe_PLC2.xml"],
            },
        ],
        "flat_output_files": [
            "IO_Map.json",
            "PLC_Tags.xml",
            "PLC_Tags_PLC1.xml",
            "PLC_Tags_PLC2.xml",
            "OB1_Main.xml",
            "FC_PLC1_Mixing.xml",
            "FC_PLC2_Mixing.xml",
            "FC_Bon_Chua_Loc.xml",
            "FC_HMI_Mirror_PLC1.xml",
            "FC_HMI_Mirror_PLC2.xml",
            "FC_Init_Default_Recipe_PLC1.xml",
            "FC_Init_Default_Recipe_PLC2.xml",
            "OB30_PID_PLC1_Bon2.xml",
            "OB31_PID_PLC2_Bon4.xml",
            "Hmi.TextList.TL_Mixing_Step.xml",
            "Hmi.TextList.TL_Canh_Bao_Mixing.xml",
            "Hmi.TextList.TL_Phan_Quyen.xml",
            "Tag_Binding.md",
            "MANUAL_STEPS.md",
            "Logic_Analysis.md",
        ],
        "io_principles": [
            "Mọi tag địa chỉ %I là tín hiệu vật lý và có tag mô phỏng/HMI cùng tên + _HMI tại %M.",
            "Mọi tag địa chỉ %Q là tín hiệu vật lý và có tag mirror cùng tên + _M tại %M.",
            "Tên tag ASCII và bắt đầu bằng AI_; mô tả/comment dùng tiếng Việt có dấu.",
            "PLC_Tags.xml gộp toàn bộ tag để QA Validator kiểm tra; khi import thực tế có thể tách theo cột plc/group.",
        ],
        "tag_counts": {
            "total": len(tags),
            "physical_inputs": len(physical_inputs),
            "input_hmi_mirrors": len(input_hmi),
            "physical_outputs": len(physical_outputs_now),
            "output_mirrors": len(output_mirrors),
        },
        "tags": [
            {
                "name": tag.name,
                "dtype": tag.dtype,
                "address": tag.address,
                "plc": tag.plc,
                "group": tag.group,
                "comment": tag.comment,
            }
            for tag in tags
        ],
    }


def write_docs() -> None:
    tag_binding = """# TAG BINDING WINCC - MIXING NƯỚC TƯƠNG MAGGI 2026

## Kiến trúc PLC
- PLC1 điều khiển Bồn 1, Bồn 2, PID Bồn 2 điều khiển van hơi CV3206; VFD chỉ giữ tốc độ khuấy từ HMI và cụm bồn chứa/lọc thành phẩm.
- PLC2 điều khiển Bồn 3, Bồn 4 và PID mô phỏng Bồn 4.
- Cờ `PLC2_Me_Nhanh2_Hoan_Thanh_Nhan` là điểm nhận kết quả Nhánh 2 về PLC1 để hiển thị hai bồn phụ trong một PLC.

## Màn hình HMI
- Login: dùng `HMI_User_Level`, `HMI_Operator_Login`, `HMI_Engineer_Login`, `HMI_Admin_Login`.
- Overview: dùng các tag `_M` của van, bơm, motor và các state `PLC1_State`, `PLC2_State`, `BonChua_State`.
- Tank Details: dùng `LT3203_Bon1`, `LT3209_Bon2`, `LT3213_Bon3`, `LT3218_Bon4` cho animation mức; dùng motor mirror cho cánh khuấy.
- Parameters: chỉ cho ghi khi `HMI_Cho_Phep_Sua_Thong_So = TRUE`.
- Sequence: gắn TextList `TL_Mixing_Step` với các tag state.
- PID: trend 3 đường SP/PV/CV cho Bồn 2 là `PID_Bon2_SP`, `TT3208_Bon2`, `PID_Bon2_CV`; Bồn 4 mô phỏng là `PID_Bon4_SP`, `TT3219_Bon4_Sim`, `PID_Bon4_CV`.
- Alarm banner: gắn `HMI_AnToan_Status` với `TL_Canh_Bao_Mixing`.

## Quy tắc mô phỏng
- Mọi tag vật lý `%I` đều có tag `_HMI` song song để nhập mô phỏng từ WinCC/PLCSIM.
- Mọi tag vật lý `%Q` đều có tag `_M` để HMI đọc trạng thái phản hồi.
- Các nút `*_Xong_HMI` dùng cho demo nhanh khi chưa cấu hình timer thật trong TIA.
"""

    manual = """# MANUAL STEPS - IMPORT VÀ DEMO DỰ ÁN MIXING

## Import vào TIA Portal V18
1. Tạo project S7-1200 hoặc S7-1500 theo cấu hình phần cứng thi đấu.
2. Import `PLC_Tags.xml` trước để có đầy đủ tag.
3. Import các block Ladder XML: `OB1_Main.xml`, `FC_PLC1_Mixing.xml`, `FC_PLC2_Mixing.xml`, `FC_Bon_Chua_Loc.xml`, `FC_HMI_Mirror_PLC1.xml`, `FC_HMI_Mirror_PLC2.xml`, `FC_Init_Default_Recipe_PLC1.xml`, `FC_Init_Default_Recipe_PLC2.xml`, `OB30_PID_PLC1_Bon2.xml`, `OB31_PID_PLC2_Bon4.xml`.
   *(Chú ý: Nếu bạn sử dụng các bộ import đóng gói chia sẵn trong thư mục `tia_import`, hãy chạy script `prepare_tia_import_sets.py` trước để tự động phân phối các block và sinh file Main.xml tương thích cho từng PLC1 và PLC2).*
4. Import các HMI TextList: `Hmi.TextList.TL_Mixing_Step.xml`, `Hmi.TextList.TL_Canh_Bao_Mixing.xml`, `Hmi.TextList.TL_Phan_Quyen.xml`.
5. PID Compact trong OB30/OB31: Cả hai PLC đều gọi PID_Compact version 1.2. PLC_1 sử dụng instance DB PID_Compact_1, PLC_2 sử dụng instance DB PID_Compact_2. Nếu TIA báo thiếu instance DB, hãy tạo các Technology Object PID_Compact_1 và PID_Compact_2 tương ứng bằng tay (chọn phiên bản 1.2) trong cây Technology objects của từng PLC trước khi biên dịch.

## Demo theo đề
1. **Khởi tạo thông số mặc định (Default Recipe):** Ở lần scan đầu tiên, các setpoint mặc định được nạp tự động thông qua các cờ độc lập `Init_Defaults_Done_PLC1`, `Init_Defaults_Done_PLC2`, và `Init_Defaults_Done_BonChua`. Bạn cũng có thể kích hoạt nạp lại recipe mặc định bất cứ lúc nào từ HMI bằng tag `HMI_Load_Default_Recipe` (Bool).
2. **Kiểm tra Setpoint hợp lệ:** Nhập setpoint cho các bồn (nước > 0.0, tốc độ > 0.0, nhiệt độ > 0.0, áp suất > 0.0, thời gian > T#0s). Nếu setpoint không hợp lệ (ví dụ: nước dosing = 0.0 hoặc thời gian khuấy = T#0s) và bạn nhấn nút Start, hệ thống sẽ chốt lỗi setpoint tương ứng (`PLC1_Loi_Setpoint`, `PLC2_Loi_Setpoint`, hoặc `BonChua_Loi_Setpoint`) và khóa không cho sequence khởi động. Lỗi setpoint có thể được xóa bằng nút nhấn Reset vật lý (`Nut_Reset_Eff`) hoặc nút Reset trên HMI (`HMI_Reset_Alarm`).
3. **Cấu hình mô phỏng độc lập và chạy thật (Sim Mode / Real Mode):**
   - **Chế độ mô phỏng (Simulation Mode):** Bật `HMI_Sim_Mode = TRUE`. Lúc này các sensor mô phỏng từ HMI được phép hoạt động:
     - Để mô phỏng toàn bộ cảm biến của một trạm: Bật thêm công tắc tổng `HMI_Use_Sim_Input_PLC1` (cho PLC1), `HMI_Use_Sim_Input_PLC2` (cho PLC2), hoặc `HMI_Use_Sim_Input_BonChua` (cho Bồn chứa).
     - Để mô phỏng từng cảm biến riêng lẻ: Bật tag `AI_<sensor>_Use_HMI` tương ứng (ví dụ: `TT3208_Bon2_Use_HMI` cho cảm biến nhiệt độ Bồn 2).
     - Khi Sim Mode ON, giá trị sensor mô phỏng HMI (`_HMI`) sẽ được ghi vào hiệu dụng (`_Eff`).
   - **Chế độ chạy thật (Real Mode):** Tắt `HMI_Sim_Mode = FALSE`. Khi Sim Mode OFF:
     - Hệ thống tự động **bỏ qua (ignore)** và **reset (dọn dẹp)** toàn bộ các tag mô phỏng cảm biến `_HMI` về `FALSE` (digital) và `0.0` (analog).
     - Toàn bộ ngõ vào hiệu dụng `_Eff` sẽ lấy trực tiếp từ tín hiệu vật lý thực tế (%I và %AI), bất kể các nút nhấn Use_Sim_Input trên HMI có đang bật hay không.
     - Các setpoint HMI (`HMI_SP_*`) và Recipe vẫn hoạt động và sử dụng bình thường cho chạy thật.
   - **Vận hành từ HMI khi chạy thật:** Tag `HMI_Run_Enable` dùng để cho phép gửi lệnh khởi chạy (`Start`) từ HMI ở chế độ thật. Các nút nhấn safety (`Stop`, `Reset`, `E-Stop`) từ HMI luôn được chấp nhận trực tiếp mà không bị khóa để đảm bảo an toàn.
   - **Trạng thái hiển thị:**
     - `System_Mode_Real = TRUE` khi đang ở chế độ chạy thật.
     - `System_Mode_Sim = TRUE` khi đang ở chế độ mô phỏng.
     - `HMI_Sim_Active_Warning = TRUE` nhấp nháy cảnh báo trên HMI khi chế độ mô phỏng đang hoạt động.
4. **Nhấn Start để chạy chu trình:** Nhấn nút Start vật lý hoặc HMI (`Nut_Khoi_Dong_Eff`). Chu trình Auto Enable sẽ được kích hoạt cho PLC1 (`PLC1_Auto_Enable`) và PLC2 (`PLC2_Auto_Enable`).
5. **Quan sát & Trend các tín hiệu quan trọng:**
   - **Bồn 2 (PID thật):** Cảm biến nhiệt độ hiệu dụng `TT3208_Bon2_Eff` -> Đưa vào PID -> Ngõ ra PID `PID_Bon2_CV` điều khiển van gia nhiệt `CV3206_Hoi_Bon2`. Cánh khuấy bồn 2 tiếp tục chạy với tốc độ không đổi đặt từ HMI (`HMI_SP_PLC1_Toc_Do_Bon2_Main`).
   - **Bồn 4 (PID mô phỏng):** Cảm biến nhiệt độ mô phỏng `TT3219_Bon4_Sim` -> Đưa vào PID -> Ngõ ra PID `PID_Bon4_CV` điều khiển van gia nhiệt mô phỏng `CV3216_Hoi_Bon4`.
   - **Kết nối Nhánh 2:** Kết quả Nhánh 2 hoàn thành được gửi qua truyền thông Modbus TCP sang PLC1 qua tag nhận `PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff` để bắt đầu cụm bồn chứa.
   - **Dịch chuyển Bồn chứa & Lọc:** Sau khi Nhánh 1 hoặc Nhánh 2 hoàn thành, cụm bồn chứa sẽ chuyển dịch qua Bồn chứa 01, giải nhiệt thông qua van tuyến tính nước làm mát `CV3304_Nuoc_Lam_Mat`, sau đó chuyển sang Bồn chứa 02, bơm qua màng lọc CCP và điều khiển van tuyến tính filler `CV_Filler_Cap_Dich` cấp xuống phễu chiết rót.
6. **Bảo vệ và giới hạn an toàn ngõ ra Analog (AO Clamping):** Mọi ngõ ra analog (AO) bao gồm CV van tuyến tính và tốc độ đặt động cơ/VFD được clamp cứng trong dải `0.0..100.0`. Khi có sự kiện Stop, E-Stop, Lỗi tổng, hoặc khi bước chương trình liên quan không hoạt động, các ngõ ra này sẽ lập tức cưỡng bức về `0.0` để bảo đảm an toàn tuyệt đối.

## Alarm và bảo mật
- Operator chỉ Start/Stop, Ack Alarm và xem màn hình.
- Engineer/Admin được sửa setpoint, bật Manual và Reset Alarm.
- Dry run: bơm chạy khi mức bồn xả gần 0 thì chốt lỗi.
- Dosing lỗi: van cấp mở nhưng lưu lượng không tăng.
- Mất truyền thông: bật `Gia_Lap_Mat_Ket_Noi_HMI` để kích hoạt còi và banner đỏ.
"""

    logic = """# LOGIC ANALYSIS - MIXING NƯỚC TƯƠNG MAGGI 2026

## Phân chia trách nhiệm
- PLC1: Bồn 1-2, PID nhiệt độ Bồn 2 qua van hơi, bồn chứa 01/02 và lọc thành phẩm.
- PLC2: Bồn 3-4, PID mô phỏng Bồn 4.
- Kết quả hai nhánh được gom về PLC1 bằng cờ hoàn thành của từng nhánh.

## Chu trình chính
1. Nhánh 1 dosing Bồn 1, tip cốt tương Nhật Bản, khuấy thuận, xả sang Bồn 2.
2. Bồn 2 dosing bổ sung, tip phụ gia, khuấy thuận/ngược, PID nhiệt độ qua van hơi, thanh trùng và báo hoàn thành.
3. Nhánh 2 tương tự với Bồn 3-4; PID Bồn 4 là mô phỏng.
4. PLC1 nhận dịch từ nhánh hoàn thành, giải nhiệt tại Bồn chứa 01 xuống setpoint 45 độ C, chuyển Bồn chứa 02, lọc CCP và chiết rót.

## Interlock
- E-Stop HMI/physical được chốt và chỉ reset khi nút dừng khẩn đã nhả và có lệnh Reset.
- Dry run ngắt bơm khi mức bồn nguồn gần 0.
- Dosing lỗi nếu van mở nhưng FT không tăng.
- Reset alarm chỉ có hiệu lực với Engineer/Admin.
"""

    pid_notes = """# PID Demo Tuning & Simulation Notes

Tài liệu này tổng hợp hướng dẫn cấu hình, chạy mô phỏng và tinh chỉnh (tuning) thời gian thực cho bộ điều khiển PID của Bồn 2 và Bồn 4 trong dự án Mixing Nước Tương Maggi 2026.

---

## 1. Cấu hình PID Bồn 2 (Điều khiển nhiệt độ qua van hơi gia nhiệt)

Vòng lặp nhiệt độ Bồn 2 sử dụng cảm biến nhiệt độ hiệu dụng `TT3208_Bon2_Eff` làm đầu vào (PV), ngõ ra bộ điều khiển `PID_Bon2_CV` (CV) điều khiển trực tiếp độ mở van hơi gia nhiệt `CV3206_Hoi_Bon2`. Cánh khuấy Bồn 2 quay liên tục ở tốc độ đặt cố định từ HMI (`HMI_SP_PLC1_Toc_Do_Bon2_Main`) trong cả quá trình chạy PID.

### Thông số mặc định khởi tạo
* **Kp (Hệ số khuếch đại):** `2.0`
* **Ti (Thời gian tích phân):** `60.0` giây
* **Td (Thời gian vi phân):** `0.0` giây (Tắt khâu vi phân D để tránh nhiễu tín hiệu)
* **Khóa liên động:** Khi PID Bồn 2 hoạt động (`PID_Bon2_Enable = TRUE`), van hơi gia nhiệt `CV3206_Hoi_Bon2` do ngõ ra PID `PID_Bon2_CV` điều khiển trực tiếp (không mở cứng 100.0%).

### Cơ chế đồng bộ tham số HMI & Watch Table
Hệ thống hỗ trợ thay đổi tham số Kp và Ti trực tiếp từ HMI hoặc bảng Watch Table qua các biến:
* `PID_Bon2_Kp_HMI` (Real)
* `PID_Bon2_Ti_HMI` (Real)

> [!TIP]
> * Nếu `PID_Bon2_Kp_HMI > 0.1`, giá trị này sẽ tự động được ghi đè vào tham số nội bộ `PID_Compact_1.sRet.r_Ctrl_Gain` của khối PID.
> * Nếu `PID_Bon2_Ti_HMI > 1.0`, giá trị này sẽ tự động được ghi đè vào tham số nội bộ `PID_Compact_1.sRet.r_Ctrl_Ti` của khối PID.
> * Nếu hai biến này nhỏ hơn ngưỡng trên, PID sẽ tự động nạp các tham số mặc định (`Kp = 2.0`, `Ti = 60.0`).

---

## 2. Cấu hình PID Bồn 4 (Mô phỏng nhiệt độ qua Van hơi tuyến tính)

Bồn 4 sử dụng cảm biến nhiệt độ mô phỏng nội bộ `TT3219_Bon4_Sim` làm PV và ngõ ra PID `PID_Bon4_CV` để điều khiển độ mở van tuyến tính cấp hơi gia nhiệt mô phỏng `CV3216_Hoi_Bon4`.

### Thông số mặc định khởi tạo
* **Kp (Hệ số khuếch đại):** `2.0`
* **Ti (Thời gian tích phân):** `60.0` giây
* **Td (Thời gian vi phân):** `0.0` giây

### Cơ chế mô phỏng nhiệt động học (OB31)
Nhiệt độ mô phỏng của Bồn 4 được tính toán ở chu kỳ ngắt 100ms trong OB31:
1. Độ mở van `CV3216_Hoi_Bon4` làm tăng nhiệt độ đích `TT3219_Bon4_Target` theo tỷ lệ: `Target = CV * 0.95 + 25.0` (trong đó 25.0 °C là nhiệt độ môi trường).
2. Nhiệt độ thực tế chưa nhiễu `TT3219_Bon4_Sim_Pure` tiếp cận nhiệt độ đích qua bộ lọc thông thấp (quán tính bậc 1): `Pure = Pure_prev * 0.99 + Target * 0.01`.
3. Một thành phần nhiễu hình sin biên độ `0.2` được cộng thêm vào để tạo ra giá trị PV có nhiễu thực tế `TT3219_Bon4_Sim`.

### Cơ chế đồng bộ tham số HMI & Watch Table
Tương tự Bồn 2, tham số PID Bồn 4 có thể chỉnh định thời gian thực thông qua:
* `PID_Bon4_Kp_HMI` (Real)
* `PID_Bon4_Ti_HMI` (Real)

---

## 3. Hướng dẫn tinh chỉnh PID khi Demo (Demo Tuning Guide)

> [!IMPORTANT]
> Trong môi trường mô phỏng PLCSIM hoặc khi chấm thi, thời gian trình diễn rất ngắn (khoảng 3-5 phút). Các tham số thực tế quá chậm sẽ khó quan sát. Khuyến nghị cấu hình tham số chạy Demo như sau:

| Thông số | Giá trị thực tế (Nhà máy) | Giá trị chạy Demo (Khuyến nghị) | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Kp Bồn 2** | `2.0` | `5.0` | Tăng khuếch đại để tốc độ cánh khuấy bám setpoint nhanh hơn. |
| **Ti Bồn 2** | `60.0` s | `15.0` s | Giảm thời gian tích phân để triệt tiêu sai số nhanh hơn. |
| **Kp Bồn 4** | `2.0` | `4.5` | Đảm bảo van hơi mô phỏng phản ứng nhạy bén. |
| **Ti Bồn 4** | `60.0` s | `20.0` s | Phù hợp với chu kỳ lọc 100ms trong OB31. |

> [!CAUTION]
> Tuyệt đối không cài đặt `Ti < 1.0` giây hoặc `Kp < 0.1` vì có thể gây mất ổn định bộ điều khiển PID hoặc khiến khối công nghệ `PID_Compact` chuyển sang trạng thái lỗi (State = 4).

---

## 4. Các bước chẩn đoán nhanh lỗi PID trên HMI
Nếu cờ lỗi `PID_Bon2_Error = TRUE` hoặc `PID_Bon4_Error = TRUE` xuất hiện:
1. Quan sát mã lỗi chi tiết tại `PID_Bon2_ErrorBits` hoặc `PID_Bon4_ErrorBits`.
2. Kiểm tra trạng thái chế độ chạy: Khối PID chỉ chạy khi `PID_Bon2_Enable = TRUE` (Bồn 2) hoặc `PID_Bon4_Enable = TRUE` (Bồn 4).
3. Đảm bảo Setpoint (`PID_Bon2_SP` / `PID_Bon4_SP`) > 0.0. Nếu Setpoint bằng 0.0 khi hệ thống khởi động, khối logic an toàn sẽ chốt lỗi setpoint (`PLC1_Loi_Setpoint` / `PLC2_Loi_Setpoint`) và dừng hệ thống.
4. Bấm nút **Reset Alarm** trên HMI hoặc kích hoạt xung `HMI_Reset_Alarm = TRUE` để xóa lỗi khối PID và phục hồi trạng thái hoạt động tự động.
"""

    (OUTPUT_DIR / "Tag_Binding.md").write_text(tag_binding, encoding="utf-8")
    (OUTPUT_DIR / "MANUAL_STEPS.md").write_text(manual, encoding="utf-8")
    (OUTPUT_DIR / "Logic_Analysis.md").write_text(logic, encoding="utf-8")
    (OUTPUT_DIR / "PID_DEMO_TUNING_NOTES.md").write_text(pid_notes, encoding="utf-8")


def generate_global_db_xml(db_name: str, members: list[tuple[str, str]]) -> str:
    member_xmls = []
    for name, dtype in members:
        member_xmls.append(f'            <Member Name="{name}" Datatype="{dtype}" Remanence="NonRetain" Accessibility="Public" />')
    members_str = "\n".join(member_xmls)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-06T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Blocks.GlobalDB ID="0">
    <AttributeList>
      <AutoNumber>true</AutoNumber>
      <HeaderAuthor />
      <HeaderFamily />
      <HeaderName />
      <HeaderVersion>0.1</HeaderVersion>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Static">
{members_str}
          </Section>
        </Sections>
      </Interface>
      <IsOnlyStoredInLoadMemory>false</IsOnlyStoredInLoadMemory>
      <IsWriteProtectedInAS>false</IsWriteProtectedInAS>
      <MemoryLayout>Optimized</MemoryLayout>
      <Name>{db_name}</Name>
      <Namespace />
      <ProgrammingLanguage>DB</ProgrammingLanguage>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="1" CompositionName="Comment">
<ObjectList>
<MultilingualTextItem ID="2" CompositionName="Items">
<AttributeList>
<Culture>en-US</Culture>
<Text>Global DB containing all timers and PID instances</Text>
</AttributeList>
</MultilingualTextItem>
</ObjectList>
</MultilingualText>
      <MultilingualText ID="3" CompositionName="Title">
        <ObjectList>
          <MultilingualTextItem ID="4" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>{db_name}</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.GlobalDB>
</Document>'''


def generate_tcon_db_xml(db_name: str, db_number: int, member_name: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-06T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Blocks.GlobalDB ID="0">
    <AttributeList>
      <AutoNumber>false</AutoNumber>
      <HeaderAuthor />
      <HeaderFamily />
      <HeaderName />
      <HeaderVersion>0.1</HeaderVersion>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Static">
            <Member Name="{member_name}" Datatype="TCON_IP_v4" Version="1.0" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
              <Sections>
                <Section Name="None">
                  <Member Name="InterfaceId" Datatype="HW_ANY" />
                  <Member Name="ID" Datatype="CONN_OUC" />
                  <Member Name="ConnectionType" Datatype="Byte" />
                  <Member Name="ActiveEstablished" Datatype="Bool" />
                  <Member Name="RemoteAddress" Datatype="IP_V4" Version="1.0">
                    <Sections>
                      <Section Name="None">
                        <Member Name="ADDR" Datatype="Array[1..4] of Byte" />
                      </Section>
                    </Sections>
                  </Member>
                  <Member Name="RemotePort" Datatype="UInt" />
                  <Member Name="LocalPort" Datatype="UInt" />
                </Section>
              </Sections>
            </Member>
          </Section>
        </Sections>
      </Interface>
      <IsOnlyStoredInLoadMemory>false</IsOnlyStoredInLoadMemory>
      <IsWriteProtectedInAS>false</IsWriteProtectedInAS>
      <MemoryLayout>Standard</MemoryLayout>
      <Name>{db_name}</Name>
      <Namespace />
      <Number>{db_number}</Number>
      <ProgrammingLanguage>DB</ProgrammingLanguage>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="1" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="2" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>DB communication via Modbus TCP</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
      <MultilingualText ID="3" CompositionName="Title">
        <ObjectList>
          <MultilingualTextItem ID="4" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>{db_name}</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.GlobalDB>
</Document>'''


def generate_standard_db_xml(db_name: str, db_number: int, members: list[tuple[str, str]], layout: str = "Standard") -> str:
    member_xmls = []
    for name, dtype in members:
        member_xmls.append(f'''            <Member Name="{name}" Datatype="{dtype}" Remanence="NonRetain" Accessibility="Public">
              <AttributeList>
                <BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute>
                <BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute>
              </AttributeList>
            </Member>''')
    members_str = "\n".join(member_xmls)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-06T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Blocks.GlobalDB ID="0">
    <AttributeList>
      <AutoNumber>false</AutoNumber>
      <HeaderAuthor />
      <HeaderFamily />
      <HeaderName />
      <HeaderVersion>0.1</HeaderVersion>
      <Interface>
        <Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
          <Section Name="Static">
{members_str}
          </Section>
        </Sections>
      </Interface>
      <IsOnlyStoredInLoadMemory>false</IsOnlyStoredInLoadMemory>
      <IsWriteProtectedInAS>false</IsWriteProtectedInAS>
      <MemoryLayout>{layout}</MemoryLayout>
      <Name>{db_name}</Name>
      <Namespace />
      <Number>{db_number}</Number>
      <ProgrammingLanguage>DB</ProgrammingLanguage>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="1" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="2" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>DB communication via Modbus TCP</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
      <MultilingualText ID="3" CompositionName="Title">
        <ObjectList>
          <MultilingualTextItem ID="4" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>{db_name}</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.GlobalDB>
</Document>'''


def main() -> None:
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_generation_state()
    define_tags()

    db_plc1_send = [
        ("CmdSeq", "Int"),
        ("Cmd_Start", "Bool"),
        ("Cmd_Stop", "Bool"),
        ("Cmd_Reset", "Bool"),
        ("Cmd_EStop", "Bool"),
        ("Cmd_Pump_Branch2_To_SubTanks", "Bool"),
        ("Cmd_Load_Recipe", "Bool"),
        ("Heartbeat", "Int"),
    ]
    db_plc1_recv = [
        ("AckSeq", "Int"),
        ("Done_Branch2", "Bool"),
        ("Done_Recipe", "Bool"),
        ("Alarm", "Bool"),
        ("State", "Int"),
        ("PID_Bon4_SP", "Real"),
        ("PID_Bon4_PV", "Real"),
        ("PID_Bon4_CV", "Real"),
        ("Done_Discharge2", "Bool"),
        ("Heartbeat", "Int"),
    ]
    db_modbus_server = [
        ("Data", "Array[0..99] of Word"),
        ("CmdSeq", "Int"),
        ("Cmd_Start", "Bool"),
        ("Cmd_Stop", "Bool"),
        ("Cmd_Reset", "Bool"),
        ("Cmd_EStop", "Bool"),
        ("Cmd_Pump_Branch2_To_SubTanks", "Bool"),
        ("Cmd_Load_Recipe", "Bool"),
        ("Heartbeat_Client", "Int"),
        ("AckSeq", "Int"),
        ("Done_Branch2", "Bool"),
        ("Done_Recipe", "Bool"),
        ("Alarm", "Bool"),
        ("State", "Int"),
        ("PID_Bon4_SP", "Real"),
        ("PID_Bon4_PV", "Real"),
        ("PID_Bon4_CV", "Real"),
        ("Done_Discharge2", "Bool"),
        ("Heartbeat_Server", "Int"),
        ("Temp_Pack_Word", "Word"),
        ("Temp_Unpack_Word", "Word"),
    ]


    db_plc1_mb_buffer = [
        ("Data", "Array[0..99] of Word"),
        ("Send_CmdSeq", "Int"),
        ("Send_Cmd_Start", "Bool"),
        ("Send_Cmd_Stop", "Bool"),
        ("Send_Cmd_Reset", "Bool"),
        ("Send_Cmd_EStop", "Bool"),
        ("Send_Cmd_Pump_Branch2_To_SubTanks", "Bool"),
        ("Send_Cmd_Load_Recipe", "Bool"),
        ("Send_Heartbeat", "Int"),
        ("Recv_AckSeq", "Int"),
        ("Recv_Done_Branch2", "Bool"),
        ("Recv_Done_Recipe", "Bool"),
        ("Recv_Alarm", "Bool"),
        ("Recv_State", "Int"),
        ("Recv_PID_Bon4_SP", "Real"),
        ("Recv_PID_Bon4_PV", "Real"),
        ("Recv_PID_Bon4_CV", "Real"),
        ("Recv_Done_Discharge2", "Bool"),
        ("Recv_Heartbeat", "Int"),
        ("Temp_Pack_Word", "Word"),
        ("Temp_Unpack_Word", "Word"),
    ]

    files = {
        "PLC_Tags.xml": tag_xml(),
        "PLC_Tags_PLC1.xml": tag_xml("PLC1"),
        "PLC_Tags_PLC2.xml": tag_xml("PLC2"),
        "OB1_Main.xml": build_ob1(),
        "FC_Manual_Control_PLC1.xml": build_manual_control_plc1(),
        "FC_Manual_Control_PLC2.xml": build_manual_control_plc2(),
        "FC_PLC1_Mixing.xml": build_plc1(),
        "FC_PLC2_Mixing.xml": build_plc2(),
        "FC_Bon_Chua_Loc.xml": build_storage(),
        "FC_Init_Default_Recipe_PLC1.xml": build_init_default_recipe_plc1(),
        "FC_Init_Default_Recipe_PLC2.xml": build_init_default_recipe_plc2(),
        "OB30_PID_PLC1_Bon2.xml": build_pid_plc1(),
        "OB31_PID_PLC2_Bon4.xml": build_pid_plc2(),
        "FC_HMI_Animation_PLC1.xml": build_hmi_animation_plc1(),
        "FC_HMI_Animation_PLC2.xml": build_hmi_animation_plc2(),
        "FC_HMI_Mirror_PLC1.xml": build_hmi_mirror_plc1(),
        "FC_VFD_Bon2_Hybrid.xml": build_vfd_bon2_hybrid(),
        "FC_HMI_Mirror_PLC2.xml": build_hmi_mirror_plc2(),
        "Timers_PLC1.xml": generate_global_db_xml("Timers_PLC1", [
            ("Timer_Dosing_Bon1", "IEC_TIMER"),
            ("Timer_Tip_Bon1", "IEC_TIMER"),
            ("Timer_Dosing_Bon2", "IEC_TIMER"),
            ("Timer_Tip_Bon2", "IEC_TIMER"),
            ("Timer_Khuay_Bon1", "IEC_TIMER"),
            ("Timer_Khuay_Thuan_Bon2", "IEC_TIMER"),
            ("Timer_Khuay_Nghich_Bon2", "IEC_TIMER"),
            ("Timer_Thanh_Trung_Bon2", "IEC_TIMER"),
            ("Timer_Heartbeat_PLC1", "IEC_TIMER"),
            ("VFD_Bon2_MB_Counter", "IEC_COUNTER"),
            ("Timer_VFD_Contactor", "IEC_TIMER"),
            ("Timer_VFD_MB_Retry", "IEC_TIMER"),
        ]),
        "Timers_PLC2.xml": generate_global_db_xml("Timers_PLC2", [
            ("Timer_Dosing_Bon3", "IEC_TIMER"),
            ("Timer_Tip_Bon3", "IEC_TIMER"),
            ("Timer_Dosing_Bon4", "IEC_TIMER"),
            ("Timer_Tip_Bon4", "IEC_TIMER"),
            ("Timer_Khuay_Bon3", "IEC_TIMER"),
            ("Timer_Khuay_Thuan_Bon4", "IEC_TIMER"),
            ("Timer_Khuay_Nghich_Bon4", "IEC_TIMER"),
            ("Timer_Thanh_Trung_Bon4", "IEC_TIMER"),
            ("Timer_Heartbeat_PLC2", "IEC_TIMER"),
        ]),
        "DB_PLC1_Send_To_PLC2_DB.xml": generate_standard_db_xml("DB_PLC1_Send_To_PLC2_DB", 11, db_plc1_send),
        "DB_PLC1_Recv_From_PLC2_DB.xml": generate_standard_db_xml("DB_PLC1_Recv_From_PLC2_DB", 10, db_plc1_recv),
        "DB_PLC1_MB_Buffer_DB.xml": generate_standard_db_xml("DB_PLC1_MB_Buffer_DB", 12, db_plc1_mb_buffer),
        "DB_Modbus_Holding_Register_DB.xml": generate_standard_db_xml("DB_Modbus_Holding_Register_DB", 20, db_modbus_server),
        # DB kết nối TCON_IP_v4 cho Modbus TCP (không dùng shortcut IP_OCTET params)
        "DB_MB_TCP_Client_Conn_DB.xml": generate_tcon_db_xml("DB_MB_TCP_Client_Conn_DB", 13, "MB_TCP"),
        "DB_MB_TCP_Server_Conn_DB.xml": generate_tcon_db_xml("DB_MB_TCP_Server_Conn_DB", 14, "MB_TCP_SERVER"),
        # DB Word buffer cho MB_CLIENT (PLC1) và MB_SERVER (PLC2) — chỉ Array of Word
        "DB_PLC1_MB_Word_Buffer_DB.xml": generate_standard_db_xml("DB_PLC1_MB_Word_Buffer_DB", 15, [("Data", "Array[0..99] of Word"), ("Temp_Pack_Word", "Word"), ("Temp_Unpack_Word", "Word")], "Standard"),
        "DB_PLC2_MB_Holding_Word_DB.xml": generate_standard_db_xml("DB_PLC2_MB_Holding_Word_DB", 21, [("Data", "Array[0..99] of Word"), ("Temp_Pack_Word", "Word"), ("Temp_Unpack_Word", "Word")], "Standard"),
    }
    files.update(hmi_text_lists())

    for name, content in files.items():
        (OUTPUT_DIR / name).write_text(content, encoding="utf-8")

    (OUTPUT_DIR / "IO_Map.json").write_text(json.dumps(build_io_map(), ensure_ascii=False, indent=2), encoding="utf-8")

    write_docs()
    print(f"Generated {len(files)} XML files and docs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
