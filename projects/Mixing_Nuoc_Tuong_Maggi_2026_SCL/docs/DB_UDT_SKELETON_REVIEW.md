# ĐÁNH GIÁ VÀ ĐẶC TẢ UDT/DB SKELETON (DB_UDT_SKELETON_REVIEW.md)

Tài liệu này đánh giá chi tiết cấu trúc các kiểu dữ liệu tự định nghĩa (UDT) và các khối dữ liệu (DB) đã được xây dựng dưới dạng SCL skeleton cho dự án `projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL`. 

---

## 1. Xác Nhận Phạm Vi Lượt Thực Hiện
*   **Mã nguồn logic vận hành:** Lượt này **CHỈ** dựng khung khai báo dữ liệu (UDT, DB skeleton) và thiết lập các giá trị mặc định ban đầu an toàn. Tuyệt đối **KHÔNG** viết logic vận hành tuần tự, không viết logic OB1, FB Grafcet, Modbus RTU/TCP call, hay các khối FC phụ trợ.
*   **Gắn kết TIA Portal:** Không thực hiện import TIA, không biên dịch trên TIA Portal, không chỉnh sửa file HMI XML, và không sửa đổi bất kỳ mã nguồn Ladder cũ nào.
*   **Nguyên tắc không dùng tiền tố `AI_`:** Đã tuân thủ 100%. Toàn bộ UDT, DB và các biến bên trong đều sử dụng tên chuẩn ASCII không dấu, không có tiền tố `AI_` (chỉ dùng các tên như `Nut_Start_Physical`, `Bon1`, `Khuay_Chay`).

---

## 2. Danh Sách Các UDT và DB SCL Đã Tạo

### Các tệp cấu trúc kiểu dữ liệu (UDT) - Thư mục `udt/`
1.  **[UDT_Tank.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_Tank.scl):**
    *   *Mục đích:* Quản lý trạng thái cánh khuấy (lệnh chạy, phản hồi, tốc độ cài đặt/phản hồi, đảo chiều), trạng thái các van xả đáy (1, 2, 3), van cấp nước (hoặc van hơi/van làm mát đối với các bồn gia nhiệt), các giá trị đo lường mức/nhiệt độ thực tế, cờ trạng thái chu trình và các biến mô phỏng tích lũy nội bộ.
2.  **[UDT_PID_Channel.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_PID_Channel.scl):**
    *   *Mục đích:* Chứa các biến điều phối của bộ điều khiển `PID_Compact` Siemens (Enable, Setpoint, PV, CV, Status, Manual_Mode, Manual_Value, Mode). Thiết kế để ghi `3` (Auto) hoặc `0` (Inactive) vào chân `sRet.i_Mode` của khối PID chuẩn.
3.  **[UDT_VFD_ATV12.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_VFD_ATV12.scl):**
    *   *Mục đích:* Lưu trữ các thanh ghi Modbus RTU của biến tần Altivar 12 (Control Word, FreqSetpoint, StatusWord, FreqFeedback) và các biến điều phối trạng thái đệm cho khối `MB_MASTER` (Step, Req, Mode, DataAddr, DataLen, Busy, Error, Status).
4.  **[UDT_ModbusTCP_Link.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_ModbusTCP_Link.scl):**
    *   *Mục đích:* Chứa các cờ trạng thái khối MB_CLIENT/MB_SERVER, các từ bắt tay gửi nhận (`CmdSeq`, `AckSeq`), watchdog truyền thông giám sát kết nối và mảng Holding Registers `Array[0..19] of Word` để truyền nhận chéo giữa hai PLC.
5.  **[UDT_HMI_Data.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_HMI_Data.scl):**
    *   *Mục đích:* Gom nhóm tất cả các nút nhấn điều khiển hệ thống, từ trạng thái lỗi, cờ an toàn, và các từ vẽ đồ họa hình động (Animation) cho mức dịch bồn chứa (0..100) trên WinCC.
6.  **[UDT_Recipe.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_Recipe.scl):**
    *   *Mục đích:* Định nghĩa các tham số cài đặt công nghệ bao gồm lượng nước cấp, tốc độ cánh khuấy cài đặt, nhiệt độ gia nhiệt PID mục tiêu, thời gian chạy các bước và ngưỡng bảo vệ áp suất tối đa.
