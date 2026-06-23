# DANH MỤC CÁC LỆNH ĐIỀU KHIỂN & KIỂM TRA (CLI COMMANDS)

Tài liệu này tổng hợp đầy đủ các dòng lệnh (CLI) thực thi trong workspace dùng để sinh dự án, chuẩn bị import, biên dịch và chạy các script kiểm chứng chất lượng.

---

## 1. Sinh Mã Nguồn & Phân Phối Import Sets (Code Generation)
Chạy các lệnh này từ thư mục gốc của workspace (`D:\AI_Agent_PLC_LADDER_ONLY`):

1.  **Sinh toàn bộ cấu trúc XML dự án Mixing Bồn:**
    ```powershell
    python projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py
    ```
    *   *Mục đích:* Tạo các tệp tin UDT, Tags, Blocks và HMI list XML trong thư mục `output`.

2.  **Phân phối các tệp tin vào bộ Import Sets của từng CPU:**
    ```powershell
    python projects\Mixing_Nuoc_Tuong_Maggi_2026\prepare_tia_import_sets.py
    ```
    *   *Mục đích:* Sắp xếp và sao chép các tệp XML vào `tia_import/PLC_1_Mixing_Import` và `tia_import/PLC_2_Mixing_Import` phục vụ cho việc nạp.

---

## 2. Kiểm Tra Chất Lượng & Đối Chiếu Logic (Verification & Auditing)
Chạy các script này để kiểm tra cấu trúc XML và đối chiếu logic thực tế sau khi import:

1.  **Kiểm tra tính hợp lệ của bộ import XML trước khi nạp:**
    ```powershell
    python scratch\validate_tia_imports.py
    ```
    *   *Mục đích:* Thẩm định tính duy nhất của UId/ID, kiểm tra tag I/O không trùng lặp và không chứa logic SCL.

2.  **Kiểm tra sạch thư mục (Không còn file Modbus TCP Conn DB thừa trên đĩa):**
    ```powershell
    python scratch\verify_clean.py
    ```
    *   *Mục đích:* Đảm bảo các file cấu hình kết nối DB Modbus TCP cũ (`DB_MB_TCP_*`) đã bị loại bỏ hoàn toàn khỏi ổ đĩa.

3.  **Đối chiếu logic trên các file export thực tế từ TIA Portal:**
    ```powershell
    python scratch\verify_post_import_export.py
    ```
    *   *Mục đích:* So sánh trực tiếp logic trong thư mục `post_import_export` (được export từ TIA Portal sau khi import) để xác thực các tiêu chí nghiệm thu P&ID.

4.  **Chạy bộ kiểm thử mô phỏng chu kỳ quét PLC offline:**
    ```powershell
    python scratch\test_plc_logic.py
    ```
    *   *Mục đích:* Giả lập chu kỳ quét PLC1 và PLC2 để kiểm tra logic sequence chuyển bước và trạng thái thiết bị an toàn.

---

## 3. Công Cụ Openness Tự Động Hóa TIA Portal (Openness Automation)
Các công cụ thực thi viết bằng C# Openness, chạy bằng cách gọi trực tiếp file `.exe` tương ứng:

1.  **Biên dịch PLC_1 trong TIA Portal đang mở:**
    ```powershell
    scratch\compile_viewer.exe PLC_1
    ```

2.  **Biên dịch PLC_2 trong TIA Portal đang mở:**
    ```powershell
    scratch\compile_viewer.exe PLC_2
    ```

3.  **Tự động tạo và nạp Watch Table cho cả 2 PLC:**
    ```powershell
    Ladder\create_watch_tables.exe
    ```

4.  **Lưu dự án TIA Portal hiện hành:**
    ```powershell
    Ladder\save_project.exe
    ```

5.  **Dọn dẹp các khối blocks rác/không dùng trong dự án:**
    ```powershell
    Ladder\delete_unused_blocks.exe
    ```

6.  **Xóa bỏ các tag trùng lặp trong PLC Tag Table:**
    ```powershell
    Ladder\delete_duplicate_tags.exe
    ```

7.  **Xuất ngược toàn bộ blocks của thiết bị từ TIA Portal ra thư mục post_import_export:**
    ```powershell
    Ladder\Export_Device_ByName.exe "d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export" "PLC_1"
    Ladder\Export_Device_ByName.exe "d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export" "PLC_2"
    ```
