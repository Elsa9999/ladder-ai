# HƯỚNG DẪN IMPORT TIA PORTAL V18 - READY 80%
 DỰ ÁN: MIXING NƯỚC TƯƠNG MAGGI 2026

Tài liệu này hướng dẫn chi tiết từng bước để import các file SimaticML XML đã sinh vào phần mềm TIA Portal V18, giải quyết liên kết, cấu hình PID Compact và liên kết màn hình HMI WinCC Advanced.

---

## 1. Thiết lập Hardware & Cấu hình CPU ban đầu
1. **Tạo Project mới:**
   - Mở TIA Portal V18, tạo một project mới tên: `Mixing_Nuoc_Tuong_Maggi_2026`.
2. **Thêm các CPU:**
   - Thêm CPU thứ nhất (PLC1): **S7-1200 CPU 1214C DC/DC/DC** (Mã hàng ví dụ: `6ES7 214-1AG40-0XB0` V4.6). Đặt tên là `PLC_1_Mixing`.
   - Thêm CPU thứ hai (PLC2): **S7-1200 CPU 1214C DC/DC/DC** (Mã hàng ví dụ: `6ES7 214-1AG40-0XB0` V4.6). Đặt tên là `PLC_2_Mixing`.
3. **Cấu hình địa chỉ IP:**
   - Vào cấu hình cổng Ethernet PROFINET của từng CPU:
     - **PLC1:** IP `192.168.0.1`, Subnet mask `255.255.255.0`.
     - **PLC2:** IP `192.168.0.2`, Subnet mask `255.255.255.0`.
4. **Kích hoạt System & Clock Memory Bytes:**
   - Chọn Properties của từng CPU -> Click **System and clock memory**:
     - Tích chọn **Enable the use of system memory byte** -> Đặt địa chỉ **MB101** (`FirstScan` tại `%M101.0`).
     - Tích chọn **Enable the use of clock memory byte** -> Đặt địa chỉ **MB100** (`Clock_1Hz` tại `%M100.5`).

---

## 2. Thứ tự Import XML cho PLC1 (`PLC_1_Mixing`)
Mở cây thư mục của `PLC_1_Mixing` và thực hiện import các file XML nằm trong thư mục `tia_import/PLC_1_Mixing_Import/` theo đúng thứ tự sau để tránh lỗi thiếu reference:

1. **PLC_Tags.xml** (Import vào mục **PLC tags** -> **Show all tags** bằng chức năng Import).
2. **Timers_PLC1.xml** (Import vào **Program blocks** để tạo DB chứa các timer).
3. **DB_PLC1_Send_To_PLC2_DB.xml** (Import vào **Program blocks** - DB gửi Modbus).
4. **DB_PLC1_Recv_From_PLC2_DB.xml** (Import vào **Program blocks** - DB nhận Modbus).
5. **FC_Init_Default_Recipe_PLC1.xml** (Import vào **Program blocks** -> FC khởi tạo).
6. **FC_HMI_Mirror_PLC1.xml** (Import vào **Program blocks** -> FC ánh xạ HMI).
7. **FC_PLC1_Mixing.xml** (Import vào **Program blocks** -> FC điều khiển chính Bồn 1-2).
8. **FC_Bon_Chua_Loc.xml** (Import vào **Program blocks** -> FC điều khiển Bồn chứa & Lọc).
9. **FC_HMI_Animation_PLC1.xml** (Import vào **Program blocks** -> FC animation cánh khuấy Bồn 1-2, block ID 60).
10. **Main.xml** (Import đè hoặc chép nội dung mạng vào **OB1**).
11. **OB30_PID_PLC1_Bon2.xml** (Import vào **Program blocks** -> OB ngắt chu kỳ cho PID Bồn 2).

---

## 3. Thứ tự Import XML cho PLC2 (`PLC_2_Mixing`)
Mở cây thư mục của `PLC_2_Mixing` và thực hiện import các file XML nằm trong thư mục `tia_import/PLC_2_Mixing_Import/` theo đúng thứ tự:

1. **PLC_Tags.xml** (Import vào mục **PLC tags** -> **Show all tags**).
2. **Timers_PLC2.xml** (Import vào **Program blocks** - DB chứa timer cho PLC2).
3. **DB_Modbus_Holding_Register_DB.xml** (Import vào **Program blocks** - DB Holding registers lưu data truyền thông).
4. **FC_Init_Default_Recipe_PLC2.xml** (Import vào **Program blocks** -> FC khởi tạo).
5. **FC_HMI_Mirror_PLC2.xml** (Import vào **Program blocks** -> FC ánh xạ HMI).
6. **FC_PLC2_Mixing.xml** (Import vào **Program blocks** -> FC điều khiển chính Bồn 3-4).
7. **FC_HMI_Animation_PLC2.xml** (Import vào **Program blocks** -> FC animation cánh khuấy Bồn 3-4, block ID 61).
8. **Main.xml** (Import đè hoặc chép nội dung mạng vào **OB1**).
9. **OB31_PID_PLC2_Bon4.xml** (Import vào **Program blocks** -> OB ngắt chu kỳ cho PID Bồn 4).

---

## 4. Xử lý & Cấu hình PID Compact (Technology Objects)
Sau khi import, nếu TIA Portal báo lỗi thiếu các instance block của PID hoặc OB báo đỏ:

1. **Tại PLC1 (OB30):**
   - Click chuột phải vào **Technology objects** -> **Add new object** -> Chọn **PID Control** -> **PID_Compact**.
   - Đặt tên chính xác là: **PID_Compact_1**.
   - **Bắt buộc chọn Version 1.2** để tương thích với cấu trúc XML của dự án.
2. **Tại PLC2 (OB31):**
   - Click chuột phải vào **Technology objects** -> **Add new object** -> Chọn **PID Control** -> **PID_Compact**.
   - Đặt tên chính xác là: **PID_Compact_2**.
   - **Bắt buộc chọn Version 1.2**.
3. **Cấu hình Cyclic Interrupt:**
   - Khi tạo OB30 và OB31, TIA Portal sẽ hỏi chu kỳ gọi (Cycle time):
     - Đặt chu kỳ cho cả OB30 (PLC1) và OB31 (PLC2) là **100 ms** (hoặc `100000 µs`).

---

## 5. Thiết lập HMI WinCC Advanced
1. **Thêm thiết bị HMI:**
   - Thêm một trạm HMI **WinCC Comfort/Advanced** (ví dụ: màn hình Comfort 12 inch `TP1200 Comfort`).
2. **Kết nối HMI:**
   - Tạo kết nối HMI (HMI Connection) trỏ về **PLC1** (CPU 192.168.0.1) làm PLC chính để thu thập và hiển thị toàn bộ hệ thống.
3. **Import/Bind Tags:**
   - Bind toàn bộ tag của PLC1 sang HMI, tập trung vào các nhóm tag chính:
     - `HMI_*` (Lệnh an toàn, phân quyền, giả lập và nút nhấn HMI).
     - `System_Mode_*` (Chế độ Sim / Real hiển thị trên tiêu đề).
     - `PID_Bon2_*` (Thông số PID bồn 2).
     - `PID_Bon4_*_Recv` (Thông số PID bồn 4 nhận từ PLC2 qua Modbus).
     - Các tag cảnh báo trạng thái an toàn: `HMI_Alarm_Status`, `HMI_AnToan_Status`.
4. **Tạo các màn hình HMI (Tối thiểu 5 màn hình):**
   - **Màn hình 1 - Overview (Tổng quan):** Hiển thị sơ đồ công nghệ (P&ID) của cả 4 bồn, đường ống, các van, bơm chính kèm màu sắc hoạt động (xanh: chạy, xám: dừng, đỏ: lỗi). Hiển thị trạng thái hoàn thành mẻ chung.
   - **Màn hình 2 - PLC1 / Bồn 1-2 (Nhánh 1):** Sơ đồ chi tiết Bồn 1 và Bồn 2. Hiển thị mức bồn, nhiệt độ, các bước chu trình của Nhánh 1, và điều khiển tay (Manual) cho các van xả, cánh khuấy của nhánh này.
   - **Màn hình 3 - PLC2 / Bồn 3-4 (Nhánh 2):** Sơ đồ chi tiết Bồn 3 và Bồn 4. Hiển thị mức bồn, nhiệt độ mô phỏng, các bước chu trình của Nhánh 2, điều khiển bơm chuyển nhánh, nút bấm mô phỏng các cảm biến.
   - **Màn hình 4 - PID Trend (Đồ thị PID):** Đồ thị thời gian thực gồm 3 đường tuyến tính: Setpoint (SP), Process Value (PV) và Control Value (CV) cho cả PID Bồn 2 và PID Bồn 4.
   - **Màn hình 5 - Alarm / Manual (Cảnh báo & Vận hành tay):** Bảng hiển thị cảnh báo hoạt động (Alarm View), nút bấm Reset/Ack lỗi, và giao diện đăng nhập phân quyền (Operator / Engineer / Admin).

---

## 6. Cấu hình Text Lists cho HMI
Import hoặc tạo thủ công WinCC Text Lists dựa trên các file XML tương ứng:

1. **Hmi.TextList.TL_Mixing_Step.xml** -> Tạo Text list `TL_Mixing_Step`:
   - `0`: Chờ lệnh
   - `10`: Dosing nước
   - `11`: Tip nguyên liệu
   - `12`: Khuấy ban đầu
   - `15`: Xả sang bồn kế tiếp
   - `20`: Dosing bổ sung
   - `21`: Tip phụ gia
   - `22`: Khuấy chiều thuận
   - `23`: Khuấy chiều ngược
   - `30`: PID gia nhiệt/điều khiển
   - `31`: Giữ thanh trùng
   - `50`: Bồn chứa 01 nhận dịch
   - `60`: Giải nhiệt
   - `70`: Chuyển sang Bồn chứa 02
   - `80`: Lọc CCP và chiết rót
2. **Hmi.TextList.TL_Canh_Bao_Mixing.xml** -> Tạo Text list `TL_Canh_Bao_Mixing`:
   - `0`: [AN TOÀN] Không có cảnh báo
   - `1`: [DOSING] Van mở nhưng lưu lượng không tăng
   - `2`: [SETPOINT] Giá trị setpoint không hợp lệ
   - `3`: [KHÓA AN TOÀN] Dry run hoặc liên động bảo vệ
   - `4`: [ESTOP ACTIVE] Dừng khẩn đang được chốt
3. **Hmi.TextList.TL_Phan_Quyen.xml** -> Tạo Text list `TL_Phan_Quyen`:
   - `0`: Chưa đăng nhập
   - `1`: Operator - Start/Stop, Ack Alarm, xem màn hình
   - `2`: Engineer - sửa thông số, manual, reset alarm
   - `3`: Admin - toàn quyền