7.  **[UDT_SystemStatus.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_SystemStatus.scl):**
    *   *Mục đích:* Quản lý các chế độ vận hành chung của toàn hệ thống (Manual, Auto, E-Stop, Safety Gate, Alarm, PLC Heartbeat).

### Các tệp khối dữ liệu (DB) - Thư mục `db/`
1.  **[DB_HMI.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_HMI.scl):**
    *   *Mục đích:* Chứa dữ liệu giao tiếp với màn hình WinCC HMI (SCADA). Sử dụng thuộc tính truy cập tối ưu hóa `{ S7_Optimized_Access := 'True' }`.
2.  **[DB_Recipe.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_Recipe.scl):**
    *   *Mục đích:* Lưu trữ công thức tích cực (Active Recipe) và công thức mặc định khởi tạo của hệ thống.
3.  **[DB_Operation.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_Operation.scl):**
    *   *Mục đích:* Chứa trạng thái làm việc chi tiết của 4 bồn chính (`Bon1` -> `Bon4`), 2 bồn chứa phụ trợ (`BonChua1`, `BonChua2`), cảm biến phễu rót, các bộ PID nhiệt độ và các cờ phân quyền/khóa liên động đường xả.
4.  **[DB_Comms.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_Comms.scl):**
    *   *Mục đích:* Vùng đệm truyền thông Modbus TCP/RTU. Sử dụng thuộc tính chuẩn `{ S7_Optimized_Access := 'False' }` (Non-Optimized) để đảm bảo độ lệch địa chỉ byte cố định nhằm tránh lỗi `16#80B6`. Khai báo sẵn các biến kết nối dạng `TCON_IP_v4` với giá trị Start Value chuẩn.
5.  **[DB_RealIO_Map.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_RealIO_Map.scl):**
    *   *Mục đích:* Lưu trữ đệm các ngõ vào/ra vật lý thật của Variant B để map với PLC Tags ở đầu và cuối vòng quét.

---

## 3. Phân Định Real_IO vs. Sim_IO trong Thiết Kế Mới

Dựa trên cấu hình phần cứng Variant B (2 PLC đấu nối thật), chúng ta phân chia rạch ròi các biến như sau:

| Tên Thiết Bị / Tín Hiệu | Địa Chỉ Vật Lý | Loại I/O | Kênh Trao Đổi / Khối Xử Lý | Ghi Chú |
| :--- | :--- | :---: | :--- | :--- |
| **Nút Start vật lý** | `%I0.0` | Real_IO | `DB_RealIO_Map.Nut_Start_Physical` | Đọc ở đầu OB1 |
| **Nút Stop vật lý** | `%I0.1` | Real_IO | `DB_RealIO_Map.Nut_Stop_Physical` | Đọc ở đầu OB1 |
| **Nút Reset vật lý** | `%I0.2` | Real_IO | `DB_RealIO_Map.Nut_Reset_Physical` | Đọc ở đầu OB1 |
| **Nút E-Stop vật lý** | `%I0.3` | Real_IO | `DB_RealIO_Map.Nut_EStop_Physical` | Thường đóng, đọc ở đầu OB1 |
| **Phao báo đầy Bồn 1** | `%I0.4` | Real_IO | `DB_RealIO_Map.LS3202_Bon1_Cao_Physical` | Chỉ có trên PLC1 |
| **Phao báo đầy Bồn 4** | `%I0.5` | Real_IO | `DB_RealIO_Map.LS3217_Bon4_Cao_Physical` | Chỉ có trên PLC2 |
| **Phao báo cao phễu rót**| `%I0.6` | Real_IO | `DB_RealIO_Map.LSH3310_Pheu_Cao_Physical` | Chỉ có trên PLC1 |
| **Phao báo thấp phễu rót**| `%I0.7` | Real_IO | `DB_RealIO_Map.LSL3311_Pheu_Thap_Physical`| Chỉ có trên PLC1 |
| **Contactor VFD Bồn 2** | `%Q0.0` | Real_IO | `DB_RealIO_Map.VFD_Bon2_Contactor` | Ghi ở cuối OB1 PLC1 |
| **Biến tần ATV12 (Bồn 2)**| Modbus RTU | Real_IO | `DB_Comms.VFD_Bon2` (Addr 8501, 8502, 3201, 3202) | RS485 qua khối `MB_MASTER` |
| **Các cảm biến đo LT/TT**| Không gán %I| Sim_IO  | `DB_Operation.BonX.Muc_Dich_PV` / `Nhiet_Do_PV` | Không gán %I, cập nhật ảo qua DB |
| **Các van xả/van cấp**  | Không gán %Q| Sim_IO  | `DB_Operation.BonX.Van_Xa_Day_Y` / `Van_Cap_Nuoc` | Không gán %Q, điều khiển ảo qua DB |

