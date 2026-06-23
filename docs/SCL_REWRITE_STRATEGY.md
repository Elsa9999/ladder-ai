# CHIẾN LƯỢC CHUYỂN ĐỔI SANG SCL (SCL REWRITE STRATEGY)

Tài liệu này đặc tả chiến lược quy hoạch và phát triển phiên bản SCL (Structured Control Language) mới cho hệ thống điều khiển Mixing nước tương Maggi 2026.

---

## 1. Lý Do Chuyển Dịch Sang Bản SCL Mới & Không Sửa Đè Bản LAD

Bản LAD đồ họa hiện tại đã hoạt động ổn định và được kiểm thử thành công (đã backup dưới tag `lad-full-workspace-before-scl-20260623`). Việc chuyển sang viết mới bằng ngôn ngữ SCL thay vì sửa đổi đè lên bản LAD xuất phát từ các lý do kỹ thuật sau:

1. **Hiệu năng quét (Scan cycle) và kích thước tệp tin XML:**
   * Bản LAD đồ họa sinh ra hàng chục nghìn dòng mã XML do phải vẽ các tiếp điểm song song, đường nối mạch phức tạp. Điều này làm tăng kích thước file nạp XML và làm chậm thời gian biên dịch của TIA Portal.
   * Bản SCL được biểu diễn dưới dạng text thuần túy, XML sinh ra cực kỳ nhỏ gọn (giảm tới 80% kích thước file), giúp tốc độ import qua Openness nhanh gấp nhiều lần.
2. **Khả năng đọc hiểu và bảo trì (Readability & Maintainability):**
   * Logic điều khiển tuần tự (Sequence) với nhiều bước phức tạp và các biểu thức toán học (mô phỏng PID, lọc nhiễu sin) viết bằng LAD cực kỳ cồng kềnh và khó debug.
   * Ngôn ngữ SCL hỗ trợ cấu trúc điều khiển `CASE...OF`, `IF...THEN`, vòng lặp và gán trực tiếp, giúp mã nguồn tường minh như các ngôn ngữ lập trình cấp cao (Pascal/C).
3. **Quản lý cấu trúc dữ liệu:**
   * LAD hạn chế trong việc làm việc với mảng (Arrays), Struct và kiểu dữ liệu người dùng (UDT). Bản LAD cũ phải lạm dụng bộ Allocator để gán cứng các tag vào vùng nhớ M-area toàn cục nhằm tránh lỗi trùng lặp địa chỉ.
   * SCL cho phép định nghĩa và truy xuất dữ liệu có cấu trúc thông qua Data Blocks (`DB`) dạng Struct một cách tự nhiên và an toàn mà không cần gán địa chỉ tuyệt đối.
4. **Bảo toàn khả năng Rollback:**
   * Việc không sửa đè giúp giữ nguyên trạng thái hoạt động tốt nhất của bản LAD cũ đã được test thực tế với VFD ATV12 và HMI. Nếu bản SCL mới gặp lỗi tích hợp phần cứng, hệ thống vẫn có thể rollback ngay lập tức về tag `lad-full-workspace-before-scl-20260623`.

---

## 2. Tách Biệt Hai Mục Tiêu Phát Triển

Để phục vụ tốt nhất cho hai mục đích sử dụng khác nhau (thi cử tự động hóa và đấu nối vận hành thực tế), dự án SCL mới sẽ được thiết kế mô-đun hóa để có thể cấu hình linh hoạt thành hai phiên bản:

### A. Bản Cuộc Thi Tự Động Hóa (Automation Competition - Mô phỏng 1 PLC)
*   **Mục tiêu:** Ưu tiên tính độc lập, dễ dàng chạy mô phỏng hoàn toàn (Offline) trên PLC Sim (chỉ cần 1 CPU S7-1200 ảo) mà không cần kết nối phần cứng thật.
*   **Kiến trúc:**
    *   Tích hợp toàn bộ logic của cả 4 bồn trộn (Bồn 1, 2, 3, 4) và cụm bồn chứa/lọc vào chung **một CPU PLC duy nhất (PLC1)**.
    *   **Truyền thông nội bộ ảo:** Các lệnh bắt tay, đồng bộ bước và trạng thái giữa hai nhánh thay vì gửi qua Modbus TCP thật sẽ được liên kết trực tiếp qua các cấu trúc dữ liệu nội bộ (Internal Structs) trong DB truyền thông ảo.
    *   **Khối mô phỏng cảm biến tích hợp:** Tự động sinh dữ liệu nhiệt độ bồn 2/4 (theo bộ lọc nhiễu sin), mức dịch dâng/hạ theo trạng thái van/bơm để chu trình tự động chuyển bước mà không cần tác động thủ công.

### B. Bản Đấu Nối Thực Tế (Real Wiring - 2 PLC + Modbus TCP + Modbus RTU ATV12)
*   **Mục tiêu:** Vận hành trên tủ điện thật với đầy đủ thiết bị ngoại vi và truyền thông phân tán.
*   **Kiến trúc:**
    *   Phân chia tải logic về đúng 2 CPU vật lý riêng biệt:
        *   `PLC1`: Quản lý nhánh 1 (Bồn 1, 2) + Cụm bồn chứa & lọc thành phẩm + Modbus RTU Master điều khiển biến tần ATV12 thật.
        *   `PLC2`: Quản lý nhánh 2 (Bồn 3, 4) + Modbus TCP Server phản hồi dữ liệu.
    *   **Truyền thông Modbus TCP:** Sử dụng `MB_CLIENT` (tại PLC1) và `MB_SERVER` (tại PLC2) phiên bản V3.1 để trao đổi dữ liệu mẻ, lệnh vận hành từ xa và đồng bộ hóa trạng thái sở hữu bồn chứa.
    *   **Truyền thông Modbus RTU:** `PLC1` gọi khối `Modbus_Master` tuần tự để đọc/ghi các thanh ghi trạng thái, tần số đặt của biến tần ATV12 điều khiển động cơ khuấy Bồn 2.
