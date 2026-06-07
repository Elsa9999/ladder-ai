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
    mirror_ao = WordAllocator("MD", 920, 4)


reset_generation_state()


def add_tag(name: str, dtype: str, address: str, comment: str, plc: str, group: str) -> None:
    if not name.startswith("AI_"):
        raise ValueError(f"Tag phải bắt đầu bằng AI_: {name}")
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
    add_physical_input("AI_Nut_Khoi_Dong", "Bool", "Nút khởi động vật lý", "PLC1", "Lenh_Chung")
    add_physical_input("AI_Nut_Dung", "Bool", "Nút dừng vật lý", "PLC1", "Lenh_Chung")
    add_physical_input("AI_Nut_Reset", "Bool", "Nút reset lỗi vật lý", "PLC1", "Lenh_Chung")
    add_physical_input("AI_Nut_EStop", "Bool", "Nút dừng khẩn vật lý", "PLC1", "Lenh_Chung")

    # PLC1: Bồn 1 và Bồn 2.
    for name, dtype, comment in [
        ("AI_FT3200_Bon1", "Real", "Cảm biến lưu lượng nước dosing vào Bồn 1"),
        ("AI_FQ3200_Bon1", "Real", "Bộ đếm lưu lượng tích lũy Bồn 1"),
        ("AI_LS3202_Bon1_Cao", "Bool", "Cảm biến mức cao Bồn 1"),
        ("AI_LT3203_Bon1", "Real", "Cảm biến mức liên tục Bồn 1"),
        ("AI_TT3204_Bon1", "Real", "Cảm biến nhiệt độ Bồn 1"),
        ("AI_FT3205_Bon2", "Real", "Cảm biến lưu lượng nước dosing vào Bồn 2"),
        ("AI_LT3209_Bon2", "Real", "Cảm biến mức liên tục Bồn 2"),
        ("AI_TT3208_Bon2", "Real", "Cảm biến nhiệt độ Bồn 2"),
    ]:
        add_physical_input(name, dtype, comment, "PLC1", "Bon_1_2")

    for name, dtype, comment in [
        ("AI_V3230_Nuoc_Bon1", "Bool", "Van on/off cấp nước Bồn 1"),
        ("AI_CV3201_Nuoc_Bon1", "Real", "Van tuyến tính cấp nước Bồn 1"),
        ("AI_AGTR3260_Khuay_Bon1", "Bool", "Động cơ khuấy Bồn 1"),
        ("AI_AGTR3260_Toc_Do_AO", "Real", "Tín hiệu tốc độ khuấy Bồn 1"),
        ("AI_V3232_Xa_Bon1", "Bool", "Van xả đáy Bồn 1 số 1"),
        ("AI_V3233_Xa_Bon1", "Bool", "Van xả đáy Bồn 1 số 2"),
        ("AI_V3234_Xa_Bon1", "Bool", "Van xả đáy Bồn 1 số 3"),
        ("AI_V3235_Nuoc_Bon2", "Bool", "Van on/off cấp nước Bồn 2"),
        ("AI_CV3206_Hoi_Bon2", "Real", "Van hơi/nhiệt Bồn 2 ở chế độ cho phép"),
        ("AI_VFD_Bon2_Run", "Bool", "Lệnh chạy VFD động cơ Bồn 2"),
        ("AI_VFD_Bon2_Dao_Chieu", "Bool", "Lệnh đảo chiều VFD động cơ Bồn 2"),
        ("AI_VFD_Bon2_Toc_Do_AO", "Real", "Tốc độ đặt VFD Bồn 2 từ PID"),
        ("AI_V3237_Xa_Bon2", "Bool", "Van xả đáy Bồn 2 số 1"),
        ("AI_V3238_Xa_Bon2", "Bool", "Van xả đáy Bồn 2 số 2"),
        ("AI_V3239_Xa_Bon2", "Bool", "Van xả đáy Bồn 2 số 3"),
        ("AI_Pump3264_Chuyen_Nhanh1", "Bool", "Bơm chuyển dung dịch Nhánh 1 xuống bồn chứa"),
    ]:
        add_physical_output(name, dtype, comment, "PLC1", "Bon_1_2")

    # PLC2: Bồn 3 và Bồn 4.
    for name, dtype, comment in [
        ("AI_FT3210_Bon3", "Real", "Cảm biến lưu lượng nước dosing vào Bồn 3"),
        ("AI_LT3213_Bon3", "Real", "Cảm biến mức liên tục Bồn 3"),
        ("AI_TT3214_Bon3", "Real", "Cảm biến nhiệt độ Bồn 3"),
        ("AI_FT3215_Bon4", "Real", "Cảm biến lưu lượng nước dosing vào Bồn 4"),
        ("AI_FQ3215_Bon4", "Real", "Bộ đếm lưu lượng tích lũy Bồn 4"),
        ("AI_LS3217_Bon4_Cao", "Bool", "Cảm biến mức cao Bồn 4"),
        ("AI_LT3218_Bon4", "Real", "Cảm biến mức liên tục Bồn 4"),
        ("AI_TT3219_Bon4", "Real", "Cảm biến nhiệt độ Bồn 4"),
    ]:
        add_physical_input(name, dtype, comment, "PLC2", "Bon_3_4")

    for name, dtype, comment in [
        ("AI_V3240_Nuoc_Bon3", "Bool", "Van on/off cấp nước Bồn 3"),
        ("AI_CV3211_Nuoc_Bon3", "Real", "Van tuyến tính cấp nước Bồn 3"),
        ("AI_AGTR3262_Khuay_Bon3", "Bool", "Động cơ khuấy Bồn 3"),
        ("AI_AGTR3262_Toc_Do_AO", "Real", "Tín hiệu tốc độ khuấy Bồn 3"),
        ("AI_V3242_Xa_Bon3", "Bool", "Van xả đáy Bồn 3 số 1"),
        ("AI_V3243_Xa_Bon3", "Bool", "Van xả đáy Bồn 3 số 2"),
        ("AI_V3244_Xa_Bon3", "Bool", "Van xả đáy Bồn 3 số 3"),
        ("AI_V3245_Nuoc_Bon4", "Bool", "Van on/off cấp nước Bồn 4"),
        ("AI_CV3216_Hoi_Bon4", "Real", "Van tuyến tính gia nhiệt mô phỏng Bồn 4"),
        ("AI_AGTR3263_Khuay_Bon4", "Bool", "Động cơ khuấy Bồn 4"),
        ("AI_AGTR3263_Dao_Chieu", "Bool", "Lệnh đảo chiều động cơ khuấy Bồn 4"),
        ("AI_AGTR3263_Toc_Do_AO", "Real", "Tốc độ đặt động cơ khuấy Bồn 4"),
        ("AI_V3247_Xa_Bon4", "Bool", "Van xả đáy Bồn 4 số 1"),
        ("AI_V3248_Xa_Bon4", "Bool", "Van xả đáy Bồn 4 số 2"),
        ("AI_V3249_Xa_Bon4", "Bool", "Van xả đáy Bồn 4 số 3"),
        ("AI_Pump3265_Chuyen_Nhanh2", "Bool", "Bơm chuyển dung dịch Nhánh 2 xuống bồn chứa"),
    ]:
        add_physical_output(name, dtype, comment, "PLC2", "Bon_3_4")

    # Bồn chứa và lọc thành phẩm gom về PLC1 để hiển thị kết quả chung.
    for name, dtype, comment in [
        ("AI_LT3302_BonChua1", "Real", "Cảm biến mức liên tục Bồn chứa 01"),
        ("AI_TT3301_BonChua1", "Real", "Cảm biến nhiệt độ Bồn chứa 01"),
        ("AI_TT3303_TraoDoiNhiet", "Real", "Cảm biến nhiệt độ bộ trao đổi nhiệt"),
        ("AI_LT3307_BonChua2", "Real", "Cảm biến mức liên tục Bồn chứa 02"),
        ("AI_TT3306_BonChua2", "Real", "Cảm biến nhiệt độ Bồn chứa 02"),
        ("AI_PI3308_Truoc_Filter", "Real", "Cảm biến áp suất trước màng lọc"),
        ("AI_FT3309_Xa_Thanh_Pham", "Real", "Cảm biến lưu lượng xả thành phẩm"),
        ("AI_LSH3310_Pheu_Cao", "Bool", "Cảm biến mức cao phễu chiết rót"),
        ("AI_LSL3311_Pheu_Thap", "Bool", "Cảm biến mức thấp phễu chiết rót"),
    ]:
        add_physical_input(name, dtype, comment, "PLC1", "Bon_Chua_Loc")

    for name, dtype, comment in [
        ("AI_V3331_Xa_BonChua1", "Bool", "Van xả đáy Bồn chứa 01 số 1"),
        ("AI_V3332_Xa_BonChua1", "Bool", "Van xả đáy Bồn chứa 01 số 2"),
        ("AI_Pump3361_LuanChuyen_BonChua1", "Bool", "Bơm luân chuyển Bồn chứa 01"),
        ("AI_Pump3362_Xa_BonChua1", "Bool", "Bơm xả Bồn chứa 01"),
        ("AI_V3333_DieuHuong_BonChua1", "Bool", "Van điều hướng Bồn chứa 01 số 1"),
        ("AI_V3334_DieuHuong_BonChua1", "Bool", "Van điều hướng Bồn chứa 01 số 2"),
        ("AI_V3335_DieuHuong_BonChua1", "Bool", "Van điều hướng Bồn chứa 01 số 3"),
        ("AI_CV3304_Nuoc_Lam_Mat", "Real", "Van tuyến tính nước làm mát"),
        ("AI_V3338_Xa_BonChua2", "Bool", "Van xả đáy Bồn chứa 02 số 1"),
        ("AI_V3339_Xa_BonChua2", "Bool", "Van xả đáy Bồn chứa 02 số 2"),
        ("AI_Pump3364_Filter", "Bool", "Bơm qua màng lọc CCP số 1"),
        ("AI_Pump3365_Filter", "Bool", "Bơm qua màng lọc CCP số 2"),
        ("AI_V3340_Duong_Filter", "Bool", "Van đường ống Filter số 1"),
        ("AI_V3341_Duong_Filter", "Bool", "Van đường ống Filter số 2"),
        ("AI_CV_Filler_Cap_Dich", "Real", "Van tuyến tính cấp dịch xuống phễu chiết rót"),
        ("AI_Coi_Bao_Dong", "Bool", "Còi báo động chung"),
    ]:
        add_physical_output(name, dtype, comment, "PLC1", "Bon_Chua_Loc")

    # HMI setpoint, quyền, bước, alarm và cờ mô phỏng.
    for name, comment in [
        ("AI_HMI_Operator_Login", "Đăng nhập quyền Operator"),
        ("AI_HMI_Engineer_Login", "Đăng nhập quyền Engineer"),
        ("AI_HMI_Admin_Login", "Đăng nhập quyền Admin"),
        ("AI_HMI_Che_Do_Manual", "Cho phép điều khiển tay từng thiết bị"),
        ("AI_HMI_Ack_Alarm", "Xác nhận cảnh báo"),
        ("AI_HMI_Reset_Alarm", "Reset alarm bằng HMI"),
        ("AI_Gia_Lap_Mat_Ket_Noi_HMI", "Nút giả lập mất kết nối PLC"),
    ]:
        add_hmi_bool(name, comment, "Shared", "HMI_Security")

    add_int("AI_HMI_User_Level", "Mức quyền hiện tại: 1 Operator, 2 Engineer, 3 Admin", "Shared", "HMI_Security")
    add_bool("AI_HMI_Cho_Phep_Sua_Thong_So", "Cờ cho phép sửa công thức và PID", "Shared", "HMI_Security")
    add_int("AI_HMI_Alarm_Status", "Mã cảnh báo tổng hợp cho WinCC TextList", "Shared", "Alarm")
    add_int("AI_HMI_AnToan_Status", "Mã chẩn đoán an toàn ưu tiên", "Shared", "Alarm")

    for plc, prefix, comment in [
        ("PLC1", "AI_PLC1", "Nhánh 1 Bồn 1-2"),
        ("PLC2", "AI_PLC2", "Nhánh 2 Bồn 3-4"),
    ]:
        add_bool(prefix + "_Auto_Enable", "Cho phép chạy Auto " + comment, plc, "Sequence")
        add_bool(prefix + "_EStop_Latch", "Chốt dừng khẩn HMI/SCADA " + comment, plc, "Safety")
        add_bool(prefix + "_Loi_Tong", "Lỗi tổng khóa Auto " + comment, plc, "Alarm")
        add_bool(prefix + "_Loi_Dry_Run", "Lỗi chạy khô bơm " + comment, plc, "Alarm")
        add_bool(prefix + "_Loi_Dosing", "Lỗi quá thời gian dosing " + comment, plc, "Alarm")
        add_bool(prefix + "_Loi_Truyen_Thong", "Lỗi truyền thông mô phỏng " + comment, plc, "Alarm")
        add_int(prefix + "_State", "Mã bước chu trình " + comment, plc, "Sequence")

    for name, comment in [
        ("AI_PLC1_Step_Bon1_Dosing", "Bồn 1 đang dosing nước"),
        ("AI_PLC1_Step_Bon1_Tip", "Bồn 1 đang mô phỏng tip cốt tương Nhật Bản"),
        ("AI_PLC1_Step_Bon1_Khuay", "Bồn 1 đang khuấy ban đầu"),
        ("AI_PLC1_Step_Bon1_Xa", "Bồn 1 đang xả sang Bồn 2"),
        ("AI_PLC1_Step_Bon2_Dosing", "Bồn 2 đang dosing bổ sung"),
        ("AI_PLC1_Step_Bon2_Tip", "Bồn 2 đang tip phụ gia"),
        ("AI_PLC1_Step_Bon2_Khuay_Thuan", "Bồn 2 khuấy chiều thuận"),
        ("AI_PLC1_Step_Bon2_Khuay_Nghich", "Bồn 2 khuấy chiều ngược"),
        ("AI_PLC1_Step_Bon2_PID", "Bồn 2 chạy PID qua VFD/động cơ"),
        ("AI_PLC1_Step_Bon2_Thanh_Trung", "Bồn 2 giữ thời gian thanh trùng"),
        ("AI_PLC1_Me_Nhanh1_Hoan_Thanh", "Nhánh 1 hoàn thành và sẵn sàng xả xuống bồn chứa"),
        ("AI_PLC1_Xa_Bon1_Xong", "Bồn 1 đã xả hết"),
        ("AI_PLC1_Xa_Bon2_Xong", "Bồn 2 đã xả hết"),
    ]:
        add_bool(name, comment, "PLC1", "Sequence")

    for name, comment in [
        ("AI_PLC2_Step_Bon3_Dosing", "Bồn 3 đang dosing nước"),
        ("AI_PLC2_Step_Bon3_Tip", "Bồn 3 đang mô phỏng tip cốt tương đậu đậm đặc"),
        ("AI_PLC2_Step_Bon3_Khuay", "Bồn 3 đang khuấy ban đầu"),
        ("AI_PLC2_Step_Bon3_Xa", "Bồn 3 đang xả sang Bồn 4"),
        ("AI_PLC2_Step_Bon4_Dosing", "Bồn 4 đang dosing bổ sung"),
        ("AI_PLC2_Step_Bon4_Tip", "Bồn 4 đang tip phụ gia"),
        ("AI_PLC2_Step_Bon4_Khuay_Thuan", "Bồn 4 khuấy chiều thuận"),
        ("AI_PLC2_Step_Bon4_Khuay_Nghich", "Bồn 4 khuấy chiều ngược"),
        ("AI_PLC2_Step_Bon4_PID_Mo_Phong", "Bồn 4 chạy PID mô phỏng"),
        ("AI_PLC2_Step_Bon4_Thanh_Trung", "Bồn 4 giữ thời gian thanh trùng"),
        ("AI_PLC2_Xa_Bon3_Xong", "Bồn 3 đã xả hết"),
        ("AI_PLC2_Xa_Bon4_Xong", "Bồn 4 đã xả hết"),
    ]:
        add_bool(name, comment, "PLC2", "Sequence")

    for name, comment in [
        ("AI_BonChua_Step_Nhan_Dich", "Bồn chứa 01 đang nhận dịch từ nhánh hoàn thành"),
        ("AI_BonChua_Step_Giai_Nhiet", "Bồn chứa 01 đang giải nhiệt xuống 45 độ C"),
        ("AI_BonChua_Step_Chuyen_Bon2", "Đang chuyển từ Bồn chứa 01 sang Bồn chứa 02"),
        ("AI_BonChua_Step_Loc_Chiet", "Đang lọc CCP và chiết rót"),
        ("AI_BonChua_Me_Hoan_Thanh", "Hoàn thành một mẻ sản xuất chung"),
    ]:
        add_bool(name, comment, "PLC1", "Bon_Chua_Loc")
    add_int("AI_BonChua_State", "Mã bước cụm bồn chứa và lọc thành phẩm", "PLC1", "Bon_Chua_Loc")

    # Communication tags (PLC1 - PLC2)
    # PLC2 -> PLC1
    add_tag("AI_PLC2_Me_Nhanh2_Hoan_Thanh", "Bool", internal_bool.next(), "Cờ hoàn thành Nhánh 2 gửi sang PLC1", "PLC2", "Comm")
    add_tag("AI_PLC2_Me_Nhanh2_Hoan_Thanh_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho cờ hoàn thành Nhánh 2 gửi sang PLC1", "PLC2", "Comm")
    physical_outputs.append(("AI_PLC2_Me_Nhanh2_Hoan_Thanh", "AI_PLC2_Me_Nhanh2_Hoan_Thanh_M", "Bool"))
    add_tag("AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan", "Bool", internal_bool.next(), "Cờ PLC1 nhận trạng thái hoàn thành từ PLC2", "PLC1", "Comm")
    add_tag("AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI song song cho cờ PLC1 nhận trạng thái hoàn thành từ PLC2", "PLC1", "Comm")
    # PLC1 -> PLC2
    add_tag("AI_Pump3265_Chuyen_Nhanh2_Cmd", "Bool", internal_bool.next(), "Lệnh chạy bơm chuyển Nhánh 2 gửi sang PLC2", "PLC1", "Comm")
    add_tag("AI_Pump3265_Chuyen_Nhanh2_Cmd_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho lệnh chạy bơm chuyển Nhánh 2 gửi sang PLC2", "PLC1", "Comm")
    physical_outputs.append(("AI_Pump3265_Chuyen_Nhanh2_Cmd", "AI_Pump3265_Chuyen_Nhanh2_Cmd_M", "Bool"))
    add_tag("AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan", "Bool", internal_bool.next(), "Nhận lệnh chạy bơm chuyển Nhánh 2 từ PLC1", "PLC2", "Comm")
    add_tag("AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI song song cho lệnh chạy bơm chuyển Nhánh 2 từ PLC1", "PLC2", "Comm")

    # S7 Connection (Modbus TCP) Status and Recv tags for PLC1
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

    # Modbus RTU tags for VFD Bon 2 (PLC1)
    add_tag("AI_VFD_Bon2_iStep", "Int", "%MW60", "Bước quét tuần tự Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_iStep_Reset", "Bool", internal_bool.next(), "Cờ reset bộ đếm bước Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_Step0_Req", "Bool", internal_bool.next(), "Yêu cầu bước 0 Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_Step1_Req", "Bool", internal_bool.next(), "Yêu cầu bước 1 Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_Step2_Req", "Bool", internal_bool.next(), "Yêu cầu bước 2 Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_Step3_Req", "Bool", internal_bool.next(), "Yêu cầu bước 3 Modbus VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MB_ControlWord", "Word", "%MW40", "Control Word gửi VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MB_FreqSetpoint", "Int", "%MW42", "Frequency Setpoint gửi VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MB_StatusWord", "Word", "%MW44", "Status Word đọc từ VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MB_ActualSpeed", "Int", "%MW46", "Actual Speed đọc từ VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MB_Error", "Bool", "%M50.0", "Lỗi Modbus Master VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MB_Busy", "Bool", "%M50.1", "Modbus Master Busy VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MB_Done", "Bool", "%M50.2", "Modbus Master Done VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MB_Status", "Word", "%MW52", "Trạng thái Modbus Master VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MBCL_Done", "Bool", "%M51.0", "Modbus Comm Load Done VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MBCL_Error", "Bool", "%M51.1", "Modbus Comm Load Error VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_MBCL_Status", "Word", "%MW54", "Trạng thái Modbus Comm Load VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_Freq_Temp", "Real", "%MD70", "Biến tạm tần số VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_Actual_Speed_Feedback", "Real", "%MD74", "Phản hồi tốc độ thực tế VFD Bồn 2", "PLC1", "VFD")
    add_tag("AI_VFD_Bon2_Actual_Speed_Feedback_M", "Real", mirror_ao.next(), "Tag gương phản hồi HMI tốc độ thực tế VFD Bồn 2", "PLC1", "VFD")
    physical_outputs.append(("AI_VFD_Bon2_Actual_Speed_Feedback", "AI_VFD_Bon2_Actual_Speed_Feedback_M", "Real"))

    # System and Comm tags
    add_tag("AI_Clock_1Hz", "Bool", "%M100.5", "Clock 1Hz system memory bit", "Shared", "System")
    add_tag("AI_FirstScan", "Bool", "%M101.0", "First Scan system memory bit", "Shared", "System")
    # Modbus TCP Client tags (PLC1)
    add_tag("AI_MB_TCP_iStep", "Int", "%MW80", "Modbus TCP Client step", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Write_Req", "Bool", "%M82.0", "Modbus TCP Client Write Request", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Read_Req", "Bool", "%M82.1", "Modbus TCP Client Read Request", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Write_Done", "Bool", "%M82.2", "Modbus TCP Client Write Done", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Write_Error", "Bool", "%M82.3", "Modbus TCP Client Write Error", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Write_Status", "Word", "%MW84", "Modbus TCP Client Write Status", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Read_Done", "Bool", "%M82.4", "Modbus TCP Client Read Done", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Read_Error", "Bool", "%M82.5", "Modbus TCP Client Read Error", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Read_Status", "Word", "%MW86", "Modbus TCP Client Read Status", "PLC1", "Comm")

    # Edge detection and latch tags for handshake (PLC1)
    add_tag("AI_Nut_Khoi_Dong_Eff_Old", "Bool", "%M83.0", "Old value of Start button", "PLC1", "Comm")
    add_tag("AI_Nut_Khoi_Dong_Eff_Edge", "Bool", "%M83.6", "Start command edge detected", "PLC1", "Comm")
    add_tag("AI_Nut_Dung_Eff_Old", "Bool", "%M83.1", "Old value of Stop button", "PLC1", "Comm")
    add_tag("AI_Nut_Dung_Eff_Edge", "Bool", "%M83.7", "Stop command edge detected", "PLC1", "Comm")
    add_tag("AI_Nut_Reset_Eff_Old", "Bool", "%M83.2", "Old value of Reset button", "PLC1", "Comm")
    add_tag("AI_Nut_Reset_Eff_Edge", "Bool", "%M84.0", "Reset command edge detected", "PLC1", "Comm")
    add_tag("AI_Nut_EStop_Eff_Old", "Bool", "%M83.3", "Old value of EStop button", "PLC1", "Comm")
    add_tag("AI_Nut_EStop_Eff_Edge", "Bool", "%M84.1", "EStop command edge detected", "PLC1", "Comm")
    add_tag("AI_Pump3265_Chuyen_Nhanh2_Cmd_Old", "Bool", "%M83.4", "Old value of Transfer command", "PLC1", "Comm")
    add_tag("AI_Pump3265_Chuyen_Nhanh2_Cmd_Edge", "Bool", "%M84.2", "Transfer command edge detected", "PLC1", "Comm")
    add_tag("AI_PLC1_Load_Default_Cmd_Old", "Bool", "%M83.5", "Old value of Load Recipe command", "PLC1", "Comm")
    add_tag("AI_PLC1_Load_Default_Cmd_Edge", "Bool", "%M84.3", "Load Recipe command edge detected", "PLC1", "Comm")
    add_tag("AI_MB_TCP_Any_Cmd_Edge", "Bool", "%M84.4", "Any handshake command edge detected", "PLC1", "Comm")

    # Modbus TCP Server tags (PLC2)
    add_tag("AI_PLC2_Last_CmdSeq", "Int", "%MW80", "Last processed command sequence", "PLC2", "Comm")
    add_tag("AI_PLC2_CmdSeq_New", "Bool", "%M82.0", "New command sequence received", "PLC2", "Comm")
    add_tag("AI_MB_TCP_Server_Error", "Bool", "%M82.1", "Modbus TCP Server Error", "PLC2", "Comm")
    add_tag("AI_MB_TCP_Server_Status", "Word", "%MW84", "Modbus TCP Server Status", "PLC2", "Comm")

    for name, comment in [
        ("AI_PLC1_Tip_Bon1_Xong_HMI", "Nút mô phỏng tip Bồn 1 đã hoàn tất"),
        ("AI_PLC1_Khuay_Bon1_Xong_HMI", "Nút mô phỏng hết thời gian khuấy Bồn 1"),
        ("AI_PLC1_Tip_Bon2_Xong_HMI", "Nút mô phỏng tip Bồn 2 đã hoàn tất"),
        ("AI_PLC1_Khuay_Thuan_Bon2_Xong_HMI", "Nút mô phỏng hết thời gian khuấy thuận Bồn 2"),
        ("AI_PLC1_Khuay_Nghich_Bon2_Xong_HMI", "Nút mô phỏng hết thời gian khuấy ngược Bồn 2"),
        ("AI_PLC1_Thanh_Trung_Bon2_Xong_HMI", "Nút mô phỏng hết thời gian thanh trùng Bồn 2"),
        ("AI_PLC2_Tip_Bon3_Xong_HMI", "Nút mô phỏng tip Bồn 3 đã hoàn tất"),
        ("AI_PLC2_Khuay_Bon3_Xong_HMI", "Nút mô phỏng hết thời gian khuấy Bồn 3"),
        ("AI_PLC2_Tip_Bon4_Xong_HMI", "Nút mô phỏng tip Bồn 4 đã hoàn tất"),
        ("AI_PLC2_Khuay_Thuan_Bon4_Xong_HMI", "Nút mô phỏng hết thời gian khuấy thuận Bồn 4"),
        ("AI_PLC2_Khuay_Nghich_Bon4_Xong_HMI", "Nút mô phỏng hết thời gian khuấy ngược Bồn 4"),
        ("AI_PLC2_Thanh_Trung_Bon4_Xong_HMI", "Nút mô phỏng hết thời gian thanh trùng Bồn 4"),
        ("AI_BonChua_Nhan_Dich_Xong_HMI", "Nút mô phỏng nhận dịch vào Bồn chứa 01 xong"),
        ("AI_BonChua_Chuyen_Bon2_Xong_HMI", "Nút mô phỏng chuyển sang Bồn chứa 02 xong"),
    ]:
        add_hmi_bool(name, comment, "Shared", "HMI_Simulation")

    for name, comment in [
        ("AI_HMI_SP_PLC1_Nuoc_Bon1", "Lượng nước dosing Bồn 1"),
        ("AI_HMI_SP_PLC1_Nuoc_Bon2", "Lượng nước dosing bổ sung Bồn 2"),
        ("AI_HMI_SP_PLC1_Toc_Do_Bon1", "Tốc độ khuấy Bồn 1"),
        ("AI_HMI_SP_PLC1_Toc_Do_Bon2_Main", "Tốc độ khuấy chính Bồn 2"),
        ("AI_HMI_SP_PLC1_Nhiet_Do_Bon2", "Setpoint nhiệt/PID Bồn 2"),
        ("AI_HMI_SP_PLC2_Nuoc_Bon3", "Lượng nước dosing Bồn 3"),
        ("AI_HMI_SP_PLC2_Nuoc_Bon4", "Lượng nước dosing bổ sung Bồn 4"),
        ("AI_HMI_SP_PLC2_Toc_Do_Bon3", "Tốc độ khuấy Bồn 3"),
        ("AI_HMI_SP_PLC2_Toc_Do_Bon4_Main", "Tốc độ khuấy chính Bồn 4"),
        ("AI_HMI_SP_PLC2_Nhiet_Do_Bon4", "Setpoint nhiệt/PID mô phỏng Bồn 4"),
        ("AI_HMI_SP_BonChua1_Nhiet_Giai_Nhiet", "Nhiệt độ giải nhiệt đích Bồn chứa 01"),
        ("AI_HMI_SP_Loc_Ap_Suat_Max", "Ngưỡng áp suất cao trước màng lọc"),
    ]:
        add_real(name, comment, "Shared", "HMI_Setpoint")

    for name, comment in [
        ("AI_HMI_SP_Time_Khuay_Bon1", "Thời gian khuấy Bồn 1"),
        ("AI_HMI_SP_Time_Khuay_Bon3", "Thời gian khuấy Bồn 3"),
        ("AI_HMI_SP_Time_Fwd", "Thời gian khuấy chiều thuận"),
        ("AI_HMI_SP_Time_Rev", "Thời gian khuấy chiều ngược"),
        ("AI_HMI_SP_Time_Sterilize", "Thời gian giữ nhiệt thanh trùng"),
    ]:
        add_time(name, comment, "Shared", "HMI_Setpoint")

    for name, comment in [
        ("AI_PLC1_Khuay_Bon1_Xong", "Trạng thái tự động xong khuấy Bồn 1"),
        ("AI_PLC1_Khuay_Thuan_Bon2_Xong", "Trạng thái tự động xong khuấy thuận Bồn 2"),
        ("AI_PLC1_Khuay_Nghich_Bon2_Xong", "Trạng thái tự động xong khuấy ngược Bồn 2"),
        ("AI_PLC1_Thanh_Trung_Bon2_Xong", "Trạng thái tự động xong thanh trùng Bồn 2"),
        ("AI_PLC2_Khuay_Bon3_Xong", "Trạng thái tự động xong khuấy Bồn 3"),
        ("AI_PLC2_Khuay_Thuan_Bon4_Xong", "Trạng thái tự động xong khuấy thuận Bồn 4"),
        ("AI_PLC2_Khuay_Nghich_Bon4_Xong", "Trạng thái tự động xong khuấy ngược Bồn 4"),
        ("AI_PLC2_Thanh_Trung_Bon4_Xong", "Trạng thái tự động xong thanh trùng Bồn 4"),
    ]:
        add_bool(name, comment, "Shared", "Internal_Status")

    for name, comment in [
        ("AI_PID_Bon2_Enable", "Cho phép PID Bồn 2"),
        ("AI_PID_Bon2_ManualEnable", "Chế độ manual PID Bồn 2"),
        ("AI_PID_Bon2_Error", "Lỗi khối PID Bồn 2"),
        ("AI_PID_Bon4_Enable", "Cho phép PID mô phỏng Bồn 4"),
        ("AI_PID_Bon4_ManualEnable", "Chế độ manual PID Bồn 4"),
        ("AI_PID_Bon4_Error", "Lỗi khối PID Bồn 4"),
    ]:
        add_bool(name, comment, "Shared", "PID")

    for name, comment in [
        ("AI_PID_Bon2_ErrorBits", "Mã lỗi DWORD PID Bồn 2"),
        ("AI_PID_Bon4_ErrorBits", "Mã lỗi DWORD PID Bồn 4"),
    ]:
        add_tag(name, "DWord", internal_real.next(), comment, "Shared", "PID")

    for name, comment in [
        ("AI_PID_Bon2_SP", "Setpoint đưa vào PID Bồn 2"),
        ("AI_PID_Bon2_Err", "Sai lệch PID Bồn 2 = SP - PV"),
        ("AI_PID_Bon2_CV", "Giá trị điều khiển PID Bồn 2"),
        ("AI_PID_Bon2_ManualValue", "Giá trị manual PID Bồn 2"),
        ("AI_PID_Bon4_SP", "Setpoint đưa vào PID mô phỏng Bồn 4"),
        ("AI_PID_Bon4_Err", "Sai lệch PID mô phỏng Bồn 4 = SP - PV"),
        ("AI_PID_Bon4_CV", "Giá trị điều khiển PID mô phỏng Bồn 4"),
        ("AI_PID_Bon4_ManualValue", "Giá trị manual PID Bồn 4"),
        ("AI_TT3219_Bon4_Sim", "Nhiệt độ mô phỏng nội bộ cho PID Bồn 4"),
        ("AI_PID_Bon4_Tang_Nhiet_Buoc", "Mức tăng nhiệt mô phỏng mỗi chu kỳ OB31"),
        ("AI_TT3219_Bon4_Target", "Nhiệt độ đích mô phỏng bồn 4"),
        ("AI_TT3219_Bon4_Sim_Pure", "Nhiệt độ mô phỏng chưa có nhiễu bồn 4"),
        ("AI_PID_Bon4_Temp_Val_1", "Biến tạm mô phỏng nhiệt độ 1"),
        ("AI_PID_Bon4_Temp_Val_2", "Biến tạm mô phỏng nhiệt độ 2"),
        ("AI_PID_Bon4_Sim_Counter", "Đồng hồ chu kỳ mô phỏng"),
        ("AI_PID_Bon4_Sim_Angle", "Góc lượng giác nhiễu"),
        ("AI_PID_Bon4_Sim_Sin", "Giá trị hình sin nhiễu"),
        ("AI_PID_Bon4_Sim_Noise", "Giá trị nhiễu nhiệt độ"),
    ]:
        add_real(name, comment, "Shared", "PID")
    add_int("AI_PID_Bon2_State", "Trạng thái khối PID Bồn 2", "PLC1", "PID")
    add_int("AI_PID_Bon4_State", "Trạng thái khối PID Bồn 4", "PLC2", "PID")

    add_bool("AI_PLC1_Stop_Active", "Tín hiệu dừng active PLC1", "PLC1", "Sequence")
    add_bool("AI_PLC2_Stop_Active", "Tín hiệu dừng active PLC2", "PLC2", "Sequence")
    add_bool("AI_VFD_Bon2_Khuay_Active", "Trạng thái khuấy Bồn 2 active", "PLC1", "Sequence")
    add_bool("AI_VFD_Bon2_Should_Run", "Yêu cầu chạy VFD Bồn 2", "PLC1", "Sequence")
    add_bool("AI_AGTR3263_Khuay_Active", "Trạng thái khuấy Bồn 4 active", "PLC2", "Sequence")
    add_bool("AI_AGTR3263_Should_Run", "Yêu cầu chạy động cơ Bồn 4", "PLC2", "Sequence")

    # Simulation selectors
    add_bool("AI_HMI_Use_Sim_Input_PLC1", "Cho phép sử dụng đầu vào mô phỏng PLC1", "PLC1", "HMI_Security")
    add_bool("AI_HMI_Use_Sim_Input_PLC2", "Cho phép sử dụng đầu vào mô phỏng PLC2", "PLC2", "HMI_Security")
    add_bool("AI_HMI_Use_Sim_Input_BonChua", "Cho phép sử dụng đầu vào mô phỏng Bồn chứa", "PLC1", "HMI_Security")

    # truyền thông Modbus TCP effective tags
    # Communication effective tags
    add_bool("AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff", "Cờ nhận trạng thái hoàn thành Nhánh 2 hiệu dụng", "PLC1", "Comm")
    add_bool("AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan_Eff", "Lệnh chạy bơm chuyển Nhánh 2 nhận được hiệu dụng", "PLC2", "Comm")
    add_bool("AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_HMI_Gated", "Cờ nhận trạng thái hoàn thành Nhánh 2 HMI gated", "PLC1", "Comm")
    add_bool("AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan_HMI_Gated", "Lệnh chạy bơm chuyển Nhánh 2 HMI gated", "PLC2", "Comm")

    # Setpoint validation & Init tags
    add_bool("AI_PLC1_SP_Valid", "Setpoint PLC1 hợp lệ", "PLC1", "Sequence")
    add_bool("AI_PLC2_SP_Valid", "Setpoint PLC2 hợp lệ", "PLC2", "Sequence")
    add_bool("AI_BonChua_SP_Valid", "Setpoint Bồn chứa hợp lệ", "PLC1", "Bon_Chua_Loc")
    add_bool("AI_PLC1_Loi_Setpoint", "Lỗi Setpoint PLC1", "PLC1", "Alarm")
    add_bool("AI_PLC2_Loi_Setpoint", "Lỗi Setpoint PLC2", "PLC2", "Alarm")
    add_bool("AI_BonChua_Loi_Setpoint", "Lỗi Setpoint Bồn chứa", "PLC1", "Alarm")
    add_bool("AI_Init_Defaults_Done_PLC1", "Khởi tạo Setpoint mặc định PLC1 hoàn tất", "PLC1", "Sequence")
    add_bool("AI_Init_Defaults_Done_PLC2", "Khởi tạo Setpoint mặc định PLC2 hoàn tất", "PLC2", "Sequence")
    add_bool("AI_Init_Defaults_Done_BonChua", "Khởi tạo Setpoint mặc định Bồn chứa hoàn tất", "PLC1", "Bon_Chua_Loc")
    add_bool("AI_Init_Trigger_PLC1", "Cờ kích hoạt nạp recipe mặc định PLC1", "PLC1", "Sequence")
    add_bool("AI_Init_Trigger_PLC2", "Cờ kích hoạt nạp recipe mặc định PLC2", "PLC2", "Sequence")
    add_bool("AI_Init_Trigger_BonChua", "Cờ kích hoạt nạp recipe mặc định Bồn chứa", "PLC1", "Bon_Chua_Loc")
    add_bool("AI_HMI_Load_Default_Recipe", "Yêu cầu nạp lại Recipe mặc định từ HMI", "Shared", "PID")

    # Communication tags for Load Default handshake
    # PLC1 -> PLC2
    add_tag("AI_PLC1_Load_Default_Cmd", "Bool", internal_bool.next(), "Lệnh nạp recipe mặc định gửi sang PLC2", "PLC1", "Comm")
    add_tag("AI_PLC1_Load_Default_Cmd_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho lệnh nạp recipe mặc định PLC1", "PLC1", "Comm")
    physical_outputs.append(("AI_PLC1_Load_Default_Cmd", "AI_PLC1_Load_Default_Cmd_M", "Bool"))
    add_tag("AI_PLC2_Load_Default_Cmd_Nhan", "Bool", internal_bool.next(), "Nhận lệnh nạp recipe mặc định từ PLC1", "PLC2", "Comm")
    add_tag("AI_PLC2_Load_Default_Cmd_Nhan_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI cho nhận lệnh nạp recipe", "PLC2", "Comm")
    add_tag("AI_PLC2_Load_Default_Cmd_Nhan_HMI_Gated", "Bool", internal_bool.next(), "Tín hiệu nhận lệnh nạp recipe HMI gated", "PLC2", "Comm")
    add_tag("AI_PLC2_Load_Default_Cmd_Nhan_Eff", "Bool", internal_bool.next(), "Tín hiệu nhận lệnh nạp recipe hiệu dụng", "PLC2", "Comm")

    # PLC2 -> PLC1
    add_tag("AI_PLC2_Load_Default_Done", "Bool", internal_bool.next(), "Báo nạp recipe mặc định xong gửi sang PLC1", "PLC2", "Comm")
    add_tag("AI_PLC2_Load_Default_Done_M", "Bool", mirror_do.next(), "Tag gương phản hồi HMI cho báo nạp recipe xong PLC2", "PLC2", "Comm")
    physical_outputs.append(("AI_PLC2_Load_Default_Done", "AI_PLC2_Load_Default_Done_M", "Bool"))
    add_tag("AI_PLC1_Load_Default_Done_Nhan", "Bool", internal_bool.next(), "Nhận báo nạp recipe xong từ PLC2", "PLC1", "Comm")
    add_tag("AI_PLC1_Load_Default_Done_Nhan_HMI", "Bool", hmi_di.next(), "Tín hiệu mô phỏng/HMI cho nhận báo nạp recipe xong", "PLC1", "Comm")
    add_tag("AI_PLC1_Load_Default_Done_Nhan_HMI_Gated", "Bool", internal_bool.next(), "Tín hiệu nhận báo nạp recipe xong HMI gated", "PLC1", "Comm")
    add_tag("AI_PLC1_Load_Default_Done_Nhan_Eff", "Bool", internal_bool.next(), "Tín hiệu nhận báo nạp recipe xong hiệu dụng", "PLC1", "Comm")

    # Simulation mode and run enable tags
    add_bool("AI_HMI_Sim_Mode", "Cho phép toàn bộ tín hiệu mô phỏng HMI tác động vào input hiệu dụng", "Shared", "HMI_Security")
    add_bool("AI_HMI_Run_Enable", "Cho phép vận hành từ HMI ở chế độ thật", "Shared", "HMI_Security")
    add_bool("AI_System_Mode_Real", "Hệ thống đang hoạt động ở chế độ thực tế", "Shared", "HMI_Security")
    add_bool("AI_System_Mode_Sim", "Hệ thống đang hoạt động ở chế độ mô phỏng", "Shared", "HMI_Security")
    add_bool("AI_HMI_Sim_Active_Warning", "Cảnh báo chế độ mô phỏng HMI đang hoạt động", "Shared", "HMI_Security")


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
      <Name>AI_Tags</Name>
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