---

## 4. Ánh Xạ Biến Cũ (LAD Legacy Tag) Sang Cấu Trúc DB Mới

Dưới đây là bảng ánh xạ sơ bộ các tag chính từ dự án Ladder cũ sang các biến thành phần trong các DB mới của SCL:

| Tên Tag Cũ (Ladder) | Địa Chỉ Cũ | Biến DB Mới (SCL-First) | Vị Trí Trong DB | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| `AI_Nut_Khoi_Dong` | `%I0.0` | `Nut_Start_Physical` | `DB_RealIO_Map` | Nút nhấn Start vật lý |
| `AI_Nut_Dung` | `%I0.1` | `Nut_Stop_Physical` | `DB_RealIO_Map` | Nút nhấn Stop vật lý |
| `AI_Nut_Reset` | `%I0.2` | `Nut_Reset_Physical` | `DB_RealIO_Map` | Nút nhấn Reset vật lý |
| `AI_Nut_EStop` | `%I0.3` | `Nut_EStop_Physical` | `DB_RealIO_Map` | Nút EStop vật lý |
| `AI_VFD_Bon2_Contactor`| `%Q0.0` | `VFD_Bon2_Contactor` | `DB_RealIO_Map` | Contactor nguồn biến tần |
| `AI_LT3203_Bon1` | `%ID108` | `Bon1.Muc_Dich_PV` | `DB_Operation` | Cảm biến báo mức Bồn 1 |
| `AI_TT3204_Bon1` | `%ID112` | `Bon1.Nhiet_Do_PV` | `DB_Operation` | Cảm biến nhiệt độ Bồn 1 |
| `AI_LT3209_Bon2` | `%ID124` | `Bon2.Muc_Dich_PV` | `DB_Operation` | Cảm biến báo mức Bồn 2 |
| `AI_TT3208_Bon2` | `%ID128` | `Bon2.Nhiet_Do_PV` | `DB_Operation` | Cảm biến nhiệt độ Bồn 2 |
| `AI_LT3213_Bon3` | `%ID140` | `Bon3.Muc_Dich_PV` | `DB_Operation` | Cảm biến báo mức Bồn 3 |
| `AI_TT3214_Bon3` | `%ID144` | `Bon3.Nhiet_Do_PV` | `DB_Operation` | Cảm biến nhiệt độ Bồn 3 |
| `AI_LT3218_Bon4` | `%ID156` | `Bon4.Muc_Dich_PV` | `DB_Operation` | Cảm biến báo mức Bồn 4 |
| `AI_TT3219_Bon4` | `%ID160` | `Bon4.Nhiet_Do_PV` | `DB_Operation` | Cảm biến nhiệt độ Bồn 4 |
| `AI_LT3302_BonChua1` | `%ID164` | `BonChua1.Muc_Dich_PV` | `DB_Operation` | Mức dịch Bồn chứa 1 |
| `AI_LT3307_BonChua2` | `%ID176` | `BonChua2.Muc_Dich_PV` | `DB_Operation` | Mức dịch Bồn chứa 2 |
| `AI_AGTR3260_Khuay_Bon1`| `%Q0.1` | `Bon1.Khuay_Chay` | `DB_Operation` | Động cơ khuấy Bồn 1 (Sim_IO) |
| `AI_V3232_Xa_Bon1` | `%Q0.2` | `Bon1.Van_Xa_Day_1` | `DB_Operation` | Van xả đáy 1 Bồn 1 (Sim_IO) |
| `AI_V3235_Nuoc_Bon2` | `%Q0.5` | `Bon2.Van_Cap_Nuoc` | `DB_Operation` | Van nước cấp Bồn 2 (Sim_IO) |
| `AI_CV3206_Hoi_Bon2` | `%QD108` | `Bon2.Van_Cap_Hoi` | `DB_Operation` | Độ mở van hơi Bồn 2 (Sim_IO) |
| `AI_PID_Bon2_Enable` | `%M412.0` | `PID_Bon2.Enable` | `DB_Operation` | Kích hoạt PID Bồn 2 |
| `AI_PID_Bon2_SP` | `%MD416` | `PID_Bon2.Setpoint` | `DB_Operation` | Setpoint nhiệt độ PID Bồn 2 |
| `AI_PID_Bon2_PV` | `%MD420` | `PID_Bon2.PV` | `DB_Operation` | Phản hồi nhiệt độ PID Bồn 2 |
| `AI_PID_Bon2_CV` | `%MD424` | `PID_Bon2.CV` | `DB_Operation` | Ngõ ra điều khiển PID Bồn 2 |
| `AI_HMI_Nut_Khoi_Dong`| `%M110.0` | `HMI.Nut_Khoi_Dong` | `DB_HMI` | Nút nhấn khởi động từ HMI |
| `AI_HMI_SP_PLC1_Nuoc_Bon1`| `%MD224` | `Recipe.SP_Nuoc_Bon1` | `DB_HMI` / `DB_Recipe` | Setpoint nước cấp Bồn 1 |
| `AI_HMI_SP_PLC1_Toc_Do_Bon1`| `%MD240` | `Recipe.SP_Toc_Do_Bon1` | `DB_HMI` / `DB_Recipe` | Setpoint tốc độ Bồn 1 |

