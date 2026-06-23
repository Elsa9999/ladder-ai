# -*- coding: utf-8 -*-
"""
Bộ kiểm tra chất lượng (Validator) cho thư viện mẫu TIA Portal V18 XML.
Kiểm tra cấu trúc thư mục, tệp manifest.json, tệp README, tệp XML SimaticML và xuất báo cáo.
Cách dùng:
  python validate_patterns.py
"""
import os
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# Đảm bảo hiển thị Tiếng Việt trên Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LIBRARY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERNS_DIR = os.path.join(LIBRARY_ROOT, "patterns")
REPORT_PATH = os.path.join(LIBRARY_ROOT, "PATTERN_LIBRARY_REPORT.md")

REQUIRED_MANIFEST_KEYS = [
    "tia_version",
    "plc_family",
    "language",
    "block_instruction_name",
    "tested_status"
]

VALID_TESTED_STATUSES = [
    "generated",
    "imported",
    "compiled",
    "manual_required"
]

def validate_pattern_dir(pattern_path):
    issues = []
    manifest = {}
    
    # 1. Kiểm tra sự tồn tại của manifest.json
    manifest_path = os.path.join(pattern_path, "manifest.json")
    if not os.path.exists(manifest_path):
        issues.append("Thiếu tệp manifest.json")
    else:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            # Validate các key bắt buộc
            for key in REQUIRED_MANIFEST_KEYS:
                if key not in manifest:
                    issues.append(f"manifest.json thiếu thuộc tính bắt buộc: '{key}'")
            
            # Validate tested_status
            if "tested_status" in manifest:
                status = manifest["tested_status"]
                if status not in VALID_TESTED_STATUSES:
                    issues.append(f"tested_status '{status}' không hợp lệ. Phải là một trong: {VALID_TESTED_STATUSES}")
                    
        except Exception as e:
            issues.append(f"Lỗi cú pháp manifest.json: {e}")

    # 2. Kiểm tra README.md
    readme_path = os.path.join(pattern_path, "README.md")
    if not os.path.exists(readme_path):
        issues.append("Thiếu tệp README.md")

    # 3. Kiểm tra compile_notes.md hoặc TODO.md
    notes_exist = os.path.exists(os.path.join(pattern_path, "compile_notes.md"))
    todo_exist = os.path.exists(os.path.join(pattern_path, "TODO.md"))
    if not (notes_exist or todo_exist):
        issues.append("Thiếu cả tệp compile_notes.md và TODO.md (Cần ít nhất một tệp)")

    # 4. Kiểm tra XML (pattern.xml hoặc network.xml)
    xml_file = None
    for f in ["pattern.xml", "network.xml"]:
        p = os.path.join(pattern_path, f)
        if os.path.exists(p):
            xml_file = p
            break
            
    if not xml_file:
        # Nếu tested_status là manual_required, chấp nhận không có XML nhưng bắt buộc phải có TODO.md
        if manifest.get("tested_status") == "manual_required":
            if not todo_exist:
                issues.append("Mẫu yêu cầu tạo thủ công (manual_required) nhưng thiếu tệp TODO.md hướng dẫn")
        else:
            issues.append("Thiếu tệp logic XML (pattern.xml hoặc network.xml)")
    else:
        try:
            ET.parse(xml_file)
        except ET.ParseError as pe:
            issues.append(f"Lỗi cú pháp XML trong {os.path.basename(xml_file)}: {pe}")
        except Exception as e:
            issues.append(f"Lỗi đọc tệp XML {os.path.basename(xml_file)}: {e}")

    return issues, manifest