def build_init_default_recipe_plc1() -> str:
    fc = TIALadderBuilder(fb_name="FC_Init_Default_Recipe_PLC1", block_id="50", block_type="FC")
    
    # 1. Startup triggers
    fc.add_network("Kích hoạt nạp recipe mặc định lần đầu scan PLC1", [
        ("NC", "AI_Init_Defaults_Done_PLC1"),
        ("SetCoil", "AI_Init_Trigger_PLC1"),
    ])
    fc.add_network("Kích hoạt nạp recipe mặc định lần đầu scan Bồn chứa", [
        ("NC", "AI_Init_Defaults_Done_BonChua"),
        ("SetCoil", "AI_Init_Trigger_BonChua"),
    ])
    
    # 2. HMI triggers (sets PLC1, BonChua and triggers PLC2 via truyền thông Modbus TCP cmd)
    fc.add_network("Kích hoạt nạp recipe mặc định từ HMI", [
        ("NO", "AI_HMI_Load_Default_Recipe"),
        ("SetCoil", "AI_Init_Trigger_PLC1"),
    ])
    fc.add_network("Kích hoạt nạp recipe mặc định Bồn chứa từ HMI", [
        ("NO", "AI_HMI_Load_Default_Recipe"),
        ("SetCoil", "AI_Init_Trigger_BonChua"),
    ])
    fc.add_network("Gửi lệnh nạp recipe mặc định sang PLC2 từ HMI", [
        ("NO", "AI_HMI_Load_Default_Recipe"),
        ("SetCoil", "AI_PLC1_Load_Default_Cmd"),
    ])
    
    # 3. Nạp giá trị recipe mặc định PLC1
    fc.add_network("Nạp giá trị recipe mặc định PLC1", [
        ("NO", "AI_Init_Trigger_PLC1"),
        ("MOVE", "100.0", "AI_HMI_SP_PLC1_Nuoc_Bon1"),
        ("MOVE", "50.0", "AI_HMI_SP_PLC1_Nuoc_Bon2"),
        ("MOVE", "60.0", "AI_HMI_SP_PLC1_Toc_Do_Bon1"),
        ("MOVE", "80.0", "AI_HMI_SP_PLC1_Toc_Do_Bon2_Main"),
        ("MOVE", "75.0", "AI_HMI_SP_PLC1_Nhiet_Do_Bon2"),
        ("MOVE", "T#10S", "AI_HMI_SP_Time_Khuay_Bon1"),
        ("MOVE", "T#3S", "AI_HMI_SP_Time_Fwd"),
        ("MOVE", "T#3S", "AI_HMI_SP_Time_Rev"),
        ("MOVE", "T#5S", "AI_HMI_SP_Time_Sterilize"),
        ("SetCoil", "AI_Init_Defaults_Done_PLC1"),
        ("ResetCoil", "AI_Init_Trigger_PLC1"),
    ])
    
    # 4. Nạp giá trị recipe mặc định Bồn chứa
    fc.add_network("Nạp giá trị recipe mặc định Bồn chứa", [
        ("NO", "AI_Init_Trigger_BonChua"),
        ("MOVE", "45.0", "AI_HMI_SP_BonChua1_Nhiet_Giai_Nhiet"),
        ("MOVE", "2.5", "AI_HMI_SP_Loc_Ap_Suat_Max"),
        ("SetCoil", "AI_Init_Defaults_Done_BonChua"),
        ("ResetCoil", "AI_Init_Trigger_BonChua"),
    ])
    
    # 5. PLC1 kết thúc quá trình nạp và reset lệnh HMI
    fc.add_network("PLC1 kết thúc nạp và reset lệnh HMI", [
        ("NO", "AI_HMI_Load_Default_Recipe"),
        ("NO", "AI_PLC1_Load_Default_Done_Nhan_Eff"),
        ("NC", "AI_Init_Trigger_PLC1"),
        ("NC", "AI_Init_Trigger_BonChua"),
        ("ResetCoil", "AI_HMI_Load_Default_Recipe"),
        ("ResetCoil", "AI_PLC1_Load_Default_Cmd"),
    ])
    return fc.generate_xml()


