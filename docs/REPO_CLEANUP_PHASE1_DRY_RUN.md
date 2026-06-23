# KẾ HOẠCH DỌN DẸP GIAI ĐOẠN 1 - CHỈ DRY RUN (REPO CLEANUP PHASE 1 DRY RUN)

Tài liệu này đặc tả kế hoạch dọn dẹp Giai đoạn 1 (Dry-run). **Tuyệt đối chưa thực hiện xóa hoặc di chuyển vật lý** bất kỳ tệp tin nào trong bước này. Kế hoạch chỉ liệt kê các tệp/thư mục rác được xác nhận an toàn để dọn dẹp sau khi được người dùng và Codex phê duyệt.

---

## 1. Danh Sách Tệp & Thư Mục Dự Kiến Xóa (Phase 1 Safe Candidates)

Dưới đây là các tệp tin và thư mục tạm được phân loại `DELETE_CANDIDATE` và có `safe_to_delete_now = TRUE` (theo [REPO_CLEANUP_DELETE_CANDIDATES.csv](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/REPO_CLEANUP_DELETE_CANDIDATES.csv)):

| Đường dẫn tài nguyên | Loại | Lý do xóa | Rủi ro |
| :--- | :--- | :--- | :--- |
| `Output_FB_Comms.xml` | File XML | Tệp XML xuất tạm thời của khối FB_Comms ở root. | Không có. Có thể xuất lại từ TIA. |
| `Output_FB_Tu_Dong.xml` | File XML | Tệp XML xuất tạm thời của khối FB_Tu_Dong ở root. | Không có. Có thể xuất lại từ TIA. |
| `Output_OB30_PID.xml` | File XML | Tệp XML xuất tạm thời của khối OB30 ở root. | Không có. Có thể xuất lại từ TIA. |
| `scratch/PLC_2_temp/` | Thư mục | Thư mục tạm chứa XML trung gian của PLC2. | Không có. Tự sinh lại khi chạy tool. |
| `scratch/dummy_out/` | Thư mục | Thư mục tạm chứa dữ liệu giả lập. | Không có. Tự sinh lại khi chạy generator. |
| `scratch/output_temp/` | Thư mục | Thư mục tạm chứa output XML của generator. | Không có. Tự sinh lại khi chạy generator. |
| `scratch/import_temp/` | Thư mục | Thư mục đệm dùng cho XML import. | Không có. Tự tạo lại khi chạy tool nạp. |
| `scratch/tags_output/` | Thư mục | Thư mục tạm chứa tag table xuất ra. | Không có. Tự sinh lại khi chạy tool. |
| `scratch/cleanup_log.txt` | File log | Nhật ký dọn dẹp cũ. | Không có. |
| `scratch/compile_log.txt` | File log | Nhật ký biên dịch Openness C# cũ. | Không có. |
| `scratch/export_log.txt` | File log | Nhật ký xuất file của Openness. | Không có. |
| `scratch/import_log.txt` | File log | Nhật ký nạp file của Openness. | Không có. |
| `scratch/hmi_compile_log.txt` | File log | Nhật ký biên dịch HMI WinCC cũ. | Không có. |
| `scratch/lang_log.txt` | File log | Nhật ký kiểm tra ngôn ngữ cũ. | Không có. |
| `scratch/python_import_log.txt` | File log | Nhật ký import python, tự sinh lại khi chạy code. | Không có. |
| `scratch/_bindings_log.txt` | File log | Nhật ký liên kết tag WinCC. | Không có. |
| `scratch/_mapping_log.txt` | File log | Nhật ký ánh xạ tag. | Không có. |
| `scratch/_mapping_v2_log.txt` | File log | Nhật ký ánh xạ tag v2. | Không có. |
| `scratch/_mapping_v3_log.txt` | File log | Nhật ký ánh xạ tag v3. | Không có. |
| `scratch/_verify_tags_log.txt` | File log | Nhật ký thẩm định tag table. | Không có. |
| `scratch/scadabai3_export.xml` | File XML | File xuất màn hình SCADA Bài 3 cũ. | Thấp. Có thể xuất lại nếu cần. |
| `scratch/scadabai4_export.xml` | File XML | File xuất màn hình SCADA Bài 4 cũ. | Thấp. Có thể xuất lại nếu cần. |
| `scratch/scadabai5_export.xml` | File XML | File xuất màn hình SCADA Bài 5 cũ. | Thấp. Có thể xuất lại nếu cần. |
| `scratch/scadabai6_export.xml` | File XML | File xuất màn hình SCADA Bài 6 cũ. | Thấp. Có thể xuất lại nếu cần. |
| `scratch/scadabai7_export.xml` | File XML | File xuất màn hình SCADA Bài 7 cũ. | Thấp. Có thể xuất lại nếu cần. |
| `scratch/debug_find.py` | File Python | Script kiểm tra nhanh ham find. | Không có. |
| `scratch/dummy_out.txt` | File text | File text tạm rỗng sinh khi test. | Không có. |

