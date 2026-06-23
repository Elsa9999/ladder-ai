# CHECKLIST KỊCH BẢN DEMO DỰ ÁN & HƯỚNG DẪN CHẨN ĐOÁN TRẠNG THÁI
DỰ ÁN: MIXING NƯỚC TƯƠNG MAGGI 2026

Bảng checklist này được sử dụng để tiến hành chạy thử nghiệm nghiệm thu (commissioning/demo) trên bàn mô phỏng hoặc TIA Portal PLCSIM nhằm kiểm tra toàn bộ 10 chức năng cốt lõi của hệ thống.

---

## 1. BẢNG KỊCH BẢN KHẢO SÁT & NGHIỆM THU

| STT | Kịch bản / Case test | Các tag tham chiếu chính | Kết quả mong đợi (Expected Results) | Đạt (Y/N) |
|---|---|---|---|---|
| **1** | **Kích hoạt Sim Mode (Mô phỏng HMI)** | - `HMI_Sim_Mode`<br>- `HMI_Use_Sim_Input_PLC1`<br>- `System_Mode_Sim`<br>- `HMI_Sim_Active_Warning` | - Bật `HMI_Sim_Mode = TRUE`. Hệ thống phải tự động chuyển sang chế độ mô phỏng (`System_Mode_Sim = TRUE`).<br>- Cảnh báo nhấp nháy `HMI_Sim_Active_Warning` kích hoạt.<br>- Cho phép mô phỏng giá trị cảm biến qua tag `*_HMI` và tự động cập nhật vào các giá trị hiệu dụng `*_Eff`. | |
| **2** | **Chạy chế độ thực tế (Real Mode)** | - `HMI_Sim_Mode`<br>- `System_Mode_Real`<br>- `TT3208_Bon2_HMI`<br>- `TT3208_Bon2_Eff` | - Tắt `HMI_Sim_Mode = FALSE`. Hệ thống chuyển sang `System_Mode_Real = TRUE`.<br>- Toàn bộ các tag `*_HMI` (mô phỏng) phải bị tự động xóa về `0.0` hoặc `FALSE`.<br>- Các tag hiệu dụng `*_Eff` chuyển sang đọc trực tiếp từ kênh vật lý thật `%I` hoặc `%AI` của PLC. | |
| **3** | **Điều khiển Start/Stop/Reset/EStop** | - `Nut_Khoi_Dong_Eff`<br>- `Nut_Dung_Eff`<br>- `Nut_Reset_Eff`<br>- `PLC1_EStop_Latch` | - Lệnh **Start** vật lý `%I0.0` hoặc HMI song song đều kích hoạt chu trình.<br>- Lệnh **Stop** vật lý `%I0.1` hoặc HMI lập tức đưa hệ thống về trạng thái dừng active.<br>- Lệnh **E-Stop** vật lý `%I0.3` hoặc HMI chốt dừng khẩn an toàn (`PLC1_EStop_Latch`).<br>- **Reset** chỉ hoạt động sau khi nhả nút dừng khẩn vật lý và nhấn reset. | |
| **4** | **PLC1 chạy tự động Nhánh 1 (Bồn 1-2)** | - `PLC1_State`<br>- `PLC1_Step_Bon1_Dosing`<br>- `PLC1_Step_Bon2_PID`<br>- `PLC1_Me_Nhanh1_Hoan_Thanh` | - Quan sát state `PLC1_State` tuần tự tăng: Dosing bồn 1 (State 10) -> Tip (11) -> Khuấy bồn 1 (12) -> Xả bồn 1 sang 2 (15) -> Dosing bồn 2 (20) -> Tip bồn 2 (21) -> Khuấy thuận bồn 2 (22) -> Khuấy ngược bồn 2 (23) -> PID (30) -> Thanh trùng (31).<br>- Chu trình dừng lại, báo hoàn thành Nhánh 1 và sẵn sàng xả xuống bồn chứa. | |
| **5** | **PLC2 chạy tự động Nhánh 2 (Bồn 3-4)** | - `PLC2_State`<br>- `PLC2_Step_Bon3_Dosing`<br>- `PLC2_Step_Bon4_PID_Mo_Phong` | - Quan sát state `PLC2_State` tăng tuần tự tương ứng nhánh 2: Dosing bồn 3 (State 10) -> Tip (11) -> Khuấy bồn 3 (12) -> Xả bồn 3 sang 4 (15) -> Dosing bồn 4 (20) -> Tip bồn 4 (21) -> Khuấy thuận bồn 4 (22) -> Khuấy ngược bồn 4 (23) -> PID mô phỏng (30) -> Thanh trùng (31).<br>- Kết thúc, báo hoàn thành Nhánh 2. | |
| **6** | **PID Bồn 2 điều khiển van hơi thật** | - `PID_Bon2_SP`<br>- `TT3208_Bon2_Eff`<br>- `PID_Bon2_CV`<br>- `CV3206_Hoi_Bon2`<br>- `VFD_Bon2_Toc_Do_AO` | - Khi bước PID bồn 2 active, PID_Compact chuyển sang tự động (i_Mode = 3).<br>- Thay đổi SP và PV, quan sát CV thay đổi tương ứng.<br>- CV của PID bồn 2 tự động được gán trực tiếp vào van hơi gia nhiệt `CV3206_Hoi_Bon2`. Cánh khuấy bồn 2 chạy ở tốc độ đặt từ HMI `HMI_SP_PLC1_Toc_Do_Bon2_Main`. | |
| **7** | **PID Bồn 4 mô phỏng trong PLC2** | - `PID_Bon4_SP`<br>- `TT3219_Bon4_Sim`<br>- `PID_Bon4_CV`<br>- `PID_Bon4_PV_Recv` | - Khi bước PID bồn 4 active, PID_Compact PLC2 chuyển sang tự động (i_Mode = 3).<br>- Hệ thống tự động mô phỏng nhiệt độ tăng dần dựa trên `PID_Bon4_CV` kèm nhiễu hình sin.<br>- Các giá trị SP, PV, CV của bồn 4 trong PLC2 được truyền thành công về PLC1 qua Modbus TCP để hiển thị trên HMI chính (thông qua các tag `*_Recv`). | |
| **8** | **Handshake Modbus TCP PLC-PLC** | - `DB_PLC1_Send_To_PLC2_DB.CmdSeq`<br>- `DB_Modbus_Holding_Register_DB.AckSeq`<br>- `DB_PLC1_Send_To_PLC2_DB.Heartbeat`<br>- `PLC1_Loi_Truyen_Thong` | - Kiểm tra truyền thông Modbus TCP hoạt động: các tag `CmdSeq` (Client) gửi đi và `AckSeq` (Server) phản hồi lại phải tự động tăng đồng bộ.<br>- Giá trị `Heartbeat` liên tục thay đổi.<br>- Khi giả lập mất kết nối (bằng tag `Gia_Lap_Mat_Ket_Noi_HMI`), hệ thống chốt lỗi truyền thông (`PLC1_Loi_Truyen_Thong = TRUE`). | |
| **9** | **Cụm Bồn chứa nhận hoàn thành 2 nhánh** | - `PLC1_Me_Nhanh1_Hoan_Thanh`<br>- `PLC2_Me_Nhanh2_Hoan_Thanh_Nhan_Eff`<br>- `BonChua_Step_Nhan_Dich` | - Bất kỳ Nhánh 1 (PLC1) hoặc Nhánh 2 (PLC2 - truyền qua Modbus) báo hoàn thành, cụm bồn chứa ngay lập tức kích hoạt bước nhận dịch (`BonChua_Step_Nhan_Dich = TRUE`).<br>- Kích hoạt bơm chuyển nhánh 1 hoặc nhánh 2 tương ứng để bơm dịch xuống Bồn chứa 01. | |
| **10** | **Xử lý cảnh báo (Alarm & Safety)** | - `PLC1_Loi_Dry_Run`<br>- `PLC1_Loi_Dosing`<br>- `PLC1_Loi_Setpoint`<br>- `Coi_Bao_Dong` | - **Dry run:** Chạy bơm xả đáy bồn khi mức nước gần bằng 0 -> chốt lỗi dry run.<br>- **Dosing lỗi:** Mở van cấp nước nhưng không có lưu lượng sau 5s -> chốt lỗi dosing.<br>- **Setpoint lỗi:** Nhập giá trị SP bằng 0 hoặc rỗng -> chốt lỗi setpoint.<br>- Các lỗi này đều kích hoạt `Coi_Bao_Dong` và khóa chu trình chạy tự động. | |