def build_init_default_recipe_plc2() -> str:
    fc = TIALadderBuilder(fb_name="FC_Init_Default_Recipe_PLC2", block_id="51", block_type="FC")
    
    # 1. Startup triggers
    fc.add_network("Kích hoạt nạp recipe mặc định lần đầu scan PLC2", [
        ("NC", "AI_Init_Defaults_Done_PLC2"),
        ("SetCoil", "AI_Init_Trigger_PLC2"),
    ])
    
    # 2. PLC2 triggers when receiving command from PLC1
    fc.add_network("Kích hoạt nạp recipe mặc định PLC2 từ truyền thông Modbus TCP Cmd", [
        ("NO", "AI_PLC2_Load_Default_Cmd_Nhan_Eff"),
        ("SetCoil", "AI_Init_Trigger_PLC2"),
    ])
    
    # 3. Nạp giá trị recipe mặc định PLC2
    fc.add_network("Nạp giá trị recipe mặc định PLC2", [
        ("NO", "AI_Init_Trigger_PLC2"),
        ("MOVE", "120.0", "AI_HMI_SP_PLC2_Nuoc_Bon3"),
        ("MOVE", "60.0", "AI_HMI_SP_PLC2_Nuoc_Bon4"),
        ("MOVE", "70.0", "AI_HMI_SP_PLC2_Toc_Do_Bon3"),
        ("MOVE", "90.0", "AI_HMI_SP_PLC2_Toc_Do_Bon4_Main"),
        ("MOVE", "80.0", "AI_HMI_SP_PLC2_Nhiet_Do_Bon4"),
        ("MOVE", "T#12S", "AI_HMI_SP_Time_Khuay_Bon3"),
        ("MOVE", "25.0", "AI_TT3219_Bon4_Sim_Pure"),
        ("MOVE", "25.0", "AI_TT3219_Bon4_Sim"),
        ("MOVE", "0.0", "AI_PID_Bon4_Sim_Counter"),
        ("SetCoil", "AI_Init_Defaults_Done_PLC2"),
        ("ResetCoil", "AI_Init_Trigger_PLC2"),
    ])
    
    # 4. PLC2 báo nạp xong sang PLC1
    fc.add_network("PLC2 báo hoàn thành nạp recipe", [
        ("NO", "AI_PLC2_Load_Default_Cmd_Nhan_Eff"),
        ("NC", "AI_Init_Trigger_PLC2"),
        ("SetCoil", "AI_PLC2_Load_Default_Done"),
    ])
    fc.add_network("PLC2 reset cờ hoàn thành nạp recipe", [
        ("NC", "AI_PLC2_Load_Default_Cmd_Nhan_Eff"),
        ("ResetCoil", "AI_PLC2_Load_Default_Done"),
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
        "AI_PLC1_Step_Bon1_Dosing",
        "AI_PLC1_Step_Bon1_Tip",
        "AI_PLC1_Step_Bon1_Khuay",
        "AI_PLC1_Step_Bon1_Xa",
        "AI_PLC1_Step_Bon2_Dosing",
        "AI_PLC1_Step_Bon2_Tip",
        "AI_PLC1_Step_Bon2_Khuay_Thuan",
        "AI_PLC1_Step_Bon2_Khuay_Nghich",
        "AI_PLC1_Step_Bon2_PID",
        "AI_PLC1_Step_Bon2_Thanh_Trung",
    ]

    # --- 1. Simulation Mapping (Digital & Analog) ---
    # Operator commands:
    fc.add_network("Khóa nút nhấn Start HMI qua Run Enable", [
        ("NO", "AI_HMI_Run_Enable"),
        ("NO", "AI_Nut_Khoi_Dong_HMI"),
        ("Coil", "AI_Nut_Khoi_Dong_HMI_Gated"),
    ])
    fc.add_network("Tín hiệu khởi động hiệu dụng", [
        ("OR2", "AI_Nut_Khoi_Dong", "AI_Nut_Khoi_Dong_HMI_Gated"),
        ("Coil", "AI_Nut_Khoi_Dong_Eff"),
    ])

    fc.add_network("Tín hiệu dừng hiệu dụng", [
        ("OR2", "AI_Nut_Dung", "AI_Nut_Dung_HMI"),
        ("Coil", "AI_Nut_Dung_Eff"),
    ])

    fc.add_network("Tín hiệu reset hiệu dụng", [
        ("OR2", "AI_Nut_Reset", "AI_Nut_Reset_HMI"),
        ("Coil", "AI_Nut_Reset_Eff"),
    ])

    fc.add_network("Tín hiệu dừng khẩn hiệu dụng", [
        ("OR2", "AI_Nut_EStop", "AI_Nut_EStop_HMI"),
        ("Coil", "AI_Nut_EStop_Eff"),
    ])

    # Sensors (digital):
    for tag in ["AI_LS3202_Bon1_Cao", "AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan", "AI_PLC1_Load_Default_Done_Nhan"]:
        fc.add_network(f"Gated HMI {tag} qua Sim Mode", [
            ("NO", "AI_HMI_Sim_Mode"),
            ("NO", tag + "_HMI"),
            ("Coil", tag + "_HMI_Gated"),
        ])
        fc.add_network(f"Tín hiệu {tag} hiệu dụng", [
            ("OR2", tag, tag + "_HMI_Gated"),
            ("Coil", tag + "_Eff"),
        ])

    # Sensors (analog):
    for tag in ["AI_FT3200_Bon1", "AI_FQ3200_Bon1", "AI_LT3203_Bon1", "AI_TT3204_Bon1", "AI_FT3205_Bon2", "AI_LT3209_Bon2", "AI_TT3208_Bon2"]:
        fc.add_network(f"Yêu cầu mô phỏng {tag} từ HMI", [
            ("OR2", "AI_HMI_Use_Sim_Input_PLC1", tag + "_Use_HMI"),
            ("Coil", tag + "_Sim_Req"),
        ])
        fc.add_network(f"Kích hoạt mô phỏng {tag} khi ở chế độ Sim Mode", [
            ("NO", "AI_HMI_Sim_Mode"),
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
        ("CMP_GT", "AI_HMI_SP_PLC1_Nuoc_Bon1", "0.0"),
        ("CMP_GT", "AI_HMI_SP_PLC1_Nuoc_Bon2", "0.0"),
        ("CMP_GT", "AI_HMI_SP_PLC1_Toc_Do_Bon1", "0.0"),
        ("CMP_GT", "AI_HMI_SP_PLC1_Toc_Do_Bon2_Main", "0.0"),
        ("CMP_GT", "AI_HMI_SP_PLC1_Nhiet_Do_Bon2", "0.0"),
        ("CMP_GT", "AI_HMI_SP_Time_Khuay_Bon1", "T#0s"),
        ("CMP_GT", "AI_HMI_SP_Time_Fwd", "T#0s"),
        ("CMP_GT", "AI_HMI_SP_Time_Rev", "T#0s"),
        ("CMP_GT", "AI_HMI_SP_Time_Sterilize", "T#0s"),
        ("Coil", "AI_PLC1_SP_Valid"),
    ])
    # --- 2. Sequence Start / Auto Control ---
    fc.add_network("Start PLC1 thành công từ nút vật lý hoặc HMI", [
        ("NO", "AI_Nut_Khoi_Dong_Eff"),
        ("NC", "AI_PLC1_Loi_Tong"),
        ("NO", "AI_PLC1_SP_Valid"),
        ("SetCoil", "AI_PLC1_Auto_Enable"),
    ])
    fc.add_network("Báo lỗi setpoint PLC1 khi bấm Start", [
        ("NO", "AI_Nut_Khoi_Dong_Eff"),
        ("NC", "AI_PLC1_Loi_Tong"),
        ("NC", "AI_PLC1_SP_Valid"),
        ("SetCoil", "AI_PLC1_Loi_Setpoint"),
    ])
    fc.add_network("Stop PLC1 từ nút vật lý hoặc HMI", [
        ("NO", "AI_Nut_Dung_Eff"),
        ("ResetCoil", "AI_PLC1_Auto_Enable"),
    ])

    # --- 3. Stop Active & Cleanup ---
    fc.add_network("Tạo tín hiệu Stop active PLC1", [
        ("NO", "AI_Nut_Dung_Eff"),
        ("Coil", "AI_PLC1_Stop_Active"),
    ])
    for step in steps + ["AI_PLC1_Me_Nhanh1_Hoan_Thanh"]:
        fc.add_network(f"Stop PLC1 - reset {step}", [("NO", "AI_PLC1_Stop_Active"), ("ResetCoil", step)])
    for out_tag in [
        "AI_V3230_Nuoc_Bon1", "AI_V3232_Xa_Bon1", "AI_V3233_Xa_Bon1", "AI_V3234_Xa_Bon1",
        "AI_V3235_Nuoc_Bon2", "AI_V3237_Xa_Bon2", "AI_V3238_Xa_Bon2", "AI_V3239_Xa_Bon2",
        "AI_Pump3264_Chuyen_Nhanh1",
    ]:
        fc.add_network(f"Stop PLC1 - reset {out_tag}", [("NO", "AI_PLC1_Stop_Active"), ("ResetCoil", out_tag)])
    fc.add_network("Stop PLC1 - reset PID Enable", [("NO", "AI_PLC1_Stop_Active"), ("ResetCoil", "AI_PID_Bon2_Enable")])
    for ao_tag in [
        "AI_CV3201_Nuoc_Bon1", "AI_AGTR3260_Toc_Do_AO", "AI_CV3206_Hoi_Bon2", "AI_VFD_Bon2_Toc_Do_AO",
    ]:
        fc.add_network(f"Stop PLC1 - clear {ao_tag}", [("NO", "AI_PLC1_Stop_Active"), ("MOVE", "0.0", ao_tag)])

    # --- 4. Safety E-Stop & Alarm Logic ---
    fc.add_network("Chốt E-Stop PLC1", [
        ("NO", "AI_Nut_EStop_Eff"),
        ("SetCoil", "AI_PLC1_EStop_Latch"),
    ])
    # Reset E-Stop path 1 (Physical reset)
    fc.add_network("Reset chốt E-Stop PLC1 an toàn (Vật lý)", [
        ("NO", "AI_Nut_Reset_Eff"),
        ("NC", "AI_Nut_EStop_Eff"),
        ("ResetCoil", "AI_PLC1_EStop_Latch"),
    ])
    # Reset E-Stop path 2 (HMI reset)
    fc.add_network("Reset chốt E-Stop PLC1 an toàn (HMI)", [
        ("NO", "AI_HMI_Reset_Alarm"),
        ("NO", "AI_HMI_Cho_Phep_Sua_Thong_So"),
        ("NC", "AI_Nut_EStop_Eff"),
        ("ResetCoil", "AI_PLC1_EStop_Latch"),
    ])

    fc.add_network("Mất truyền thông PLC1", [
        ("NO", "AI_Gia_Lap_Mat_Ket_Noi_HMI"),
        ("SetCoil", "AI_PLC1_Loi_Truyen_Thong"),
    ])
    fc.add_network("Dry Run bơm Nhánh 1", [
        ("NO", "AI_Pump3264_Chuyen_Nhanh1"),
        ("CMP_LE", "AI_LT3209_Bon2_Eff", "0.5"),
        ("SetCoil", "AI_PLC1_Loi_Dry_Run"),
    ])
    fc.add_network("Dosing Bồn 1 lỗi quá 5 giây không có lưu lượng", [
        ("NO", "AI_V3230_Nuoc_Bon1"),
        ("CMP_LE", "AI_FT3200_Bon1_Eff", "0.01"),
        ("TON", "AI_Timers_PLC1.AI_Timer_Dosing_Bon1", "T#5S", "AI_PLC1_Loi_Dosing"),
    ])
    fc.add_network("Dosing Bồn 2 lỗi quá 5 giây không có lưu lượng", [
        ("NO", "AI_V3235_Nuoc_Bon2"),
        ("CMP_LE", "AI_FT3205_Bon2_Eff", "0.01"),
        ("TON", "AI_Timers_PLC1.AI_Timer_Dosing_Bon2", "T#5S", "AI_PLC1_Loi_Dosing"),
    ])
    for fault in ["AI_PLC1_EStop_Latch", "AI_PLC1_Loi_Dry_Run", "AI_PLC1_Loi_Dosing", "AI_PLC1_Loi_Truyen_Thong", "AI_PLC1_Loi_Setpoint", "AI_BonChua_Loi_Setpoint"]:
        fc.add_network(f"Tổng hợp lỗi PLC1 từ {fault}", [("NO", fault), ("SetCoil", "AI_PLC1_Loi_Tong")])

    # Reset all alarms (Physical path)
    for alarm in ["AI_PLC1_Loi_Tong", "AI_PLC1_Loi_Dry_Run", "AI_PLC1_Loi_Dosing", "AI_PLC1_Loi_Truyen_Thong", "AI_PID_Bon2_Error", "AI_PLC1_Loi_Setpoint", "AI_BonChua_Loi_Setpoint"]:
        fc.add_network(f"Reset {alarm} từ nút vật lý", [
            ("NO", "AI_Nut_Reset_Eff"),
            ("NC", "AI_PLC1_EStop_Latch"),
            ("NC", "AI_Nut_EStop_Eff"),
            ("ResetCoil", alarm),
        ])
    # Reset all alarms (HMI path)
    for alarm in ["AI_PLC1_Loi_Tong", "AI_PLC1_Loi_Dry_Run", "AI_PLC1_Loi_Dosing", "AI_PLC1_Loi_Truyen_Thong", "AI_PID_Bon2_Error", "AI_PLC1_Loi_Setpoint", "AI_BonChua_Loi_Setpoint"]:
        fc.add_network(f"Reset {alarm} từ HMI", [
            ("NO", "AI_HMI_Reset_Alarm"),
            ("NO", "AI_HMI_Cho_Phep_Sua_Thong_So"),
            ("NC", "AI_PLC1_EStop_Latch"),
            ("NC", "AI_Nut_EStop_Eff"),
            ("ResetCoil", alarm),
        ])

    reset_many(fc, "AI_PLC1_Loi_Tong", steps, "Lỗi PLC1")

    # --- 5. Step Prevention Sequence Start ---
    start_ops = [
        ("NO", "AI_PLC1_Auto_Enable"),
        ("NC", "AI_PLC1_Me_Nhanh1_Hoan_Thanh"),
        ("NO", "AI_PLC1_SP_Valid"),
    ]
    for step in steps:
        start_ops.append(("NC", step))
    start_ops.append(("SetCoil", "AI_PLC1_Step_Bon1_Dosing"))
    fc.add_network("Bắt đầu chu trình Nhánh 1", start_ops)

    # --- 6. Step Transitions & Main Logic ---
    fc.add_network("State 10 - Dosing Bồn 1", [("NO", "AI_PLC1_Step_Bon1_Dosing"), ("MOVE", "10", "AI_PLC1_State")])
    fc.add_network("Mở nước Bồn 1", [("NO", "AI_PLC1_Step_Bon1_Dosing"), ("SetCoil", "AI_V3230_Nuoc_Bon1")])
    fc.add_network("CV nước Bồn 1 mở 100 phần trăm", [("NO", "AI_PLC1_Step_Bon1_Dosing"), ("MOVE", "100.0", "AI_CV3201_Nuoc_Bon1")])
    fc.add_network("Hoàn tất dosing Bồn 1", [
        ("NO", "AI_PLC1_Step_Bon1_Dosing"),
        ("CMP_GE", "AI_FQ3200_Bon1_Eff", "AI_HMI_SP_PLC1_Nuoc_Bon1"),
        ("SetCoil", "AI_PLC1_Step_Bon1_Tip"),
    ])
    fc.add_network("Đóng nước Bồn 1 sau dosing", [("NO", "AI_PLC1_Step_Bon1_Tip"), ("ResetCoil", "AI_V3230_Nuoc_Bon1")])
    fc.add_network("Reset bước dosing Bồn 1", [("NO", "AI_PLC1_Step_Bon1_Tip"), ("ResetCoil", "AI_PLC1_Step_Bon1_Dosing")])

    fc.add_network("State 11 - Tip cốt tương Nhật Bản", [("NO", "AI_PLC1_Step_Bon1_Tip"), ("MOVE", "11", "AI_PLC1_State")])
    fc.add_network("Tip Bồn 1 xong chuyển sang khuấy", [
        ("NO", "AI_PLC1_Step_Bon1_Tip"),
        ("NO", "AI_PLC1_Tip_Bon1_Xong_HMI"),
        ("SetCoil", "AI_PLC1_Step_Bon1_Khuay"),
    ])
    fc.add_network("Reset bước tip Bồn 1", [("NO", "AI_PLC1_Step_Bon1_Khuay"), ("ResetCoil", "AI_PLC1_Step_Bon1_Tip")])

    fc.add_network("State 12 - Khuấy Bồn 1", [("NO", "AI_PLC1_Step_Bon1_Khuay"), ("MOVE", "12", "AI_PLC1_State")])
    fc.add_network("Đặt tốc độ khuấy Bồn 1", [("NO", "AI_PLC1_Step_Bon1_Khuay"), ("MOVE", "AI_HMI_SP_PLC1_Toc_Do_Bon1", "AI_AGTR3260_Toc_Do_AO")])
    fc.add_network("Timer đếm thời gian khuấy Bồn 1", [
        ("NO", "AI_PLC1_Step_Bon1_Khuay"),
        ("TON", "AI_Timers_PLC1.AI_Timer_Khuay_Bon1", "AI_HMI_SP_Time_Khuay_Bon1", "AI_PLC1_Khuay_Bon1_Xong"),
    ])
    fc.add_network("Khuấy Bồn 1 xong chuyển xả", [
        ("NO", "AI_PLC1_Step_Bon1_Khuay"),
        ("OR2", "AI_PLC1_Khuay_Bon1_Xong", "AI_PLC1_Khuay_Bon1_Xong_HMI"),
        ("SetCoil", "AI_PLC1_Step_Bon1_Xa"),
    ])
    fc.add_network("Reset bước khuấy Bồn 1", [("NO", "AI_PLC1_Step_Bon1_Xa"), ("ResetCoil", "AI_PLC1_Step_Bon1_Khuay")])

    fc.add_network("State 15 - Xả Bồn 1 sang Bồn 2", [("NO", "AI_PLC1_Step_Bon1_Xa"), ("MOVE", "15", "AI_PLC1_State")])
    for valve in ["AI_V3232_Xa_Bon1", "AI_V3233_Xa_Bon1", "AI_V3234_Xa_Bon1"]:
        fc.add_network(f"Mở {valve}", [("NO", "AI_PLC1_Step_Bon1_Xa"), ("SetCoil", valve)])
    fc.add_network("Bồn 1 cạn", [("NO", "AI_PLC1_Step_Bon1_Xa"), ("CMP_LE", "AI_LT3203_Bon1_Eff", "0.5"), ("SetCoil", "AI_PLC1_Xa_Bon1_Xong")])
    fc.add_network("Xả Bồn 1 xong chuyển Bồn 2 dosing", [
        ("NO", "AI_PLC1_Xa_Bon1_Xong"),
        ("SetCoil", "AI_PLC1_Step_Bon2_Dosing"),
    ])
    for valve in ["AI_V3232_Xa_Bon1", "AI_V3233_Xa_Bon1", "AI_V3234_Xa_Bon1"]:
        fc.add_network(f"Đóng {valve}", [("NO", "AI_PLC1_Step_Bon2_Dosing"), ("ResetCoil", valve)])
    fc.add_network("Reset bước xả Bồn 1", [("NO", "AI_PLC1_Step_Bon2_Dosing"), ("ResetCoil", "AI_PLC1_Step_Bon1_Xa")])

    fc.add_network("State 20 - Dosing Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Dosing"), ("MOVE", "20", "AI_PLC1_State")])
    fc.add_network("Mở nước Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Dosing"), ("SetCoil", "AI_V3235_Nuoc_Bon2")])
    fc.add_network("Hoàn tất dosing Bồn 2", [
        ("NO", "AI_PLC1_Step_Bon2_Dosing"),
        ("CMP_GE", "AI_FT3205_Bon2_Eff", "AI_HMI_SP_PLC1_Nuoc_Bon2"),
        ("SetCoil", "AI_PLC1_Step_Bon2_Tip"),
    ])
    fc.add_network("Đóng nước Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Tip"), ("ResetCoil", "AI_V3235_Nuoc_Bon2")])
    fc.add_network("Reset bước dosing Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Tip"), ("ResetCoil", "AI_PLC1_Step_Bon2_Dosing")])

    fc.add_network("State 21 - Tip phụ gia Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Tip"), ("MOVE", "21", "AI_PLC1_State")])
    fc.add_network("Tip Bồn 2 xong chuyển khuấy thuận", [
        ("NO", "AI_PLC1_Step_Bon2_Tip"),
        ("NO", "AI_PLC1_Tip_Bon2_Xong_HMI"),
        ("SetCoil", "AI_PLC1_Step_Bon2_Khuay_Thuan"),
    ])
    fc.add_network("Reset bước tip Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Khuay_Thuan"), ("ResetCoil", "AI_PLC1_Step_Bon2_Tip")])

    fc.add_network("State 22 - Khuấy thuận Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Khuay_Thuan"), ("MOVE", "22", "AI_PLC1_State")])
    fc.add_network("Tốc độ khuấy thuận Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Khuay_Thuan"), ("MOVE", "AI_HMI_SP_PLC1_Toc_Do_Bon2_Main", "AI_VFD_Bon2_Toc_Do_AO")])
    fc.add_network("Timer đếm thời gian khuấy thuận Bồn 2", [
        ("NO", "AI_PLC1_Step_Bon2_Khuay_Thuan"),
        ("TON", "AI_Timers_PLC1.AI_Timer_Khuay_Thuan_Bon2", "AI_HMI_SP_Time_Fwd", "AI_PLC1_Khuay_Thuan_Bon2_Xong"),
    ])
    fc.add_network("Hết khuấy thuận chuyển khuấy ngược", [
        ("NO", "AI_PLC1_Step_Bon2_Khuay_Thuan"),
        ("OR2", "AI_PLC1_Khuay_Thuan_Bon2_Xong", "AI_PLC1_Khuay_Thuan_Bon2_Xong_HMI"),
        ("SetCoil", "AI_PLC1_Step_Bon2_Khuay_Nghich"),
    ])
    fc.add_network("Reset bước khuấy thuận Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Khuay_Nghich"), ("ResetCoil", "AI_PLC1_Step_Bon2_Khuay_Thuan")])

    fc.add_network("State 23 - Khuấy ngược Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Khuay_Nghich"), ("MOVE", "23", "AI_PLC1_State")])
    fc.add_network("Timer đếm thời gian khuấy ngược Bồn 2", [
        ("NO", "AI_PLC1_Step_Bon2_Khuay_Nghich"),
        ("TON", "AI_Timers_PLC1.AI_Timer_Khuay_Nghich_Bon2", "AI_HMI_SP_Time_Rev", "AI_PLC1_Khuay_Nghich_Bon2_Xong"),
    ])
    fc.add_network("Hết khuấy ngược chuyển PID Bồn 2", [
        ("NO", "AI_PLC1_Step_Bon2_Khuay_Nghich"),
        ("OR2", "AI_PLC1_Khuay_Nghich_Bon2_Xong", "AI_PLC1_Khuay_Nghich_Bon2_Xong_HMI"),
        ("SetCoil", "AI_PLC1_Step_Bon2_PID"),
    ])
    fc.add_network("Reset bước khuấy ngược Bồn 2", [("NO", "AI_PLC1_Step_Bon2_PID"), ("ResetCoil", "AI_PLC1_Step_Bon2_Khuay_Nghich")])

    fc.add_network("State 30 - PID Bồn 2 qua VFD", [("NO", "AI_PLC1_Step_Bon2_PID"), ("MOVE", "30", "AI_PLC1_State")])
    fc.add_network("Cho phép PID Bồn 2", [("NO", "AI_PLC1_Step_Bon2_PID"), ("SetCoil", "AI_PID_Bon2_Enable")])
    fc.add_network("Nạp SP PID Bồn 2", [("NO", "AI_PLC1_Step_Bon2_PID"), ("MOVE", "AI_HMI_SP_PLC1_Nhiet_Do_Bon2", "AI_PID_Bon2_SP")])
    fc.add_network("Gia nhiệt Bồn 2 đạt SP", [
        ("NO", "AI_PLC1_Step_Bon2_PID"),
        ("CMP_GE", "AI_TT3208_Bon2_Eff", "AI_HMI_SP_PLC1_Nhiet_Do_Bon2"),
        ("SetCoil", "AI_PLC1_Step_Bon2_Thanh_Trung"),
    ])
    fc.add_network("Reset bước PID sang thanh trùng Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Thanh_Trung"), ("ResetCoil", "AI_PLC1_Step_Bon2_PID")])

    fc.add_network("State 31 - Thanh trùng Bồn 2", [("NO", "AI_PLC1_Step_Bon2_Thanh_Trung"), ("MOVE", "31", "AI_PLC1_State")])
    fc.add_network("Timer đếm thời gian thanh trùng Bồn 2", [
        ("NO", "AI_PLC1_Step_Bon2_Thanh_Trung"),
        ("TON", "AI_Timers_PLC1.AI_Timer_Thanh_Trung_Bon2", "AI_HMI_SP_Time_Sterilize", "AI_PLC1_Thanh_Trung_Bon2_Xong"),
    ])
    fc.add_network("Thanh trùng Bồn 2 xong", [
        ("NO", "AI_PLC1_Step_Bon2_Thanh_Trung"),
        ("OR2", "AI_PLC1_Thanh_Trung_Bon2_Xong", "AI_PLC1_Thanh_Trung_Bon2_Xong_HMI"),
        ("SetCoil", "AI_PLC1_Me_Nhanh1_Hoan_Thanh"),
    ])
    fc.add_network("Dừng PID khi hoàn thành Nhánh 1", [("NO", "AI_PLC1_Me_Nhanh1_Hoan_Thanh"), ("ResetCoil", "AI_PID_Bon2_Enable")])
    fc.add_network("Reset bước thanh trùng Bồn 2", [("NO", "AI_PLC1_Me_Nhanh1_Hoan_Thanh"), ("ResetCoil", "AI_PLC1_Step_Bon2_Thanh_Trung")])

    # --- 7. Standard Coils for Motors & VFDs ---
    fc.add_network("Chạy cánh khuấy Bồn 1 (Coil thường)", [
        ("NO", "AI_PLC1_Step_Bon1_Khuay"),
        ("NC", "AI_PLC1_Loi_Tong"),
        ("Coil", "AI_AGTR3260_Khuay_Bon1"),
    ])
    fc.add_network("Gom trạng thái khuấy thuận/ngược Bồn 2", [
        ("OR2", "AI_PLC1_Step_Bon2_Khuay_Thuan", "AI_PLC1_Step_Bon2_Khuay_Nghich"),
        ("Coil", "AI_VFD_Bon2_Khuay_Active"),
    ])
    fc.add_network("Yêu cầu chạy VFD Bồn 2 bao gồm PID", [
        ("OR2", "AI_VFD_Bon2_Khuay_Active", "AI_PLC1_Step_Bon2_PID"),
        ("Coil", "AI_VFD_Bon2_Should_Run"),
    ])
    fc.add_network("Lệnh chạy VFD Bồn 2 (Coil thường)", [
        ("NO", "AI_VFD_Bon2_Should_Run"),
        ("NC", "AI_PLC1_Loi_Tong"),
        ("Coil", "AI_VFD_Bon2_Run"),
    ])
    fc.add_network("Lệnh đảo chiều VFD Bồn 2 (Coil thường)", [
        ("NO", "AI_PLC1_Step_Bon2_Khuay_Nghich"),
        ("NC", "AI_PLC1_Loi_Tong"),
        ("Coil", "AI_VFD_Bon2_Dao_Chieu"),
    ])

    # --- 8. AO Idle Cleanups, Safety Interlocks & Clamping ---
    # AI_CV3201_Nuoc_Bon1
    fc.add_network("Reset CV nước Bồn 1 khi không dosing", [
        ("NC", "AI_PLC1_Step_Bon1_Dosing"),
        ("MOVE", "0.0", "AI_CV3201_Nuoc_Bon1"),
    ])
    fc.add_network("Reset CV nước Bồn 1 khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "AI_PLC1_Stop_Active", "AI_PLC1_Loi_Tong"),
        ("MOVE", "0.0", "AI_CV3201_Nuoc_Bon1"),
    ])
    fc.add_network("Clamp CV nước Bồn 1 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_CV3201_Nuoc_Bon1", "0.0"),
        ("MOVE", "0.0", "AI_CV3201_Nuoc_Bon1"),
    ])
    fc.add_network("Clamp CV nước Bồn 1 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_CV3201_Nuoc_Bon1", "100.0"),
        ("MOVE", "100.0", "AI_CV3201_Nuoc_Bon1"),
    ])

    # AI_AGTR3260_Toc_Do_AO
    fc.add_network("Reset tốc độ cánh khuấy Bồn 1 khi không khuấy", [
        ("NC", "AI_PLC1_Step_Bon1_Khuay"),
        ("MOVE", "0.0", "AI_AGTR3260_Toc_Do_AO"),
    ])
    fc.add_network("Reset tốc độ cánh khuấy Bồn 1 khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "AI_PLC1_Stop_Active", "AI_PLC1_Loi_Tong"),
        ("MOVE", "0.0", "AI_AGTR3260_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ cánh khuấy Bồn 1 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_AGTR3260_Toc_Do_AO", "0.0"),
        ("MOVE", "0.0", "AI_AGTR3260_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ cánh khuấy Bồn 1 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_AGTR3260_Toc_Do_AO", "100.0"),
        ("MOVE", "100.0", "AI_AGTR3260_Toc_Do_AO"),
    ])

    # AI_CV3206_Hoi_Bon2
    fc.add_network("Reset CV hơi Bồn 2 khi không chạy PID", [
        ("NC", "AI_PLC1_Step_Bon2_PID"),
        ("MOVE", "0.0", "AI_CV3206_Hoi_Bon2"),
    ])
    fc.add_network("Reset CV hơi Bồn 2 khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "AI_PLC1_Stop_Active", "AI_PLC1_Loi_Tong"),
        ("MOVE", "0.0", "AI_CV3206_Hoi_Bon2"),
    ])
    fc.add_network("Clamp CV hơi Bồn 2 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_CV3206_Hoi_Bon2", "0.0"),
        ("MOVE", "0.0", "AI_CV3206_Hoi_Bon2"),
    ])
    fc.add_network("Clamp CV hơi Bồn 2 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_CV3206_Hoi_Bon2", "100.0"),
        ("MOVE", "100.0", "AI_CV3206_Hoi_Bon2"),
    ])

    # AI_VFD_Bon2_Toc_Do_AO
    fc.add_network("Reset tốc độ VFD Bồn 2 khi không chạy", [
        ("NC", "AI_VFD_Bon2_Run"),
        ("MOVE", "0.0", "AI_VFD_Bon2_Toc_Do_AO"),
    ])
    fc.add_network("Reset tốc độ VFD Bồn 2 khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "AI_PLC1_Stop_Active", "AI_PLC1_Loi_Tong"),
        ("MOVE", "0.0", "AI_VFD_Bon2_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ VFD Bồn 2 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_VFD_Bon2_Toc_Do_AO", "0.0"),
        ("MOVE", "0.0", "AI_VFD_Bon2_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ VFD Bồn 2 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_VFD_Bon2_Toc_Do_AO", "100.0"),
        ("MOVE", "100.0", "AI_VFD_Bon2_Toc_Do_AO"),
    ])

    # Modbus RTU VFD Bon 2 Control Logic
    fc.add_network("VFD Bon 2 Freq Scale: Speed SP x 5.0", [
        ("MOVE", "AI_VFD_Bon2_Toc_Do_AO", "AI_VFD_Bon2_Freq_Temp"),
        ("MATH_MUL", "AI_VFD_Bon2_Freq_Temp", "5.0", "AI_VFD_Bon2_Freq_Temp")
    ])
    fc.add_network("VFD Bon 2 Freq Negate for Reverse Direction", [
        ("NO", "AI_VFD_Bon2_Dao_Chieu"),
        ("MATH_MUL", "AI_VFD_Bon2_Freq_Temp", "-1.0", "AI_VFD_Bon2_Freq_Temp")
    ])
    fc.add_network("VFD Bon 2 Convert Freq Real to Int", [
        ("CONV_Convert", "AI_VFD_Bon2_Freq_Temp", "AI_VFD_Bon2_MB_FreqSetpoint", "Real", "Int")
    ])
    fc.add_network("VFD Bon 2 Control Word: Fault Reset (0x008F)", [
        ("OR2", "AI_Nut_Reset_Eff", "AI_HMI_Reset_Alarm"),
        ("MOVE", "143", "AI_VFD_Bon2_MB_ControlWord")
    ])
    fc.add_network("VFD Bon 2 Control Word: Run Forward/Reverse (0x000F)", [
        ("NC", "AI_Nut_Reset_Eff"),
        ("NC", "AI_HMI_Reset_Alarm"),
        ("NO", "AI_VFD_Bon2_Run"),
        ("MOVE", "15", "AI_VFD_Bon2_MB_ControlWord")
    ])
    fc.add_network("VFD Bon 2 Control Word: Stop Ready (0x0006)", [
        ("NC", "AI_Nut_Reset_Eff"),
        ("NC", "AI_HMI_Reset_Alarm"),
        ("NC", "AI_VFD_Bon2_Run"),
        ("MOVE", "6", "AI_VFD_Bon2_MB_ControlWord")
    ])
    fc.add_network("VFD Bon 2 Actual Speed Convert Int to Real & Scale x 0.2", [
        ("CONV_Convert", "AI_VFD_Bon2_MB_ActualSpeed", "AI_VFD_Bon2_Actual_Speed_Feedback", "Int", "Real"),
        ("MATH_MUL", "AI_VFD_Bon2_Actual_Speed_Feedback", "0.2", "AI_VFD_Bon2_Actual_Speed_Feedback")
    ])

    # --- 9. Safety Outputs Reset ---
    for out_tag in [
        "AI_V3230_Nuoc_Bon1", "AI_V3232_Xa_Bon1", "AI_V3233_Xa_Bon1",
        "AI_V3234_Xa_Bon1", "AI_V3235_Nuoc_Bon2",
        "AI_V3237_Xa_Bon2", "AI_V3238_Xa_Bon2", "AI_V3239_Xa_Bon2", "AI_Pump3264_Chuyen_Nhanh1",
    ]:
        fc.add_network(f"Dừng an toàn PLC1 reset {out_tag}", [("NO", "AI_PLC1_Loi_Tong"), ("ResetCoil", out_tag)])
    return fc.generate_xml()


