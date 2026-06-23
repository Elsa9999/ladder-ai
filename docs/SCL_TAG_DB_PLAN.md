# QUY HOẠCH BẢNG BIẾN VÀ KHỐI DỮ LIỆU SCL (SCL TAG & DB PLAN)

Tài liệu này đặc tả phương án phân bổ và tổ chức lại dữ liệu cho phiên bản SCL mới, định nghĩa rõ quy tắc đặt tên và loại trừ hoàn toàn việc lạm dụng vùng nhớ M-area toàn cục.

---

## 1. Quy Tắc Đặt Tên Biến Mới (Naming Conventions)

Để chuẩn hóa mã nguồn SCL sạch, dễ đọc và phù hợp với tiêu chuẩn lập trình IEC 61131-3, chúng ta áp dụng các quy tắc sau:

1.  **KHÔNG sử dụng tiền tố `AI_`:** Loại bỏ hoàn toàn tiền tố `AI_` ở đầu tất cả các biến, nhãn HMI hay khối dữ liệu mới (ví dụ: đổi `AI_Nut_Khoi_Dong` thành `Nut_Khoi_Dong`).
2.  **Ngôn ngữ đặt tên:** 
    *   **Tên Biến/Tag, Khối DB, Struct:** Sử dụng tiếng Việt KHÔNG DẤU (ASCII-only, chữ cái A-Z, a-z, số 0-9, dấu gạch dưới `_`).
    *   **Comment, Network Title, Description:** Sử dụng tiếng Việt CÓ DẤU (UTF-8) để phục vụ vận hành và bảo trì.
3.  **Quy ước CamelCase và Snake_case:**
    *   *Tên khối DB, UDT, FB:* Dùng CamelCase (ví dụ: `DB_HmiData`, `FB_MixingBranch`).
    *   *Tên biến I/O vật lý và HMI:* Dùng Snake_case (ví dụ: `Nut_Khoi_Dong`, `LT3203_Bon1`).

---

## 2. Quy Hoạch Các Khối Dữ Liệu Tập Trung (Data Blocks)

Thay vì ánh xạ toàn bộ biến trung gian, setpoint HMI và cờ điều khiển vào vùng nhớ M-area (từ `%M110` đến `%MD1200`), bản SCL sẽ lưu trữ tập trung dữ liệu trong các khối Global DB có cấu trúc:

### A. Khối dữ liệu HMI (`DB_HmiData` - DB100)
Chứa tất cả các tag tương tác trực tiếp với giao diện SCADA/HMI.
*   **Struct `Security`:**
    *   `operator_login` : Bool (Đăng nhập quyền Operator)
    *   `engineer_login` : Bool (Đăng nhập quyền Engineer)
    *   `admin_login` : Bool (Đăng nhập quyền Admin)
    *   `user_level` : Int (Mức quyền hiện hành: 1, 2, 3)
    *   `che_do_manual` : Bool (Cho phép điều khiển bằng tay)
*   **Struct `Setpoint`:**
    *   `sp_nuoc_bon1` : Real (Lượng nước dosing Bồn 1, đơn vị L)
    *   `sp_nuoc_bon2` : Real (Lượng nước dosing bổ sung Bồn 2, đơn vị L)
    *   `sp_nhiet_do_bon2` : Real (Setpoint nhiệt độ Bồn 2, đơn vị °C)
    *   `sp_toc_do_bon2` : Real (Setpoint tốc độ khuấy Bồn 2, đơn vị Hz)
    *   `sp_time_khuay_bon1` : Time (Thời gian khuấy Bồn 1)
    *   `sp_time_thanh_trung_bon2` : Time (Thời gian giữ nhiệt Bồn 2)
*   **Struct `Status`:**
    *   `alarm_status` : Int (Mã lỗi WinCC TextList)
    *   `safety_status` : Int (Mã an toàn ưu tiên)

### B. Khối dữ liệu Vận hành (`DB_OperationData` - DB101)
Chứa các biến trạng thái, bước tuần tự và các cờ nhớ liên động quá trình.
*   **Struct `Sys`:**
    *   `auto_enable` : Bool (Cho phép chạy chế độ tự động)
    *   `estop_latch` : Bool (Chốt trạng thái dừng khẩn cấp)
    *   `loi_tong` : Bool (Lỗi tổng khóa hệ thống)
    *   `loi_dry_run` : Bool (Bơm chạy khô)