---

## 2. CHẨN ĐOÁN TRẠNG THÁI SEQUENCE (STATE MACHINE DIAGNOSTICS)

Mã trạng thái của PLC1 (`PLC1_State`) và PLC2 (`PLC2_State`) hiển thị số bước hiện tại của máy trạng thái tự động tuần tự:

| Mã trạng thái (State) | Tên bước (Step Name) | Thiết bị tác động chính | Điều kiện chuyển tiếp (Transition Condition) |
| :---: | :--- | :--- | :--- |
| **0** | **Chờ lệnh (IDLE)** | Không | Nhấn nút **Start** (`Nut_Khoi_Dong_Eff = TRUE`) và setpoint hợp lệ. |
| **10** | **Dosing nước** | Van cấp nước mở, van xả đóng | Cân lượng nước tích lũy (`_Eff`) đạt giá trị Setpoint HMI. |
| **11** | **Tip cốt/phụ gia** | Motor dịch chuyển phễu | Cờ báo đã hoàn tất tip (`AI_*_Tip_*_Xong_HMI = TRUE`). |
| **12** | **Khuấy** | Motor cánh khuấy chạy thuận | Hết thời gian khuấy cài đặt (`HMI_SP_Time_Khuay_*`). |
| **15** | **Xả trung gian** (Bon 1/3) | Van xả đáy bồn 1/3 mở | Cảm biến mức báo bồn cạn (`_Eff <= 0.5`). |
| **20** | **Dosing bổ sung** | Van cấp nước bồn 2/4 mở | Cân lượng nước bổ sung đạt setpoint. |
| **21** | **Tip phụ gia** (Bon 2/4) | Motor dịch chuyển phễu phụ | Cờ báo hoàn tất tip phụ gia bằng TRUE. |
| **22** | **Khuấy thuận** (Bon 2/4) | Cánh khuấy quay thuận | Hết thời gian khuấy chiều thuận (`HMI_SP_Time_Fwd`). |
| **23** | **Khuấy ngược** (Bon 2/4) | Cánh khuấy quay ngược | Hết thời gian khuấy chiều ngược (`HMI_SP_Time_Rev`). |
| **30** | **Gia nhiệt PID** | Khối PID chuyển Auto, van nhiệt mở | Nhiệt độ bồn đạt setpoint gia nhiệt (`TT3208_Bon2_Eff >= SP`). |
| **31** | **Thanh trùng** | Van hơi duy trì nhiệt độ | Hết thời gian giữ nhiệt thanh trùng (`HMI_SP_Time_Sterilize`). |
| **40** | **Xả thành phẩm** (PLC1) | Bơm chuyển nhánh, van xả mở | Cảm biến mức bồn 2 báo bồn cạn (`_Eff <= 0.5`). |