---

## 2. Danh Sách Tài Nguyên Tuyệt Đối KHÔNG Được Đụng (Strictly Untouched List)

Để đảm bảo an toàn cho dự án, các thành phần sau nằm ngoài phạm vi dọn dẹp và **tuyệt đối giữ nguyên**:

1.  **Harnes & Validators:** Thư mục `harness/` (chứa `run_acceptance.py`) và toàn bộ script thẩm định trong `scratch/` (như `validate_plc_overlaps.py`, `validate_tia_imports.py`, `verify_mixing_runtime_fixes.py`, `verify_clean.py`, `test_plc_logic.py`, `verify_post_import_export_manual.py`).
2.  **Logic LAD Cũ Đã Nghiệm Thu:** Thư mục `projects/Mixing_Nuoc_Tuong_Maggi_2026/output/` và file ánh xạ `migration_map.csv`.
3.  **Tài liệu SCL:** Thư mục `docs/SCL_*.md` và `docs/REPO_CLEANUP_*.md` hiện tại.
4.  **Báo cáo Readback:** Thư mục `post_import_export` và `post_import_export_manual`.
5.  **Bằng chứng kiểm thử màn hình HMI (KEEP_EVIDENCE & ARCHIVE):** 
    - `Screen_1_patched.xml` và `Screen_1_readback.xml`
    - `bon_tron_*_patched.xml` và `bon_tron_*_readback.xml`
    - `Screen_1_export.xml` và `bon_tron_*_export.xml`
6.  **Công cụ Openness Tooling:** Toàn bộ file source C# (`*.cs`) và file chạy compiled (`*.exe`) cùng các thư viện liên kết động (`Siemens.Engineering.dll`, `Siemens.Engineering.Hmi.dll`) trong `scratch/`.

---

## 3. Lịch Trình Lệnh PowerShell Dự Kiến Chạy (PowerShell Commands - NOT Executed)

> [!IMPORTANT]
> **Đây là code block mô phỏng.** Các lệnh này chỉ được ghi lại ở đây làm tài liệu hướng dẫn và **tuyệt đối không được thực thi** trong bước này.

```powershell
# === KỊCH BẢN LỆNH DỌN DẸP GIAI ĐOẠN 1 (CHƯA CHẠY) ===

# 1. Xóa các tệp XML xuất tạm thời tại thư mục gốc (root)
Remove-Item -Path "Output_FB_Comms.xml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "Output_FB_Tu_Dong.xml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "Output_OB30_PID.xml" -Force -ErrorAction SilentlyContinue

# 2. Xóa các thư mục tạm trong scratch/ (sử dụng -Recurse)
Remove-Item -Path "scratch/PLC_2_temp" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/dummy_out" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/output_temp" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/import_temp" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/tags_output" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Xóa các file logs và tệp tạm trong scratch/
Remove-Item -Path "scratch/cleanup_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/compile_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/export_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/import_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/hmi_compile_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/lang_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/python_import_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/_bindings_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/_mapping_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/_mapping_v2_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/_mapping_v3_log.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/_verify_tags_log.txt" -Force -ErrorAction SilentlyContinue

# 4. Xóa các tệp XML của các dự án SCADA cũ
Remove-Item -Path "scratch/scadabai3_export.xml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/scadabai4_export.xml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/scadabai5_export.xml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/scadabai6_export.xml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/scadabai7_export.xml" -Force -ErrorAction SilentlyContinue

# 5. Xóa các file script/text tạm khác
Remove-Item -Path "scratch/debug_find.py" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "scratch/dummy_out.txt" -Force -ErrorAction SilentlyContinue
```
