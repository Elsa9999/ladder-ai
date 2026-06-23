# -*- coding: utf-8 -*-
"""
plc_modbus_simulator.py
========================
Mô phỏng PLC S7-1200 gửi dữ liệu cảm biến thực tế qua Modbus TCP.
HMI WinCC Pro kết nối đến PLC qua Modbus → nhận giá trị giả lập.

Cài đặt: pip install pymodbus

Chạy: python plc_modbus_simulator.py
       (Giữ chạy, HMI sẽ poll dữ liệu tự động)

Dữ liệu mô phỏng (thay đổi theo chu kỳ thực tế):
  - Nhiệt độ: dao động nhẹ quanh giá trị cài đặt
  - Lưu lượng: dao động theo trạng thái bơm
  - Trạng thái thiết bị: bật/tắt theo pattern
"""

import time
import math
import random
import struct
import threading
from datetime import datetime

# ============================================================
# KIỂM TRA PYMODBUS
# ============================================================
try:
    from pymodbus.server import StartTcpServer
    from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
    from pymodbus.device import ModbusDeviceIdentification
    PYMODBUS_AVAILABLE = True
    print("[OK] pymodbus được tìm thấy. Server Modbus TCP sẽ khởi động.")
except ImportError:
    PYMODBUS_AVAILABLE = False
    print("[WARN] pymodbus chưa cài. Chạy ở chế độ hiển thị thô (dry-run).")
    print("       Để cài: pip install pymodbus")

# ============================================================
# CẤU HÌNH MODBUS SERVER
# ============================================================
HOST = "0.0.0.0"    # Lắng nghe tất cả interfaces (HMI kết nối qua IP máy tính này)
PORT = 502          # Cổng Modbus TCP tiêu chuẩn
UNIT_ID = 1         # Slave ID

# ============================================================
# TAG MAPPING - SIM DATA
# Ánh xạ từ tag HMI → địa chỉ Modbus Holding Register (40001+)
# PLC S7-1200 với MB_SERVER dùng %DB để map Modbus registers
# ============================================================
# Real (Float 32-bit IEEE754) tags dùng 2 register liên tiếp (Big Endian Word Swap)
TAG_REGISTER_MAP = {
    # Tag Name              : (Reg_Start, Type, Unit,  Min,  Max,  Description)
    "1400_TT32_PV"         : ( 0,  "float", "°C",   60.0,  80.0,  "Nhiệt độ TT32"),
    "1400_FS51_PV"         : ( 2,  "float", "Hz",   45.0,  55.0,  "Tần số bơm FS51"),
    "1400_LGFE01_PV"       : ( 4,  "float", "%",   200.0, 500.0,  "Lưu lượng LGFE01"),
    "1406_TX35_PV"         : ( 6,  "float", "°C",    2.0,   8.0,  "Nhiệt độ/Áp suất TX35"),
    "1400_FT101_PV"        : ( 8,  "float", "Bar",  1.0,   5.0,  "Áp suất FT101"),
    "1400_FY301_PV"        : (10,  "float", "%",   10.0, 90.0,   "Điều chỉnh FY301"),
    "1400_FT115_PV"        : (12,  "float", "°C",   50.0,  75.0,  "Nhiệt độ FT115"),
    "1400_TT64_PV"         : (14,  "float", "°C",   55.0,  70.0,  "Nhiệt độ TT64"),
    "1400_FT102_PV"        : (16,  "float", "L/h", 100.0, 800.0,  "Lưu lượng FT102"),
    "1400_TT101_PV"        : (18,  "float", "°C",   58.0,  72.0,  "Nhiệt độ TT101"),
    "1400_FTT02_PV"        : (20,  "float", "°C",   48.0,  68.0,  "Nhiệt độ FTT02"),
    "1400_1_02_PV"         : (22,  "float", "°C",   60.0,  85.0,  "Cảm biến 1-02"),
    # Bool tags dùng Coils (địa chỉ Coil 00001+)
}

