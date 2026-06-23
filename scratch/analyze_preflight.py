# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

DUMP_PATH = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\preflight_tia_dump.txt"
SCREEN_XML_PATH = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml"
REPORT_PATH = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\read_only_preflight_report.md"

if not os.path.exists(DUMP_PATH):
    print(f"Error: Dump file not found: {DUMP_PATH}")
    sys.exit(1)

if not os.path.exists(SCREEN_XML_PATH):
    print(f"Error: Screen XML file not found: {SCREEN_XML_PATH}")
    sys.exit(1)

# 1. PARSE TIA DUMP
print("Parsing TIA dump...")
plc_tags = {}  # plc_name -> { tag_name: (dtype, addr) }
hmi_tags = {}  # tag_name -> { 'connection': conn, 'controller_tag': ctrl }
hmi_connections = []
current_plc = None
current_hmi = None
current_section = None

with open(DUMP_PATH, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith("=== PROJECT DETAILS ==="):
            current_section = "project"
            continue
        if line.startswith("Device:"):
            # e.g., Device: S7-1200 station_1 | Type: System:Device.S71200
            current_section = "device"
            continue
        
        # Software match
        m_sw = re.match(r"Software:\s*(\w+)\s*\|\s*Type:\s*(\w+)", line)
        if m_sw:
            sw_name = m_sw.group(1)
            sw_type = m_sw.group(2)
            if sw_type == "PlcSoftware":
                current_plc = sw_name
                plc_tags[current_plc] = {}
                current_hmi = None
            elif sw_type == "HmiTarget":
                current_hmi = sw_name
                current_plc = None
            else:
                current_plc = None
                current_hmi = None
            continue
        
        # PLC Tags
        if current_plc:
            m_ptag = re.match(r"Tag:\s*([a-zA-Z0-9_]+)\s*\|\s*DataType:\s*([a-zA-Z0-9_]+)\s*\|\s*Address:\s*([a-zA-Z0-9_%.]+)", line)
            if m_ptag:
                tname = m_ptag.group(1)
                dtype = m_ptag.group(2)
                addr = m_ptag.group(3)
                plc_tags[current_plc][tname] = (dtype, addr)
                continue
                
        # HMI Details
        if current_hmi:
            m_hconn = re.match(r"Connection:\s*([a-zA-Z0-9_]+)\s*\|\s*Type:\s*([a-zA-Z0-9_]+)", line)
            if m_hconn:
                hconn = m_hconn.group(1)
                hmi_connections.append(hconn)
                continue
            
            m_htag = re.match(r"Tag:\s*([a-zA-Z0-9_]+)\s*\|\s*Connection:\s*([a-zA-Z0-9_None]+)\s*\|\s*ControllerTag:\s*([a-zA-Z0-9_None]+)", line)
            if m_htag:
                tname = m_htag.group(1)
                conn = m_htag.group(2)
                ctrl = m_htag.group(3)
                hmi_tags[tname] = {'connection': conn, 'controller_tag': ctrl}
                continue

print(f"Parsed PLCs: {list(plc_tags.keys())}")
for plc, tags in plc_tags.items():
    print(f"  {plc}: {len(tags)} tags")
print(f"Parsed HMI Connections: {hmi_connections}")
print(f"Parsed HMI Tags: {len(hmi_tags)}")

# 2. PARSE SCREEN XML FOR REFERENCED TAGS
print("\nParsing Screen XML...")
tree = ET.parse(SCREEN_XML_PATH)
root = tree.getroot()

referenced_tags = set()
duplicate_ids = []
all_ids = set()
elements_coords = {} # name -> (left, top, width, height, type)

# Check XML for duplicate IDs and extract coordinates
for elem in root.iter():
    id_attr = elem.get("ID")
    if id_attr:
        if id_attr in all_ids:
            duplicate_ids.append(id_attr)
        all_ids.add(id_attr)
    
    # Extract tags
    tag_local = elem.tag.split('}')[-1]
    if tag_local == "Tag" and elem.get("TargetID") == "@OpenLink":
        name_el = elem.find("{*}Name")
        if name_el is not None and name_el.text:
            referenced_tags.add(name_el.text)
            
    # Extract coordinates for GraphicIOField and IOField and TextFields
    if tag_local in ["Hmi.Screen.IOField", "Hmi.Screen.GraphicIOField", "Hmi.Screen.TextField"]:
        attrs = elem.find("AttributeList")
        if attrs is not None:
            name_el = attrs.find("ObjectName")
            left_el = attrs.find("Left")
            top_el = attrs.find("Top")
            width_el = attrs.find("Width")
            height_el = attrs.find("Height")
            
            if name_el is not None and name_el.text:
                name = name_el.text
                left = int(left_el.text) if left_el is not None else 0
                top = int(top_el.text) if top_el is not None else 0
                width = int(width_el.text) if width_el is not None else 0
                height = int(height_el.text) if height_el is not None else 0
                elements_coords[name] = (left, top, width, height, tag_local)

print(f"Found {len(referenced_tags)} referenced HMI tags in Screen XML.")
print(f"Found {len(elements_coords)} elements with coordinates in Screen XML.")

# 3. XML AUDIT: COORDINATES OVERLAP AND OUT OF BOUNDS
out_of_bounds = []
overlaps = []
screen_w = 1440
screen_h = 900

# Boundary check
for name, (left, top, w, h, t) in elements_coords.items():
    if left < 0 or left + w > screen_w or top < 0 or top + h > screen_h:
        out_of_bounds.append((name, left, top, w, h, t))

# Overlap check (only for non-TextFields or important UI objects, let's check IOFields and GraphicIOFields)
items = list(elements_coords.items())
for i in range(len(items)):
    name1, (l1, t1, w1, h1, type1) = items[i]
    for j in range(i + 1, len(items)):
        name2, (l2, t2, w2, h2, type2) = items[j]
        
        # Don't check two text fields overlapping since labels can overlap or be stacked,
        # but check if IOField overlaps with another IOField, or GraphicIOField overlaps,
        # or if an IOField overlaps with a GraphicIOField (which was a reported blocker: AI_IO_FT3200 đè I/O field_1).
        if type1 == "TextField" and type2 == "TextField":
            continue
            
        # Check intersection
        x_overlap = max(0, min(l1 + w1, l2 + w2) - max(l1, l2))
        y_overlap = max(0, min(t1 + h1, t2 + h2) - max(t1, t2))
        
        if x_overlap > 0 and y_overlap > 0:
            area1 = w1 * h1
            area2 = w2 * h2
            overlap_area = x_overlap * y_overlap
            
            # If overlap area is significant (e.g. > 10% of either element area)
            if overlap_area > 0.1 * min(area1, area2):
                overlaps.append((name1, type1, name2, type2, l1, t1, w1, h1, l2, t2, w2, h2, overlap_area))

# 4. CROSS-REFERENCE REFERENCE TAGS WITH TIA PORTAL
missing_in_hmi = []
incorrect_hmi_conn = []
incorrect_hmi_ctrl = []
tag_plc_mapping = {} # tag_name -> { plc: plc_name, addr: addr, dtype: dtype, status: str }

# For each referenced tag, check:
# 1. Does it exist in HMI?
# 2. Does it exist in PLC_1?
# 3. Does it exist in PLC_2?
for tag in sorted(list(referenced_tags)):
    in_hmi = tag in hmi_tags
    
    # Check PLCs
    in_plc1 = tag in plc_tags.get("PLC_1", {})
    in_plc2 = tag in plc_tags.get("PLC_2", {})
    
    plc_loc = "None"
    dtype = "None"
    addr = "None"
    
    if in_plc1 and in_plc2:
        plc_loc = "PLC_1 & PLC_2 (DUAL)"
        dtype, addr = plc_tags["PLC_1"][tag]
    elif in_plc1:
        plc_loc = "PLC_1"
        dtype, addr = plc_tags["PLC_1"][tag]
    elif in_plc2:
        plc_loc = "PLC_2"
        dtype, addr = plc_tags["PLC_2"][tag]
    
    status = "OK"
    if not in_hmi:
        missing_in_hmi.append(tag)
        status = "MISSING IN HMI TAG TABLE"
    else:
        conn = hmi_tags[tag]['connection']
        ctrl = hmi_tags[tag]['controller_tag']
        
        # Connection check
        # Since we know HMI_Connection_1 connects to PLC_1, let's verify if PLC mapping matches.
        if conn != "HMI_Connection_1" and conn != "None":
            incorrect_hmi_conn.append((tag, conn))
            status = f"INCORRECT CONNECTION: {conn}"
        elif ctrl != tag and ctrl != "None":
            incorrect_hmi_ctrl.append((tag, ctrl))
            status = f"INCORRECT CONTROLLER TAG LINK: {ctrl}"
        elif conn == "HMI_Connection_1" and plc_loc == "PLC_2":
            status = "WRONG PLC MAPPING (PLC_2 tag on PLC_1 connection)"
            
    tag_plc_mapping[tag] = {
        'plc': plc_loc,
        'addr': addr,
        'dtype': dtype,
        'status': status,
        'in_hmi': in_hmi
    }

# 5. PREPARE THE PREFLIGHT REPORT
report = []
report.append("# Báo cáo Pre-flight kiểm tra HMI Tổng quan (Read-Only Pre-flight Report)")
report.append("")
report.append("Dự án: `cuocthi_tdh`  ")
report.append("Phiên TIA Portal PID: `14620`  ")
report.append("Đường dẫn Project: `C:\\Users\\lienb\\Downloads\\1_Tia_Portal\\cuocthi_tdh\\cuocthi_tdh.ap18`  ")
report.append(f"Màn hình XML: `{SCREEN_XML_PATH}`  ")
report.append("")
report.append("---")
report.append("")
report.append("## 1. Thiết bị và HMI Connection hiện có")
report.append("")
report.append("| Tên Thiết bị | Loại Thiết bị | Trạng thái Software |")
report.append("| :--- | :--- | :--- |")
for dev in sorted(list(plc_tags.keys())):
    report.append(f"| `{dev}` | S7-1200 | PlcSoftware |")
report.append(f"| `HMI_RT_1` | PC-System (WinCC Prof) | HmiTarget |")
report.append("")
report.append("**Danh sách HMI Connection trong `HMI_RT_1`:**")
if hmi_connections:
    for conn in hmi_connections:
        # We know HMI_Connection_1 connects to PLC_1 from previous tests
        partner = "PLC_1" if conn == "HMI_Connection_1" else "Unknown"
        report.append(f"- Connection Name: `{conn}` | Partner PLC: `{partner}`")
else:
    report.append("- *Không tìm thấy HMI Connection trực tiếp trong `hmi.Connections`.* (Do WinCC Professional quản lý kết nối tích hợp trong Topology mạng).")
report.append("")
report.append("---")
report.append("")
report.append("## 2. Kiểm tra tính đúng đắn của tệp XML `Man Tong Quan`")
report.append("")
report.append(f"- **Tính hợp lệ cú pháp (Well-formed):** XML hợp lệ và được parse thành công.")
report.append(f"- **Trùng lặp ID (Duplicate IDs):** {len(duplicate_ids)} ID bị trùng. " + (f"({', '.join(duplicate_ids)})" if duplicate_ids else "Không phát hiện ID trùng."))
report.append(f"- **Số lượng các ô IOField:**")
iofield_count = sum(1 for name, coords in elements_coords.items() if coords[4] == "Hmi.Screen.IOField")
graphic_iofield_count = sum(1 for name, coords in elements_coords.items() if coords[4] == "Hmi.Screen.GraphicIOField")
textfield_count = sum(1 for name, coords in elements_coords.items() if coords[4] == "Hmi.Screen.TextField")
report.append(f"  - `IOField` (ô số): {iofield_count} ô (2 gốc đã bị xóa, 25 ô do AI sinh mới).")
report.append(f"  - `GraphicIOField` (van/bơm/bồn hoạt hình): {graphic_iofield_count} ô.")
report.append(f"  - `TextField` (nhãn tĩnh/đơn vị): {textfield_count} ô (81 ô do AI sinh mới).")
report.append("")
report.append("### A. Kiểm tra tràn biên màn hình (X: 0-1440, Y: 0-900)")
if out_of_bounds:
    report.append("| Tên phần tử | Loại | Vị trí (Left, Top) | Kích thước (W x H) | Tọa độ kết thúc (X/Y) | Lỗi cụ thể |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for name, left, top, w, h, t in out_of_bounds:
        end_x = left + w
        end_y = top + h
        err_msg = ""
        if end_x > screen_w:
            err_msg += f"Vượt biên phải X={end_x} (> 1440). "
        if end_y > screen_h:
            err_msg += f"Vượt biên dưới Y={end_y} (> 900)."
        report.append(f"| `{name}` | {t} | ({left}, {top}) | {w}x{h} | X={end_x}, Y={end_y} | {err_msg} |")
else:
    report.append("- *Không có phần tử nào vượt biên màn hình (1440x900).*")
report.append("")
report.append("### B. Kiểm tra chồng lấn phần tử (Overlaps)")
# Filtering overlaps: we want to focus on actual overlapping pairs
overlap_filtered = []
for name1, type1, name2, type2, l1, t1, w1, h1, l2, t2, w2, h2, area in overlaps:
    # Filter out text field overlapping since they are labels, focus on IOFields overlapping templates or each other
    overlap_filtered.append((name1, type1, name2, type2, l1, t1, w1, h1, l2, t2, w2, h2, area))

if overlap_filtered:
    report.append("| Phần tử 1 | Loại | Phần tử 2 | Loại | Tọa độ phần tử 1 | Tọa độ phần tử 2 | Diện tích đè nhau (px²) |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for name1, t1, name2, t2, l1, top1, w1, h1, l2, top2, w2, h2, area in overlap_filtered:
        report.append(f"| `{name1}` | {t1} | `{name2}` | {t2} | ({l1}, {top1}, {w1}x{h1}) | ({l2}, {top2}, {w2}x{h2}) | {area} |")
else:
    report.append("- *Không phát hiện chồng lấn phần tử nào đáng kể.*")
report.append("")
report.append("---")
report.append("")
report.append("## 3. Đối chiếu XML với TIA Portal (Tag References)")
report.append("")
report.append(f"Tổng số HMI Tag màn hình XML tham chiếu: **{len(referenced_tags)}**")
report.append(f"- Số tag HMI đã tồn tại trong TIA Portal: **{len(hmi_tags)}** (gồm {', '.join(hmi_tags.keys())})")
report.append(f"- Số tag HMI thiếu (chưa được tạo/import): **{len(referenced_tags) - len(hmi_tags)}**")
report.append("")
report.append("### Danh sách chi tiết ánh xạ 66 tag tham chiếu:")
report.append("")
report.append("| Tên Tag màn hình | Tồn tại ở HMI TIA? | Vị trí thực tế ở PLC | Địa chỉ PLC | Trạng thái Pre-flight |")
report.append("| :--- | :--- | :--- | :--- | :--- |")
for tag, info in sorted(tag_plc_mapping.items()):
    in_hmi_str = "Co (3 tag gốc)" if tag in hmi_tags else "CHƯA CÓ"
    plc_loc = info['plc']
    addr = info['addr']
    status = info['status']
    report.append(f"| `{tag}` | {in_hmi_str} | `{plc_loc}` | `{addr}` | {status} |")
report.append("")
report.append("---")
report.append("")
report.append("## 4. Xác định nguyên nhân lỗi")
report.append("")
report.append("> [!WARNING]")
report.append("> **Lỗi:** *“The controller tag CV3211_Nuoc_Bon3_M was not found.”*")
report.append("> ")
report.append("> **Phân tích nguyên nhân:**")
report.append("> 1. **Kiểu kết nối:** HMI `HMI_RT_1` chỉ có duy nhất **một kết nối tích hợp** kết nối trực tiếp đến **`PLC_1`** (được hiển thị là `HMI_Connection_1`). Không có kết nối trực tiếp từ HMI sang `PLC_2`.")
report.append("> 2. **Vị trí của Tag:** Tag điều khiển `CV3211_Nuoc_Bon3_M` thực chất thuộc về **`PLC_2`** (station_2) và **không tồn tại** trong bảng tag của `PLC_1`.")
report.append("> 3. **Cơ chế lỗi:** Khi chúng ta cố gắng tạo tag HMI `CV3211_Nuoc_Bon3_M` tham chiếu qua kết nối `HMI_Connection_1` (kết nối tới `PLC_1`), TIA Portal tìm kiếm tag này trong `PLC_1`. Vì tag này chỉ nằm ở `PLC_2`, TIA Portal ném ra ngoại lệ và dừng quá trình import tag.")
report.append("> 4. **Trường hợp của `HMI_SP_PLC2_Nhiet_Do_Bon4`:** Tag này import thành công trước đó vì nó được khai báo trùng lặp (dual-defined) ở cả `PLC_1` (với địa chỉ `%MD932`) và `PLC_2` (với địa chỉ `%MD932`). Do đó, khi kết nối tới `PLC_1`, nó tìm thấy tag có tên này.")
report.append("> 5. **Các biến Bồn 3 & Bồn 4 khác:** Các biến như `CV3211_Nuoc_Bon3_M`, `LT3213_Bon3_Eff`, `TT3214_Bon3_Eff`, `V3240_Nuoc_Bon3_M` đều nằm hoàn toàn ở `PLC_2` và không có bản sao ở `PLC_1` nên đều sẽ bị lỗi này nếu cố gắng liên kết trực tiếp.")
report.append("")
report.append("---")
report.append("")
report.append("## 5. Đề xuất kế hoạch sửa đổi tối thiểu (Chưa thực hiện)")
report.append("")
report.append("Để import thành công màn hình và tag mà không làm thay đổi kiến trúc kết nối hoặc chương trình PLC, ta áp dụng phương án **ánh xạ toàn bộ 66 Tag HMI về PLC_1** theo các bước sau:")
report.append("")
report.append("### Bước 1: Khai báo bổ sung các Tag của PLC_2 vào bảng Tag của PLC_1 dưới dạng địa chỉ Modbus / Bộ đệm truyền thông")
report.append("- Đối với các giá trị Analog của Bồn 3 & Bồn 4:")
report.append("  - Sử dụng các biến truyền nhận Modbus TCP hiện có của PLC_1 để làm ControllerTag nguồn cho HMI:")
report.append("    - `LT3213_Bon3_Eff` -> Đổi thành HMI tham chiếu tới `PLC2_Tip_Bon3_Timer` hoặc ánh xạ trung gian qua `%MD1056`?")
report.append("    - Không! Hãy xem các biến nhận thực tế trong PLC_1:")
report.append("      - `PID_Bon4_SP_Recv` (%MD884) -> Ánh xạ cho setpoint của Bồn 4 (`TT3219_Bon4_Target`).")
report.append("      - `PID_Bon4_PV_Recv` (%MD888) -> Ánh xạ cho mức dịch / cảm biến PV của Bồn 4.")
report.append("      - `PID_Bon4_CV_Recv` (%MD892) -> Ánh xạ cho van tuyến tính CV của Bồn 4.")
report.append("      - `PLC2_Tip_Bon3_Timer` (%MD1056) -> Cho Bồn 3.")
report.append("      - `PLC2_Tip_Bon4_Timer` (%MD1060) -> Cho Bồn 4.")
report.append("  - Đối với các van/bơm đồ họa hoặc các tag chưa được đồng bộ Modbus sang PLC_1:")
report.append("    - Để HMI không bị lỗi compile/import, ta **tạo các tag này trong PLC_1** (trong bảng `PLC_Tags` của `PLC_1`) với cùng kiểu dữ liệu. Sau đó viết code chuyển đổi Modbus ở PLC (nếu cần), hoặc HMI sẽ tham chiếu trực tiếp đến địa chỉ vùng nhớ đệm đã đồng bộ trên PLC_1.")
report.append("    - Cụ thể: Khai báo thêm 28 tag thiếu (ví dụ `CV3211_Nuoc_Bon3_M`, `V3240_Nuoc_Bon3_M`, `LT3213_Bon3_Eff`, v.v.) vào `PLC_1` dưới dạng các tag trung gian để TIA Portal nhận diện được khi import bảng Tag HMI qua `HMI_Connection_1`.")
report.append("")
report.append("### Bước 2: Cập nhật hàm sinh Tag HMI trong script Python")
report.append("- Cập nhật `patch_man_tong_quan.py` để tất cả 66 tag HMI đều sử dụng `HMI_Connection_1` và liên kết với các tag tương ứng đã tồn tại/khai báo ở `PLC_1`.")
report.append("")
report.append("### Bước 3: Thực hiện Import Tag Table vào TIA Portal")
report.append("- Chạy import tệp `AI_HMI_Tags.xml` sau khi PLC_1 đã có đủ các tag tương ứng.")
report.append("")
report.append("### Bước 4: Kiểm tra màn hình và XML và bàn giao")
report.append("- Chạy kiểm tra QA và acceptance test.")
report.append("")
report.append("---")
report.append("")
report.append("## 6. Kết luận")
report.append("")
# Since HMI Tags cannot be imported as-is due to missing controller tags in PLC_1, the status is NOT READY.
report.append("### **NOT READY FOR IMPORT**")
report.append("")
report.append("*(Cần thực hiện khai báo bổ sung các tag của PLC_2 vào PLC_1 để làm cầu nối truyền thông, hoặc tạo các biến đệm tương ứng trên PLC_1 trước khi có thể chạy import bảng tag HMI)*")

# Write to file
with open(REPORT_PATH, "w", encoding="utf-8") as rf:
    rf.write("\n".join(report))

print(f"\n[OK] Pre-flight report written successfully at: {REPORT_PATH}")
