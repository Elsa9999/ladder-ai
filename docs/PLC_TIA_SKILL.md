# QUY TRÌNH CHUYÊN MÔN PLC SIEMENS, MODBUS TCP, PID & TIA OPENNESS

Tài liệu này cung cấp các nguyên tắc nghiệp vụ kỹ thuật cốt lõi và hướng dẫn vận hành cho các AI Agent thực hiện lập trình, tích hợp và kiểm thử hệ thống PLC Siemens S7-1200 thông qua TIA Portal V18 Openness.

---

## 1. Nguyên Tắc Lập Trình Đồ Họa Ladder XML (LAD Only)
- **Ladder-only Policy:** 100% logic điều khiển trên PLC phải dùng Ladder. Không được chứa mã SCL (Structured Control Language) trong bất kỳ khối chương trình hay mạng logic nào.
- **Tính toàn vẹn tham chiếu:** Mọi tag I/O vật lý `%I`/`%Q` và tag nội bộ `%M` phải được khai báo đầy đủ trong Tag Table trước khi import khối logic.
- **Tiêu chuẩn đặt tên & ngôn ngữ:**
  - **Tên biến/DB/UDT:** Tiếng Việt KHÔNG DẤU, bắt đầu bằng tiền tố `AI_` (ví dụ: `AI_VFD_Bon2_Toc_Do_AO`).
  - **Chú thích/Mô tả/Tiêu đề mạng:** Tiếng Việt CÓ DẤU Unicode UTF-8 để người vận hành hiểu rõ trên HMI WinCC.

---

## 2. Quy Trình Truyền Thông Modbus TCP PLC-PLC
Để giao tiếp giữa các CPU PLC mà không dùng S7 GET/PUT (bị cấm):
1.  **Sử dụng Thư Viện Modbus V3.1:** Phù hợp nhất cho S7-1200 firmware V4.5+.
2.  **Khối Client (PLC1):**
    *   Gọi khối `MB_CLIENT` (instance `MB_CLIENT_DB`).
    *   Sử dụng biến bước điều khiển tuần tự (ví dụ: `AI_MB_TCP_iStep`) để điều phối việc ghi dữ liệu lệnh (MODE = 1) và đọc dữ liệu trạng thái (MODE = 0) tránh xung đột kênh truyền.
3.  **Khối Server (PLC2):**
    *   Gọi khối `MB_SERVER` (instance `MB_SERVER_DB`).
    *   Liên kết chân `MB_HOLD_REG` trực tiếp với DB Modbus thô `DB_Modbus_Holding_Register_DB` dạng Standard layout (Non-Optimized).
4.  **Thiết lập TCON cấu hình kết nối:**
    *   Không khai báo tĩnh cấu hình kết nối trong DB.
    *   **Bắt buộc gán động** các thông số IP kết nối, ID kết nối, Connection type và Port thông qua lệnh `MOVE` trong mạng khởi động `AI_FirstScan` (OB100 hoặc block khởi tạo tương đương).
5.  **Cơ chế bắt tay chống trùng/chồng lệnh (Handshake):**
    *   Sử dụng số thứ tự lệnh `CmdSeq` (gửi từ Client) và `AckSeq` (phản hồi từ Server).
    *   Định kiểu dữ liệu của các tag handshake là **`Int`** để tránh cảnh báo ép kiểu (type-mismatch warnings) when biên dịch trong TIA.

---

## 3. Quy Trình Cấu HÌnh Bộ Điều Khiển PID Compact
Đối với các bồn gia nhiệt dùng bộ PID Compact:
1.  **Phiên bản:** Luôn chọn **`PID_Compact` Version 1.2** để tương thích với cấu trúc SimaticML XML.
2.  **Khóa liên động chế độ PID (`sRet.i_Mode`):** 
    *   Mặc định khi PLC khởi động hoặc dừng khẩn, PID có thể bị kẹt ở chế độ không mong muốn.
    *   Bắt buộc thiết kế logic điều khiển `sRet.i_Mode` thông qua lệnh `MOVE`:
        *   Khi cờ kích hoạt PID (`AI_PID_*_Enable`) đóng: `MOVE 3` (Auto mode) vào `sRet.i_Mode`.
        *   Khi cờ kích hoạt PID ngắt: `MOVE 0` (Inactive mode) vào `sRet.i_Mode`.

---

## 4. Quy Trình Tự Động Hóa & Tích Hợp TIA Portal (Openness)
Khi làm việc với TIA Portal Openness API:
1.  **Dọn dẹp trước khi nạp:** 
    *   Chạy `delete_duplicate_tags.exe` để xóa tag rác/trùng lặp.
    *   Chạy `delete_dirty_blocks.exe` để xóa các khối block cũ bị lỗi.
2.  **Thứ tự Import XML bắt buộc:**
    *   **B1:** Import các kiểu dữ liệu UDT (`Types`) trước.
    *   **B2:** Import bảng biến `PLC tags` (`Tags`).
    *   **B3:** Import các khối chương trình (`Blocks`: OB, FB, FC, DB).
    *   **B4:** Import danh sách Text list/Graphic list của HMI (`HmiLists`).
3.  **Biên dịch & QA Gate:**
    *   Sử dụng công cụ `compile_viewer.exe` để kích hoạt biên dịch phần cứng/phần mềm. Đảm bảo **0 Errors**.
    *   Sử dụng công cụ `Export_Device_ByName.exe` xuất ngược blocks đã nạp ra thư mục đối chứng `post_import_export`.
    *   Chạy `verify_post_import_export.py` để thẩm định chất lượng trên dữ liệu thực tế.
