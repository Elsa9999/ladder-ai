# CHIẾN LƯỢC CHUYỂN ĐỔI SANG SCL (SCL REWRITE STRATEGY)

Tài liệu này đặc tả chiến lược quy hoạch và phát triển phiên bản SCL (Structured Control Language) mới cho hệ thống điều khiển Mixing nước tương Maggi 2026.

---

## 1. Lý Do Chuyển Dịch Sang Bản SCL Mới & Không Sửa Đè Bản LAD

Bản LAD đồ họa hiện tại đã hoạt động ổn định và được kiểm thử thành công (đã backup dưới tag `lad-full-workspace-before-scl-20260623`). Việc chuyển sang viết mới bằng ngôn ngữ SCL thay vì sửa đổi đè lên bản LAD xuất phát từ các lý do kỹ thuật sau:

1. **Hiệu năng quét (Scan cycle) và kích thước tệp tin XML:**
   * Bản LAD đồ họa sinh ra hàng chục nghìn dòng mã XML do phải vẽ các tiếp điểm song song, đường nối mạch phức tạp. Điều này làm tăng kích thước file nạp XML và làm chậm thời gian biên dịch của TIA Portal.
   * Bản SCL được biểu diễn dưới dạng text thuần túy, XML sinh ra cực kỳ nhỏ gọn (giảm tới 80% kích thước file), giúp tốc độ import qua Openness nhanh gấp nhiều lần.
2. **Khả năng đọc hiểu và bảo trì (Readability & Maintainability):**
   * Logic điều khiển tuần tự (Sequence) với nhiều bước phức tạp và các biểu thức toán học viết bằng LAD cực kỳ cồng kềnh và khó debug.
   * Ngôn ngữ SCL hỗ trợ cấu trúc điều khiển `CASE...OF`, `IF...THEN`, vòng lặp và gán trực tiếp, giúp mã nguồn tường minh như các ngôn ngữ lập trình cấp cao (Pascal/C).
3. **Quản lý cấu trúc dữ liệu:**
   * LAD hạn chế trong việc làm việc với mảng (Arrays), Struct và kiểu dữ liệu người dùng (UDT). Bản LAD cũ phải lạm dụng bộ Allocator để gán cứng các tag vào vùng nhớ M-area toàn cục nhằm tránh lỗi trùng lặp địa chỉ.
   * SCL cho phép định nghĩa và truy xuất dữ liệu có cấu trúc thông qua Data Blocks (`DB`) dạng Struct một cách tự nhiên và an toàn mà không cần gán địa chỉ tuyệt đối.
4. **Bảo toàn khả năng Rollback:**
   * Việc không sửa đè giúp giữ nguyên trạng thái hoạt động tốt nhất của bản LAD cũ đã được test thực tế với VFD ATV12 và HMI. Nếu bản SCL mới gặp lỗi tích hợp phần cứng, hệ thống vẫn có thể rollback ngay lập tức về tag `lad-full-workspace-before-scl-20260623`.

---

## 2. Tách Biệt Hai Mục Tiêu Phát Triển

Để phục vụ tốt nhất cho hai mục đích sử dụng khác nhau (thi cử tự động hóa và đấu nối vận hành thực tế), dự án SCL mới sẽ được thiết kế mô-đun hóa để có thể cấu hình linh hoạt thành hai phiên bản:

### A. Bản Cuộc Thi Tự Động Hóa (Automation Competition — 1 PLC duy nhất)
*   **Mục tiêu:** Ưu tiên chạy toàn bộ trên 1 CPU S7-1200 (ảo hoặc thật), không phụ thuộc PLC2 hay Modbus TCP.
*   **Kiến trúc:**
    *   **Khối logic:** Tích hợp toàn bộ Bồn 1, 2, 3, 4 và cụm bồn chứa/lọc vào **một CPU PLC1 duy nhất**.
    *   **`PID_Compact_1` (OB30 trên PLC1):** Điều khiển nhiệt độ Bồn 2, PV từ `TT3208_Bon2_Eff`.
    *   **`PID_Compact_2` (OB31 trên PLC1):** Điều khiển nhiệt độ Bồn 4, PV từ tag nội bộ mô phỏng quá trình (thay cảm biến thật). Cả hai OB30/OB31 đều nằm trên PLC1.
    *   **`FB_VFD_ATV12_ModbusRTU` (FB30, Instance DB30):** Điều khiển biến tần ATV12 qua Modbus RTU (chỉ dùng nếu có phần cứng ATV12; có thể tắt trong bản mô phỏng thuần).
    *   **Truyền thông nội bộ:** Hai nhánh trao đổi dữ liệu qua Internal Struct trong DB nội bộ — **không dùng Modbus TCP**.
    *   **Mô phỏng mức dịch:** `FC_Sensor_Sim` (FC40) sinh dữ liệu mức dịch theo trạng thái van/bơm. PV nhiệt độ bồn 4 là tag nội bộ; `PID_Compact_2` vẫn là bộ điều khiển chuẩn Siemens sinh CV — **không tự viết thuật toán PID**.

### B. Bản Đấu Nối Thực Tế (Real Wiring — 2 PLC + Modbus TCP + Modbus RTU ATV12)
*   **Mục tiêu:** Vận hành trên tủ điện thật với đầy đủ thiết bị ngoại vi và truyền thông phân tán.
*   **Kiến trúc:**
    *   **PLC1:** Bồn 1, 2 + `PID_Compact_1` (OB30) + `FB_VFD_ATV12_ModbusRTU` (FB30) điều khiển ATV12 qua Modbus RTU + Modbus TCP Client (`MB_CLIENT` V3.1).
    *   **PLC2:** Bồn 3, 4 + `PID_Compact_2` (OB31) + Modbus TCP Server (`MB_SERVER` V3.1) phản hồi dữ liệu.
    *   **Truyền thông Modbus TCP:** Chỉ bật ở bản B. PLC1 đọc/ghi dữ liệu Bồn 3–4 và đồng bộ lệnh với PLC2.
    *   **Truyền thông Modbus RTU:** PLC1 gọi `FB_VFD_ATV12_ModbusRTU` tuần tự để đọc/ghi thanh ghi trạng thái, tần số đặt của ATV12.
