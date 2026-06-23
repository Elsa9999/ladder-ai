# Đặc Tả Phạm Vi Các Variant (VARIANT_SCOPE.md)

Tài liệu này phân định phạm vi kỹ thuật, mục tiêu và yêu cầu hệ thống cho hai biến thể (Variant) phát triển của dự án Mixing Nước Tương Maggi 2026 SCL.

---

## 1. Variant A: Bản Cuộc Thi Tự Động Hóa (1 PLC - Mô Phỏng)

### Mục tiêu:
*   Mô phỏng toàn bộ quy trình pha chế và phối trộn của cả 4 bồn trên một CPU duy nhất.
*   Phù hợp cho chạy kiểm thử offline nhanh, mô phỏng hoạt động độc lập hoặc phục vụ cuộc thi tự động hóa không có phần cứng ngoài.

### Đặc tả kỹ thuật:
*   **Cấu hình phần cứng:** Sử dụng 1 CPU S7-1200 ảo hoặc thật (ví dụ CPU 1214C DC/DC/DC).
*   **Logic điều khiển:**
    *   Tích hợp toàn bộ chu trình Grafcet/State Machine của cả Bồn 1-2 và Bồn 3-4 chung trong một PLC.
    *   Mô phỏng động học bồn chứa (mức dịch bồn chứa thay đổi dựa trên trạng thái đóng/mở van xả và bơm).
*   **Bộ điều khiển PID:**
    *   Sử dụng khối công nghệ **`PID_Compact` Version 1.2** để điều khiển nhiệt độ của Bồn 2.
    *   Sử dụng khối công nghệ **`PID_Compact` Version 1.2** để điều khiển nhiệt độ của Bồn 4.
    *   Viết logic điều phối: Khi cờ chạy PID bật $\rightarrow$ ghi `3` (Auto) vào `sRet.i_Mode`. Khi cờ chạy PID tắt $\rightarrow$ ghi `0` (Inactive) vào `sRet.i_Mode`.
*   **Giao diện HMI:** Tái sử dụng màn hình tổng quan và các màn chi tiết hiển thị toàn bộ trạng thái của cả 4 bồn trên cùng một PLC kết nối.

---

## 2. Variant B: Bản Đấu Nối Thực Tế (2 PLC - Phân Tán)

### Mục tiêu:
*   Triển khai trên hệ thống tủ điện điều khiển phân tán chạy thực tế.
*   PLC1 làm Client điều khiển Bồn 1, Bồn 2 và biến tần ATV12 thật. PLC2 làm Server điều khiển Bồn 3 và Bồn 4.
*   Kết nối truyền thông liên kết dữ liệu giữa hai PLC qua Modbus TCP và kết nối biến tần qua Modbus RTU.

### Đặc tả kỹ thuật:
*   **Cấu hình phần cứng:** Sử dụng 2 CPU S7-1200 riêng biệt (PLC_1 và PLC_2).
*   **Phân bổ điều khiển:**
    *   **PLC_1 (Client):** Điều khiển Bồn 1, Bồn 2 và biến tần cánh khuấy ATV12 của Bồn 2 qua cổng truyền thông RS485 (Modbus RTU).
    *   **PLC_2 (Server):** Điều khiển Bồn 3 và Bồn 4.
*   **Truyền thông PLC-PLC (Modbus TCP):**
    *   Nghiêm cấm sử dụng giao thức S7 GET/PUT.
    *   Sử dụng thư viện **`MB_CLIENT`** (trên PLC_1) và **`MB_SERVER`** (trên PLC_2) phiên bản **V3.1**.
    *   Cấu hình kết nối Modbus TCP sử dụng DB kiểu dữ liệu `TCON_IP_v4` tường minh. Chân `CONNECT` của khối `MB_CLIENT`/`MB_SERVER` phải trỏ trực tiếp vào DB `TCON_IP_v4` này. Các thông số cấu hình IP, Port, Connection ID có thể đặt bằng Start Value trong DB hoặc khởi tạo ở `OB100`/`FirstScan`, đảm bảo compile và readback từ TIA Portal khớp chính xác. Không sử dụng các shortcut kết nối `CONNECT_ID`/`IP_OCTET` mơ hồ.
    *   Thiết lập cơ chế bắt tay (Handshake) truyền nhận dữ liệu lệnh và phản hồi bằng các tag kiểu dữ liệu **`Int`** (`CmdSeq` và `AckSeq`) để chống trùng hoặc chồng lệnh và không sinh lỗi cảnh báo kiểu dữ liệu khi biên dịch.
*   **Truyền thông Biến Tần (Modbus RTU):**
    *   PLC_1 giao tiếp với biến tần Altivar 12 (ATV12) qua mô-đun truyền thông RS485.
    *   Sử dụng State Machine tuần tự trong SCL để điều phối việc đọc/ghi các thanh ghi trạng thái và lệnh của biến tần, ngăn chặn việc gọi đồng thời instance DB gây lỗi bận kênh (Busy).
*   **Bộ điều khiển PID:**
    *   PLC_1 điều khiển nhiệt độ Bồn 2 thông qua khối công nghệ `PID_Compact` V1.2.
    *   PLC_2 điều khiển nhiệt độ Bồn 4 thông qua khối công nghệ `PID_Compact` V1.2.
    *   Logic điều khiển PID tương tự Variant A, gọi trực tiếp và phối hợp chế độ qua SCL.

---

## 3. Điểm Chung và Tái Sử Dụng Từ Bản LAD Cũ

*   **Logic Grafcet và Liên động an toàn:** Kế thừa toàn bộ logic chu trình, trình tự xả dosing, trộn cánh khuấy, xả bồn và các khóa liên động an toàn (như cảm biến cạn, quá nhiệt, E-Stop) từ bản LAD cũ để viết lại chính xác sang SCL.
*   **HMI Reuse:** Cả hai Variant đều giữ nguyên giao diện HMI Screen_1 và các màn hình chi tiết hiện hữu. Bố cục thứ tự bồn trên tổng quan bắt buộc giữ nguyên: **Bồn 1 $\rightarrow$ Bồn 2 $\rightarrow$ Bồn 4 $\rightarrow$ Bồn 3** để khớp với giao diện WinCC thực tế. Các liên kết tag HMI sẽ được map lại dựa trên bảng `migration_map.csv`.