BOOL_TAG_REGISTER_MAP = {
    # Tag Name                      : (Coil_Addr, Description)
    "1500S_Trang_Thai"              : ( 0, "Dòng liệu 1500S đang chảy"),
    "1404T_Trang_Thai"              : ( 1, "Dòng liệu 1404T đang chảy"),
    "CR_2013_FO_104_Trang_Thai"     : ( 2, "Dòng CR-2013-FO-104"),
    "BFOC_SS_20_06_Trang_Thai"      : ( 3, "Dòng BFOC-SS-20-06"),
    "PC03010T01_Trang_Thai"         : ( 4, "PC03010T01 đang hoạt động"),
    "1401_Trang_Thai"               : ( 5, "1401 đang chạy"),
    "1400_PT91_Chay"                : ( 6, "Bơm PT91 đang chạy"),
    "1400_KCK01_Chay"               : ( 7, "Khuấy KCK01 đang chạy"),
    "1400_FT102_Mo"                 : ( 8, "Van FT102 mở"),
    "1400_TY33_Mo"                  : ( 9, "Van TY33 mở"),
    "160_FEC53_Mo"                  : (10, "Van 160-FEC53 mở"),
    "1400_TXC32_Mo"                 : (11, "Van TXC32 mở"),
    "1400_TC32_Mo"                  : (12, "Van TC32 mở"),
    "1400_FIC01_Mo"                 : (13, "Van FIC01 mở"),
    "1400_FS51_Mo"                  : (14, "FS51 đang mở"),
}

# ============================================================
# HÀM MÔ PHỎNG GIÁ TRỊ (THAY ĐỔI THEO THỜI GIAN)
# ============================================================
sim_time = 0.0

def sim_float(tag_name, t):
    """Trả về giá trị float mô phỏng thực tế cho tag"""
    cfg = TAG_REGISTER_MAP.get(tag_name)
    if cfg is None:
        return 0.0
    _, _, unit, min_v, max_v, _ = cfg
    mid = (min_v + max_v) / 2.0
    amp = (max_v - min_v) / 4.0
    
    # Mỗi tag có tần số dao động riêng để trông thực tế hơn
    freq_map = {
        "1400_TT32_PV":    0.05,   "1400_FS51_PV":    0.1,
        "1400_LGFE01_PV":  0.03,   "1406_TX35_PV":    0.08,
        "1400_FT101_PV":   0.07,   "1400_FY301_PV":   0.04,
        "1400_FT115_PV":   0.06,   "1400_TT64_PV":    0.05,
        "1400_FT102_PV":   0.09,   "1400_TT101_PV":   0.04,
        "1400_FTT02_PV":   0.06,   "1400_1_02_PV":    0.05,
    }
    freq = freq_map.get(tag_name, 0.05)
    noise = random.uniform(-0.2, 0.2) * amp * 0.1
    val = mid + amp * math.sin(2 * math.pi * freq * t) + noise
    return round(max(min_v, min(max_v, val)), 2)

def sim_bool(tag_name, t):
    """Trả về trạng thái bool mô phỏng"""
    # Một số thiết bị luôn ON, một số theo chu kỳ
    always_on = {"1500S_Trang_Thai", "1404T_Trang_Thai", "1400_PT91_Chay",
                 "1400_KCK01_Chay", "1400_FS51_Mo", "1400_FIC01_Mo"}
    if tag_name in always_on:
        return True
    # Các van mở/đóng theo chu kỳ 30 giây
    cycle_period = 30
    phase_map = {
        "CR_2013_FO_104_Trang_Thai": 0,
        "BFOC_SS_20_06_Trang_Thai":  5,
        "PC03010T01_Trang_Thai":     10,
        "1401_Trang_Thai":            15,
        "1400_FT102_Mo":              0,
        "1400_TY33_Mo":               5,
        "160_FEC53_Mo":               10,
        "1400_TXC32_Mo":              15,
        "1400_TC32_Mo":               20,
    }
    phase = phase_map.get(tag_name, 0)
    return ((t + phase) % cycle_period) < (cycle_period * 0.7)  # 70% thời gian là ON

# ============================================================
# HÀM FLOAT → MODBUS REGISTERS (2 regs, Big-Endian Word Swap)
# ============================================================
def float_to_registers(value):
    """Chuyển float IEEE754 thành 2 Modbus Holding Registers (Big-Endian Word-Swap)"""
    packed = struct.pack('>f', float(value))
    high = struct.unpack('>H', packed[0:2])[0]
    low  = struct.unpack('>H', packed[2:4])[0]
    return [high, low]