*   **Struct `Bon1` & `Bon2`:**
    *   `state` : Int (Bước chu trình hiện tại: 0 = Idle, 10 = Dosing, 20 = Mixing, 30 = Heating, 40 = Sterilizing, 50 = Discharging)
    *   `temp_eff` : Real (Nhiệt độ hiệu dụng)
    *   `flow_eff` : Real (Lưu lượng hiệu dụng)
    *   `volume_eff` : Real (Thể tích tích lũy hiệu dụng)
    *   `dosing_active` : Bool (Đang trong bước nạp nước)
    *   `discharge_active` : Bool (Đang trong bước xả đáy)

### C. Khối dữ liệu Công thức (`DB_RecipeData` - DB102)
Lưu trữ các bộ thông số cài đặt mặc định (Default Recipes) được load tự động khi First Scan hoặc khi người dùng nhấn nút Reset trên HMI:
*   `recipe_default_maggi` : Struct (Chứa đầy đủ các trường setpoint thể tích, nhiệt độ, tốc độ, thời gian cho cả 4 bồn).

### D. Khối đệm Truyền thông (`DB_CommsData` - DB103)
Vùng đệm trao đổi dữ liệu Modbus TCP/RTU giữa các CPU và VFD.
*   `plc2_recv_buffer` : Array[0..10] of Word (Bộ đệm nhận từ PLC2)
*   `plc2_send_buffer` : Array[0..10] of Word (Bộ đệm gửi sang PLC2)
*   `vfd_rtu_buffer` : Struct (Chứa Control Word, Freq Setpoint, Status Word, Freq Actual).

---

## 3. Bảo Toàn Bản Đồ Địa Chỉ I/O Vật Lý (Physical I/O Map)

Để đảm bảo tương thích 100% với tủ điện đấu nối phần cứng hiện tại, địa chỉ I/O vật lý của PLC1 và PLC2 **bắt buộc phải giữ nguyên**, không được thay đổi hoặc đè lên địa chỉ khác:

### A. Địa chỉ đầu vào vật lý (PLC1)
*   `Nut_Khoi_Dong` : `%I0.0` (Nút khởi động vật lý)
*   `Nut_Dung` : `%I0.1` (Nút dừng vật lý)
*   `Nut_Reset` : `%I0.2` (Nút reset lỗi vật lý)
*   `Nut_EStop` : `%I0.3` (Nút dừng khẩn vật lý)
*   `LS3202_Bon1_Cao` : `%I0.4` (Cảm biến báo mức cao Bồn 1)
*   `FT3200_Bon1` : `%ID100` (Cảm biến lưu lượng Bồn 1)
*   `FQ3200_Bon1` : `%ID104` (Bộ đếm tích lũy Bồn 1)
*   `LT3203_Bon1` : `%ID108` (Cảm biến mức liên tục Bồn 1)
*   `TT3204_Bon1` : `%ID112` (Cảm biến nhiệt độ Bồn 1)

### B. Địa chỉ đầu ra vật lý (PLC1)
*   `VFD_Bon2_Contactor` : `%Q0.0` (Contactor nguồn VFD Bồn 2)
*   `AGTR3260_Khuay_Bon1` : `%Q0.1` (Động cơ khuấy Bồn 1)
*   `V3232_Xa_Bon1` : `%Q0.2` (Van xả đáy Bồn 1 số 1)
*   `V3233_Xa_Bon1` : `%Q0.3` (Van xả đáy Bồn 1 số 2)
*   `V3234_Xa_Bon1` : `%Q0.4` (Van xả đáy Bồn 1 số 3)
*   `V3235_Nuoc_Bon2` : `%Q0.5` (Van on/off cấp nước Bồn 2)
*   `V3237_Xa_Bon2` : `%Q0.6` (Van xả đáy Bồn 2 số 1)
*   `V3238_Xa_Bon2` : `%Q0.7` (Van xả đáy Bồn 2 số 2)
*   `V3239_Xa_Bon2` : `%Q1.0` (Van xả đáy Bồn 2 số 3)
*   `Pump3264_Chuyen_Nhanh1` : `%Q1.1` (Bơm chuyển Nhánh 1)
*   `CV3201_Nuoc_Bon1` : `%QD100` (Van tuyến tính cấp nước Bồn 1)
*   `AGTR3260_Toc_Do_AO` : `%QD104` (AO Tốc độ khuấy Bồn 1)
*   `CV3206_Hoi_Bon2` : `%QD108` (AO Van hơi Bồn 2)
