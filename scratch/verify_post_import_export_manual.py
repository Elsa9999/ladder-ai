# -*- coding: utf-8 -*-
"""
verify_post_import_export_manual.py  (v3)
==========================================
Xác thực XML readback từ TIA Portal qua update_tia_project.exe.

Quy tắc bảo vệ (exit codes):
  exit(2) = SKIP  – CHỈ cho 2 trường hợp "chưa chạy TIA update":
                     1. post_import_export_manual chưa tồn tại.
                     2. readback_manifest.json chưa tồn tại.
  exit(1) = FAIL  – readback có nhưng dữ liệu sai / thiếu / lỗi compile:
                     parse JSON lỗi, ErrorCount != 0, project_path sai,
                     timestamp không hợp lệ, thiếu PLC_1/Blocks hoặc
                     PLC_2/Blocks, thư mục Blocks rỗng, thiếu file,
                     nội dung XML sai.
  exit(0) = PASS  – toàn bộ checks xanh.

Checks:
  0. Guard: thư mục + manifest + ErrorCount == 0 + độ mới
  1. OB30 PID mapping và không có MOVE 100.0 cứng
  2. FC_PLC1_Mixing van xả Bồn 2 theo Pump3264
  3. FC_PLC2_Mixing van xả Bồn 4 theo Pump3265
  4. VFD Bồn 2 và AGTR3263 chạy khi PID Enable
  5. Dosing timers T#5S
  6. FC_Manual_Control BlockNumber == 62 (parsed từ XML, không tìm chuỗi)
  7. FC_HMI_Animation BlockNumber == 60 / 61
  8. Timers blocks tồn tại và không có Timer_DryRun
  9. Inventory: đủ file bắt buộc
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

# ──────────────────────────────────────────────────────────────────────────────
EXPORT_DIR    = r'd:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export_manual'
OLD_EXPORT    = r'd:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export'
MANIFEST_PATH = os.path.join(EXPORT_DIR, 'readback_manifest.json')
P1_BLOCKS     = os.path.join(EXPORT_DIR, 'PLC_1', 'Blocks')
P2_BLOCKS     = os.path.join(EXPORT_DIR, 'PLC_2', 'Blocks')

FRESHNESS_WARN_HOURS = 24   # warn if readback older than this

# Required block files
PLC1_REQUIRED = [
    'OB30_PID_PLC1_Bon2.xml',   'FC_PLC1_Mixing.xml',
    'FC_HMI_Animation_PLC1.xml','FC_HMI_Mirror_PLC1.xml',
    'FC_Manual_Control_PLC1.xml','FC_Bon_Chua_Loc.xml',
    'FC_Init_Default_Recipe_PLC1.xml', 'Timers_PLC1.xml',
    'Main.xml', 'DB_MB_TCP_Client_Conn_DB.xml', 'DB_PLC1_MB_Word_Buffer_DB.xml', 'DB_PLC1_MB_Buffer_DB.xml',
    'DB_PLC1_Recv_From_PLC2_DB.xml', 'DB_PLC1_Send_To_PLC2_DB.xml',
    'FC_VFD_Bon2_Hybrid.xml',
]
PLC2_REQUIRED = [
    'OB31_PID_PLC2_Bon4.xml',   'FC_PLC2_Mixing.xml',
    'FC_HMI_Animation_PLC2.xml','FC_HMI_Mirror_PLC2.xml',
    'FC_Manual_Control_PLC2.xml','FC_Init_Default_Recipe_PLC2.xml',
    'Timers_PLC2.xml', 'Main.xml', 'DB_MB_TCP_Server_Conn_DB.xml', 'DB_PLC2_MB_Holding_Word_DB.xml', 'DB_Modbus_Holding_Register_DB.xml',
]

print("=========================================================")
print(" POST IMPORT EXPORT VERIFIER  (post_import_export_manual v3)")
print("=========================================================")

errors   = []
warnings = []

def pass_msg(msg):  print(f"  [PASS] {msg}")
def fail_msg(msg):  errors.append(msg);   print(f"  [FAIL] {msg}")
def warn_msg(msg):  warnings.append(msg); print(f"  [WARN] {msg}")
def skip_abort(msg):
    """exit(2) = SKIP: chưa chạy TIA update (dir / manifest missing)."""
    print(f"\n[SKIP] {msg}")
    sys.exit(2)

def fail_abort(msg):
    """exit(1) = FAIL: readback tồn tại nhưng nội dung sai / lỗi compile."""
    print(f"\n[FAIL] {msg}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# GUARD 0a – Directory exists
# ══════════════════════════════════════════════════════════════════════════════
if not os.path.isdir(EXPORT_DIR):
    skip_abort(
        f"Thư mục readback chưa tồn tại: {EXPORT_DIR}\n"
        "Hãy chạy update_tia_project.exe trước."
    )

if os.path.isdir(OLD_EXPORT):
    print(f"[INFO] Thư mục cũ post_import_export vẫn tồn tại nhưng bị bỏ qua.")

# ══════════════════════════════════════════════════════════════════════════════
# GUARD 0b – Manifest exists
# ══════════════════════════════════════════════════════════════════════════════
if not os.path.exists(MANIFEST_PATH):
    skip_abort(
        f"readback_manifest.json không tồn tại trong {EXPORT_DIR}\n"
        "Có thể update_tia_project.exe chưa chạy hoặc bị lỗi trước bước export."
    )

# ══════════════════════════════════════════════════════════════════════════════
# GUARD 0c – Parse manifest and check ErrorCount
# ══════════════════════════════════════════════════════════════════════════════
try:
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
except Exception as e:
    fail_abort(f"Không thể parse readback_manifest.json: {e}")

plc1_errors = manifest.get('plc1_errors', -1)
plc2_errors = manifest.get('plc2_errors', -1)
ts_str      = manifest.get('timestamp', '')
proj_path   = manifest.get('project_path', '')

print(f"\n  Manifest:")
print(f"    timestamp     : {ts_str}")
print(f"    project_path  : {proj_path}")
print(f"    plc1_errors   : {plc1_errors}")
print(f"    plc2_errors   : {plc2_errors}")
print(f"    plc1_warnings : {manifest.get('plc1_warnings', '?')}")
print(f"    plc2_warnings : {manifest.get('plc2_warnings', '?')}")
print(f"    exported_files: {len(manifest.get('exported_files', []))} entries")

if plc1_errors < 0 or plc2_errors < 0:
    fail_abort(
        f"Manifest thiếu trường plc1_errors/plc2_errors (got {plc1_errors}/{plc2_errors}).\n"
        "Manifest bị hỏng hoặc do phiên bản cũ tạo ra."
    )

if plc1_errors != 0 or plc2_errors != 0:
    fail_abort(
        f"Manifest báo lỗi biên dịch: PLC1={plc1_errors} error(s), PLC2={plc2_errors} error(s).\n"
        "Readback không hợp lệ – phải sửa lỗi compile và chạy lại update_tia_project.exe."
    )

# ──────────────────────────────────────────────────────────────────────────────
# GUARD 0c2 – Verify project_path in manifest matches known OriginalPath
# ──────────────────────────────────────────────────────────────────────────────
EXPECTED_PROJ_SUFFIX = 'cuocthi_tdh.ap18'
if not proj_path:
    fail_abort("Manifest thiếu trường project_path!")
elif not proj_path.lower().endswith(EXPECTED_PROJ_SUFFIX.lower()):
    fail_abort(
        f"Manifest project_path không khớp!\n"
        f"  Mong đợi kết thúc bằng: {EXPECTED_PROJ_SUFFIX}\n"
        f"  Thực tế             : {proj_path}"
    )
else:
    pass_msg(f"project_path hợp lệ: {proj_path}")

# ══════════════════════════════════════════════════════════════════════════════
# GUARD 0d – Freshness check
# ══════════════════════════════════════════════════════════════════════════════
if not ts_str:
    fail_abort("Manifest thiếu trường timestamp!")
else:
    try:
        # Parse ISO 8601 UTC timestamp (format: 2026-06-22T06:00:00Z)
        ts_dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - ts_dt).total_seconds() / 3600
        if age_h > FRESHNESS_WARN_HOURS:
            warn_msg(f"Readback đã {age_h:.1f} giờ tuổi (> {FRESHNESS_WARN_HOURS}h). Cân nhắc chạy lại update_tia_project.exe.")
        else:
            pass_msg(f"Readback còn mới: {age_h:.1f} giờ tuổi.")
    except Exception as e:
        fail_abort(f"Timestamp trong manifest không hợp lệ: '{ts_str}' – {e}")

# ══════════════════════════════════════════════════════════════════════════════
# GUARD 0e – Block dirs exist and not empty
# ══════════════════════════════════════════════════════════════════════════════
if not os.path.isdir(P1_BLOCKS):
    fail_abort(f"Thư mục PLC_1/Blocks không tồn tại: {P1_BLOCKS}")
if not os.path.isdir(P2_BLOCKS):
    fail_abort(f"Thư mục PLC_2/Blocks không tồn tại: {P2_BLOCKS}")

p1_xmls = [f for f in os.listdir(P1_BLOCKS) if f.endswith('.xml')]
p2_xmls = [f for f in os.listdir(P2_BLOCKS) if f.endswith('.xml')]
if not p1_xmls:
    fail_abort(f"PLC_1/Blocks rỗng (không có .xml) – export thất bại hoặc bị xóa: {P1_BLOCKS}")
if not p2_xmls:
    fail_abort(f"PLC_2/Blocks rỗng (không có .xml) – export thất bại hoặc bị xóa: {P2_BLOCKS}")

print(f"\n  PLC_1/Blocks: {len(p1_xmls)} xml files")
print(f"  PLC_2/Blocks: {len(p2_xmls)} xml files")


# ══════════════════════════════════════════════════════════════════════════════
# XML Helpers
# ══════════════════════════════════════════════════════════════════════════════
def load_xml_stripped(path):
    """Parse XML and strip namespace prefixes."""
    it = ET.iterparse(path)
    for _, el in it:
        _, has_ns, postfix = el.tag.partition('}')
        if has_ns:
            el.tag = postfix
    return it.root


def get_title_text(net):
    for mt in net.findall(".//MultilingualText"):
        if mt.attrib.get("CompositionName") == "Title":
            text_el = mt.find(".//Text")
            if text_el is not None:
                return text_el.text or ""
    return ""


def parse_block_number(xml_path):
    """
    Parse the numeric block number from a TIA Portal exported block XML.
    Looks for <Number> inside SW.Blocks.FC/FB/OB/GlobalDB AttributeList.
    Returns int or None if not found.
    """
    try:
        root = load_xml_stripped(xml_path)
        block_types = ('SW.Blocks.FC', 'SW.Blocks.FB', 'SW.Blocks.OB',
                       'SW.Blocks.GlobalDB', 'SW.Blocks.InstanceDB')
        for bt in block_types:
            for el in root.findall('.//' + bt):
                al = el.find('AttributeList')
                if al is not None:
                    num_el = al.find('Number')
                    if num_el is not None and num_el.text and num_el.text.strip().isdigit():
                        return int(num_el.text.strip())
    except Exception:
        pass
    # Regex fallback: only match <Number>NNN</Number> (not AutoNumber etc.)
    try:
        with open(xml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(r'<Number>(\d+)</Number>', content)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def cu_vars(cu):
    return {c.attrib.get('Name', '') for c in cu.findall('.//Component')}


def cu_str(cu):
    return ET.tostring(cu, encoding='utf-8').decode('utf-8')


def check_file(path, label):
    if not os.path.exists(path):
        fail_msg(f"{label}: File không tồn tại – {path}")
        return False
    return True


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 1 – OB30: PID mapping, no hardcoded MOVE 100.0, strict dual-mode hybrid check
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 1] OB30_PID_PLC1_Bon2 – PID mapping / không có MOVE 100.0 cứng")
ob30_path = os.path.join(P1_BLOCKS, 'OB30_PID_PLC1_Bon2.xml')
if check_file(ob30_path, 'OB30_PID_PLC1_Bon2'):
    with open(ob30_path, encoding='utf-8') as f: raw = f.read()
    ob30 = load_xml_stripped(ob30_path)
    cus  = ob30.findall('.//SW.Blocks.CompileUnit')
    print(f"  Networks: {len(cus)}")

    if 'Move PID Bon 2 CV to VFD' in raw:
        fail_msg("Network 'Move PID Bon 2 CV to VFD' vẫn còn (stale)!")
    else:
        pass_msg("Network 'Move PID Bon 2 CV to VFD' đã được xóa.")

    # Kiểm tra các tag bắt buộc trong OB30
    required_ob30_tags = [
        'HMI_Che_Do_Thi',
        'PID_Bon2_PV_Eff',
        'PID_Bon2_Enable_Eff',
        'HMI_PID_Bon2_Dau_Noi_Enable',
        'VFD_Bon2_Toc_Do_Cmd'
    ]
    for tag in required_ob30_tags:
        if tag in raw:
            pass_msg(f"OB30 chứa cờ/tag bắt buộc: {tag}")
        else:
            fail_msg(f"OB30 THIẾU cờ/tag bắt buộc: {tag}!")

    # Cấm ghi trực tiếp VFD_Bon2_Toc_Do_AO
    if 'VFD_Bon2_Toc_Do_AO' in raw:
        fail_msg("OB30 vẫn chứa tag ghi trực tiếp VFD_Bon2_Toc_Do_AO (phải ghi qua VFD_Bon2_Toc_Do_Cmd)!")
    else:
        pass_msg("OB30 không ghi trực tiếp vào VFD_Bon2_Toc_Do_AO.")

    # Kiểm tra chi tiết dual-mode mapping
    has_m0_sp = has_m1_sp = has_m0_pv = has_m1_pv = False
    has_m0_en = has_m1_en = has_m0_spd = has_m1_spd = False
    hw100 = False

    for idx, cu in enumerate(cus):
        v = cu_vars(cu)
        s = cu_str(cu)
        consts = [c.text for c in cu.findall('.//ConstantValue')]
        
        if '100.0' in consts and 'CV3206_Hoi_Bon2' in v and 'Move' in s:
            hw100 = True
            fail_msg(f"Hardcoded MOVE 100.0→CV3206_Hoi_Bon2 tại network {idx}!")

        if 'HMI_Che_Do_Thi' in v:
            # Mode 0 SP: HMI_Che_Do_Thi, HMI_SP_PLC1_Nhiet_Do_Bon2, PID_Bon2_SP
            if 'HMI_SP_PLC1_Nhiet_Do_Bon2' in v and 'PID_Bon2_SP' in v and 'Move' in s:
                has_m0_sp = True
            # Mode 1 SP: HMI_Che_Do_Thi, HMI_SP_PLC1_Toc_Do_Bon2_Main, PID_Bon2_SP
            if 'HMI_SP_PLC1_Toc_Do_Bon2_Main' in v and 'PID_Bon2_SP' in v and 'Move' in s:
                has_m1_sp = True
            # Mode 0 PV: HMI_Che_Do_Thi, TT3208_Bon2_Eff, PID_Bon2_PV_Eff
            if 'TT3208_Bon2_Eff' in v and 'PID_Bon2_PV_Eff' in v and 'Move' in s:
                has_m0_pv = True
            # Mode 1 PV: HMI_Che_Do_Thi, VFD_Bon2_Actual_Speed_Feedback, PID_Bon2_PV_Eff
            if 'VFD_Bon2_Actual_Speed_Feedback' in v and 'PID_Bon2_PV_Eff' in v and 'Move' in s:
                has_m1_pv = True
            # Mode 0 Enable: HMI_Che_Do_Thi, PID_Bon2_Enable, PID_Bon2_Enable_Eff
            if 'PID_Bon2_Enable' in v and 'PID_Bon2_Enable_Eff' in v:
                has_m0_en = True
            # Mode 1 Enable: HMI_Che_Do_Thi, HMI_PID_Bon2_Dau_Noi_Enable, PID_Bon2_Enable_Eff
            if 'HMI_PID_Bon2_Dau_Noi_Enable' in v and 'PID_Bon2_Enable_Eff' in v:
                has_m1_en = True
            # Mode 0 Speed: HMI_Che_Do_Thi, HMI_SP_PLC1_Toc_Do_Bon2_Main, VFD_Bon2_Toc_Do_Cmd
            if 'HMI_SP_PLC1_Toc_Do_Bon2_Main' in v and 'VFD_Bon2_Toc_Do_Cmd' in v and 'Move' in s:
                has_m0_spd = True
            # Mode 1 Speed: HMI_Che_Do_Thi, PID_Bon2_CV, VFD_Bon2_Toc_Do_Cmd
            if 'PID_Bon2_CV' in v and 'VFD_Bon2_Toc_Do_Cmd' in v and 'Move' in s:
                has_m1_spd = True

    if has_m0_sp: pass_msg("OB30 chứa logic Mode 0 SP (Nhiệt độ → Setpoint)")
    else: fail_msg("OB30 THIẾU logic Mode 0 SP!")
    if has_m1_sp: pass_msg("OB30 chứa logic Mode 1 SP (Tốc độ → Setpoint)")
    else: fail_msg("OB30 THIẾU logic Mode 1 SP!")
    if has_m0_pv: pass_msg("OB30 chứa logic Mode 0 PV (Nhiệt độ thực → PV)")
    else: fail_msg("OB30 THIẾU logic Mode 0 PV!")
    if has_m1_pv: pass_msg("OB30 chứa logic Mode 1 PV (VFD Speed Feedback → PV)")
    else: fail_msg("OB30 THIẾU logic Mode 1 PV!")
    if has_m0_en: pass_msg("OB30 chứa logic Mode 0 Enable (PID_Bon2_Enable → Eff)")
    else: fail_msg("OB30 THIẾU logic Mode 0 Enable!")
    if has_m1_en: pass_msg("OB30 chứa logic Mode 1 Enable (Đấu nối Enable → Eff)")
    else: fail_msg("OB30 THIẾU logic Mode 1 Enable!")
    if has_m0_spd: pass_msg("OB30 chứa logic Mode 0 Speed (Tốc độ HMI → Cmd)")
    else: fail_msg("OB30 THIẾU logic Mode 0 Speed!")
    if has_m1_spd: pass_msg("OB30 chứa logic Mode 1 Speed (PID CV → Cmd)")
    else: fail_msg("OB30 THIẾU logic Mode 1 Speed!")
    if not hw100: pass_msg("Không có MOVE 100.0 cứng vào CV3206_Hoi_Bon2.")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 2 – FC_PLC1_Mixing: van xả Bồn 2 theo Pump3264
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 2] FC_PLC1_Mixing – van xả Bồn 2 theo Pump3264_Chuyen_Nhanh1")
fc1_path = os.path.join(P1_BLOCKS, 'FC_PLC1_Mixing.xml')
if check_file(fc1_path, 'FC_PLC1_Mixing'):
    root1 = load_xml_stripped(fc1_path)
    valves = ['V3237_Xa_Bon2', 'V3238_Xa_Bon2', 'V3239_Xa_Bon2']
    found  = {v: False for v in valves}
    for cu in root1.findall('.//SW.Blocks.CompileUnit'):
        v = cu_vars(cu); s = cu_str(cu)
        for valve in valves:
            if 'Pump3264_Chuyen_Nhanh1' in v and valve in v and ('Coil' in s or 'SetCoil' in s):
                found[valve] = True
    for valve, ok in found.items():
        if ok: pass_msg(f"{valve} mở theo Pump3264_Chuyen_Nhanh1.")
        else:  fail_msg(f"FC_PLC1_Mixing: {valve} KHÔNG kết nối Pump3264_Chuyen_Nhanh1!")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 3 – FC_PLC2_Mixing: van xả Bồn 4 theo Pump3265
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 3] FC_PLC2_Mixing – van xả Bồn 4 theo Pump3265_Chuyen_Nhanh2")
fc2_path = os.path.join(P2_BLOCKS, 'FC_PLC2_Mixing.xml')
if check_file(fc2_path, 'FC_PLC2_Mixing'):
    root2 = load_xml_stripped(fc2_path)
    valves = ['V3247_Xa_Bon4', 'V3248_Xa_Bon4', 'V3249_Xa_Bon4']
    found  = {v: False for v in valves}
    for cu in root2.findall('.//SW.Blocks.CompileUnit'):
        v = cu_vars(cu); s = cu_str(cu)
        for valve in valves:
            if 'Pump3265_Chuyen_Nhanh2' in v and valve in v and ('Coil' in s or 'SetCoil' in s):
                found[valve] = True
    for valve, ok in found.items():
        if ok: pass_msg(f"{valve} mở theo Pump3265_Chuyen_Nhanh2.")
        else:  fail_msg(f"FC_PLC2_Mixing: {valve} KHÔNG kết nối Pump3265_Chuyen_Nhanh2!")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 4 – VFD/AGTR chạy khi PID Enable
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 4] VFD/AGTR chạy khi PID Enable")
if os.path.exists(fc1_path):
    root1_b = load_xml_stripped(fc1_path)
    vfd_ok = False
    uses_pid_enable = False
    for cu in root1_b.findall('.//SW.Blocks.CompileUnit'):
        vars_in_cu = cu_vars(cu)
        if 'VFD_Bon2_Should_Run' in vars_in_cu:
            if 'PID_Bon2_Enable_Eff' in vars_in_cu:
                vfd_ok = True
            if 'PID_Bon2_Enable' in vars_in_cu:
                uses_pid_enable = True
    if vfd_ok and not uses_pid_enable:
        pass_msg("Agitator Bồn 2 VFD Should Run sử dụng PID_Bon2_Enable_Eff và KHÔNG sử dụng PID_Bon2_Enable.")
    else:
        fail_msg("Agitator Bồn 2 VFD Should Run dùng sai cờ kích hoạt PID! Phải dùng PID_Bon2_Enable_Eff và không dùng PID_Bon2_Enable.")

if os.path.exists(fc2_path):
    root2_b = load_xml_stripped(fc2_path)
    agtr_ok = any(
        'PID_Bon4_Enable' in cu_vars(cu) and (
            'AGTR3263_Khuay_Active' in cu_vars(cu) or 'AGTR3263_Khuay_Bon4' in cu_vars(cu)
        )
        for cu in root2_b.findall('.//SW.Blocks.CompileUnit')
    )
    if agtr_ok: pass_msg("AGTR3263 Bồn 4 chạy khi PID_Bon4_Enable = TRUE.")
    else:       fail_msg("AGTR3263 Bồn 4 KHÔNG chạy khi PID_Bon4_Enable = TRUE!")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 5 – Dosing timers T#5S
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 5] Dosing timers preset T#5S")
dosing = {t: False for t in ('Timer_Dosing_Bon1','Timer_Dosing_Bon2','Timer_Dosing_Bon3','Timer_Dosing_Bon4')}

def scan_dosing(xml_path):
    if not os.path.exists(xml_path): return
    root = load_xml_stripped(xml_path)
    for cu in root.findall('.//SW.Blocks.CompileUnit'):
        s = cu_str(cu)
        for t in dosing:
            if t in s and 'T#5S' in s:
                dosing[t] = True

scan_dosing(fc1_path)
scan_dosing(fc2_path)
for t, ok in dosing.items():
    if ok: pass_msg(f"{t} đặt T#5S.")
    else:  fail_msg(f"Dosing timer {t} KHÔNG tìm thấy preset T#5S!")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 6 – FC_Manual_Control BlockNumber == 62  (parsed from XML)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 6] FC_Manual_Control – BlockNumber == 62 (parsed XML)")
for path, label in [
    (os.path.join(P1_BLOCKS, 'FC_Manual_Control_PLC1.xml'), 'FC_Manual_Control_PLC1'),
    (os.path.join(P2_BLOCKS, 'FC_Manual_Control_PLC2.xml'), 'FC_Manual_Control_PLC2'),
]:
    if not os.path.exists(path):
        fail_msg(f"{label}: File không được export!")
    else:
        num = parse_block_number(path)
        if num is None:
            fail_msg(f"{label}: Không parse được BlockNumber từ XML!")
        elif num == 62:
            pass_msg(f"{label} có BlockNumber = 62.")
        else:
            fail_msg(f"{label} có BlockNumber = {num} (mong đợi 62)!")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 7 – FC_HMI_Animation BlockNumber == 60 / 61  (parsed from XML)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 7] FC_HMI_Animation – BlockNumber (parsed XML)")
for path, label, expected in [
    (os.path.join(P1_BLOCKS, 'FC_HMI_Animation_PLC1.xml'), 'FC_HMI_Animation_PLC1', 60),
    (os.path.join(P2_BLOCKS, 'FC_HMI_Animation_PLC2.xml'), 'FC_HMI_Animation_PLC2', 61),
]:
    if not os.path.exists(path):
        fail_msg(f"{label}: File không được export!")
    else:
        num = parse_block_number(path)
        if num is None:
            fail_msg(f"{label}: Không parse được BlockNumber!")
        elif num == expected:
            pass_msg(f"{label} có BlockNumber = {expected}.")
        else:
            fail_msg(f"{label} có BlockNumber = {num} (mong đợi {expected})!")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 8 – Timers blocks tồn tại và KHÔNG có Timer_DryRun
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 8] Timers blocks – không có Timer_DryRun")
for path, label in [
    (os.path.join(P1_BLOCKS, 'Timers_PLC1.xml'), 'Timers_PLC1'),
    (os.path.join(P2_BLOCKS, 'Timers_PLC2.xml'), 'Timers_PLC2'),
]:
    if not os.path.exists(path):
        fail_msg(f"{label}: File không được export!")
    else:
        with open(path, encoding='utf-8') as f: content = f.read()
        if 'Timer_DryRun' in content:
            fail_msg(f"{label} vẫn chứa Timer_DryRun (phải đã được xóa)!")
        else:
            pass_msg(f"{label} tồn tại và không chứa Timer_DryRun.")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 9 – Inventory: đủ file bắt buộc
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 9] Inventory – tối thiểu file bắt buộc")
for fname in PLC1_REQUIRED:
    p = os.path.join(P1_BLOCKS, fname)
    if os.path.exists(p): pass_msg(f"PLC_1/{fname}")
    else:                  fail_msg(f"PLC_1/{fname} THIẾU trong readback!")

for fname in PLC2_REQUIRED:
    p = os.path.join(P2_BLOCKS, fname)
    if os.path.exists(p): pass_msg(f"PLC_2/{fname}")
    else:                  fail_msg(f"PLC_2/{fname} THIẾU trong readback!")

manifest_files = set(manifest.get('exported_files', []))
print(f"\n  Manifest khai báo {len(manifest_files)} file export.")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 10 – Level State Animation tags and logic (FC60 / FC61)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 10] Level State Animation logic (readback XML)")
p1_tags_path = os.path.join(EXPORT_DIR, 'PLC_1', 'PLC_Tags.xml')
p2_tags_path = os.path.join(EXPORT_DIR, 'PLC_2', 'PLC_Tags.xml')

def get_xml_tags(path):
    tag_map = {}
    if not os.path.exists(path): return tag_map
    try:
        root = load_xml_stripped(path)
        for tag_el in root.iter():
            if tag_el.tag.endswith("PlcTag"):
                name_el = tag_el.find(".//Name")
                addr_el = tag_el.find(".//LogicalAddress")
                type_el = tag_el.find(".//DataTypeName")
                if name_el is not None and addr_el is not None and type_el is not None:
                    tag_map[name_el.text] = (addr_el.text, type_el.text)
    except Exception as e:
        fail_msg(f"Error parsing tags XML {path}: {e}")
    return tag_map

p1_readback_tags = get_xml_tags(p1_tags_path)
p2_readback_tags = get_xml_tags(p2_tags_path)

# Verify PLC1 Tags
for tname in ('HMI_Anim_Bon1_MucDich', 'HMI_Anim_Bon2_MucDich', 'HMI_Anim_BonChua1_MucDich', 'HMI_Anim_BonChua2_MucDich'):
    if tname in p1_readback_tags:
        addr, dtype = p1_readback_tags[tname]
        if addr.startswith('%MW') and dtype == 'Int':
            pass_msg(f"Tag readback PLC1: {tname} declared at {addr} as Int.")
        else:
            fail_msg(f"Tag readback PLC1: {tname} has wrong addr {addr} or type {dtype}!")
    else:
        fail_msg(f"Tag readback PLC1: {tname} THIẾU trong readback!")

# Verify PLC2 Tags
for tname in ('HMI_Anim_Bon3_MucDich', 'HMI_Anim_Bon4_MucDich'):
    if tname in p2_readback_tags:
        addr, dtype = p2_readback_tags[tname]
        if addr.startswith('%MW') and dtype == 'Int':
            pass_msg(f"Tag readback PLC2: {tname} declared at {addr} as Int.")
        else:
            fail_msg(f"Tag readback PLC2: {tname} has wrong addr {addr} or type {dtype}!")
    else:
        fail_msg(f"Tag readback PLC2: {tname} THIẾU trong readback!")

# Verify FC60 XML
fc60_readback_path = os.path.join(P1_BLOCKS, 'FC_HMI_Animation_PLC1.xml')
if os.path.exists(fc60_readback_path):
    root_fc60 = load_xml_stripped(fc60_readback_path)
    titles_fc60 = [get_title_text(n) for n in root_fc60.findall('.//SW.Blocks.CompileUnit')]
    tanks_p1 = [
        "Bồn 1 Mức dịch", "Bồn 2 Mức dịch", "Bồn chứa 1 Mức dịch", "Bồn chứa 2 Mức dịch"
    ]
    for t in tanks_p1:
        nets = [x for x in titles_fc60 if t in x or t.replace("Bồn", "Bon") in x]
        if len(nets) == 3:
            pass_msg(f"FC60 readback: 3 level state animation networks for '{t}' found.")
        else:
            fail_msg(f"FC60 readback: Expected 3 networks for '{t}', found {len(nets)}!")

# Verify FC61 XML
fc61_readback_path = os.path.join(P2_BLOCKS, 'FC_HMI_Animation_PLC2.xml')
if os.path.exists(fc61_readback_path):
    root_fc61 = load_xml_stripped(fc61_readback_path)
    titles_fc61 = [get_title_text(n) for n in root_fc61.findall('.//SW.Blocks.CompileUnit')]
    tanks_p2 = [
        "Bồn 3 Mức dịch", "Bồn 4 Mức dịch"
    ]
    for t in tanks_p2:
        nets = [x for x in titles_fc61 if t in x or t.replace("Bồn", "Bon") in x]
        if len(nets) == 3:
            pass_msg(f"FC61 readback: 3 level state animation networks for '{t}' found.")
        else:
            fail_msg(f"FC61 readback: Expected 3 networks for '{t}', found {len(nets)}!")

# ══════════════════════════════════════════════════════════════════════════════
# CHECK 11 – Tag tables legacy và compile warnings check
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 11] Tag tables legacy và compile warnings check")

# Check AI_Tags in PLC2
plc2_tag_tables = manifest.get("plc2_tag_tables", [])
if "AI_Tags" in plc2_tag_tables:
    fail_msg("PLC2 vẫn còn bảng tag legacy 'AI_Tags'!")
else:
    pass_msg("PLC2 không còn bảng tag legacy 'AI_Tags'.")

# Check ambiguous address warnings in manifest
plc1_ambig = manifest.get("plc1_ambiguous_address_warnings", 0)
plc2_ambig = manifest.get("plc2_ambiguous_address_warnings", 0)
if plc1_ambig > 0 or plc2_ambig > 0:
    fail_msg(f"Phát hiện cảnh báo ambiguous address trong manifest: PLC1={plc1_ambig}, PLC2={plc2_ambig}")
else:
    pass_msg("Không phát hiện cảnh báo ambiguous address trong manifest.")

# Check compile_warnings_report.txt directly
report_path = r"d:\AI_Agent_PLC_LADDER_ONLY\scratch\compile_warnings_report.txt"
if os.path.exists(report_path):
    try:
        with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
            report_text = f.read()
        if "ambiguous address" in report_text.lower():
            fail_msg("Phát hiện cảnh báo 'ambiguous address' trong file compile_warnings_report.txt!")
        else:
            pass_msg("Không phát hiện cảnh báo 'ambiguous address' trong compile_warnings_report.txt.")
    except Exception as e:
        warn_msg(f"Không thể đọc file compile_warnings_report.txt: {e}")
else:
    warn_msg("Không tìm thấy file compile_warnings_report.txt để kiểm tra.")

# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 12 – Modbus TCP Client & Server parameters (CONNECT & Data Buffers)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[CHECK 12] Modbus TCP Client/Server configuration (TCON_IP_v4 & Word Buffers)")

p1_main_path = os.path.join(P1_BLOCKS, 'Main.xml')
if os.path.exists(p1_main_path):
    with open(p1_main_path, 'r', encoding='utf-8') as f:
        p1_main = f.read()
    if 'DB_MB_TCP_Client_Conn_DB' in p1_main and 'DB_PLC1_MB_Word_Buffer_DB' in p1_main:
        pass_msg("PLC1 MB_CLIENT: CONNECT trỏ vào DB_MB_TCP_Client_Conn_DB.MB_TCP, MB_DATA_PTR trỏ vào DB_PLC1_MB_Word_Buffer_DB.Data")
    else:
        fail_msg("PLC1 MB_CLIENT: Sai cấu hình CONNECT hoặc MB_DATA_PTR!")
else:
    fail_msg("PLC1 Main.xml không tồn tại!")

p2_main_path = os.path.join(P2_BLOCKS, 'Main.xml')
if os.path.exists(p2_main_path):
    with open(p2_main_path, 'r', encoding='utf-8') as f:
        p2_main = f.read()
    if 'DB_MB_TCP_Server_Conn_DB' in p2_main and 'DB_PLC2_MB_Holding_Word_DB' in p2_main:
        pass_msg("PLC2 MB_SERVER: CONNECT trỏ vào DB_MB_TCP_Server_Conn_DB.MB_TCP_SERVER, MB_HOLD_REG trỏ vào DB_PLC2_MB_Holding_Word_DB.Data")
    else:
        fail_msg("PLC2 MB_SERVER: Sai cấu hình CONNECT hoặc MB_HOLD_REG!")
else:
    fail_msg("PLC2 Main.xml không tồn tại!")

# Final report
# ══════════════════════════════════════════════════════════════════════════════
print("\n=========================================================")
if warnings:
    print("WARNINGS:")
    for w in warnings: print(f"  ⚠  {w}")
if errors:
    print(f"\nVERIFICATION FAILED – {len(errors)} lỗi:")
    for e in errors: print(f"  ✗  {e}")
    print("")
    print("exit(1) = FAIL  (readback tồn tại nhưng nội dung sai)")
    print("=========================================================")
    sys.exit(1)
else:
    print("VERIFICATION SUCCESS! Tất cả tiêu chí đều đạt.")
    print("exit(0) = PASS")
    print("=========================================================")
    sys.exit(0)