---

## 5. Các Điểm Chưa Chắc Chắn Cần Codex Phê Duyệt Trước Khi Lập Trình Logic

1.  **Cú pháp khai báo biến `TCON_IP_v4`:**
    *   *Chi tiết:* Chúng tôi đã sử dụng trực tiếp kiểu dữ liệu hệ thống `TCON_IP_v4` cho các biến kết nối Modbus TCP. Khi import vào TIA Portal V18, TIA sẽ tự động nhận diện kiểu này vì nó là kiểu dữ liệu tích hợp của Siemens. Tuy nhiên, nếu CPU đích chưa cài đặt thư viện Modbus TCP hoặc cấu hình phần cứng khác biệt, có thể phát sinh lỗi biên dịch.
    *   *Đề xuất:* Đặt giá trị mặc định cho cấu trúc này bằng Start Value chuẩn giống như mã đã khai báo trong `DB_Comms.scl`.
2.  **Khối ngắt chu kỳ (Cyclic Interrupt OB30/OB31) gọi PID:**
    *   *Chi tiết:* Theo thiết kế, `PID_Compact` phải được gọi trong các OB ngắt chu kỳ (ví dụ `OB30_PID_Bon2` chạy mỗi 100ms) để giải thuật tích phân hoạt động chính xác. Khối SCL skeleton hiện tại chỉ thiết lập cấu trúc DB điều phối (`DB_Operation.PID_Bon2`). Việc gọi khối instance thực tế của PID (`PID_Compact_Bon2_DB`) sẽ được cấu hình khi import và viết OB30/OB31 ở nhiệm vụ tiếp theo.
3.  **Tách biệt Variant A và Variant B trên DB:**
    *   *Chi tiết:* Để tránh trùng lặp mã nguồn, chúng tôi thiết kế các DB dùng chung (`DB_HMI`, `DB_Recipe`, `DB_Operation`, `DB_Comms`) chứa đầy đủ các trường thông tin cho cả 4 bồn và cả 2 chế độ (Modbus RTU, Modbus TCP).
    *   *Đề xuất:* Khi lập trình logic vận hành, với Variant A (1 PLC) sẽ bỏ qua phần truyền thông Modbus trong `DB_Comms` và chỉ xử lý nội bộ, còn Variant B sẽ kích hoạt đầy đủ các bộ điều khiển Modbus RTU/TCP. Cách tiếp cận này giúp giữ cấu trúc DB đồng nhất giữa hai PLC và giao diện HMI.

---

## 6. Xác Nhận Cuối Cùng
Chúng tôi xác nhận không viết bất kỳ dòng mã logic vận hành thực tế nào (case-sequence, vòng quét, tính toán điều khiển PID, truyền thông thực tế) trong các tệp tin UDT và DB skeleton đã tạo.
Các tệp SCL đã được lưu trữ đúng vị trí quy định và sẵn sàng cho các nhiệm vụ tiếp theo sau khi được phê duyệt.
