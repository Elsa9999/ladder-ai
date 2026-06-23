# ĐÁNH GIÁ RỦI RO DI CHUYỂN LAD SANG SCL (SCL MIGRATION RISK)

Tài liệu này phân tích các thành phần cốt lõi cần bảo toàn hành vi, nhận diện các rủi ro kỹ thuật khi chuyển đổi sang SCL và đề xuất các biện pháp phòng ngừa/kiểm tra tương ứng.

---

## 1. Các Thành Phần Cốt Lõi Bắt Buộc Bảo Toàn Hành Vi (Tested Legacy Behaviors)

Khi chuyển dịch chương trình sang ngôn ngữ SCL, các thành phần đã được thử nghiệm thực tế và vận hành trơn tru ở bản cũ **bắt buộc phải được tái hiện chính xác hành vi**:

1.  **Vận hành Biến tần ATV12 (Modbus RTU):**
    *   *Yêu cầu hành vi:* Trình tự bật Contactor nguồn động cơ $\rightarrow$ trễ khởi động VFD $\rightarrow$ gửi Control Word bắt tay chạy thuận/chạy ngược $\rightarrow$ tăng tốc theo tần số đặt $\rightarrow$ ngắt Contactor khi lỗi/dừng.
    *   *Mục tiêu SCL:* FC điều khiển biến tần ATV12 phải kế thừa đúng sơ đồ trạng thái (State Sequencer) và thời gian trễ này từ bản LAD cũ.
2.  **Bộ PID Bồn 2 điều khiển van hơi thật:**
    *   *Yêu cầu hành vi:* Đọc nhiệt độ thực tế từ cảm biến `%ID112` $\rightarrow$ xử lý PID $\rightarrow$ xuất giá trị CV điều khiển van hơi tuyến tính `%QD108`.
    *   *Mục tiêu SCL:* Thuật toán PID_Compact phải được cấu hình chạy trong khối ngắt chu kỳ OB30 định kỳ 100ms, đảm bảo thời gian lấy mẫu (Sampling Time) không bị trôi lệch.
3.  **Giao diện HMI Screen_1 (Màn hình tổng quan):**
    *   *Yêu cầu hành vi:* Các biểu tượng van, bơm, cánh khuấy đổi màu động theo trạng thái, các ô IO Field cập nhật đúng giá trị đo lường và setpoint.
    *   *Mục tiêu SCL:* Hệ thống SCL mới phải cung cấp các tag tương ứng với cùng kiểu dữ liệu để HMI liên kết mà không bị vỡ giao diện (HMI Screen_1 tuyệt đối không được sửa thủ công).

---

## 2. Các Rủi Ro Kỹ Thuật Chính & Giải Pháp Khắc Phục (Risks & Mitigations)

### A. Rủi ro về giao thức con trỏ Modbus (`DATA_PTR` / `Variant` Pointer)
*   **Chi tiết rủi ro:** Trong SCL, việc truyền tham số con trỏ vùng nhớ đệm dữ liệu vào chân `DATA_PTR` của khối `Modbus_Master` hoặc `MB_CLIENT` rất dễ xảy ra lỗi kiểu dữ liệu (Type Mismatch) tại TIA Portal compile time, do SCL kiểm soát kiểu dữ liệu nghiêm ngặt hơn LAD.
*   **Giải pháp phòng ngừa:** 
    *   Định nghĩa rõ vùng đệm truyền thông là một mảng Array cố định (`Array[0..10] of Word`) nằm trong một DB không tối ưu (Standard DB - Disable Optimized Block Access).
    *   Khi gọi khối, sử dụng cú pháp chỉ định con trỏ tường minh: `DATA_PTR := "DB_CommsData".ATV12.MB_Buffer`.

### B. Rủi ro Mode-Locking của Technology Object `PID_Compact`
*   **Chi tiết rủi ro:** Cú pháp SCL gọi bộ PID nếu không kiểm soát việc gán chế độ `sRet.i_Mode` đúng chu kỳ quét có thể làm bộ PID tự động chuyển về chế độ Inactive (0) hoặc Manual (4) khi CPU khởi động lại hoặc khi có xung cạnh lên lỗi, khiến người vận hành không thể kích hoạt lại từ HMI.
*   **Giải pháp phòng ngừa:**
    *   Viết logic rẽ nhánh rõ ràng: Khi `PID_Enable = TRUE`, liên tục ghi giá trị `3` (Auto) vào `sRet.i_Mode`. Chỉ khi `PID_Enable = FALSE` mới ghi `0` (Inactive).
    *   Tránh việc ghi đè liên tục nhiều chế độ khác nhau lên biến `sRet.i_Mode` trong cùng một chu kỳ quét.

### C. Rủi ro đứt gãy liên kết HMI Tag (Tag Binding Breakage)
*   **Chi tiết rủi ro:** Bản LAD cũ sử dụng vùng nhớ M-area toàn cục và đã liên kết với HMI Tag Table. Khi bản SCL chuyển toàn bộ biến vận hành và setpoint sang vùng nhớ DB-area, nếu không ánh xạ đúng, TIA Portal biên dịch HMI sẽ báo hàng loạt lỗi cảnh báo *"The process tag is missing"* làm vỡ liên kết đồ họa.
*   **Giải pháp phòng ngừa:**
    *   Duy trì một bảng ánh xạ (Mapping Map) và sử dụng tool Openness để tự động re-bind các HMI Tag cũ từ địa chỉ `%MX.Y` sang biến tương ứng trong `DB_HmiData` (ví dụ: `DB_HmiData.sp_nuoc_bon1`).
    *   Không thay đổi tên của các tag HMI đã được khai báo trên màn hình.

### D. Rủi ro xung đột chu kỳ quét mô phỏng Offline
*   **Chi tiết rủi ro:** Bộ giả lập chu kỳ quét PLC offline (`scratch/test_plc_logic.py`) được thiết kế dựa trên thứ tự chạy và tên các biến LAD cũ. Khi cấu trúc lại SCL, bộ test này có thể bị lỗi cú pháp hoặc báo sai lệch hành vi chuyển bước.
*   **Giải pháp phòng ngừa:**
    *   Đồng bộ hóa mô hình giả lập của `test_plc_logic.py` để phản ánh đúng cấu trúc biến trong các khối DB mới của SCL.
    *   Chạy test runner liên tục sau mỗi thay đổi kiến trúc nhỏ.
    *   Sử dụng cờ kiểm tra tĩnh XML để xác nhận không có logic SCL nào bị trôi hoặc thiếu trong các import set.
