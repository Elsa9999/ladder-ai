# -*- coding: utf-8 -*-
"""
plc_sim_cip_mixing.py
==============================================
Mô phỏng PLC S7-1200 cho hệ thống CIP-MIXING
Theo yêu cầu bài thi SCADA (Facebook post):
  - Nhiệt độ: 50-80°C (TT3204/08/14/19)
  - Áp suất:  7-8 bar  (PT3204/08)
  - Lưu lượng: 100-200 L/h (FT3213)
  - Tần số:  20-30 Hz  (FS51)

Kết nối HMI qua Modbus TCP:
  IP: 127.0.0.1 (hoặc IP máy tính)
  Port: 502
  Unit ID: 1

  Holding Registers (FC3) - đọc giá trị float:
    Reg 0-1  : AI_TT3204_PV (°C)
    Reg 2-3  : AI_TT3208_PV (°C)
    Reg 4-5  : AI_TT3214_PV (°C)
    Reg 6-7  : AI_TT3219_PV (°C)
    Reg 8-9  : AI_PT3204_PV (bar)
    Reg 10-11: AI_PT3208_PV (bar)
    Reg 12-13: AI_FT3213_PV (L/h)
    Reg 14-15: AI_FS51_PV   (Hz)
    Reg 16   : AI_BON1_Chay (bool, 1=ON)
    Reg 17   : AI_BON2_Chay (bool, 1=ON)
    Reg 18   : AI_BON3_Chay (bool, 1=ON)
    Reg 19   : AI_BON4_Chay (bool, 1=ON)
    Reg 20   : AI_PUMP3264_Chay (bool)
    Reg 21   : AI_PUMP3265_Chay (bool)

Chạy: python plc_sim_cip_mixing.py
==============================================
"""

import sys, time, math, random, struct, threading
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

try:
    from pymodbus.server import StartTcpServer
    from pymodbus.datastore import (ModbusSequentialDataBlock,
                                    ModbusSlaveContext,
                                    ModbusServerContext)
    from pymodbus.device import ModbusDeviceIdentification
    HAS_MODBUS = True
except ImportError:
    HAS_MODBUS = False

# ============================================================
# CẤU HÌNH SERVER
# ============================================================
HOST    = "0.0.0.0"
PORT    = 502
UNIT_ID = 1

# ============================================================
# TAG DEFINITIONS
# ============================================================
ANALOG_TAGS = [
    # (Name,            Reg,  Unit,  Min,    Max,   Freq,  Phase)
    ("AI_LT3203_PV",    0,   "L",   100.0,  900.0,  0.04,  0.0),
    ("AI_TT3204_PV",    2,   "°C",   25.0,   35.0,  0.05,  1.5),
    ("AI_LT3209_PV",    4,   "L",   100.0,  900.0,  0.03,  3.0),
    ("AI_TT3208_PV",    6,   "°C",   68.0,   78.0,  0.04,  4.5),
    ("AI_LT3213_PV",    8,   "L",   100.0,  900.0,  0.035, 0.3),
    ("AI_TT3214_PV",   10,   "°C",   25.0,   35.0,  0.045, 1.0),
    ("AI_LT3218_PV",   12,   "L",   100.0,  900.0,  0.03,  2.0),
    ("AI_TT3219_PV",   14,   "°C",   88.0,   98.0,  0.05,  0.5),
]

BOOL_TAGS = [
    # (Name,                 Reg,  Always_on, Cycle_s)
    ("AI_BON1_Chay",         16,   True,      0),
    ("AI_BON2_Chay",         17,   True,      0),
    ("AI_BON3_Chay",         18,   True,      0),
    ("AI_BON4_Chay",         19,   True,      0),
    ("AI_PUMP3264_Chay",     20,   True,      0),
    ("AI_PUMP3265_Chay",     21,   True,      0),
]

# ============================================================
# HÀM TÍNH GIÁ TRỊ MÔ PHỎNG
# ============================================================
def sim_val(min_v, max_v, freq, phase, t):
    mid = (min_v + max_v) / 2.0
    amp = (max_v - min_v) / 2.5
    noise = random.uniform(-1, 1) * (max_v - min_v) * 0.02
    val = mid + amp * math.sin(2 * math.pi * freq * t + phase) + noise
    return round(max(min_v, min(max_v, val)), 2)