def build_plc2() -> str:
    fc = TIALadderBuilder(fb_name="FC_PLC2_Mixing", block_id="20", block_type="FC")
    steps = [
        "AI_PLC2_Step_Bon3_Dosing",
        "AI_PLC2_Step_Bon3_Tip",
        "AI_PLC2_Step_Bon3_Khuay",
        "AI_PLC2_Step_Bon3_Xa",
        "AI_PLC2_Step_Bon4_Dosing",
        "AI_PLC2_Step_Bon4_Tip",
        "AI_PLC2_Step_Bon4_Khuay_Thuan",
        "AI_PLC2_Step_Bon4_Khuay_Nghich",
        "AI_PLC2_Step_Bon4_PID_Mo_Phong",
        "AI_PLC2_Step_Bon4_Thanh_Trung",
    ]

    # --- 1. Simulation Mapping (Digital & Analog) ---
    # Operator commands (received from PLC1):
    fc.add_network("Khóa nút nhấn Start HMI qua Run Enable PLC2", [
        ("NO", "AI_HMI_Run_Enable"),
        ("NO", "AI_Nut_Khoi_Dong_Nhan_HMI"),
        ("Coil", "AI_Nut_Khoi_Dong_Nhan_HMI_Gated"),
    ])
    fc.add_network("Tín hiệu khởi động hiệu dụng PLC2", [
        ("OR2", "AI_Nut_Khoi_Dong_Nhan", "AI_Nut_Khoi_Dong_Nhan_HMI_Gated"),
        ("Coil", "AI_Nut_Khoi_Dong_Nhan_Eff"),
    ])

    fc.add_network("Tín hiệu dừng hiệu dụng PLC2", [
        ("OR2", "AI_Nut_Dung_Nhan", "AI_Nut_Dung_Nhan_HMI"),
        ("Coil", "AI_Nut_Dung_Nhan_Eff"),
    ])

    fc.add_network("Tín hiệu reset hiệu dụng PLC2", [
        ("OR2", "AI_Nut_Reset_Nhan", "AI_Nut_Reset_Nhan_HMI"),
        ("Coil", "AI_Nut_Reset_Nhan_Eff"),
    ])

    fc.add_network("Tín hiệu dừng khẩn hiệu dụng PLC2", [
        ("OR2", "AI_Nut_EStop_Nhan", "AI_Nut_EStop_Nhan_HMI"),
        ("Coil", "AI_Nut_EStop_Nhan_Eff"),
    ])

    # Sensors (digital):
    for tag in ["AI_LS3217_Bon4_Cao", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan", "AI_PLC2_Load_Default_Cmd_Nhan"]:
        fc.add_network(f"Gated HMI {tag} qua Sim Mode", [
            ("NO", "AI_HMI_Sim_Mode"),
            ("NO", tag + "_HMI"),
            ("Coil", tag + "_HMI_Gated"),
        ])
        fc.add_network(f"Tín hiệu {tag} hiệu dụng", [
            ("OR2", tag, tag + "_HMI_Gated"),
            ("Coil", tag + "_Eff"),
        ])

    # Sensors (analog):
    for tag in ["AI_FT3210_Bon3", "AI_LT3213_Bon3", "AI_TT3214_Bon3", "AI_FT3215_Bon4", "AI_FQ3215_Bon4", "AI_LT3218_Bon4", "AI_TT3219_Bon4"]:
        fc.add_network(f"Yêu cầu mô phỏng {tag} từ HMI", [
            ("OR2", "AI_HMI_Use_Sim_Input_PLC2", tag + "_Use_HMI"),
            ("Coil", tag + "_Sim_Req"),
        ])
        fc.add_network(f"Kích hoạt mô phỏng {tag} khi ở chế độ Sim Mode", [
            ("NO", "AI_HMI_Sim_Mode"),
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
        ("CMP_GT", "AI_HMI_SP_PLC2_Nuoc_Bon3", "0.0"),
        ("CMP_GT", "AI_HMI_SP_PLC2_Nuoc_Bon4", "0.0"),
        ("CMP_GT", "AI_HMI_SP_PLC2_Toc_Do_Bon3", "0.0"),
        ("CMP_GT", "AI_HMI_SP_PLC2_Toc_Do_Bon4_Main", "0.0"),
        ("CMP_GT", "AI_HMI_SP_PLC2_Nhiet_Do_Bon4", "0.0"),
        ("CMP_GT", "AI_HMI_SP_Time_Khuay_Bon3", "T#0s"),
        ("CMP_GT", "AI_HMI_SP_Time_Fwd", "T#0s"),
        ("CMP_GT", "AI_HMI_SP_Time_Rev", "T#0s"),
        ("CMP_GT", "AI_HMI_SP_Time_Sterilize", "T#0s"),
        ("Coil", "AI_PLC2_SP_Valid"),
    ])
    # --- 2. Sequence Start / Auto Control ---
    fc.add_network("Start PLC2 thành công từ HMI dùng chung", [
        ("NO", "AI_Nut_Khoi_Dong_Nhan_Eff"),
        ("NC", "AI_PLC2_Loi_Tong"),
        ("NO", "AI_PLC2_SP_Valid"),
        ("SetCoil", "AI_PLC2_Auto_Enable"),
    ])
    fc.add_network("Báo lỗi setpoint PLC2 khi bấm Start", [
        ("NO", "AI_Nut_Khoi_Dong_Nhan_Eff"),
        ("NC", "AI_PLC2_Loi_Tong"),
        ("NC", "AI_PLC2_SP_Valid"),
        ("SetCoil", "AI_PLC2_Loi_Setpoint"),
    ])
    fc.add_network("Stop PLC2 từ HMI dùng chung", [
        ("NO", "AI_Nut_Dung_Nhan_Eff"),
        ("ResetCoil", "AI_PLC2_Auto_Enable"),
    ])

    # --- 3. Stop Active & Cleanup ---
    fc.add_network("Tạo tín hiệu Stop active PLC2", [
        ("NO", "AI_Nut_Dung_Nhan_Eff"),
        ("Coil", "AI_PLC2_Stop_Active"),
    ])
    for step in steps + ["AI_PLC2_Me_Nhanh2_Hoan_Thanh"]:
        fc.add_network(f"Stop PLC2 - reset {step}", [("NO", "AI_PLC2_Stop_Active"), ("ResetCoil", step)])
    for out_tag in [
        "AI_V3240_Nuoc_Bon3", "AI_V3242_Xa_Bon3", "AI_V3243_Xa_Bon3", "AI_V3244_Xa_Bon3",
        "AI_V3245_Nuoc_Bon4", "AI_V3247_Xa_Bon4", "AI_V3248_Xa_Bon4", "AI_V3249_Xa_Bon4",
        "AI_Pump3265_Chuyen_Nhanh2",
    ]:
        fc.add_network(f"Stop PLC2 - reset {out_tag}", [("NO", "AI_PLC2_Stop_Active"), ("ResetCoil", out_tag)])
    fc.add_network("Stop PLC2 - reset PID Enable", [("NO", "AI_PLC2_Stop_Active"), ("ResetCoil", "AI_PID_Bon4_Enable")])
    for ao_tag in [
        "AI_CV3211_Nuoc_Bon3", "AI_AGTR3262_Toc_Do_AO", "AI_CV3216_Hoi_Bon4", "AI_AGTR3263_Toc_Do_AO",
    ]:
        fc.add_network(f"Stop PLC2 - clear {ao_tag}", [("NO", "AI_PLC2_Stop_Active"), ("MOVE", "0.0", ao_tag)])

    # --- 4. Safety E-Stop & Alarm Logic ---
    fc.add_network("Chốt E-Stop PLC2", [
        ("NO", "AI_Nut_EStop_Nhan_Eff"),
        ("SetCoil", "AI_PLC2_EStop_Latch"),
    ])
    # Reset E-Stop path 1 (Physical reset)
    fc.add_network("Reset chốt E-Stop PLC2 an toàn (Vật lý)", [
        ("NO", "AI_Nut_Reset_Nhan_Eff"),
        ("NC", "AI_Nut_EStop_Nhan_Eff"),
        ("ResetCoil", "AI_PLC2_EStop_Latch"),
    ])
    # Reset E-Stop path 2 (HMI reset)
    fc.add_network("Reset chốt E-Stop PLC2 an toàn (HMI)", [
        ("NO", "AI_HMI_Reset_Alarm"),
        ("NO", "AI_HMI_Cho_Phep_Sua_Thong_So"),
        ("NC", "AI_Nut_EStop_Nhan_Eff"),
        ("ResetCoil", "AI_PLC2_EStop_Latch"),
    ])

    fc.add_network("Mất truyền thông PLC2", [("NO", "AI_Gia_Lap_Mat_Ket_Noi_HMI"), ("SetCoil", "AI_PLC2_Loi_Truyen_Thong")])
    fc.add_network("Dry Run bơm Nhánh 2", [
        ("NO", "AI_Pump3265_Chuyen_Nhanh2"),
        ("CMP_LE", "AI_LT3218_Bon4_Eff", "0.5"),
        ("SetCoil", "AI_PLC2_Loi_Dry_Run"),
    ])
    fc.add_network("Dosing Bồn 3 lỗi quá 5 giây không có lưu lượng", [
        ("NO", "AI_V3240_Nuoc_Bon3"),
        ("CMP_LE", "AI_FT3210_Bon3_Eff", "0.01"),
        ("TON", "AI_Timers_PLC2.AI_Timer_Dosing_Bon3", "T#5S", "AI_PLC2_Loi_Dosing"),
    ])
    fc.add_network("Dosing Bồn 4 lỗi quá 5 giây không có lưu lượng", [
        ("NO", "AI_V3245_Nuoc_Bon4"),
        ("CMP_LE", "AI_FT3215_Bon4_Eff", "0.01"),
        ("TON", "AI_Timers_PLC2.AI_Timer_Dosing_Bon4", "T#5S", "AI_PLC2_Loi_Dosing"),
    ])
    for fault in ["AI_PLC2_EStop_Latch", "AI_PLC2_Loi_Dry_Run", "AI_PLC2_Loi_Dosing", "AI_PLC2_Loi_Truyen_Thong", "AI_PLC2_Loi_Setpoint"]:
        fc.add_network(f"Tổng hợp lỗi PLC2 từ {fault}", [("NO", fault), ("SetCoil", "AI_PLC2_Loi_Tong")])

    # Reset all alarms (Physical path)
    for alarm in ["AI_PLC2_Loi_Tong", "AI_PLC2_Loi_Dry_Run", "AI_PLC2_Loi_Dosing", "AI_PLC2_Loi_Truyen_Thong", "AI_PID_Bon4_Error", "AI_PLC2_Loi_Setpoint"]:
        fc.add_network(f"Reset {alarm} từ nút vật lý", [
            ("NO", "AI_Nut_Reset_Nhan_Eff"),
            ("NC", "AI_PLC2_EStop_Latch"),
            ("NC", "AI_Nut_EStop_Nhan_Eff"),
            ("ResetCoil", alarm),
        ])
    # Reset all alarms (HMI path)
    for alarm in ["AI_PLC2_Loi_Tong", "AI_PLC2_Loi_Dry_Run", "AI_PLC2_Loi_Dosing", "AI_PLC2_Loi_Truyen_Thong", "AI_PID_Bon4_Error", "AI_PLC2_Loi_Setpoint"]:
        fc.add_network(f"Reset {alarm} từ HMI", [
            ("NO", "AI_HMI_Reset_Alarm"),
            ("NO", "AI_HMI_Cho_Phep_Sua_Thong_So"),
            ("NC", "AI_PLC2_EStop_Latch"),
            ("NC", "AI_Nut_EStop_Nhan_Eff"),
            ("ResetCoil", alarm),
        ])

    reset_many(fc, "AI_PLC2_Loi_Tong", steps, "Lỗi PLC2")

    # --- 5. Step Prevention Sequence Start ---
    start_ops_plc2 = [
        ("NO", "AI_PLC2_Auto_Enable"),
        ("NC", "AI_PLC2_Me_Nhanh2_Hoan_Thanh"),
        ("NO", "AI_PLC2_SP_Valid"),
    ]
    for step in steps:
        start_ops_plc2.append(("NC", step))
    start_ops_plc2.append(("SetCoil", "AI_PLC2_Step_Bon3_Dosing"))
    fc.add_network("Bắt đầu chu trình Nhánh 2", start_ops_plc2)

    # --- 6. Step Transitions & Main Logic ---
    fc.add_network("State 10 - Dosing Bồn 3", [("NO", "AI_PLC2_Step_Bon3_Dosing"), ("MOVE", "10", "AI_PLC2_State")])
    fc.add_network("Mở nước Bồn 3", [("NO", "AI_PLC2_Step_Bon3_Dosing"), ("SetCoil", "AI_V3240_Nuoc_Bon3")])
    fc.add_network("CV nước Bồn 3 mở 100 phần trăm", [("NO", "AI_PLC2_Step_Bon3_Dosing"), ("MOVE", "100.0", "AI_CV3211_Nuoc_Bon3")])
    fc.add_network("Hoàn tất dosing Bồn 3", [
        ("NO", "AI_PLC2_Step_Bon3_Dosing"),
        ("CMP_GE", "AI_FT3210_Bon3_Eff", "AI_HMI_SP_PLC2_Nuoc_Bon3"),
        ("SetCoil", "AI_PLC2_Step_Bon3_Tip"),
    ])
    fc.add_network("Đóng nước Bồn 3 sau dosing", [("NO", "AI_PLC2_Step_Bon3_Tip"), ("ResetCoil", "AI_V3240_Nuoc_Bon3")])
    fc.add_network("Reset bước dosing Bồn 3", [("NO", "AI_PLC2_Step_Bon3_Tip"), ("ResetCoil", "AI_PLC2_Step_Bon3_Dosing")])

    fc.add_network("State 11 - Tip cốt tương đậu đậm đặc", [("NO", "AI_PLC2_Step_Bon3_Tip"), ("MOVE", "11", "AI_PLC2_State")])
    fc.add_network("Tip Bồn 3 xong chuyển sang khuấy", [
        ("NO", "AI_PLC2_Step_Bon3_Tip"),
        ("NO", "AI_PLC2_Tip_Bon3_Xong_HMI"),
        ("SetCoil", "AI_PLC2_Step_Bon3_Khuay"),
    ])
    fc.add_network("Reset bước tip Bồn 3", [("NO", "AI_PLC2_Step_Bon3_Khuay"), ("ResetCoil", "AI_PLC2_Step_Bon3_Tip")])

    fc.add_network("State 12 - Khuấy Bồn 3", [("NO", "AI_PLC2_Step_Bon3_Khuay"), ("MOVE", "12", "AI_PLC2_State")])
    fc.add_network("Đặt tốc độ khuấy Bồn 3", [("NO", "AI_PLC2_Step_Bon3_Khuay"), ("MOVE", "AI_HMI_SP_PLC2_Toc_Do_Bon3", "AI_AGTR3262_Toc_Do_AO")])
    fc.add_network("Timer đếm thời gian khuấy Bồn 3", [
        ("NO", "AI_PLC2_Step_Bon3_Khuay"),
        ("TON", "AI_Timers_PLC2.AI_Timer_Khuay_Bon3", "AI_HMI_SP_Time_Khuay_Bon3", "AI_PLC2_Khuay_Bon3_Xong"),
    ])
    fc.add_network("Khuấy Bồn 3 xong chuyển xả", [
        ("NO", "AI_PLC2_Step_Bon3_Khuay"),
        ("OR2", "AI_PLC2_Khuay_Bon3_Xong", "AI_PLC2_Khuay_Bon3_Xong_HMI"),
        ("SetCoil", "AI_PLC2_Step_Bon3_Xa"),
    ])
    fc.add_network("Reset bước khuấy Bồn 3", [("NO", "AI_PLC2_Step_Bon3_Xa"), ("ResetCoil", "AI_PLC2_Step_Bon3_Khuay")])

    fc.add_network("State 15 - Xả Bồn 3 sang Bồn 4", [("NO", "AI_PLC2_Step_Bon3_Xa"), ("MOVE", "15", "AI_PLC2_State")])
    for valve in ["AI_V3242_Xa_Bon3", "AI_V3243_Xa_Bon3", "AI_V3244_Xa_Bon3"]:
        fc.add_network(f"Mở {valve}", [("NO", "AI_PLC2_Step_Bon3_Xa"), ("SetCoil", valve)])
    fc.add_network("Bồn 3 cạn", [("NO", "AI_PLC2_Step_Bon3_Xa"), ("CMP_LE", "AI_LT3213_Bon3_Eff", "0.5"), ("SetCoil", "AI_PLC2_Xa_Bon3_Xong")])
    fc.add_network("Xả Bồn 3 xong chuyển Bồn 4 dosing", [("NO", "AI_PLC2_Xa_Bon3_Xong"), ("SetCoil", "AI_PLC2_Step_Bon4_Dosing")])
    for valve in ["AI_V3242_Xa_Bon3", "AI_V3243_Xa_Bon3", "AI_V3244_Xa_Bon3"]:
        fc.add_network(f"Đóng {valve}", [("NO", "AI_PLC2_Step_Bon4_Dosing"), ("ResetCoil", valve)])
    fc.add_network("Reset bước xả Bồn 3", [("NO", "AI_PLC2_Step_Bon4_Dosing"), ("ResetCoil", "AI_PLC2_Step_Bon3_Xa")])

    fc.add_network("State 20 - Dosing Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Dosing"), ("MOVE", "20", "AI_PLC2_State")])
    fc.add_network("Mở nước Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Dosing"), ("SetCoil", "AI_V3245_Nuoc_Bon4")])
    fc.add_network("Hoàn tất dosing Bồn 4", [
        ("NO", "AI_PLC2_Step_Bon4_Dosing"),
        ("CMP_GE", "AI_FQ3215_Bon4_Eff", "AI_HMI_SP_PLC2_Nuoc_Bon4"),
        ("SetCoil", "AI_PLC2_Step_Bon4_Tip"),
    ])
    fc.add_network("Đóng nước Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Tip"), ("ResetCoil", "AI_V3245_Nuoc_Bon4")])
    fc.add_network("Reset bước dosing Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Tip"), ("ResetCoil", "AI_PLC2_Step_Bon4_Dosing")])

    fc.add_network("State 21 - Tip phụ gia Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Tip"), ("MOVE", "21", "AI_PLC2_State")])
    fc.add_network("Tip Bồn 4 xong chuyển khuấy thuận", [
        ("NO", "AI_PLC2_Step_Bon4_Tip"),
        ("NO", "AI_PLC2_Tip_Bon4_Xong_HMI"),
        ("SetCoil", "AI_PLC2_Step_Bon4_Khuay_Thuan"),
    ])
    fc.add_network("Reset bước tip Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Khuay_Thuan"), ("ResetCoil", "AI_PLC2_Step_Bon4_Tip")])

    fc.add_network("State 22 - Khuấy thuận Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Khuay_Thuan"), ("MOVE", "22", "AI_PLC2_State")])
    fc.add_network("Tốc độ khuấy thuận Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Khuay_Thuan"), ("MOVE", "AI_HMI_SP_PLC2_Toc_Do_Bon4_Main", "AI_AGTR3263_Toc_Do_AO")])
    fc.add_network("Timer đếm thời gian khuấy thuận Bồn 4", [
        ("NO", "AI_PLC2_Step_Bon4_Khuay_Thuan"),
        ("TON", "AI_Timers_PLC2.AI_Timer_Khuay_Thuan_Bon4", "AI_HMI_SP_Time_Fwd", "AI_PLC2_Khuay_Thuan_Bon4_Xong"),
    ])
    fc.add_network("Hết khuấy thuận chuyển khuấy ngược Bồn 4", [
        ("NO", "AI_PLC2_Step_Bon4_Khuay_Thuan"),
        ("OR2", "AI_PLC2_Khuay_Thuan_Bon4_Xong", "AI_PLC2_Khuay_Thuan_Bon4_Xong_HMI"),
        ("SetCoil", "AI_PLC2_Step_Bon4_Khuay_Nghich"),
    ])
    fc.add_network("Reset bước khuấy thuận Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Khuay_Nghich"), ("ResetCoil", "AI_PLC2_Step_Bon4_Khuay_Thuan")])

    fc.add_network("State 23 - Khuấy ngược Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Khuay_Nghich"), ("MOVE", "23", "AI_PLC2_State")])
    fc.add_network("Timer đếm thời gian khuấy ngược Bồn 4", [
        ("NO", "AI_PLC2_Step_Bon4_Khuay_Nghich"),
        ("TON", "AI_Timers_PLC2.AI_Timer_Khuay_Nghich_Bon4", "AI_HMI_SP_Time_Rev", "AI_PLC2_Khuay_Nghich_Bon4_Xong"),
    ])
    fc.add_network("Hết khuấy ngược chuyển PID mô phỏng", [
        ("NO", "AI_PLC2_Step_Bon4_Khuay_Nghich"),
        ("OR2", "AI_PLC2_Khuay_Nghich_Bon4_Xong", "AI_PLC2_Khuay_Nghich_Bon4_Xong_HMI"),
        ("SetCoil", "AI_PLC2_Step_Bon4_PID_Mo_Phong"),
    ])
    fc.add_network("Reset bước khuấy ngược Bồn 4", [("NO", "AI_PLC2_Step_Bon4_PID_Mo_Phong"), ("ResetCoil", "AI_PLC2_Step_Bon4_Khuay_Nghich")])

    fc.add_network("State 30 - PID mô phỏng Bồn 4", [("NO", "AI_PLC2_Step_Bon4_PID_Mo_Phong"), ("MOVE", "30", "AI_PLC2_State")])
    fc.add_network("Cho phép PID mô phỏng Bồn 4", [("NO", "AI_PLC2_Step_Bon4_PID_Mo_Phong"), ("SetCoil", "AI_PID_Bon4_Enable")])
    fc.add_network("Nạp SP PID Bồn 4", [("NO", "AI_PLC2_Step_Bon4_PID_Mo_Phong"), ("MOVE", "AI_HMI_SP_PLC2_Nhiet_Do_Bon4", "AI_PID_Bon4_SP")])
    fc.add_network("Bồn 4 đạt nhiệt độ mô phỏng", [
        ("NO", "AI_PLC2_Step_Bon4_PID_Mo_Phong"),
        ("CMP_GE", "AI_TT3219_Bon4_Sim", "AI_HMI_SP_PLC2_Nhiet_Do_Bon4"),
        ("SetCoil", "AI_PLC2_Step_Bon4_Thanh_Trung"),
    ])
    fc.add_network("Reset bước PID mô phỏng Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Thanh_Trung"), ("ResetCoil", "AI_PLC2_Step_Bon4_PID_Mo_Phong")])

    fc.add_network("State 31 - Thanh trùng Bồn 4", [("NO", "AI_PLC2_Step_Bon4_Thanh_Trung"), ("MOVE", "31", "AI_PLC2_State")])
    fc.add_network("Timer đếm thời gian thanh trùng Bồn 4", [
        ("NO", "AI_PLC2_Step_Bon4_Thanh_Trung"),
        ("TON", "AI_Timers_PLC2.AI_Timer_Thanh_Trung_Bon4", "AI_HMI_SP_Time_Sterilize", "AI_PLC2_Thanh_Trung_Bon4_Xong"),
    ])
    fc.add_network("Thanh trùng Bồn 4 xong", [
        ("NO", "AI_PLC2_Step_Bon4_Thanh_Trung"),
        ("OR2", "AI_PLC2_Thanh_Trung_Bon4_Xong", "AI_PLC2_Thanh_Trung_Bon4_Xong_HMI"),
        ("SetCoil", "AI_PLC2_Me_Nhanh2_Hoan_Thanh"),
    ])
    fc.add_network("Reset cờ hoàn thành Nhánh 2 khi bắt đầu chuyển dịch", [
        ("NO", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan_Eff"),
        ("ResetCoil", "AI_PLC2_Me_Nhanh2_Hoan_Thanh"),
    ])
    fc.add_network("Điều khiển bơm chuyển Nhánh 2 từ PLC1", [
        ("NO", "AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan_Eff"),
        ("NC", "AI_PLC2_Loi_Tong"),
        ("Coil", "AI_Pump3265_Chuyen_Nhanh2"),
    ])
    fc.add_network("Dừng PID khi hoàn thành Nhánh 2", [("NO", "AI_PLC2_Me_Nhanh2_Hoan_Thanh"), ("ResetCoil", "AI_PID_Bon4_Enable")])
    fc.add_network("Reset bước thanh trùng Bồn 4", [("NO", "AI_PLC2_Me_Nhanh2_Hoan_Thanh"), ("ResetCoil", "AI_PLC2_Step_Bon4_Thanh_Trung")])

    # --- 7. Standard Coils for Motors & VFDs ---
    fc.add_network("Chạy cánh khuấy Bồn 3 (Coil thường)", [
        ("NO", "AI_PLC2_Step_Bon3_Khuay"),
        ("NC", "AI_PLC2_Loi_Tong"),
        ("Coil", "AI_AGTR3262_Khuay_Bon3"),
    ])
    fc.add_network("Gom trạng thái khuấy thuận/ngược Bồn 4", [
        ("OR2", "AI_PLC2_Step_Bon4_Khuay_Thuan", "AI_PLC2_Step_Bon4_Khuay_Nghich"),
        ("Coil", "AI_AGTR3263_Khuay_Active"),
    ])
    fc.add_network("Yêu cầu chạy động cơ Bồn 4", [
        ("NO", "AI_AGTR3263_Khuay_Active"),
        ("Coil", "AI_AGTR3263_Should_Run"),
    ])
    fc.add_network("Lệnh chạy động cơ khuấy Bồn 4 (Coil thường)", [
        ("NO", "AI_AGTR3263_Should_Run"),
        ("NC", "AI_PLC2_Loi_Tong"),
        ("Coil", "AI_AGTR3263_Khuay_Bon4"),
    ])
    fc.add_network("Lệnh đảo chiều động cơ khuấy Bồn 4 (Coil thường)", [
        ("NO", "AI_PLC2_Step_Bon4_Khuay_Nghich"),
        ("NC", "AI_PLC2_Loi_Tong"),
        ("Coil", "AI_AGTR3263_Dao_Chieu"),
    ])

    # --- 8. AO Idle Cleanups, Safety Interlocks & Clamping ---
    # AI_CV3211_Nuoc_Bon3
    fc.add_network("Reset CV nước Bồn 3 khi không dosing", [
        ("NC", "AI_PLC2_Step_Bon3_Dosing"),
        ("MOVE", "0.0", "AI_CV3211_Nuoc_Bon3"),
    ])
    fc.add_network("Reset CV nước Bồn 3 khi Stop hoặc Lỗi tổng PLC2", [
        ("OR2", "AI_PLC2_Stop_Active", "AI_PLC2_Loi_Tong"),
        ("MOVE", "0.0", "AI_CV3211_Nuoc_Bon3"),
    ])
    fc.add_network("Clamp CV nước Bồn 3 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_CV3211_Nuoc_Bon3", "0.0"),
        ("MOVE", "0.0", "AI_CV3211_Nuoc_Bon3"),
    ])
    fc.add_network("Clamp CV nước Bồn 3 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_CV3211_Nuoc_Bon3", "100.0"),
        ("MOVE", "100.0", "AI_CV3211_Nuoc_Bon3"),
    ])

    # AI_AGTR3262_Toc_Do_AO
    fc.add_network("Reset tốc độ cánh khuấy Bồn 3 khi không khuấy", [
        ("NC", "AI_PLC2_Step_Bon3_Khuay"),
        ("MOVE", "0.0", "AI_AGTR3262_Toc_Do_AO"),
    ])
    fc.add_network("Reset tốc độ cánh khuấy Bồn 3 khi Stop hoặc Lỗi tổng PLC2", [
        ("OR2", "AI_PLC2_Stop_Active", "AI_PLC2_Loi_Tong"),
        ("MOVE", "0.0", "AI_AGTR3262_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ cánh khuấy Bồn 3 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_AGTR3262_Toc_Do_AO", "0.0"),
        ("MOVE", "0.0", "AI_AGTR3262_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ cánh khuấy Bồn 3 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_AGTR3262_Toc_Do_AO", "100.0"),
        ("MOVE", "100.0", "AI_AGTR3262_Toc_Do_AO"),
    ])

    # AI_CV3216_Hoi_Bon4
    fc.add_network("Reset CV hơi Bồn 4 khi không chạy PID", [
        ("NC", "AI_PLC2_Step_Bon4_PID_Mo_Phong"),
        ("MOVE", "0.0", "AI_CV3216_Hoi_Bon4"),
    ])
    fc.add_network("Reset CV hơi Bồn 4 khi Stop hoặc Lỗi tổng PLC2", [
        ("OR2", "AI_PLC2_Stop_Active", "AI_PLC2_Loi_Tong"),
        ("MOVE", "0.0", "AI_CV3216_Hoi_Bon4"),
    ])
    fc.add_network("Clamp CV hơi Bồn 4 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_CV3216_Hoi_Bon4", "0.0"),
        ("MOVE", "0.0", "AI_CV3216_Hoi_Bon4"),
    ])
    fc.add_network("Clamp CV hơi Bồn 4 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_CV3216_Hoi_Bon4", "100.0"),
        ("MOVE", "100.0", "AI_CV3216_Hoi_Bon4"),
    ])

    # AI_AGTR3263_Toc_Do_AO
    fc.add_network("Reset tốc độ động cơ khuấy Bồn 4 khi không chạy", [
        ("NC", "AI_AGTR3263_Khuay_Bon4"),
        ("MOVE", "0.0", "AI_AGTR3263_Toc_Do_AO"),
    ])
    fc.add_network("Reset tốc độ động cơ khuấy Bồn 4 khi Stop hoặc Lỗi tổng PLC2", [
        ("OR2", "AI_PLC2_Stop_Active", "AI_PLC2_Loi_Tong"),
        ("MOVE", "0.0", "AI_AGTR3263_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ động cơ khuấy Bồn 4 trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_AGTR3263_Toc_Do_AO", "0.0"),
        ("MOVE", "0.0", "AI_AGTR3263_Toc_Do_AO"),
    ])
    fc.add_network("Clamp tốc độ động cơ khuấy Bồn 4 trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_AGTR3263_Toc_Do_AO", "100.0"),
        ("MOVE", "100.0", "AI_AGTR3263_Toc_Do_AO"),
    ])

    # --- 9. Safety Outputs Reset ---
    for out_tag in [
        "AI_V3240_Nuoc_Bon3", "AI_V3242_Xa_Bon3", "AI_V3243_Xa_Bon3",
        "AI_V3244_Xa_Bon3", "AI_V3245_Nuoc_Bon4",
        "AI_V3247_Xa_Bon4", "AI_V3248_Xa_Bon4", "AI_V3249_Xa_Bon4",
    ]:
        fc.add_network(f"Dừng an toàn PLC2 reset {out_tag}", [("NO", "AI_PLC2_Loi_Tong"), ("ResetCoil", out_tag)])
    return fc.generate_xml()


