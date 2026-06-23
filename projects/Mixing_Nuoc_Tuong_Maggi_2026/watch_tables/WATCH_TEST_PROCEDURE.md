# Quy Trình Kiểm Thử Ngoại Tuyến Qua Watch Table (WATCH_TEST_PROCEDURE)

Tài liệu này hướng dẫn chi tiết cách kiểm thử từng bộ điều khiển PLC1 và PLC2 độc lập trong TIA Portal / PLCSIM thường (không cần kết nối truyền thông Modbus TCP thực tế giữa 2 PLC và không yêu cầu phần cứng/HMI thực tế).

> [!IMPORTANT]
> **Lưu ý về PLCSIM thường:**
> PLCSIM thường không hỗ trợ truyền thông Modbus TCP qua lại giữa 2 PLC ảo. Do đó, để kiểm thử liên kết giữa PLC1 và PLC2 trên PLCSIM thường, chúng ta sử dụng các bảng **Watch Table giả lập** để nhập tay dữ liệu nhận được như thể tín hiệu được truyền qua mạng.
> Đồng thời, các bước chuyển trạng thái trung gian (như Tip phụ gia hay thời gian khuấy) đã được tự động hóa bằng bộ Timer TON nội bộ trong PLC. Tester không cần kích hoạt thủ công các nút nhấn ảo `*_Xong_HMI` như trước đây nữa.

---

## 1. Chuẩn Bị Trước Khi Kiểm Thử (Pre-requisites)