def main():
    print("==========================================================")
    print(" KHỞI CHẠY BỘ KIỂM TRA CHẤT LƯỢNG THƯ VIỆN MẪU TIA XML    ")
    print("==========================================================\n")

    if not os.path.exists(PATTERNS_DIR):
        print(f"[ERROR] Thư mục patterns không tồn tại: {PATTERNS_DIR}")
        sys.exit(1)

    categories = os.listdir(PATTERNS_DIR)
    
    report_lines = []
    report_lines.append("# BÁO CÁO THƯ VIỆN MẪU XML TIA PORTAL V18 (PATTERN LIBRARY REPORT)")
    report_lines.append(f"- **Thời gian kiểm tra:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    total_patterns = 0
    passed_patterns = 0
    failed_patterns = 0
    
    category_summary = {}
    detailed_results = []
    
    for cat in categories:
        cat_path = os.path.join(PATTERNS_DIR, cat)
        if not os.path.isdir(cat_path):
            continue
            
        category_summary[cat] = {"total": 0, "passed": 0, "failed": 0}
        subdirs = os.listdir(cat_path)
        
        for sub in subdirs:
            pattern_path = os.path.join(cat_path, sub)
            if not os.path.isdir(pattern_path):
                continue
                
            total_patterns += 1
            category_summary[cat]["total"] += 1
            
            issues, manifest = validate_pattern_dir(pattern_path)
            
            status = "ĐẠT (PASS)" if len(issues) == 0 else "THẤT BẠI (FAIL)"
            if len(issues) == 0:
                passed_patterns += 1
                category_summary[cat]["passed"] += 1
            else:
                failed_patterns += 1
                category_summary[cat]["failed"] += 1
                
            block_name = manifest.get("block_instruction_name", sub)
            tested_status = manifest.get("tested_status", "N/A")
            
            detailed_results.append({
                "category": cat,
                "name": sub,
                "block_name": block_name,
                "status": status,
                "tested_status": tested_status,
                "issues": issues
            })

    # Ghi tóm tắt báo cáo
    report_lines.append("## Tóm tắt kết quả kiểm tra")
    report_lines.append(f"- **Tổng số mẫu:** {total_patterns}")
    report_lines.append(f"- **Số mẫu đạt:** {passed_patterns} ({(passed_patterns/total_patterns)*100:.1f}%)")
    report_lines.append(f"- **Số mẫu chưa đạt:** {failed_patterns} ({(failed_patterns/total_patterns)*100:.1f}%)")
    report_lines.append("")
    
    report_lines.append("### Bảng tổng hợp theo chuyên mục")
    report_lines.append("| Chuyên mục | Tổng số mẫu | Đạt | Chưa đạt |")
    report_lines.append("|---|---|---|---|")
    for cat, stat in category_summary.items():
        report_lines.append(f"| {cat} | {stat['total']} | {stat['passed']} | {stat['failed']} |")
    report_lines.append("")
    
    report_lines.append("## Chi tiết kết quả từng mẫu")
    report_lines.append("| Chuyên mục | Tên mẫu | Tên khối/lệnh | Trạng thái kiểm tra | Tested Status | Phát hiện lỗi |")
    report_lines.append("|---|---|---|---|---|---|")
    for res in detailed_results:
        issues_str = "; ".join(res["issues"]) if res["issues"] else "Không phát hiện lỗi"
        report_lines.append(f"| {res['category']} | {res['name']} | {res['block_name']} | {res['status']} | {res['tested_status']} | {issues_str} |")
    
    # Ghi đè file báo cáo
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"[SUCCESS] Đã tạo báo cáo kiểm tra tại: {REPORT_PATH}")
    print(f"Tổng số: {total_patterns} mẫu. Đạt: {passed_patterns}. Lỗi: {failed_patterns}.")
    
    # Cập nhật số lượng mẫu vào file manifest.json của thư viện
    manifest_path = os.path.join(LIBRARY_ROOT, "manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                lib_manifest = json.load(f)
            lib_manifest["patterns_count"] = total_patterns
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(lib_manifest, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARNING] Không thể cập nhật patterns_count trong manifest.json: {e}")

    sys.exit(0 if failed_patterns == 0 else 1)

if __name__ == "__main__":
    main()