def build_storage() -> str:
    fc = TIALadderBuilder(fb_name="FC_Bon_Chua_Loc", block_id="30", block_type="FC")
    steps = [
        "AI_BonChua_Step_Nhan_Dich",
        "AI_BonChua_Step_Giai_Nhiet",
        "AI_BonChua_Step_Chuyen_Bon2",
        "AI_BonChua_Step_Loc_Chiet",
    ]

    # --- 1. Simulation Mapping (Digital & Analog) ---
    # Sensors (digital):
    for tag in ["AI_LSH3310_Pheu_Cao", "AI_LSL3311_Pheu_Thap"]:
        fc.add_network(f"Gated HMI {tag} qua Sim Mode", [
            ("NO", "AI_HMI_Sim_Mode"),
            ("NO", tag + "_HMI"),
            ("Coil", tag + "_HMI_Gated"),
        ])
        fc.add_network(f"Tín hiệu {tag} hiệu dụng", [
            ("OR2", tag, tag + "_HMI_Gated"),
            ("Coil", tag + "_Eff"),
        ])

    # Sensors (analog):
    for tag in [
        "AI_LT3302_BonChua1", "AI_TT3301_BonChua1", "AI_TT3303_TraoDoiNhiet",
        "AI_LT3307_BonChua2", "AI_TT3306_BonChua2", "AI_PI3308_Truoc_Filter",
        "AI_FT3309_Xa_Thanh_Pham"
    ]:
        fc.add_network(f"Yêu cầu mô phỏng {tag} từ HMI", [
            ("OR2", "AI_HMI_Use_Sim_Input_BonChua", tag + "_Use_HMI"),
            ("Coil", tag + "_Sim_Req"),
        ])
        fc.add_network(f"Kích hoạt mô phỏng {tag} khi ở chế độ Sim Mode", [
            ("NO", "AI_HMI_Sim_Mode"),
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
    fc.add_network("Kiểm tra hợp lệ Setpoint Bồn chứa", [
        ("CMP_GT", "AI_HMI_SP_BonChua1_Nhiet_Giai_Nhiet", "0.0"),
        ("CMP_GT", "AI_HMI_SP_Loc_Ap_Suat_Max", "0.0"),
        ("Coil", "AI_BonChua_SP_Valid"),
    ])

    # --- 2. Stop Logic (Uses PLC1 Stop active) ---
    # Reset all steps under Stop
    for step in steps + ["AI_BonChua_Me_Hoan_Thanh"]:
        fc.add_network(f"Stop Storage - reset {step}", [("NO", "AI_PLC1_Stop_Active"), ("ResetCoil", step)])
    
    # Reset all DOs under Stop
    for out_tag in [
        "AI_V3331_Xa_BonChua1", "AI_V3332_Xa_BonChua1", "AI_Pump3361_LuanChuyen_BonChua1",
        "AI_Pump3362_Xa_BonChua1", "AI_V3333_DieuHuong_BonChua1", "AI_V3334_DieuHuong_BonChua1",
        "AI_V3335_DieuHuong_BonChua1", "AI_V3338_Xa_BonChua2", "AI_V3339_Xa_BonChua2",
        "AI_Pump3364_Filter", "AI_Pump3365_Filter", "AI_V3340_Duong_Filter", "AI_V3341_Duong_Filter",
        "AI_Pump3264_Chuyen_Nhanh1", "AI_Pump3265_Chuyen_Nhanh2_Cmd",
    ]:
        fc.add_network(f"Stop Storage - reset {out_tag}", [("NO", "AI_PLC1_Stop_Active"), ("ResetCoil", out_tag)])

    # Move 0.0 to all AOs under Stop
    for ao_tag in [
        "AI_CV3304_Nuoc_Lam_Mat", "AI_CV_Filler_Cap_Dich",
    ]:
        fc.add_network(f"Stop Storage - clear {ao_tag}", [("NO", "AI_PLC1_Stop_Active"), ("MOVE", "0.0", ao_tag)])

    # --- 3. Step Prevention Sequence Start ---
    start_ops_storage = [
        ("OR2", "AI_PLC1_Me_Nhanh1_Hoan_Thanh", "AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff"),
        ("NO", "AI_BonChua_SP_Valid"),
    ]
    for step in steps:
        start_ops_storage.append(("NC", step))
    start_ops_storage.append(("SetCoil", "AI_BonChua_Step_Nhan_Dich"))
    fc.add_network("Nhận mẻ từ Nhánh 1 hoặc Nhánh 2 thành công", start_ops_storage)

    fc.add_network("Báo lỗi setpoint bồn chứa khi nhận mẻ", [
        ("OR2", "AI_PLC1_Me_Nhanh1_Hoan_Thanh", "AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff"),
        ("NC", "AI_BonChua_SP_Valid"),
        ("SetCoil", "AI_BonChua_Loi_Setpoint"),
    ])

    # --- 4. Main Logic ---
    fc.add_network("State 50 - Bồn chứa 01 nhận dịch", [("NO", "AI_BonChua_Step_Nhan_Dich"), ("MOVE", "50", "AI_BonChua_State")])
    fc.add_network("Reset cờ hoàn thành mẻ khi bắt đầu nhận dịch mới", [("NO", "AI_BonChua_Step_Nhan_Dich"), ("ResetCoil", "AI_BonChua_Me_Hoan_Thanh")])
    fc.add_network("Bật bơm chuyển Nhánh 1 khi hoàn thành", [("NO", "AI_PLC1_Me_Nhanh1_Hoan_Thanh"), ("SetCoil", "AI_Pump3264_Chuyen_Nhanh1")])
    fc.add_network("Bật bơm chuyển Nhánh 2 khi hoàn thành", [("NO", "AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff"), ("SetCoil", "AI_Pump3265_Chuyen_Nhanh2_Cmd")])
    fc.add_network("Nhận dịch xong chuyển giải nhiệt", [
        ("NO", "AI_BonChua_Step_Nhan_Dich"),
        ("NO", "AI_BonChua_Nhan_Dich_Xong_HMI"),
        ("SetCoil", "AI_BonChua_Step_Giai_Nhiet"),
    ])
    fc.add_network("Reset bước nhận dịch", [("NO", "AI_BonChua_Step_Giai_Nhiet"), ("ResetCoil", "AI_BonChua_Step_Nhan_Dich")])

    fc.add_network("State 60 - Giải nhiệt Bồn chứa 01", [("NO", "AI_BonChua_Step_Giai_Nhiet"), ("MOVE", "60", "AI_BonChua_State")])
    fc.add_network("Tắt bơm chuyển Nhánh 1 sau nhận dịch", [("NO", "AI_BonChua_Step_Giai_Nhiet"), ("ResetCoil", "AI_Pump3264_Chuyen_Nhanh1")])
    fc.add_network("Tắt bơm chuyển Nhánh 2 sau nhận dịch", [("NO", "AI_BonChua_Step_Giai_Nhiet"), ("ResetCoil", "AI_Pump3265_Chuyen_Nhanh2_Cmd")])
    fc.add_network("Reset cờ hoàn thành Nhánh 1", [("NO", "AI_BonChua_Step_Giai_Nhiet"), ("ResetCoil", "AI_PLC1_Me_Nhanh1_Hoan_Thanh")])
    fc.add_network("Mở nước làm mát 100 phần trăm", [("NO", "AI_BonChua_Step_Giai_Nhiet"), ("MOVE", "100.0", "AI_CV3304_Nuoc_Lam_Mat")])
    fc.add_network("Mở van xả đáy 01 để luân chuyển giải nhiệt", [("NO", "AI_BonChua_Step_Giai_Nhiet"), ("SetCoil", "AI_V3331_Xa_BonChua1")])
    fc.add_network("Bật bơm luân chuyển giải nhiệt", [("NO", "AI_BonChua_Step_Giai_Nhiet"), ("SetCoil", "AI_Pump3361_LuanChuyen_BonChua1")])
    fc.add_network("Đạt 45 độ C chuyển Bồn chứa 02", [
        ("NO", "AI_BonChua_Step_Giai_Nhiet"),
        ("CMP_LE", "AI_TT3301_BonChua1_Eff", "AI_HMI_SP_BonChua1_Nhiet_Giai_Nhiet"),
        ("SetCoil", "AI_BonChua_Step_Chuyen_Bon2"),
    ])
    fc.add_network("Reset bước giải nhiệt", [("NO", "AI_BonChua_Step_Chuyen_Bon2"), ("ResetCoil", "AI_BonChua_Step_Giai_Nhiet")])

    fc.add_network("State 70 - Chuyển sang Bồn chứa 02", [("NO", "AI_BonChua_Step_Chuyen_Bon2"), ("MOVE", "70", "AI_BonChua_State")])
    fc.add_network("Đóng van hơi giải nhiệt", [("NO", "AI_BonChua_Step_Chuyen_Bon2"), ("MOVE", "0.0", "AI_CV3304_Nuoc_Lam_Mat")])
    fc.add_network("Đóng van xả đáy 01 sau giải nhiệt", [("NO", "AI_BonChua_Step_Chuyen_Bon2"), ("ResetCoil", "AI_V3331_Xa_BonChua1")])
    fc.add_network("Dừng bơm luân chuyển sau giải nhiệt", [("NO", "AI_BonChua_Step_Chuyen_Bon2"), ("ResetCoil", "AI_Pump3361_LuanChuyen_BonChua1")])
    fc.add_network("Mở van xả đáy 02 để chuyển bồn", [("NO", "AI_BonChua_Step_Chuyen_Bon2"), ("SetCoil", "AI_V3332_Xa_BonChua1")])
    for out_tag in ["AI_Pump3362_Xa_BonChua1", "AI_V3333_DieuHuong_BonChua1", "AI_V3334_DieuHuong_BonChua1", "AI_V3335_DieuHuong_BonChua1"]:
        fc.add_network(f"Mở {out_tag}", [("NO", "AI_BonChua_Step_Chuyen_Bon2"), ("SetCoil", out_tag)])
    fc.add_network("Chuyển sang Bồn chứa 02 xong", [
        ("NO", "AI_BonChua_Step_Chuyen_Bon2"),
        ("NO", "AI_BonChua_Chuyen_Bon2_Xong_HMI"),
        ("SetCoil", "AI_BonChua_Step_Loc_Chiet"),
    ])
    fc.add_network("Reset bước chuyển bồn", [("NO", "AI_BonChua_Step_Loc_Chiet"), ("ResetCoil", "AI_BonChua_Step_Chuyen_Bon2")])

    fc.add_network("State 80 - Lọc CCP và chiết rót", [("NO", "AI_BonChua_Step_Loc_Chiet"), ("MOVE", "80", "AI_BonChua_State")])
    for out_tag in ["AI_Pump3362_Xa_BonChua1", "AI_V3332_Xa_BonChua1", "AI_V3333_DieuHuong_BonChua1", "AI_V3334_DieuHuong_BonChua1", "AI_V3335_DieuHuong_BonChua1"]:
        fc.add_network(f"Đóng {out_tag} sau khi chuyển bồn", [("NO", "AI_BonChua_Step_Loc_Chiet"), ("ResetCoil", out_tag)])
    for out_tag in ["AI_Pump3364_Filter", "AI_Pump3365_Filter", "AI_V3340_Duong_Filter", "AI_V3341_Duong_Filter"]:
        fc.add_network(f"Chạy {out_tag}", [("NO", "AI_BonChua_Step_Loc_Chiet"), ("SetCoil", out_tag)])
    fc.add_network("Mở van filler theo lưu lượng", [("NO", "AI_BonChua_Step_Loc_Chiet"), ("MOVE", "75.0", "AI_CV_Filler_Cap_Dich")])
    fc.add_network("Áp suất filter cao báo lỗi", [
        ("NO", "AI_BonChua_Step_Loc_Chiet"),
        ("CMP_GT", "AI_PI3308_Truoc_Filter_Eff", "AI_HMI_SP_Loc_Ap_Suat_Max"),
        ("SetCoil", "AI_PLC1_Loi_Tong"),
    ])
    fc.add_network("Bồn chứa 02 cạn hoàn thành mẻ", [
        ("NO", "AI_BonChua_Step_Loc_Chiet"),
        ("CMP_LE", "AI_LT3307_BonChua2_Eff", "0.5"),
        ("SetCoil", "AI_BonChua_Me_Hoan_Thanh"),
    ])
    fc.add_network("Reset lọc sau khi hoàn thành", [("NO", "AI_BonChua_Me_Hoan_Thanh"), ("ResetCoil", "AI_BonChua_Step_Loc_Chiet")])

    for out_tag in ["AI_Pump3364_Filter", "AI_Pump3365_Filter", "AI_V3340_Duong_Filter", "AI_V3341_Duong_Filter"]:
        fc.add_network(f"Dừng {out_tag} sau khi hoàn thành mẻ", [("NO", "AI_BonChua_Me_Hoan_Thanh"), ("ResetCoil", out_tag)])
    fc.add_network("Đóng van filler sau khi hoàn thành mẻ", [("NO", "AI_BonChua_Me_Hoan_Thanh"), ("MOVE", "0.0", "AI_CV_Filler_Cap_Dich")])

    # --- 5. AO Idle Cleanups, Safety Interlocks & Clamping ---
    # AI_CV3304_Nuoc_Lam_Mat
    fc.add_network("Reset CV nước làm mát khi không giải nhiệt", [
        ("NC", "AI_BonChua_Step_Giai_Nhiet"),
        ("MOVE", "0.0", "AI_CV3304_Nuoc_Lam_Mat"),
    ])
    fc.add_network("Reset CV nước làm mát khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "AI_PLC1_Stop_Active", "AI_PLC1_Loi_Tong"),
        ("MOVE", "0.0", "AI_CV3304_Nuoc_Lam_Mat"),
    ])
    fc.add_network("Clamp CV nước làm mát trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_CV3304_Nuoc_Lam_Mat", "0.0"),
        ("MOVE", "0.0", "AI_CV3304_Nuoc_Lam_Mat"),
    ])
    fc.add_network("Clamp CV nước làm mát trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_CV3304_Nuoc_Lam_Mat", "100.0"),
        ("MOVE", "100.0", "AI_CV3304_Nuoc_Lam_Mat"),
    ])

    # AI_CV_Filler_Cap_Dich
    fc.add_network("Reset CV cấp dịch khi không lọc chiết", [
        ("NC", "AI_BonChua_Step_Loc_Chiet"),
        ("MOVE", "0.0", "AI_CV_Filler_Cap_Dich"),
    ])
    fc.add_network("Reset CV cấp dịch khi Stop hoặc Lỗi tổng PLC1", [
        ("OR2", "AI_PLC1_Stop_Active", "AI_PLC1_Loi_Tong"),
        ("MOVE", "0.0", "AI_CV_Filler_Cap_Dich"),
    ])
    fc.add_network("Clamp CV cấp dịch trong dải 0.0-100.0 (Dưới)", [
        ("CMP_LT", "AI_CV_Filler_Cap_Dich", "0.0"),
        ("MOVE", "0.0", "AI_CV_Filler_Cap_Dich"),
    ])
    fc.add_network("Clamp CV cấp dịch trong dải 0.0-100.0 (Trên)", [
        ("CMP_GT", "AI_CV_Filler_Cap_Dich", "100.0"),
        ("MOVE", "100.0", "AI_CV_Filler_Cap_Dich"),
    ])

    for bit in steps:
        fc.add_network(f"Reset {bit} khi lỗi PLC1", [("NO", "AI_PLC1_Loi_Tong"), ("ResetCoil", bit)])
    for out_tag in [
        "AI_Pump3264_Chuyen_Nhanh1", "AI_Pump3265_Chuyen_Nhanh2_Cmd", "AI_Pump3361_LuanChuyen_BonChua1",
        "AI_Pump3362_Xa_BonChua1", "AI_Pump3364_Filter", "AI_Pump3365_Filter", "AI_V3331_Xa_BonChua1",
        "AI_V3332_Xa_BonChua1", "AI_V3333_DieuHuong_BonChua1", "AI_V3334_DieuHuong_BonChua1",
        "AI_V3335_DieuHuong_BonChua1", "AI_V3340_Duong_Filter", "AI_V3341_Duong_Filter",
    ]:
        fc.add_network(f"Dừng an toàn bồn chứa reset {out_tag}", [("NO", "AI_PLC1_Loi_Tong"), ("ResetCoil", out_tag)])
    return fc.generate_xml()


