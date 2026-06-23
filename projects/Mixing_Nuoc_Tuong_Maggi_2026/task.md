# Tiến độ liên kết HMI tag cho 4 màn hình chi tiết bồn trộn (`bon tron 1` - `4`)

- [x] Bước 1: Xây dựng script Python sinh mapping và patch XML (`patch_detail_screens.py`)
  - [x] Thiết kế thuật toán khớp nhãn gần nhất cho IOField và SymbolLibrary
  - [x] Khắc phục trường hợp thiếu nhãn bơm bằng cách fallback theo tọa độ `(408, 650)`
  - [x] Áp dụng các quy tắc: Mode=Output cho SymbolLibrary, căn giữa, định dạng số `99.9`/`999.9` cho IOField, nhãn đơn vị cách 8px
  - [x] Sinh dry-run CSV `graphic_mapping_dry_run_detail.csv` và 4 file XML patched
- [x] Bước 2: Viết script kiểm định XML ngoại tuyến (offline verifier)
  - [x] Kiểm tra tính chính xác của XML patched trước khi import
- [x] Bước 3: Viết và chạy chương trình C# Openness (`import_detail_screens.cs`)
  - [x] Thực hiện xóa màn hình cũ và import 4 màn hình XML patched vào TIA Portal
  - [x] Biên dịch HMI Target và kiểm tra lỗi biên dịch
- [x] Bước 4: Xuất ngược readback từ TIA và chạy kiểm định chính thức
  - [x] Xuất 4 màn hình readback và bảng tag table
  - [x] Chạy script verifier để kiểm chứng readback đạt PASS 100%
- [x] Bước 5: Tổng hợp báo cáo nghiệm thu cuối cùng và cập nhật walkthrough.md / task.md
