# ĐÁNH GIÁ LOGIC NỀN SCL: REAL IO MIRROR & SAFETY INTERLOCK

Tài liệu này đánh giá các khối logic SCL nền tảng đầu tiên được tạo cho dự án **Mixing Nước Tương Maggi 2026 SCL** nhằm thiết lập nền móng điều khiển cho cả Variant A (mô phỏng) và Variant B (đấu nối thật).

---

## 1. Các file tạo mới
Hai khối chức năng (FC) SCL mới đã được tạo trong thư mục `fc/` và tài liệu đánh giá này tại `docs/`:
1. **[FC_RealIO_Mirror.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/fc/FC_RealIO_Mirror.scl)**: Ánh xạ ngõ vào/ra vật lý trung gian.
2. **[FC_Safety_Interlock.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/fc/FC_Safety_Interlock.scl)**: Liên động an toàn và chốt lỗi dừng khẩn cấp (E-Stop).
3. **[SCL_FOUNDATION_LOGIC_REVIEW.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/docs/SCL_FOUNDATION_LOGIC_REVIEW.md)**: File đánh giá này.

---

## 2. Các biến và trường dữ liệu (Fields) đã sử dụng
Các khối SCL nền này chỉ tham chiếu và thao tác trên các trường dữ liệu hiện có trong các DB/UDT đã được Codex phê duyệt ở các lượt trước, tuyệt đối không dùng tiền tố `AI_`.

### A. Ngõ vào/ra vật lý (trong `DB_RealIO_Map`)
> [!NOTE]
> `DB_RealIO_Map` hiện tại chỉ đóng vai trò là khối DB đệm trung gian (intermediate mirror DB) để lưu trữ trạng thái I/O thực tế của Variant B, chưa phải là binding phần cứng %I/%Q trực tiếp. Việc cấu hình và thực thi binding địa chỉ vật lý %I/%Q thật sự sẽ được xử lý trong một task riêng biệt sau này.

- `Nut_Start_Physical` (Bool): Nút nhấn chạy hệ thống thực tế (%I0.0).
- `Nut_Stop_Physical` (Bool): Nút nhấn dừng hệ thống thực tế (%I0.1).
- `Nut_Reset_Physical` (Bool): Nút nhấn Reset lỗi thực tế (%I0.2).
- `Nut_EStop_Physical` (Bool): Nút nhấn E-Stop vật lý kiểu tiếp điểm thường đóng (%I0.3).
- `VFD_Bon2_Contactor` (Bool): Contactor cấp nguồn/enable cho biến tần cánh khuấy Bồn 2 (%Q0.0).

### B. Biến điều khiển từ HMI (trong `DB_HMI`)
- `HMI.Nut_Khoi_Dong` (Bool): Lệnh chạy ảo từ nút nhấn HMI.
- `HMI.Nut_Dung` (Bool): Lệnh dừng ảo từ nút nhấn HMI.
- `HMI.Nut_Reset` (Bool): Lệnh Reset lỗi ảo từ HMI.
- `HMI.Nut_EStop` (Bool): Lệnh dừng khẩn ảo từ HMI.
- `HMI.System_Running` (Bool): Đèn báo trạng thái hệ thống chạy phản hồi lên HMI.
- `HMI.System_Alarms` (Word): Mã lỗi hệ thống (Bit 0 chốt lỗi E-Stop).
- `HMI.Safety_Ok` (Bool): Báo trạng thái an toàn hệ thống lên HMI.

### C. Trạng thái hệ thống chung (trong `DB_HMI.System`)
- `System.EStop_Pressed` (Bool): Cờ giám sát nút E-Stop bị tác động (TRUE = bị nhấn/hở mạch).
- `System.Auto_Active` (Bool): Trạng thái hệ thống đang vận hành tự động.
- `System.System_Alarm_Active` (Bool): Cờ báo hệ thống đang có lỗi tích cực.
- `System.Coi_Bao_Dong` (Bool): Trạng thái còi báo động trên HMI.