def build_pid_plc1() -> str:
    ob = TIALadderBuilder(fb_name="OB30_PID_PLC1_Bon2", block_id="30", block_type="OB")
    ob.add_network("PID Compact Bon 2 - call technology block", [
        ("PID_Compact", "AI_PID_Compact_1",
            {
                "Setpoint": "AI_PID_Bon2_SP",
                "Input": "AI_TT3208_Bon2_Eff",
                "ManualEnable": "AI_PID_Bon2_ManualEnable",
                "ManualValue": "AI_PID_Bon2_ManualValue",
                "Reset": "AI_HMI_Reset_Alarm",
            },
            {
                "Output": "AI_PID_Bon2_CV",
                "State": "AI_PID_Bon2_State",
                "Error": "AI_PID_Bon2_ErrorBits",
            },
            "1.2"),
    ])
    ob.add_network("Detect PID Bon 2 Error", [
        ("CMP_NE", "AI_PID_Bon2_ErrorBits", "0"),
        ("Coil", "AI_PID_Bon2_Error"),
    ])
    ob.add_pid_mode_network("PID Compact Bon 2 - set i_Mode 3 or 0 like sample", "AI_PID_Bon2_Enable", "AI_PID_Compact_1")
    ob.add_network("Move PID Bon 2 CV to VFD", [
        ("NO", "AI_PID_Bon2_Enable"),
        ("MOVE", "AI_PID_Bon2_CV", "AI_VFD_Bon2_Toc_Do_AO"),
    ])
    ob.add_network("Allow Bon 2 steam valve while PID runs", [
        ("NO", "AI_PID_Bon2_Enable"),
        ("MOVE", "100.0", "AI_CV3206_Hoi_Bon2"),
    ])
    return cyclic_interrupt_xml(ob)