def float_to_regs(value):
    """IEEE754 float → 2 Modbus Holding Registers (Big-Endian Word)"""
    b = struct.pack('>f', float(value))
    return [int.from_bytes(b[0:2],'big'), int.from_bytes(b[2:4],'big')]

# ============================================================
# THREAD CẬP NHẬT DỮ LIỆU
# ============================================================
def sim_loop(context, stop_ev):
    t = 0.0
    print("\n" + "="*60)
    print("  CIP-MIXING PLC SIMULATOR - DANG CHAY")
    print("="*60)
    print(f"  Modbus TCP  : {HOST}:{PORT}  Unit={UNIT_ID}")
    print("  Analog tags : %d   Bool tags: %d" % (len(ANALOG_TAGS), len(BOOL_TAGS)))
    print("="*60)

    while not stop_ev.is_set():
        # Build register block (tối đa 30 regs)
        regs = [0] * 30

        # Analog (float, 2 regs mỗi tag)
        vals = {}
        for name, reg, unit, mn, mx, freq, phase in ANALOG_TAGS:
            v = sim_val(mn, mx, freq, phase, t)
            vals[name] = (v, unit)
            r0, r1 = float_to_regs(v)
            regs[reg]   = r0
            regs[reg+1] = r1

        # Bool → register 1 (ON) or 0 (OFF)
        for name, reg, always_on, cycle in BOOL_TAGS:
            regs[reg] = 1 if always_on else int((t % max(cycle,1)) < (cycle*0.75))

        if HAS_MODBUS and context is not None:
            context[UNIT_ID].setValues(3, 0, regs)

        # In console mỗi 3 giây
        if int(t * 2) % 6 == 0:
            ts = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{ts}]  t={t:.0f}s")
            for name, reg, unit, mn, mx, freq, phase in ANALOG_TAGS:
                v, _ = vals[name]
                bar_w = int((v - mn) / max(mx - mn, 0.001) * 24)
                bar   = "█"*bar_w + "░"*(24-bar_w)
                flag  = " ⚠" if (v < mn*1.01 or v > mx*0.99) else "  "
                print(f"  {name:22s}: {v:7.2f} {unit:5s}  [{bar}]{flag}")

        t += 0.5
        time.sleep(0.5)

# ============================================================
# MAIN
# ============================================================
def main():
    print("="*60)
    print("  CIP-MIXING PLC MODBUS TCP SIMULATOR")
    print("  Project: scadabai3_V18")
    print("="*60)
    print("\nRegister Map (Holding Registers FC3):")
    for name, reg, unit, mn, mx, *_ in ANALOG_TAGS:
        print(f"  Reg {reg:2d}-{reg+1}: {name:22s}  {unit:5s}  [{mn}-{mx}]")
    for name, reg, *_ in BOOL_TAGS:
        print(f"  Reg {reg:2d}  : {name:22s}  Bool  (1=ON)")

    stop_ev = threading.Event()

    if HAS_MODBUS:
        store = ModbusSlaveContext(
            hr=ModbusSequentialDataBlock(0, [0]*64),
        )
        ctx = ModbusServerContext(slaves={UNIT_ID: store}, single=False)

        t = threading.Thread(target=sim_loop, args=(ctx, stop_ev), daemon=True)
        t.start()

        identity = ModbusDeviceIdentification()
        identity.VendorName  = "AI Agent Lab"
        identity.ProductName = "CIP-MIXING Sim"
        identity.ModelName   = "S7-1200 SIM"
        identity.MajorMinorRevision = "1.0"

        print(f"\n[OK] Modbus TCP Server khoi dong: {HOST}:{PORT}")
        print("     Bam Ctrl+C de dung\n")
        try:
            StartTcpServer(context=ctx, identity=identity, address=(HOST, PORT))
        except KeyboardInterrupt:
            print("\n[STOP] Dung simulator.")
            stop_ev.set()
    else:
        print("\n[WARN] pymodbus chua cai. Chay dry-run (chi hien thi)...")
        print("       Cai: pip install pymodbus==3.6.9\n")
        try:
            sim_loop(None, stop_ev)
        except KeyboardInterrupt:
            print("\n[STOP] Dung.")
            stop_ev.set()

if __name__ == "__main__":
    main()