# ============================================================
# CẬP NHẬT DATASTORE (chạy trong thread riêng)
# ============================================================
def update_simulation(context, stop_event):
    global sim_time
    print("\n[SIM] Bắt đầu mô phỏng dữ liệu PLC...")
    print("=" * 60)

    while not stop_event.is_set():
        t = sim_time

        # Cập nhật Holding Registers (Float tags)
        regs = [0] * 100
        for tag_name, cfg in TAG_REGISTER_MAP.items():
            reg_start, typ, unit, *_ = cfg
            val = sim_float(tag_name, t)
            r0, r1 = float_to_registers(val)
            regs[reg_start]     = r0
            regs[reg_start + 1] = r1

        # Cập nhật Coils (Bool tags)
        coils = [False] * 32
        for tag_name, (addr, _) in BOOL_TAG_REGISTER_MAP.items():
            coils[addr] = sim_bool(tag_name, t)

        if PYMODBUS_AVAILABLE:
            # Cập nhật datastore
            slave = context[UNIT_ID]
            slave.setValues(3, 0, regs[:50])   # Holding Registers (FC3)
            slave.setValues(1, 0, coils[:32])   # Coils (FC1)

        # In trạng thái ra console mỗi 5 giây
        if int(t) % 5 == 0 and (t - int(t)) < 0.5:
            ts = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{ts}] t={t:.1f}s")
            for tag_name, cfg in TAG_REGISTER_MAP.items():
                reg_start, typ, unit, min_v, max_v, desc = cfg
                val = sim_float(tag_name, t)
                bar_len = int((val - min_v) / max(max_v - min_v, 0.01) * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                print(f"  {tag_name:22s}: {val:7.2f} {unit:5s}  [{bar}]  {desc}")

        sim_time += 0.5
        time.sleep(0.5)

# ============================================================
# MAIN
# ============================================================
def run_simulation_only():
    """Chế độ hiển thị khi không có pymodbus"""
    stop_event = threading.Event()
    try:
        update_simulation(None, stop_event)
    except KeyboardInterrupt:
        print("\n\n[SIM] Dừng mô phỏng.")
        stop_event.set()

def run_modbus_server():
    """Khởi động Modbus TCP Server thực sự"""
    # Tạo datastore
    store = ModbusSlaveContext(
        di = ModbusSequentialDataBlock(0, [0] * 64),    # Discrete Inputs
        co = ModbusSequentialDataBlock(0, [False] * 64), # Coils
        hr = ModbusSequentialDataBlock(0, [0] * 200),   # Holding Registers
        ir = ModbusSequentialDataBlock(0, [0] * 64),    # Input Registers
    )
    context = ModbusServerContext(slaves={UNIT_ID: store}, single=False)

    # Device identity
    identity = ModbusDeviceIdentification()
    identity.VendorName  = "AI Agent PLC Simulator"
    identity.ProductCode = "SCADA-SIM-V1"
    identity.ProductName = "CIP-Mixing PLC Simulator"
    identity.ModelName   = "S7-1200 SIM"
    identity.MajorMinorRevision = "1.0"

    # Khởi động thread cập nhật dữ liệu
    stop_event = threading.Event()
    sim_thread = threading.Thread(
        target=update_simulation,
        args=(context, stop_event),
        daemon=True
    )
    sim_thread.start()

    print("=" * 60)
    print(" CIP-MIXING PLC MODBUS TCP SIMULATOR")
    print("=" * 60)
    print(f"  Server: {HOST}:{PORT}  Unit ID: {UNIT_ID}")
    print(f"  Holding Registers (FC3/FC6): Float tags ({len(TAG_REGISTER_MAP)} tags)")
    print(f"  Coils (FC1/FC5): Bool tags  ({len(BOOL_TAG_REGISTER_MAP)} tags)")
    print()
    print("  CẤU HÌNH HMI (WinCC Pro):")
    print("    Driver: Modbus TCP/IP")
    print(f"    IP: {HOST} (IP máy tính này)")
    print(f"    Port: {PORT}")
    print(f"    Unit ID: {UNIT_ID}")
    print()
    print("  REGISTER MAP (Holding Registers, đọc bằng FC3):")
    for tag_name, cfg in TAG_REGISTER_MAP.items():
        reg_start, typ, unit, min_v, max_v, desc = cfg
        print(f"    Reg {reg_start:3d}-{reg_start+1}: {tag_name:22s} ({unit})")
    print()
    print("  COIL MAP (đọc bằng FC1):")
    for tag_name, (addr, desc) in BOOL_TAG_REGISTER_MAP.items():
        print(f"    Coil {addr:3d}: {tag_name:35s} ({desc})")
    print()
    print("  [Ctrl+C để dừng]")
    print("=" * 60)

    try:
        StartTcpServer(context=context, identity=identity, address=(HOST, PORT))
    except KeyboardInterrupt:
        print("\n[SIM] Dừng Modbus server.")
        stop_event.set()

# ============================================================
if __name__ == "__main__":
    if PYMODBUS_AVAILABLE:
        run_modbus_server()
    else:
        print()
        print("Cài pymodbus: pip install pymodbus==3.6.9")
        print("Chạy ở chế độ hiển thị (không có server)...")
        print()
        run_simulation_only()