---

## 3. KHẮC PHỤC SỰ CỐ KHÓA LIÊN ĐỘNG AN TOÀN (LOCKOUT TROUBLESHOOTING)

> [!WARNING]
> Nếu bạn nhấn Start nhưng hệ thống không chạy (`PLC1_State` hoặc `PLC2_State` đứng im tại `0`), hoặc cờ lỗi tổng hợp `PLC1_Loi_Tong` hiển thị `TRUE`, hệ thống đã kích hoạt khóa liên động an toàn (Lockout).

### Nguyên nhân phổ biến:
1. **Lỗi Setpoint (`AI_*_Loi_Setpoint = TRUE`):** Do các giá trị setpoint lưu lượng dosing, tốc độ khuấy, nhiệt độ hoặc thời gian bằng `0.0` hoặc rỗng khi nhấn Start.
2. **Dừng khẩn chốt (`AI_*_EStop_Latch = TRUE`):** Do nút nhấn dừng khẩn vật lý (%I0.3) hoặc HMI chưa được giải phóng.
3. **Dosing lỗi (`AI_*_Loi_Dosing = TRUE`):** Do van cấp nước mở quá 5 giây (theo đúng yêu cầu đề thi) nhưng cảm biến lưu lượng hiệu dụng không phản hồi.

### Các bước khôi phục (Reset Lockout):
1. **Bước 1: Nạp Recipe mặc định từ HMI**
   - Tìm tag `HMI_Load_Default_Recipe` (%M340.2) trong Watch Table.
   - Gán (Force/Modify) giá trị này lên `TRUE`.
   - Hệ thống sẽ tự động ghi các setpoint mặc định hợp lệ vào các bồn.
2. **Bước 2: Xử lý nút E-Stop**
   - Đảm bảo tag dừng khẩn vật lý và HMI đã được trả về trạng thái bình thường (E-Stop vật lý `%I0.3 = TRUE` - trạng thái NC - thường đóng).
3. **Bước 3: Nhấn nút Reset lỗi**
   - Kích hoạt xung `Nut_Reset_Eff = TRUE` (hoặc nhấn nút Reset vật lý `%I0.2` hoặc HMI `HMI_Reset_Alarm = TRUE`).
   - Cờ lỗi tổng hợp `PLC1_Loi_Tong` / `PLC2_Loi_Tong` sẽ tắt (về `FALSE`), các cờ lỗi thành phần bị xóa.
4. **Bước 4: Nhấn Start**
   - Kích hoạt xung `Nut_Khoi_Dong_Eff = TRUE`. Máy trạng thái sequence sẽ khởi chạy tuần tự từ trạng thái 0 lên trạng thái 10.