1. Mở dự án TIA Portal `cuocthi_tdh`.
2. Khởi động **PLCSIM thường** và nạp chương trình tương ứng vào PLC_1 và PLC_2.
3. Trong thư mục dự án TIA Portal của từng PLC, tạo các bảng Watch Table và copy-paste danh sách các tag tương ứng từ các tệp CSV trong thư mục `watch_tables/`:
   * **PLC_1:** 
     * `WT_PLC1_Main_Sequence` (từ [PLC1_Watch_Main_Sequence.csv](file:///d:/Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026/watch_tables/PLC1_Watch_Main_Sequence.csv))
     * `WT_PLC1_PID_VFD` (từ [PLC1_Watch_PID_VFD.csv](file:///d:/Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026/watch_tables/PLC1_Watch_PID_VFD.csv))
     * `WT_PLC1_Fake_PLC2_Modbus_Return` (từ [PLC1_Watch_Fake_PLC2_Modbus_Return.csv](file:///d:/Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026/watch_tables/PLC1_Watch_Fake_PLC2_Modbus_Return.csv))
   * **PLC_2:**
     * `WT_PLC2_Main_Sequence` (từ [PLC2_Watch_Main_Sequence.csv](file:///d:/Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026/watch_tables/PLC2_Watch_Main_Sequence.csv))
     * `WT_PLC2_PID_Sim` (từ [PLC2_Watch_PID_Sim.csv](file:///d:/Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026/watch_tables/PLC2_Watch_PID_Sim.csv))
     * `WT_PLC2_Fake_PLC1_Modbus_Command` (từ [PLC2_Watch_Fake_PLC1_Modbus_Command.csv](file:///d:/Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026/watch_tables/PLC2_Watch_Fake_PLC1_Modbus_Command.csv))
4. Chuyển các PLC sang chế độ **RUN** và bật chế độ giám sát (Monitor All) trên Watch Table.

---

## 2. Hướng Dẫn Kiểm Thử PLC1 Độc Lập (PLC1 Independent Testing)

Thực hiện kiểm thử tuần tự chu trình Nhánh 1 (Bồn 1 & Bồn 2) và cụm Bồn Chứa/Lọc từ State 0 trở lại 0.

### Bước 2.1: Khởi động & Kích hoạt chế độ mô phỏng
1. Trên bảng `WT_PLC1_Main_Sequence`, set các giá trị sau lên `True` và nhấn nút "Modify Now" (Ctrl+F12):
   * `HMI_Sim_Mode` = `True`
   * `HMI_Run_Enable` = `True`
   * `HMI_Use_Sim_Input_PLC1` = `True`
   * `HMI_Use_Sim_Input_BonChua` = `True`
2. Kích hoạt cờ nạp Recipe mặc định: set `HMI_Load_Default_Recipe` = `True` rồi `False` để nạp các Setpoint mặc định.
3. Quan sát các giá trị Setpoint thời gian và lưu lượng tự động được điền giá trị.

### Bước 2.2: Chạy Sequence Bồn 1 (State 0 -> 10 -> 11 -> 12 -> 15)
1. **State 0 (Idle):** Quan sát `PLC1_State` = `0`.
2. **State 10 (Dosing Bồn 1):** Set `Nut_Khoi_Dong_HMI` = `True` rồi `False` (tạo xung).
   * `PLC1_State` chuyển sang `10`.
   * Van nước `V3230_Nuoc_Bon1` mở (`True`).
   * Tăng dần giá trị đo mô phỏng lưu lượng `FQ3200_Bon1_HMI` lên `100.0`. Khi đạt `>= 100.0`, van đóng và tự động chuyển sang State 11.
3. **State 11 (Tip Bồn 1):** 
   * `PLC1_State` = `11`.
   * Sau 3 giây (timer `Timer_Tip_Bon1` chạy xong), sequence tự động chuyển sang `12`.
4. **State 12 (Khuấy Bồn 1):**
   * `PLC1_State` = `12`. Động cơ khuấy `AGTR3260_Khuay_Bon1` chạy.
   * Sau khi hết thời gian khuấy cài đặt (mặc định 5s), sequence tự động chuyển sang `15`.
5. **State 15 (Xả đáy Bồn 1 sang Bồn 2):**
   * `PLC1_State` = `15`. Các van xả đáy Bồn 1 mở.
   * Đưa mức bồn 1 về cạn bằng cách set mức mô phỏng `LT3203_Bon1_HMI` = `0.0`.
   * Nhánh 1 tự động hoàn tất xả Bồn 1 và chuyển sang State 20.

### Bước 2.3: Sequence Bồn 2 (State 20 -> 21 -> 22 -> 23 -> 30 -> 31 -> 40 -> 0)
1. **State 20 (Dosing bổ sung Bồn 2):**
   * `PLC1_State` = `20`. Van nước `V3235_Nuoc_Bon2` mở.
   * Tăng dần `FQ3205_Bon2_HMI` lên `120.0`. Đạt setpoint van nước đóng và chuyển sang `21`.
2. **State 21 (Tip phụ gia Bồn 2):**
   * `PLC1_State` = `21`. Sau 3 giây tip ảo tự động hoàn thành, chuyển sang `22`.
3. **State 22 (Khuấy thuận Bồn 2):**
   * `PLC1_State` = `22`. VFD khuấy `VFD_Bon2_Run` chạy thuận (`VFD_Bon2_Dao_Chieu` = `False`).
   * Sau khi hết thời gian chạy thuận (mặc định 5s), tự động chuyển sang `23`.
4. **State 23 (Khuấy ngược Bồn 2):**
   * `PLC1_State` = `23`. Động cơ chạy ngược (`VFD_Bon2_Dao_Chieu` = `True`).
   * Sau khi hết thời gian chạy ngược (mặc định 5s), tự động chuyển sang `30`.
5. **State 30 (Gia nhiệt PID Bồn 2):**
   * `PLC1_State` = `30`. Quan sát `PID_Bon2_Enable` = `True`.
   * Tăng dần nhiệt độ mô phỏng `TT3208_Bon2_HMI` lên `>= 75.0` (°C).
   * Khi nhiệt độ đạt, chu trình tự động chuyển sang `31`.
6. **State 31 (Thanh trùng / Giữ nhiệt Bồn 2):**
   * `PLC1_State` = `31`.
   * Sau khi hết thời gian giữ nhiệt (mặc định 5s), Nhánh 1 hoàn thành mẻ trộn, chuyển sang trạng thái chờ xả.

### Bước 2.4: Phân xử cụm Bồn Chứa & Xả đáy (State 40 -> 0)
1. **Owner Grant & Kích hoạt xả:**
   * Cụm bồn chứa đang rảnh, quyền sở hữu tự động cấp cho Nhánh 1 (`BonChua_State` chuyển sang `50`).
   * Bơm chuyển nhanh `Pump3264_Chuyen_Nhanh1` tự động chạy.
   * Các van xả đáy Bồn 2 (`V3235_Nuoc_Bon2` đóng, các van xả Bồn 2 mở) và `PLC1_State` chuyển sang `40` (Discharging).
2. **Kết thúc xả tự động (Auto-end):**
   * Giảm dần mức dung dịch bồn 2 mô phỏng `LT3209_Bon2_HMI` về `0.0`.
   * Khi `LT3209_Bon2_HMI` <= 0.5 (Bồn 2 cạn):
     * Quyền sở hữu được giải phóng.
     * Bơm dừng, van xả đóng.
     * PLC1 tự động quay về trạng thái IDLE (`PLC1_State` = `0`).

---

## 3. Hướng Dẫn Kiểm Thử PLC2 Độc Lập (PLC2 Independent Testing)

Vì PLC2 chạy ở chế độ Modbus TCP Server nhận lệnh từ PLC1, ta sử dụng bảng `WT_PLC2_Fake_PLC1_Modbus_Command` để nạp lệnh của PLC1.

### Bước 3.1: Khởi tạo chế độ mô phỏng PLC2
1. Trên bảng `WT_PLC2_Main_Sequence`, set cờ mô phỏng cảm biến:
   * `HMI_Sim_Mode` = `True`
   * `HMI_Use_Sim_Input_PLC2` = `True`
2. Tạo giả lập kết nối bằng cách duy trì thay đổi giá trị của Heartbeat gửi từ PLC1:
   * Nhập thay đổi liên tục giá trị `DB_Modbus_Holding_Register_DB.Heartbeat_Client` (ví dụ: 1, 2, 3...) sau mỗi vài giây trên bảng `WT_PLC2_Fake_PLC1_Modbus_Command` để tránh lỗi truyền thông `PLC2_Loi_Truyen_Thong`.

### Bước 3.2: Gửi lệnh Start từ PLC1 giả lập
1. Để kích hoạt chu trình tự động của PLC2:
   * Nhập lệnh Start: Set `DB_Modbus_Holding_Register_DB.Cmd_Start` = `True`.
   * Tăng giá trị Sequence number: Cộng 1 vào giá trị hiện tại của `DB_Modbus_Holding_Register_DB.CmdSeq`. Nhấn Modify (Ctrl+F12).
   * **Kết quả:** PLC2 nhận lệnh mới, `PLC2_State` chuyển sang `10` (Dosing Bồn 3).
   * Trả cờ lệnh `Cmd_Start` về `False` trên Watch Table (giống xung nút nhấn thực tế).

### Bước 3.3: Chạy Sequence PLC2 (State 10 -> 11 -> 12 -> 15 -> 20 -> 21 -> 22 -> 23 -> 30 -> 31 -> Complete)
1. **Dosing & Khuấy Bồn 3 (State 10 - 11 - 12):**
   * Tại `State 10`, tăng dần `FQ3210_Bon3_HMI` lên `>= 100.0`. State tự động chuyển sang `11`.
   * `State 11` (Tip) tự động đếm 3s chuyển sang `12`.
   * `State 12` (Khuấy) tự động đếm 5s chuyển sang `15`.
2. **Xả đáy Bồn 3 (State 15):**
   * Giảm dần `LT3213_Bon3_HMI` về `0.0`. Xả xong tự chuyển sang `20`.
3. **Dosing & Khuấy thuận nghịch Bồn 4 (State 20 - 21 - 22 - 23):**
   * Tại `State 20`, tăng dần `FQ3215_Bon4_HMI` lên `>= 120.0` -> tự chuyển sang `21`.
   * `State 21` (Tip) tự động đếm 3s chuyển sang `22`.
   * `State 22` (Khuấy thuận) tự động đếm 5s chuyển sang `23`.
   * `State 23` (Khuấy nghịch) tự động đếm 5s chuyển sang `30`.
4. **PID Mô phỏng & Sterilize Bồn 4 (State 30 - 31):**
   * Tại `State 30`, bạn có thể nhập cưỡng bức nhiệt độ mô phỏng trên Watch Table: set `TT3219_Bon4_HMI` = `96.0` (°C).
   * Khi nhiệt độ đạt, bước chuyển sang `31`.
   * `State 31` (Thanh trùng) tự động đếm 5s hoàn thành mẻ. Cờ `PLC2_Me_Nhanh2_Hoan_Thanh` tự động bật lên `True` (giá trị tương ứng trong `DB_Modbus_Holding_Register_DB.Done_Branch2` cũng được set lên `True`).

### Bước 3.4: Xả đáy Bồn 4
1. Khi PLC2 đã hoàn thành mẻ trộn, ta giả lập lệnh chạy bơm từ PLC1 gửi xuống:
   * Sét trực tiếp `Pump3265_Chuyen_Nhanh2` = `True` trong bảng `WT_PLC2_Main_Sequence`.
   * **Kết quả:** Bơm xả chạy và các van xả đáy Bồn 4 tự động mở.
2. Khi xả hết mức dung dịch Bồn 4 mô phỏng:
   * Set `LT3218_Bon4_HMI` = `0.0` (Bồn 4 cạn).
   * **Kết quả:** PLC2 tự động nhận biết xả xong, set cờ `PLC2_Xa_Bon4_Xong` = `True` (và `DB_Modbus_Holding_Register_DB.Done_Discharge2` = `True`), đồng thời quay trở về trạng thái IDLE (`State` = `0`), tắt bơm xả và đóng các van xả đáy.

---

## 4. Hướng Dẫn Giả Lập PLC2 Cho PLC1 (Faking PLC2 for PLC1)

Khi chạy thử PLC1 độc lập và đến bước cụm Bồn Chứa cần xả Nhánh 2, tester sử dụng bảng `WT_PLC1_Fake_PLC2_Modbus_Return` để mô phỏng sự phản hồi của PLC2:

1. **Giả lập kết nối sống (Heartbeat):** Thỉnh thoảng tăng giá trị của `DB_PLC1_Recv_From_PLC2_DB.Heartbeat` lên để tránh báo lỗi truyền thông PLC1.
2. **Giả lập hoàn thành mẻ Nhánh 2:** Khi PLC1 đang chờ Nhánh 2 hoàn thành để xả, set `DB_PLC1_Recv_From_PLC2_DB.Done_Branch2` = `True`.
   * Cờ `PLC2_Me_Nhanh2_Hoan_Thanh_Nhan` trên PLC1 sẽ lên `True`.
   * Cụm bồn chứa của PLC1 sẽ tự động cấp quyền sở hữu Nhánh 2: `BonChua_Owner_Nhanh2` = `True` và chạy bơm xả Nhánh 2.
3. **Giả lập xả xong Nhánh 2:** Khi đang bơm xả, set `DB_PLC1_Recv_From_PLC2_DB.Done_Discharge2` = `True`.
   * Cờ nhận tín hiệu xả xong `PLC2_Xa_Bon4_Xong_Nhan` sẽ lên `True`.
   * Cụm bồn chứa tự động hoàn tất nhận dịch Nhánh 2 và chuyển bước tiếp theo, đồng thời reset cờ sở hữu `BonChua_Owner_Nhanh2` về `False`.

---

## 5. Bảng Chẩn Đoán Lỗi Nhanh (`WT_PLC1_PID_VFD`)

Bảng này được cấu hình rút gọn tối đa chỉ dùng để **Debug lỗi hệ thống** khi cờ lỗi tổng `PLC1_Loi_Tong` = `True`.
Tester chỉ cần quan sát các tag lỗi sau để khoanh vùng nguyên nhân sự cố:
* `PLC1_EStop_Latch`: Lỗi dừng khẩn từ nút EStop.
* `PLC1_Loi_Dry_Run`: Lỗi chạy khô bơm Nhánh 1 (kích hoạt sau 2s khi bồn nguồn cạn mà bơm vẫn chạy).
* `PLC1_Loi_Dosing`: Lỗi quá thời gian dosing (kích hoạt sau 5s nếu lưu lượng đo được không tăng khi van nước mở).
* `PLC1_Loi_Truyen_Thong`: Lỗi mất truyền thông Modbus TCP PLC-PLC hoặc HMI.
* `PLC1_Loi_Setpoint` / `BonChua_Loi_Setpoint`: Các giá trị cài đặt công thức vượt quá giới hạn an toàn.
* `PID_Bon2_Error` / `PID_Bon2_ErrorBits`: Lỗi xảy ra trong khối hàm điều khiển nhiệt độ PID.
* `VFD_Bon2_MB_Error`: Lỗi truyền thông Modbus RTU đến biến tần khuấy Bồn 2.
