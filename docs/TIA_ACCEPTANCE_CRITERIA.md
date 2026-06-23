# TIÊU CHÍ NGHIỆM THU TIA PORTAL (TIA PORTAL ACCEPTANCE CRITERIA)

> [!NOTE]
> **TÀI LIỆU LỊCH SỬ / LEGACY REFERENCE:**
> Tài liệu này liệt kê các tiêu chí nghiệm thu của phiên bản đồ họa Ladder (LAD) cũ.
> Hiện tại, repository đã chuyển sang chiến lược phát triển **SCL-first**. Quy tắc "Lập trình 100% Ladder" dưới đây chỉ dùng để đối chiếu khi cần thiết và **không còn hiệu lực** đối với logic PLC mới.

Tài liệu này liệt kê các tiêu chuẩn kỹ thuật bắt buộc mà dự án PLC sinh ra phải đáp ứng để vượt qua các bộ kiểm duyệt tự động và được chấp nhận tích hợp vào phần mềm TIA Portal V18.

---

## 1. Tiêu Chí Lập Trình & Logic PLC (PLC Programming & Logic)
1.  **Lập trình 100% Ladder (Ladder-only Policy):**
    *   Tất cả logic điều khiển trong CPU PLC (các khối OB, FB, FC) phải được lập trình hoàn toàn bằng đồ họa Ladder XML.
    *   **Tuyệt đối nghiêm cấm** sử dụng hoặc sinh bất kỳ mã nguồn SCL nào (bao gồm khối SCL, mạng SCL hoặc file `.scl`) để chạy trên PLC.
2.  **Cấu hình khối PID (PID_Compact Configuration):**
    *   Bắt buộc sử dụng khối điều khiển **`PID_Compact` phiên bản 1.2** (`Version="1.2"`).
    *   **Khóa liên động chế độ PID (`sRet.i_Mode`):** Để tránh lỗi kẹt chế độ PID khi khởi động PLC hoặc dừng chu trình, bắt buộc phải viết mạng logic ghi chế độ:
        *   Khi khối PID được cho phép chạy (Enable): Lệnh `MOVE` ghi giá trị **`3`** (Chế độ tự động - Auto) vào tham số `sRet.i_Mode`.
        *   Khi khối PID bị dừng/không cho phép (Disable): Lệnh `MOVE` ghi giá trị **`0`** (Chế độ ngưng hoạt động - Inactive) vào tham số `sRet.i_Mode`.
3.  **Không sử dụng lệnh GET/PUT:**
    *   Tuyệt đối không sử dụng các khối giao tiếp truyền thông S7 GET (`SFB14` / `GET`) hoặc S7 PUT (`SFB15` / `PUT`) để trao đổi dữ liệu giữa các PLC CPU.
4.  **Trao đổi dữ liệu qua Modbus TCP:**
    *   Sử dụng giao thức truyền thông Modbus TCP qua các khối thư viện **`MB_CLIENT`** (tại PLC Client) và **`MB_SERVER`** (tại PLC Server).
    *   **Phiên bản Modbus:** Bắt buộc sử dụng phiên bản **V3.1** nhằm tương thích tốt nhất với dòng CPU S7-1200 có firmware **V4.5** trở lên.
    *   Các chân cấu hình IP và thông số kết nối của struct `TCON_IP_v4` phải được gán động bằng lệnh `MOVE` trong mạng khởi tạo (`AI_FirstScan`) thay vì gán tĩnh trong DB để đảm bảo tính an toàn tham chiếu khi import XML.

---

## 2. Quy Trình Tích Hợp & Kiểm Thử (Integration & Testing Workflow)
1.  **Thẩm định chất lượng XML trước khi nạp (Validate before Import):**
    *   Luôn chạy công cụ kiểm duyệt `Agent_QA_Validator.py` trên các tệp tin XML được sinh ra trước khi tiến hành import vào TIA Portal. Đảm bảo cấu trúc XML hợp lệ, các ID và UId là duy nhất và không bị xung đột địa chỉ I/O vật lý.
2.  **Sao lưu và Xuất dữ liệu đối chứng (Backup & Export Policy):**
    *   Trước khi tiến hành nạp (import) bất kỳ bộ tag hay blocks mới nào vào dự án TIA Portal đang mở, bắt buộc phải thực hiện sao lưu dự án (`SaveAs`) hoặc lưu lại trạng thái hoạt động tốt gần nhất.
    *   Sau khi import thành công, bắt buộc dùng công cụ Openness `Export_Device_ByName.exe` xuất toàn bộ blocks thực tế từ TIA Portal ra thư mục `post_import_export` để đối chiếu kiểm tra chéo bằng script `verify_post_import_export.py`. Không dùng file nguồn tự sinh để tự kết luận kết quả.
3.  **Biên dịch không có lỗi (Zero Compilation Errors):**
    *   Sau khi nạp toàn bộ khối chương trình vào TIA Portal, thực hiện biên dịch phần cứng và phần mềm cho cả `PLC_1` và `PLC_2`.
    *   Yêu cầu bắt buộc: **Kết quả biên dịch phải đạt 0 Errors** (chấp nhận các cảnh báo Warning thông thường).
