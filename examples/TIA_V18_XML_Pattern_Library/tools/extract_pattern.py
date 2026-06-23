# -*- coding: utf-8 -*-
"""
Công cụ trích xuất các phân đoạn XML (SimaticML) từ file block xuất bản của TIA Portal.
Cách dùng:
  python extract_pattern.py --src <path_to_xml> --network-title "Tên network" --out <output_path>
  python extract_pattern.py --src <path_to_xml> --part-name "TON" --out <output_path>
"""
import os
import sys
import argparse
import xml.etree.ElementTree as ET

# Đảm bảo hiển thị Tiếng Việt trên Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def extract_by_network_title(xml_path, title):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for unit in root.findall(".//{*}SW.Blocks.CompileUnit"):
            title_node = unit.find(".//{*}Title//{*}Text")
            if title_node is not None and title_node.text and title.strip().lower() in title_node.text.strip().lower():
                return ET.tostring(unit, encoding='utf-8').decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Không thể đọc {xml_path}: {e}")
    return None

def extract_by_part_name(xml_path, part_name):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for unit in root.findall(".//{*}SW.Blocks.CompileUnit"):
            part = unit.find(f".//{{*}}Part[@Name='{part_name}']")
            if part is not None:
                return ET.tostring(unit, encoding='utf-8').decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Không thể đọc {xml_path}: {e}")
    return None

def extract_block_body(xml_path):
    """Trích xuất phần Interface và toàn bộ ObjectList chính của block"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        # Tìm phần tử đầu tiên khớp SW.Blocks
        for child in root:
            if child.tag.split('}')[-1].startswith("SW.Blocks."):
                return ET.tostring(child, encoding='utf-8').decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Không thể trích xuất block body: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Trích xuất mẫu XML từ file TIA Portal SimaticML.")
    parser.add_argument("--src", required=True, help="Đường dẫn file XML nguồn")
    parser.add_argument("--network-title", help="Tìm theo tiêu đề network")
    parser.add_argument("--part-name", help="Tìm theo tên của Part (ví dụ: TON, CTU)")
    parser.add_argument("--block", action="store_true", help="Trích xuất toàn bộ khối block thay vì chỉ 1 network")
    parser.add_argument("--out", help="Đường dẫn lưu file kết quả")

    args = parser.parse_args()

    if not os.path.exists(args.src):
        print(f"[ERROR] File nguồn không tồn tại: {args.src}")
        sys.exit(1)

    result = None
    if args.block:
        result = extract_block_body(args.src)
    elif args.network_title:
        result = extract_by_network_title(args.src, args.network_title)
    elif args.part_name:
        result = extract_by_part_name(args.src, args.part_name)
    else:
        print("[WARNING] Bạn chưa chọn phương pháp trích xuất (dùng --network-title, --part-name, hoặc --block).")
        sys.exit(1)

    if result:
        # Làm sạch định dạng XML cơ bản (đầu ra xml.etree có thể bị thừa xmlns ở các node con)
        # Giữ cấu trúc xmlns ở root của node trích xuất
        if args.out:
            os.makedirs(os.path.dirname(args.out), exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"[SUCCESS] Đã lưu kết quả trích xuất vào: {args.out}")
        else:
            print(result)
    else:
        print("[WARNING] Không tìm thấy mẫu phù hợp yêu cầu.")

if __name__ == "__main__":
    main()