def build_pid_plc2() -> str:
    ob = TIALadderBuilder(fb_name="OB31_PID_PLC2_Bon4", block_id="31", block_type="OB")
    ob.add_network("PID Compact Bon 4 - call technology block", [
        ("PID_Compact", "AI_PID_Compact_2",
            {
                "Setpoint": "AI_PID_Bon4_SP",
                "Input": "AI_TT3219_Bon4_Sim",
                "ManualEnable": "AI_PID_Bon4_ManualEnable",
                "ManualValue": "AI_PID_Bon4_ManualValue",
                "Reset": "AI_HMI_Reset_Alarm",
            },
            {
                "Output": "AI_PID_Bon4_CV",
                "State": "AI_PID_Bon4_State",
                "Error": "AI_PID_Bon4_ErrorBits",
            },
            "1.2"),
    ])
    ob.add_network("Detect PID Bon 4 Error", [
        ("CMP_NE", "AI_PID_Bon4_ErrorBits", "0"),
        ("Coil", "AI_PID_Bon4_Error"),
    ])
    ob.add_pid_mode_network("PID Compact Bon 4 - set i_Mode 3 or 0 like sample", "AI_PID_Bon4_Enable", "AI_PID_Compact_2")
    ob.add_network("Move PID Bon 4 CV to simulated heat valve", [
        ("NO", "AI_PID_Bon4_Enable"),
        ("MOVE", "AI_PID_Bon4_CV", "AI_CV3216_Hoi_Bon4"),
    ])
    ob.add_network("If PID enabled, calculate heating target", [
        ("NO", "AI_PID_Bon4_Enable"),
        ("MATH_MUL", "AI_PID_Bon4_CV", "0.95", "AI_TT3219_Bon4_Target"),
    ])
    ob.add_network("If PID enabled, add ambient base to target", [
        ("NO", "AI_PID_Bon4_Enable"),
        ("MATH_ADD", "AI_TT3219_Bon4_Target", "25.0", "AI_TT3219_Bon4_Target"),
    ])
    ob.add_network("If PID disabled, set target to ambient", [
        ("NC", "AI_PID_Bon4_Enable"),
        ("MOVE", "25.0", "AI_TT3219_Bon4_Target"),
    ])
    ob.add_network("Calculate memory term: Pure * 0.99", [
        ("MATH_MUL", "AI_TT3219_Bon4_Sim_Pure", "0.99", "AI_PID_Bon4_Temp_Val_1"),
    ])
    ob.add_network("Calculate target term: Target * 0.01", [
        ("MATH_MUL", "AI_TT3219_Bon4_Target", "0.01", "AI_PID_Bon4_Temp_Val_2"),
    ])
    ob.add_network("Combine terms: Pure = Pure_prev * 0.99 + Target * 0.01", [
        ("MATH_ADD", "AI_PID_Bon4_Temp_Val_1", "AI_PID_Bon4_Temp_Val_2", "AI_TT3219_Bon4_Sim_Pure"),
    ])
    ob.add_network("Increment simulation counter", [
        ("MATH_ADD", "AI_PID_Bon4_Sim_Counter", "1.0", "AI_PID_Bon4_Sim_Counter"),
    ])
    ob.add_network("Reset simulation counter at 1000", [
        ("CMP_GE", "AI_PID_Bon4_Sim_Counter", "1000.0"),
        ("MOVE", "0.0", "AI_PID_Bon4_Sim_Counter"),
    ])
    ob.add_network("Calculate noise angle", [
        ("MATH_MUL", "AI_PID_Bon4_Sim_Counter", "0.05", "AI_PID_Bon4_Sim_Angle"),
    ])
    ob.add_network("Calculate sine of noise angle", [
        ("MATH1_Sin", "AI_PID_Bon4_Sim_Angle", "AI_PID_Bon4_Sim_Sin"),
    ])
    ob.add_network("Calculate noise value (amplitude 0.2)", [
        ("MATH_MUL", "AI_PID_Bon4_Sim_Sin", "0.2", "AI_PID_Bon4_Sim_Noise"),
    ])
    ob.add_network("Add noise to pure temperature to get noisy PV", [
        ("MATH_ADD", "AI_TT3219_Bon4_Sim_Pure", "AI_PID_Bon4_Sim_Noise", "AI_TT3219_Bon4_Sim"),
    ])
    return cyclic_interrupt_xml(ob)


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

    # Mô phỏng truyền thông Modbus TCP offline trên PLC1
    fc.add_network("Mô phỏng truyền thông Modbus TCP: Link Done nạp recipe PLC2 sang PLC1_HMI", [
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

    # Mô phỏng truyền thông Modbus TCP offline trên PLC2
    fc.add_network("Mô phỏng truyền thông Modbus TCP: Link Cmd nạp recipe PLC1 sang PLC2_HMI", [
        ("NO", "AI_HMI_Sim_Mode"),
        ("NO", "AI_HMI_Load_Default_Recipe"),
        ("Coil", "AI_PLC2_Load_Default_Cmd_Nhan_HMI"),
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
                "scope": "Điều khiển Bồn 1-2, PID Bồn 2 qua VFD/động cơ, và logic gom Bồn chứa/Lọc thành phẩm.",
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
            "AI_Tags.xml",
            "AI_Tags_PLC1.xml",
            "AI_Tags_PLC2.xml",
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
            "AI_Tags.xml gộp toàn bộ tag để QA Validator kiểm tra; khi import thực tế có thể tách theo cột plc/group.",
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
- PLC1 điều khiển Bồn 1, Bồn 2, PID Bồn 2 qua VFD/động cơ và cụm bồn chứa/lọc thành phẩm.
- PLC2 điều khiển Bồn 3, Bồn 4 và PID mô phỏng Bồn 4.
- Cờ `AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan` là điểm nhận kết quả Nhánh 2 về PLC1 để hiển thị hai bồn phụ trong một PLC.

## Màn hình HMI
- Login: dùng `AI_HMI_User_Level`, `AI_HMI_Operator_Login`, `AI_HMI_Engineer_Login`, `AI_HMI_Admin_Login`.
- Overview: dùng các tag `_M` của van, bơm, motor và các state `AI_PLC1_State`, `AI_PLC2_State`, `AI_BonChua_State`.
- Tank Details: dùng `AI_LT3203_Bon1`, `AI_LT3209_Bon2`, `AI_LT3213_Bon3`, `AI_LT3218_Bon4` cho animation mức; dùng motor mirror cho cánh khuấy.
- Parameters: chỉ cho ghi khi `AI_HMI_Cho_Phep_Sua_Thong_So = TRUE`.
- Sequence: gắn TextList `TL_Mixing_Step` với các tag state.
- PID: trend 3 đường SP/PV/CV cho Bồn 2 là `AI_PID_Bon2_SP`, `AI_TT3208_Bon2`, `AI_PID_Bon2_CV`; Bồn 4 mô phỏng là `AI_PID_Bon4_SP`, `AI_TT3219_Bon4_Sim`, `AI_PID_Bon4_CV`.
- Alarm banner: gắn `AI_HMI_AnToan_Status` với `TL_Canh_Bao_Mixing`.

## Quy tắc mô phỏng
- Mọi tag vật lý `%I` đều có tag `_HMI` song song để nhập mô phỏng từ WinCC/PLCSIM.
- Mọi tag vật lý `%Q` đều có tag `_M` để HMI đọc trạng thái phản hồi.
- Các nút `*_Xong_HMI` dùng cho demo nhanh khi chưa cấu hình timer thật trong TIA.
"""

    manual = """# MANUAL STEPS - IMPORT VÀ DEMO DỰ ÁN MIXING

## Import vào TIA Portal V18
1. Tạo project S7-1200 hoặc S7-1500 theo cấu hình phần cứng thi đấu.
2. Import `AI_Tags.xml` trước để có đầy đủ tag.
3. Import các block Ladder XML: `OB1_Main.xml`, `FC_PLC1_Mixing.xml`, `FC_PLC2_Mixing.xml`, `FC_Bon_Chua_Loc.xml`, `FC_HMI_Mirror_PLC1.xml`, `FC_HMI_Mirror_PLC2.xml`, `FC_Init_Default_Recipe_PLC1.xml`, `FC_Init_Default_Recipe_PLC2.xml`, `OB30_PID_PLC1_Bon2.xml`, `OB31_PID_PLC2_Bon4.xml`.
   *(Chú ý: Nếu bạn sử dụng các bộ import đóng gói chia sẵn trong thư mục `tia_import`, hãy chạy script `prepare_tia_import_sets.py` trước để tự động phân phối các block và sinh file Main.xml tương thích cho từng PLC1 và PLC2).*
4. Import các HMI TextList: `Hmi.TextList.TL_Mixing_Step.xml`, `Hmi.TextList.TL_Canh_Bao_Mixing.xml`, `Hmi.TextList.TL_Phan_Quyen.xml`.
5. PID Compact trong OB30/OB31: Cả hai PLC đều gọi PID_Compact version 1.2. PLC_1 sử dụng instance DB AI_PID_Compact_1, PLC_2 sử dụng instance DB AI_PID_Compact_2. Nếu TIA báo thiếu instance DB, hãy tạo các Technology Object AI_PID_Compact_1 và AI_PID_Compact_2 tương ứng bằng tay (chọn phiên bản 1.2) trong cây Technology objects của từng PLC trước khi biên dịch.

## Demo theo đề
1. **Khởi tạo thông số mặc định (Default Recipe):** Ở lần scan đầu tiên, các setpoint mặc định được nạp tự động thông qua các cờ độc lập `AI_Init_Defaults_Done_PLC1`, `AI_Init_Defaults_Done_PLC2`, và `AI_Init_Defaults_Done_BonChua`. Bạn cũng có thể kích hoạt nạp lại recipe mặc định bất cứ lúc nào từ HMI bằng tag `AI_HMI_Load_Default_Recipe` (Bool).
2. **Kiểm tra Setpoint hợp lệ:** Nhập setpoint cho các bồn (nước > 0.0, tốc độ > 0.0, nhiệt độ > 0.0, áp suất > 0.0, thời gian > T#0s). Nếu setpoint không hợp lệ (ví dụ: nước dosing = 0.0 hoặc thời gian khuấy = T#0s) và bạn nhấn nút Start, hệ thống sẽ chốt lỗi setpoint tương ứng (`AI_PLC1_Loi_Setpoint`, `AI_PLC2_Loi_Setpoint`, hoặc `AI_BonChua_Loi_Setpoint`) và khóa không cho sequence khởi động. Lỗi setpoint có thể được xóa bằng nút nhấn Reset vật lý (`AI_Nut_Reset_Eff`) hoặc nút Reset trên HMI (`AI_HMI_Reset_Alarm`).
3. **Cấu hình mô phỏng độc lập và chạy thật (Sim Mode / Real Mode):**
   - **Chế độ mô phỏng (Simulation Mode):** Bật `AI_HMI_Sim_Mode = TRUE`. Lúc này các sensor mô phỏng từ HMI được phép hoạt động:
     - Để mô phỏng toàn bộ cảm biến của một trạm: Bật thêm công tắc tổng `AI_HMI_Use_Sim_Input_PLC1` (cho PLC1), `AI_HMI_Use_Sim_Input_PLC2` (cho PLC2), hoặc `AI_HMI_Use_Sim_Input_BonChua` (cho Bồn chứa).
     - Để mô phỏng từng cảm biến riêng lẻ: Bật tag `AI_<sensor>_Use_HMI` tương ứng (ví dụ: `AI_TT3208_Bon2_Use_HMI` cho cảm biến nhiệt độ Bồn 2).
     - Khi Sim Mode ON, giá trị sensor mô phỏng HMI (`_HMI`) sẽ được ghi vào hiệu dụng (`_Eff`).
   - **Chế độ chạy thật (Real Mode):** Tắt `AI_HMI_Sim_Mode = FALSE`. Khi Sim Mode OFF:
     - Hệ thống tự động **bỏ qua (ignore)** và **reset (dọn dẹp)** toàn bộ các tag mô phỏng cảm biến `_HMI` về `FALSE` (digital) và `0.0` (analog).
     - Toàn bộ ngõ vào hiệu dụng `_Eff` sẽ lấy trực tiếp từ tín hiệu vật lý thực tế (%I và %AI), bất kể các nút nhấn Use_Sim_Input trên HMI có đang bật hay không.
     - Các setpoint HMI (`AI_HMI_SP_*`) và Recipe vẫn hoạt động và sử dụng bình thường cho chạy thật.
   - **Vận hành từ HMI khi chạy thật:** Tag `AI_HMI_Run_Enable` dùng để cho phép gửi lệnh khởi chạy (`Start`) từ HMI ở chế độ thật. Các nút nhấn safety (`Stop`, `Reset`, `E-Stop`) từ HMI luôn được chấp nhận trực tiếp mà không bị khóa để đảm bảo an toàn.
   - **Trạng thái hiển thị:**
     - `AI_System_Mode_Real = TRUE` khi đang ở chế độ chạy thật.
     - `AI_System_Mode_Sim = TRUE` khi đang ở chế độ mô phỏng.
     - `AI_HMI_Sim_Active_Warning = TRUE` nhấp nháy cảnh báo trên HMI khi chế độ mô phỏng đang hoạt động.
4. **Nhấn Start để chạy chu trình:** Nhấn nút Start vật lý hoặc HMI (`AI_Nut_Khoi_Dong_Eff`). Chu trình Auto Enable sẽ được kích hoạt cho PLC1 (`AI_PLC1_Auto_Enable`) và PLC2 (`AI_PLC2_Auto_Enable`).
5. **Quan sát & Trend các tín hiệu quan trọng:**
   - **Bồn 2 (PID thật):** Cảm biến nhiệt độ hiệu dụng `AI_TT3208_Bon2_Eff` -> Đưa vào PID -> Ngõ ra PID `AI_PID_Bon2_CV` điều khiển tốc độ cánh khuấy qua VFD `AI_VFD_Bon2_Toc_Do_AO`.
   - **Bồn 4 (PID mô phỏng):** Cảm biến nhiệt độ mô phỏng `AI_TT3219_Bon4_Sim` -> Đưa vào PID -> Ngõ ra PID `AI_PID_Bon4_CV` điều khiển van gia nhiệt mô phỏng `AI_CV3216_Hoi_Bon4`.
   - **Kết nối Nhánh 2:** Kết quả Nhánh 2 hoàn thành được gửi qua truyền thông Modbus TCP sang PLC1 qua tag nhận `AI_PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff` để bắt đầu cụm bồn chứa.
   - **Dịch chuyển Bồn chứa & Lọc:** Sau khi Nhánh 1 hoặc Nhánh 2 hoàn thành, cụm bồn chứa sẽ chuyển dịch qua Bồn chứa 01, giải nhiệt thông qua van tuyến tính nước làm mát `AI_CV3304_Nuoc_Lam_Mat`, sau đó chuyển sang Bồn chứa 02, bơm qua màng lọc CCP và điều khiển van tuyến tính filler `AI_CV_Filler_Cap_Dich` cấp xuống phễu chiết rót.
6. **Bảo vệ và giới hạn an toàn ngõ ra Analog (AO Clamping):** Mọi ngõ ra analog (AO) bao gồm CV van tuyến tính và tốc độ đặt động cơ/VFD được clamp cứng trong dải `0.0..100.0`. Khi có sự kiện Stop, E-Stop, Lỗi tổng, hoặc khi bước chương trình liên quan không hoạt động, các ngõ ra này sẽ lập tức cưỡng bức về `0.0` để bảo đảm an toàn tuyệt đối.

## Alarm và bảo mật
- Operator chỉ Start/Stop, Ack Alarm và xem màn hình.
- Engineer/Admin được sửa setpoint, bật Manual và Reset Alarm.
- Dry run: bơm chạy khi mức bồn xả gần 0 thì chốt lỗi.
- Dosing lỗi: van cấp mở nhưng lưu lượng không tăng.
- Mất truyền thông: bật `AI_Gia_Lap_Mat_Ket_Noi_HMI` để kích hoạt còi và banner đỏ.
"""

    logic = """# LOGIC ANALYSIS - MIXING NƯỚC TƯƠNG MAGGI 2026

## Phân chia trách nhiệm
- PLC1: Bồn 1-2, PID Bồn 2 qua VFD/động cơ, bồn chứa 01/02 và lọc thành phẩm.
- PLC2: Bồn 3-4, PID mô phỏng Bồn 4.
- Kết quả hai nhánh được gom về PLC1 bằng cờ hoàn thành của từng nhánh.

## Chu trình chính
1. Nhánh 1 dosing Bồn 1, tip cốt tương Nhật Bản, khuấy thuận, xả sang Bồn 2.
2. Bồn 2 dosing bổ sung, tip phụ gia, khuấy thuận/ngược, PID qua VFD/động cơ, thanh trùng và báo hoàn thành.
3. Nhánh 2 tương tự với Bồn 3-4; PID Bồn 4 là mô phỏng.
4. PLC1 nhận dịch từ nhánh hoàn thành, giải nhiệt tại Bồn chứa 01 xuống setpoint 45 độ C, chuyển Bồn chứa 02, lọc CCP và chiết rót.

## Interlock
- E-Stop HMI/physical được chốt và chỉ reset khi nút dừng khẩn đã nhả và có lệnh Reset.
- Dry run ngắt bơm khi mức bồn nguồn gần 0.
- Dosing lỗi nếu van mở nhưng FT không tăng.
- Reset alarm chỉ có hiệu lực với Engineer/Admin.
"""

    (OUTPUT_DIR / "Tag_Binding.md").write_text(tag_binding, encoding="utf-8")
    (OUTPUT_DIR / "MANUAL_STEPS.md").write_text(manual, encoding="utf-8")
    (OUTPUT_DIR / "Logic_Analysis.md").write_text(logic, encoding="utf-8")


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


def generate_standard_db_xml(db_name: str, db_number: int, members: list[tuple[str, str]]) -> str:
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


def main() -> None:
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
        ("Heartbeat", "Int"),
    ]
    db_modbus_server = [
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
        ("Heartbeat_Server", "Int"),
    ]

    files = {
        "AI_Tags.xml": tag_xml(),
        "AI_Tags_PLC1.xml": tag_xml("PLC1"),
        "AI_Tags_PLC2.xml": tag_xml("PLC2"),
        "OB1_Main.xml": build_ob1(),
        "FC_PLC1_Mixing.xml": build_plc1(),
        "FC_PLC2_Mixing.xml": build_plc2(),
        "FC_Bon_Chua_Loc.xml": build_storage(),
        "FC_Init_Default_Recipe_PLC1.xml": build_init_default_recipe_plc1(),
        "FC_Init_Default_Recipe_PLC2.xml": build_init_default_recipe_plc2(),
        "OB30_PID_PLC1_Bon2.xml": build_pid_plc1(),
        "OB31_PID_PLC2_Bon4.xml": build_pid_plc2(),
        "FC_HMI_Mirror_PLC1.xml": build_hmi_mirror_plc1(),
        "FC_HMI_Mirror_PLC2.xml": build_hmi_mirror_plc2(),
        "AI_Timers_PLC1.xml": generate_global_db_xml("AI_Timers_PLC1", [
            ("AI_Timer_Dosing_Bon1", "IEC_TIMER"),
            ("AI_Timer_Dosing_Bon2", "IEC_TIMER"),
            ("AI_Timer_Khuay_Bon1", "IEC_TIMER"),
            ("AI_Timer_Khuay_Thuan_Bon2", "IEC_TIMER"),
            ("AI_Timer_Khuay_Nghich_Bon2", "IEC_TIMER"),
            ("AI_Timer_Thanh_Trung_Bon2", "IEC_TIMER"),
            ("AI_VFD_Bon2_MB_Counter", "IEC_COUNTER"),
        ]),
        "AI_Timers_PLC2.xml": generate_global_db_xml("AI_Timers_PLC2", [
            ("AI_Timer_Dosing_Bon3", "IEC_TIMER"),
            ("AI_Timer_Dosing_Bon4", "IEC_TIMER"),
            ("AI_Timer_Khuay_Bon3", "IEC_TIMER"),
            ("AI_Timer_Khuay_Thuan_Bon4", "IEC_TIMER"),
            ("AI_Timer_Khuay_Nghich_Bon4", "IEC_TIMER"),
            ("AI_Timer_Thanh_Trung_Bon4", "IEC_TIMER"),
        ]),
        "DB_PLC1_Send_To_PLC2_DB.xml": generate_standard_db_xml("DB_PLC1_Send_To_PLC2_DB", 11, db_plc1_send),
        "DB_PLC1_Recv_From_PLC2_DB.xml": generate_standard_db_xml("DB_PLC1_Recv_From_PLC2_DB", 10, db_plc1_recv),
        "DB_MB_TCP_Client_Conn_DB.xml": generate_standard_db_xml("DB_MB_TCP_Client_Conn_DB", 15, [("MB_TCP", "TCON_IP_v4")]),
        "DB_MB_TCP_Server_Conn_DB.xml": generate_standard_db_xml("DB_MB_TCP_Server_Conn_DB", 16, [("MB_TCP_SERVER", "TCON_IP_v4")]),
        "DB_Modbus_Holding_Register_DB.xml": generate_standard_db_xml("DB_Modbus_Holding_Register_DB", 20, db_modbus_server),
    }
    files.update(hmi_text_lists())

    for name, content in files.items():
        (OUTPUT_DIR / name).write_text(content, encoding="utf-8")

    (OUTPUT_DIR / "IO_Map.json").write_text(json.dumps(build_io_map(), ensure_ascii=False, indent=2), encoding="utf-8")

    write_docs()
    print(f"Generated {len(files)} XML files and docs in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