### D. Biến liên động vận hành nội bộ (trong `DB_Operation`)
- `Safety_Estop_Active` (Bool): Chốt lỗi an toàn hệ thống (phải Reset để xóa).
- `System_Reset` (Bool): Cờ xung đồng bộ Reset trong nội bộ chu kỳ.
- `Coi_Bao_Dong` (Bool): Kích hoạt còi báo động vật lý hoặc còi nội bộ.
- `Bon2.Khuay_Chay` (Bool): Lệnh chạy cánh khuấy Bồn 2 từ logic quy trình.

---

## 3. Xác nhận về việc sửa đổi cấu trúc dữ liệu (DB/UDT)
> [!IMPORTANT]
> **KHÔNG CẦN SỬA ĐỔI DB/UDT**. 
> Cấu trúc DB và UDT skeleton hiện tại đã chứa đầy đủ tất cả các trường dữ liệu cần thiết để thực hiện liên động an toàn và ánh xạ I/O cơ bản. Không có bất kỳ trường dữ liệu mới nào được thêm hay sửa đổi trong DB/UDT ở lượt này.

---

## 4. Lý do chưa thực hiện PID, Modbus và Grafcet
Để đảm bảo chất lượng kiểm soát và tuân thủ nguyên tắc phát triển từng bước an toàn của dự án:
1. **Chưa gọi PID_Compact**: Cần hoàn thiện công cụ cấu hình Technology Object (TO) PID trên TIA Portal trước. Logic SCL chỉ chuẩn bị sẵn các biến UDT dạng skeleton để phối hợp, tránh đưa thuật toán tự viết hoặc lệnh gọi TO khi chưa khai báo phần cứng.
2. **Chưa thiết lập Modbus TCP/RTU**: Truyền thông Modbus đòi hỏi các khối dữ liệu DB_Comms hoàn chỉnh và cấu hình kết nối mạng. Việc này được tách riêng sang một task độc lập để kiểm thử khả năng kết nối giữa PLC1 và PLC2 mà không làm rối loạn phần logic an toàn.
3. **Chưa viết State Machine / Grafcet**: Tiến trình chạy mẻ của các bồn cần được thiết kế tỉ mỉ dựa trên tài liệu công nghệ trộn. Logic an toàn và mirror I/O này đóng vai trò "vòng đai bảo vệ" bên ngoài, sẵn sàng ngắt động cơ cánh khuấy ngay cả khi tiến trình Grafcet đang chạy nếu xảy ra sự cố.

---

## 5. Kế hoạch kiểm thử dự kiến bằng bảng theo dõi (Watch Table)

Để xác minh hành vi của hai khối FC mới trước khi tích hợp vào OB1, ta sử dụng Watch Table với 4 kịch bản kiểm thử tĩnh sau:

### Kịch bản 1: Kiểm tra chốt lỗi E-Stop vật lý
*   **Điều kiện ban đầu**: Hệ thống đang bình thường (`DB_RealIO_Map.Nut_EStop_Physical` = TRUE, `DB_Operation.Safety_Estop_Active` = FALSE).
*   **Hành động**: Force `DB_RealIO_Map.Nut_EStop_Physical` = FALSE (giả lập nhấn E-Stop vật lý).
*   **Kết quả kỳ vọng**:
    *   `DB_Operation.Safety_Estop_Active` chuyển sang TRUE.
    *   `DB_HMI.System.EStop_Pressed` chuyển sang TRUE.
    *   `DB_HMI.System.System_Alarm_Active` chuyển sang TRUE.
    *   `DB_HMI.System.Auto_Active` chuyển sang FALSE.
    *   `DB_RealIO_Map.VFD_Bon2_Contactor` chuyển sang FALSE (ngắt contactor lực lập tức).

### Kịch bản 2: Kiểm tra giải phóng lỗi (Reset) an toàn
*   **Điều kiện ban đầu**: Lỗi chốt đang tích cực (`Safety_Estop_Active` = TRUE). Nút nhấn E-Stop vật lý vẫn đang bị giữ (`DB_RealIO_Map.Nut_EStop_Physical` = FALSE).
*   **Hành động**: Force `DB_RealIO_Map.Nut_Reset_Physical` = TRUE.
*   **Kết quả kỳ vọng**:
    *   Lỗi chốt không được xóa (`Safety_Estop_Active` vẫn giữ nguyên TRUE) do E-Stop chưa được nhả.
