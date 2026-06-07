# -*- coding: utf-8 -*-
"""
Agent_QA_Validator.py
Bộ thẩm định chất lượng tự động (QA Validator) cho hệ thống sinh Siemens TIA Portal V18 100% Ladder XML.
"""
import os
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# Đảm bảo hiển thị Tiếng Việt trên Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_accented(msg):
    print(msg)

def run_qa_validator(output_dir):
    print_accented(f"============================================================")
    print_accented(f" KHỞI CHẠY BỘ THẨM ĐỊNH CHẤT LƯỢNG TỰ ĐỘNG (QA VALIDATOR)  ")
    print_accented(f"============================================================")
    print_accented(f"Thư mục kiểm tra: {output_dir}\n")

    report_lines = []
    report_lines.append(f"# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG (QA REPORT)")
    report_lines.append(f"")
    report_lines.append(f"- **Thư mục kiểm tra:** `{output_dir}`")
    report_lines.append(f"- **Thời gian thực hiện:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    is_overall_pass = True
    
    # 1. Kiểm tra sự tồn tại của các file cấu hình bắt buộc
    required_files = {
        "IO_Map.json": "Bản đồ I/O định dạng JSON",
        "OB1_Main.xml": "Khối OB1 Main của chương trình PLC"
    }
    
    report_lines.append(f"## 1. Kiểm tra các file bắt buộc")
    print_accented("--- 1. KIỂM TRA SỰ TỒN TẠI CỦA CÁC FILE BẮT BUỘC ---")
    
    file_checks = {}
    for filename, desc in required_files.items():
        filepath = os.path.join(output_dir, filename)
        exists = os.path.exists(filepath)
        status = "ĐẠT (PASS)" if exists else "THẤT BẠI (FAIL)"
        file_checks[filename] = exists
        print_accented(f"  - {filename} ({desc}): {status}")
        report_lines.append(f"- **{filename}** ({desc}): {status}")
        if not exists:
            is_overall_pass = False

    # Kiểm tra AI_Tags.xml hoặc PLC_Tags.csv
    ai_tags_path = os.path.join(output_dir, "AI_Tags.xml")
    plc_tags_path = os.path.join(output_dir, "PLC_Tags.csv")
    tags_exist = os.path.exists(ai_tags_path) or os.path.exists(plc_tags_path)
    tags_status = "ĐẠT (PASS)" if tags_exist else "THẤT BẠI (FAIL)"
    print_accented(f"  - AI_Tags.xml hoặc PLC_Tags.csv (Bảng tag PLC): {tags_status}")
    report_lines.append(f"- **Bảng Tag PLC** (`AI_Tags.xml` hoặc `PLC_Tags.csv`): {tags_status}")
    if not tags_exist:
        is_overall_pass = False

    # 2. Kiểm tra không chứa file logic .scl
    report_lines.append(f"")
    report_lines.append(f"## 2. Kiểm tra quy tắc không dùng SCL (LADDER-ONLY POLICY)")
    print_accented("\n--- 2. KIỂM TRA QUY TẮC LADDER-ONLY ---")
    scl_files = []
    for r, d, fs in os.walk(output_dir):
        for f in fs:
            if f.lower().endswith(".scl"):
                scl_files.append(os.path.relpath(os.path.join(r, f), output_dir))
                
    if len(scl_files) > 0:
        print_accented(f"  - Lỗi: Phát hiện {len(scl_files)} file logic SCL:")
        report_lines.append(f"- **Trạng thái:** THẤT BẠI (FAIL)")
        report_lines.append(f"- **Chi tiết:** Phát hiện các file SCL vi phạm quy tắc 100% Ladder:")
        for sf in scl_files:
            print_accented(f"    - {sf}")
            report_lines.append(f"  - `{sf}`")
        is_overall_pass = False
    else:
        print_accented("  - Đạt yêu cầu: Không phát hiện file logic SCL nào.")
        report_lines.append(f"- **Trạng thái:** ĐẠT (PASS)")
        report_lines.append(f"- **Chi tiết:** Không phát hiện file logic SCL nào.")

    # Đọc các tag từ bảng tag để dùng cho kiểm tra khớp tag và mirror
    tag_names = set()
    tag_addresses = {} # name -> address
    tag_names_by_address = {} # address -> list of names
    
    if os.path.exists(ai_tags_path):
        try:
            tree = ET.parse(ai_tags_path)
            root = tree.getroot()
            # Tìm tất cả PlcTag dot-agnostic
            for tag_node in root.iter():
                tag_base = tag_node.tag.split('.')[-1]
                if tag_base == "PlcTag":
                    name_node = tag_node.find(".//Name")
                    addr_node = tag_node.find(".//LogicalAddress")
                    if name_node is not None and name_node.text:
                        name = name_node.text.strip()
                        tag_names.add(name)
                        if addr_node is not None and addr_node.text:
                            addr = addr_node.text.strip()
                            tag_addresses[name] = addr
                            if addr not in tag_names_by_address:
                                tag_names_by_address[addr] = []
                            tag_names_by_address[addr].append(name)
        except Exception as e:
            print_accented(f"  - Cảnh báo: Không thể phân tích cú pháp AI_Tags.xml: {str(e)}")
            
    elif os.path.exists(plc_tags_path):
        try:
            with open(plc_tags_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        name = parts[0].strip().replace('"', '')
                        addr = parts[2].strip().replace('"', '')
                        if name and name != "Name":
                            tag_names.add(name)
                            tag_addresses[name] = addr
                            if addr not in tag_names_by_address:
                                tag_names_by_address[addr] = []
                            tag_names_by_address[addr].append(name)
        except Exception as e:
            print_accented(f"  - Cảnh báo: Không thể phân tích cú pháp PLC_Tags.csv: {str(e)}")

    # 3. Kiểm tra các block XML (LAD Only, UId/ID Uniqueness, Symbolic Tag Matching)
    report_lines.append(f"")
    report_lines.append(f"## 3. Thẩm định các block XML của PLC")
    print_accented("\n--- 3. THẨM ĐỊNH CÁC KHỐI CHƯƠNG TRÌNH PLC (XML BLOCKS) ---")
    
    # Chỉ lấy các file XML làm khối chương trình PLC (bỏ qua HMI Text/Graphic lists và PLC Tag Table)
    xml_files = []
    for f in os.listdir(output_dir):
        if f.endswith(".xml") and not f.startswith("AI_Tags"):
            filepath = os.path.join(output_dir, f)
            try:
                with open(filepath, "r", encoding="utf-8") as file_obj:
                    content = file_obj.read()
                    if "<Hmi.TextGraphicList." in content:
                        continue # Bỏ qua các file cấu hình danh sách HMI
            except Exception:
                pass
            xml_files.append(f)
    
    if not xml_files:
        print_accented("  - Lỗi: Không tìm thấy bất kỳ file XML block nào.")
        report_lines.append("- **Trạng thái:** THẤT BẠI (FAIL) (Không tìm thấy block XML nào)")
        is_overall_pass = False
    else:
        for xml_file in xml_files:
            filepath = os.path.join(output_dir, xml_file)
            print_accented(f"  Thẩm định file: {xml_file} ...")
            report_lines.append(f"### Khối `{xml_file}`")
            
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                
                # Check 3.1: Programming Language must be LAD
                lang_nodes = root.findall(".//{*}ProgrammingLanguage")
                if not lang_nodes:
                    is_lad = False  # Thất bại nếu hoàn toàn thiếu thuộc tính ProgrammingLanguage
                else:
                    is_lad = True
                    for ln in lang_nodes:
                        val = ln.text.strip().upper() if ln.text else ""
                        if val not in ("LAD", "DB"):
                            is_lad = False
                            break
                
                lang_status = "ĐẠT (PASS - LAD/DB)" if is_lad else "THẤT BẠI (FAIL - Phát hiện SCL/FBD trong block)"
                print_accented(f"    - Ngôn ngữ lập trình: {lang_status}")
                report_lines.append(f"- **Ngôn ngữ lập trình:** {lang_status}")
                if not is_lad:
                    is_overall_pass = False
                
                # Check 3.2: UID and ID uniqueness
                uids = []
                ids = []
                for elem in root.iter():
                    # Chỉ đếm các phần tử KHAI BÁO UId (không phải các phần tử liên kết kết thúc bằng 'Con')
                    tag_base = elem.tag.split('.')[-1]
                    if not tag_base.endswith("Con"):
                        uid = elem.attrib.get("UId")
                        if uid is not None:
                            uids.append(uid)
                    
                    el_id = elem.attrib.get("ID")
                    if el_id is not None:
                        ids.append(el_id)
                
                dup_uids = set([u for u in uids if uids.count(u) > 1])
                dup_ids = set([i for i in ids if ids.count(i) > 1])
                
                uid_ok = len(dup_uids) == 0 and len(dup_ids) == 0
                uid_status = "ĐẠT (PASS - Không trùng lặp)" if uid_ok else "THẤT BẠI (FAIL - Phát hiện trùng lặp định danh!)"
                print_accented(f"    - Tính duy nhất của UId/ID: {uid_status}")
                report_lines.append(f"- **Tính duy nhất của UId/ID:** {uid_status}")
                if not uid_ok:
                    is_overall_pass = False
                    if dup_uids:
                        print_accented(f"      * Trùng UId: {list(dup_uids)}")
                        report_lines.append(f"  * Trùng UId: `{list(dup_uids)}`")
                    if dup_ids:
                        print_accented(f"      * Trùng ID: {list(dup_ids)}")
                        report_lines.append(f"  * Trùng ID: `{list(dup_ids)}`")
                
                # Check 3.3: Local variables and Symbolic Tag matching
                local_vars = set()
                for member in root.findall(".//{*}Member"):
                    m_name = member.attrib.get("Name")
                    if m_name:
                        local_vars.add(m_name)
                
                missing_in_tag_table = []
                for access in root.findall(".//{*}Access"):
                    scope = access.attrib.get("Scope")
                    if scope == "GlobalVariable":
                        symbol = access.find(".//{*}Symbol")
                        if symbol is not None:
                            components = symbol.findall(".//{*}Component")
                            # If it's a single component access, it must be in the tag table or be local interface variable
                            if len(components) == 1:
                                var_name = components[0].attrib.get("Name")
                                if var_name and var_name not in local_vars:
                                    # Skip system constants like T#5S or numbers and Instance DB names ending with _DB
                                    if var_name not in tag_names and not (var_name.startswith("T#") or var_name.startswith("W#16#") or var_name.endswith("_DB")):
                                        missing_in_tag_table.append(var_name)
                                        
                missing_set = set(missing_in_tag_table)
                match_ok = len(missing_set) == 0
                match_status = "ĐẠT (PASS)" if match_ok else "THẤT BẠI (FAIL - Phát hiện tag chưa khai báo)"
                print_accented(f"    - Kiểm tra khớp Tag Table: {match_status}")
                report_lines.append(f"- **Độ khớp Tag Table:** {match_status}")
                if not match_ok:
                    is_overall_pass = False
                    print_accented(f"      * Lỗi: Các tag sau dùng trong logic nhưng chưa được khai báo ở Tag Table:")
                    report_lines.append(f"  * **Các tag thiếu trong Tag Table:**")
                    for mt in missing_set:
                        print_accented(f"        - {mt}")
                        report_lines.append(f"    - `{mt}`")
                        
            except Exception as e:
                print_accented(f"    - Lỗi khi đọc file XML: {str(e)}")
                report_lines.append(f"- **Trạng thái:** THẤT BẠI (FAIL) (Lỗi đọc XML: {str(e)})")
                is_overall_pass = False

    # 4. Kiểm tra nguyên tắc an toàn I/O (mỗi %I song song %M, mỗi %Q có %M mirror)
    report_lines.append(f"")
    report_lines.append(f"## 4. Kiểm tra nguyên tắc an toàn tín hiệu I/O")
    print_accented("\n--- 4. KIỂM TRA NGUYÊN TẮC AN TOÀN TÍN HIỆU I/O ---")
    
    if not tag_addresses:
        print_accented("  - Bỏ qua: Không tìm thấy tag nào để phân tích I/O.")
        report_lines.append("- **Trạng thái:** BỎ QUA (Không tìm thấy tag table)")
    else:
        # Check input song hành: %I -> %M kết thúc bằng _HMI
        physical_inputs = {name: addr for name, addr in tag_addresses.items() if addr.upper().startswith("%I")}
        physical_outputs = {name: addr for name, addr in tag_addresses.items() if addr.upper().startswith("%Q")}
        
        input_errors = []
        for name, addr in physical_inputs.items():
            hmi_name = name + "_HMI"
            if hmi_name not in tag_addresses:
                input_errors.append(name)
            else:
                hmi_addr = tag_addresses[hmi_name]
                if not hmi_addr.upper().startswith("%M"):
                    input_errors.append(f"{name} (Có tag HMI nhưng địa chỉ '{hmi_addr}' không phải %M)")
                    
        output_errors = []
        for name, addr in physical_outputs.items():
            mirror_name = name + "_M"
            if mirror_name not in tag_addresses:
                output_errors.append(name)
            else:
                mirror_addr = tag_addresses[mirror_name]
                if not mirror_addr.upper().startswith("%M"):
                    output_errors.append(f"{name} (Có tag Mirror nhưng địa chỉ '{mirror_addr}' không phải %M)")
                    
        inputs_ok = len(input_errors) == 0
        inputs_status = "ĐẠT (PASS)" if inputs_ok else "THẤT BẠI (FAIL - Thiếu tag ảo song hành)"
        print_accented(f"  - Mỗi %I vật lý có %M song song (_HMI): {inputs_status}")
        report_lines.append(f"- **Mỗi %I vật lý có %M song song (_HMI):** {inputs_status}")
        if not inputs_ok:
            is_overall_pass = False
            print_accented("    * Danh sách đầu vào %I bị thiếu tag HMI tương ứng:")
            report_lines.append("  * **Các tag %I thiếu tag ảo tương ứng:**")
            for ie in input_errors:
                print_accented(f"      - {ie}")
                report_lines.append(f"    - `{ie}`")
                
        outputs_ok = len(output_errors) == 0
        outputs_status = "ĐẠT (PASS)" if outputs_ok else "THẤT BẠI (FAIL - Thiếu tag gương mirror)"
        print_accented(f"  - Mỗi %Q vật lý có %M gương mirror (_M): {outputs_status}")
        report_lines.append(f"- **Mỗi %Q vật lý có %M gương mirror (_M):** {outputs_status}")
        if not outputs_ok:
            is_overall_pass = False
            print_accented("    * Danh sách đầu ra %Q bị thiếu tag gương tương ứng:")
            report_lines.append("  * **Các tag %Q thiếu tag gương tương ứng:**")
            for oe in output_errors:
                print_accented(f"      - {oe}")
                report_lines.append(f"    - `{oe}`")

    # 5. KẾT LUẬN CHUNG
    overall_status = "ĐẠT (PASS)" if is_overall_pass else "THẤT BẠI (FAIL - CẦN SỬA LẠI)"
    report_lines.insert(3, f"- **KẾT LUẬN CHUNG:** **{overall_status}**")
    report_lines.insert(4, f"")
    
    print_accented(f"\n============================================================")
    print_accented(f" KẾT LUẬN CHUNG: {overall_status}")
    print_accented(f"============================================================")
    
    # Ghi file báo cáo QA_Report.md
    report_path = os.path.join(output_dir, "QA_Report.md")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print_accented(f"-> Đã ghi báo cáo QA thành công vào file: {report_path}\n")
    except Exception as e:
        print_accented(f"Lỗi khi ghi báo cáo QA_Report.md: {str(e)}\n")
        
    return is_overall_pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_accented("Lỗi cú pháp: Vui lòng truyền đường dẫn thư mục cần kiểm tra.")
        print_accented("Ví dụ: python Ladder/Agent_QA_Validator.py projects/my_project/output")
        sys.exit(1)
    
    out_dir = sys.argv[1]
    success = run_qa_validator(out_dir)
    sys.exit(0 if success else 1)