*   **Hành động tiếp theo**: Trả `DB_RealIO_Map.Nut_EStop_Physical` = TRUE (nhả E-Stop), sau đó Force `DB_RealIO_Map.Nut_Reset_Physical` = TRUE.
*   **Kết quả kỳ vọng**:
    *   `DB_Operation.Safety_Estop_Active` chuyển sang FALSE.
    *   `DB_HMI.System.EStop_Pressed` chuyển sang FALSE.
    *   `DB_HMI.HMI.Safety_Ok` chuyển sang TRUE.

### Kịch bản 3: Kiểm tra khởi động hệ thống (Start)
*   **Điều kiện ban đầu**: Không có lỗi chốt (`Safety_Estop_Active` = FALSE), hệ thống ở trạng thái dừng.
*   **Hành động**: Force `DB_RealIO_Map.Nut_Start_Physical` = TRUE.
*   **Kết quả kỳ vọng**:
    *   `DB_HMI.System.Auto_Active` chuyển sang TRUE.
    *   `DB_HMI.HMI.System_Running` chuyển sang TRUE.

### Kịch bản 4: Kiểm tra bảo vệ liên động cưỡng bức
*   **Điều kiện ban đầu**: Đang bật chạy cánh khuấy Bồn 2 (`DB_Operation.Bon2.Khuay_Chay` = TRUE), hệ thống đang chạy bình thường, contactor đang đóng (`VFD_Bon2_Contactor` = TRUE).
*   **Hành động**: Nhấn dừng khẩn cấp (`DB_RealIO_Map.Nut_EStop_Physical` = FALSE).
*   **Kết quả kỳ vọng**:
    *   `DB_Operation.Bon2.Khuay_Chay` lập tức bị cưỡng bức về FALSE bởi `FC_Safety_Interlock`.
    *   `DB_RealIO_Map.VFD_Bon2_Contactor` chuyển sang FALSE.

---

## 6. Thứ tự gọi khối (Call Order) bắt buộc khi tích hợp vào OB1

Để đảm bảo mức độ an toàn cao nhất và ngăn ngừa hiện tượng ghi đè trạng thái từ các logic khác, trình tự gọi các khối chức năng trong OB1 (hoặc OB cyclic) phải tuân thủ nghiêm ngặt quy tắc sau:

1.  **Đọc và ánh xạ đầu vào (Mirror Input Blocks)**: Gọi `FC_RealIO_Mirror` (hoặc phân đoạn đọc input) đầu tiên để cập nhật trạng thái các nút nhấn vật lý và HMI vào hệ thống.
2.  **Chạy logic vận hành chính (Sequencer / Manual / Auto Control Logic)**: Chạy các khối điều khiển mẻ, bước tuần tự Grafcet, hoặc logic điều khiển tay để tính toán lệnh chạy thiết bị (ví dụ: `Bon2.Khuay_Chay`).
3.  **Chạy liên động an toàn (Safety Interlock Blocks) sau cùng**: Gọi `FC_Safety_Interlock` **ở cuối vòng quét**, ngay trước khi ghi đè trạng thái ra ngõ ra thực tế.

> [!IMPORTANT]
> **Lý do thiết kế:** Safety Interlock bắt buộc phải được gọi sau cùng để đóng vai trò là "lớp bảo vệ cuối cùng". Điều này đảm bảo rằng nếu nút dừng khẩn E-Stop được kích hoạt, cờ lỗi `Safety_Estop_Active` = TRUE sẽ lập tức cưỡng bức `Bon2.Khuay_Chay` = FALSE và `VFD_Bon2_Contactor` = FALSE, không cho phép bất kỳ logic vận hành hay sequencer nào vô tình bật lại các thiết bị này trong cùng chu kỳ quét.
