# ĐÁNH GIÁ VÀ ĐẶC TẢ UDT/DB SKELETON (DB_UDT_SKELETON_REVIEW.md)

Tài liệu này đánh giá chi tiết cấu trúc các kiểu dữ liệu tự định nghĩa (UDT) và các khối dữ liệu (DB) đã được xây dựng dưới dạng SCL skeleton cho dự án `projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL`.

---

## 1. Xác Nhận Phạm Vi Lượt Thực Hiện
*   **Mã nguồn logic vận hành:** Lượt này **CHỈ** dựng khung khai báo dữ liệu (UDT, DB skeleton) và thiết lập các giá trị mặc định ban đầu an toàn. Tuyệt đối **KHÔNG** viết logic vận hành tuần tự, không viết logic OB1, FB Grafcet, Modbus RTU/TCP call, hay các khối FC phụ trợ.
*   **Gắn kết TIA Portal:** Không thực hiện import TIA, không biên dịch trên TIA Portal, không chỉnh sửa file HMI XML, và không sửa đổi bất kỳ mã nguồn Ladder cũ nào.
*   **Nguyên tắc không dùng tiền tố `AI_`:** Đã tuân thủ 100% trong toàn bộ các file UDT/DB được tạo. Toàn bộ UDT, DB và các biến bên trong đều sử dụng tên chuẩn ASCII không dấu, không có tiền tố `AI_` (chỉ dùng các tên như `Nut_Start_Physical`, `Bon1`, `Khuay_Chay`).
*   **Lưu ý về tên lịch sử pre-migration:** Tiền tố `AI_` chỉ là tên lịch sử trong dự án cũ trước khi migration và **không được dùng làm nguồn mapping chính** hay dùng trong các khai báo mới.

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
    *   *Mục đích:* Lưu trữ đệm các ngõ vào/ra vật lý thật đã xác nhận của Variant B (các nút nhấn vật lý, contactor nguồn biến tần) để ánh xạ với PLC Tags ở đầu và cuối vòng quét OB1.

---

## 3. Phân Định Real_IO vs. Sim_IO trong Thiết Kế Mới

Theo nguyên tắc phân định nghiêm ngặt: Mọi van, cảm biến mức, cảm biến nhiệt độ, cảm biến lưu lượng, phao mức nếu chưa có bảng đấu nối xác nhận chính thức từ bản vẽ thi công đều phải được coi là **Sim_IO** (mô phỏng ảo trong DB). Chỉ những thiết bị vật lý thật đã được xác nhận mới nằm trong bảng Real_IO.

### A. Bảng Real_IO Xác Nhận (Được định nghĩa trong `DB_RealIO_Map.scl`)
Các ngõ vào/ra vật lý thật có đấu nối trực tiếp vào tủ điều khiển Variant B:

| Tên Thiết Bị / Tín Hiệu | Địa Chỉ Vật Lý | Loại I/O | Kênh Ánh Xạ Trong SCL | Ghi Chú |
| :--- | :--- | :---: | :--- | :--- |
| **Nút Start vật lý** | `%I0.0` | Real_IO | `DB_RealIO_Map.Nut_Start_Physical` | Đọc ở đầu OB1 PLC1 |
| **Nút Stop vật lý** | `%I0.1` | Real_IO | `DB_RealIO_Map.Nut_Stop_Physical` | Đọc ở đầu OB1 PLC1 |
| **Nút Reset vật lý** | `%I0.2` | Real_IO | `DB_RealIO_Map.Nut_Reset_Physical` | Đọc ở đầu OB1 PLC1 |
| **Nút E-Stop vật lý** | `%I0.3` | Real_IO | `DB_RealIO_Map.Nut_EStop_Physical` | Thường đóng, đọc ở đầu OB1 PLC1 |
| **Contactor VFD Bồn 2** | `%Q0.0` | Real_IO | `DB_RealIO_Map.VFD_Bon2_Contactor` | Ghi ở cuối OB1 PLC1 để cấp nguồn/enable ATV12 |
| **Biến tần ATV12 (Bồn 2)**| RS485/RTU | Real_IO | `DB_Comms.VFD_Bon2` | Truyền thông thanh ghi qua Modbus RTU |

### B. Nhóm Cảm Biến / Phao Chưa Xác Nhận (UNCONFIRMED_OPTIONAL_IO)
Các tín hiệu dưới đây là phao cơ học trong dự án cũ nhưng **chưa có bảng đấu nối xác nhận chính thức cho Variant B**. Do đó, chúng được đưa ra khỏi `DB_RealIO_Map` và xử lý như các biến mô phỏng ảo (Sim_IO) trong `DB_Operation`/`DB_HMI`:

*   `LS3202_Bon1_Cao` (Phao báo đầy Bồn 1)
*   `LS3217_Bon4_Cao` (Phao báo đầy Bồn 4)
*   `LSH3310_Pheu_Cao` (Phao báo cao phễu rót)
*   `LSL3311_Pheu_Thap` (Phao báo thấp phễu rót)

### C. Nhóm Sim_IO Mặc Định (Xử lý hoàn toàn trong DB)
Tất cả các van cấp/xả, cảm biến mức liên tục LT, cảm biến nhiệt độ TT, lưu lượng kế FT đều là Sim_IO và không gán địa chỉ vật lý `%I/%Q`:

*   **Đo lường liên tục:** `LT3203_Bon1`, `LT3209_Bon2`, `LT3213_Bon3`, `LT3218_Bon4`, `LT3302_BonChua1`, `LT3307_BonChua2`, `TT3204_Bon1`, `TT3208_Bon2`, `TT3214_Bon3`, `TT3219_Bon4`, `FT3200_Bon1`, `FT3205_Bon2`, `FT3210_Bon3`, `FT3215_Bon4`.
*   **Chấp hành cơ cấu:** `AGTR3260_Khuay_Bon1`, `AGTR3262_Khuay_Bon3`, `AGTR3263_Khuay_Bon4`, `V3232_Xa_Bon1`, `V3235_Nuoc_Bon2`, `V3237_Xa_Bon2`, `V3240_Nuoc_Bon3`, `V3242_Xa_Bon3`, `V3245_Nuoc_Bon4`, `V3247_Xa_Bon4`, v.v.

---

## 4. Ánh Xạ Biến Cũ (Ladder Tags) Sang Cấu Trúc DB Mới

> [!NOTE]
> Tiền tố `AI_` là tên lịch sử pre-migration và đã được loại bỏ hoàn toàn trong dự án SCL-first. Bản đồ mapping sử dụng các tag hiện hữu sạch sau khi migration từ legacy project (ví dụ: `Nut_Khoi_Dong`, `Nut_Dung` thay vì `AI_Nut_Khoi_Dong`).

Bảng ánh xạ các tag chính từ legacy project sang cấu trúc DB/UDT mới:

| Tên Tag Legacy (Ladder) | Địa Chỉ Cũ | Biến DB Mới (SCL-First) | Vị Trí Trong DB | Ghi Chú |
| :--- | :--- | :--- | :--- | :--- |
| `Nut_Khoi_Dong` | `%I0.0` | `Nut_Start_Physical` | `DB_RealIO_Map` | Nút nhấn Start vật lý thật |
| `Nut_Dung` | `%I0.1` | `Nut_Stop_Physical` | `DB_RealIO_Map` | Nút nhấn Stop vật lý thật |
| `Nut_Reset` | `%I0.2` | `Nut_Reset_Physical` | `DB_RealIO_Map` | Nút nhấn Reset lỗi vật lý thật |
| `Nut_EStop` | `%I0.3` | `Nut_EStop_Physical` | `DB_RealIO_Map` | Nút EStop vật lý thật |
| `VFD_Bon2_Contactor` | `%Q0.0` | `VFD_Bon2_Contactor` | `DB_RealIO_Map` | Contactor nguồn biến tần thật |
| `LT3203_Bon1` | `%ID108` | `Bon1.Muc_Dich_PV` | `DB_Operation` | Cảm biến báo mức Bồn 1 (Sim_IO) |
| `TT3204_Bon1` | `%ID112` | `Bon1.Nhiet_Do_PV` | `DB_Operation` | Cảm biến nhiệt độ Bồn 1 (Sim_IO) |
| `LT3209_Bon2` | `%ID124` | `Bon2.Muc_Dich_PV` | `DB_Operation` | Cảm biến báo mức Bồn 2 (Sim_IO) |
| `TT3208_Bon2` | `%ID128` | `Bon2.Nhiet_Do_PV` | `DB_Operation` | Cảm biến nhiệt độ Bồn 2 (Sim_IO) |
| `LT3213_Bon3` | `%ID140` | `Bon3.Muc_Dich_PV` | `DB_Operation` | Cảm biến báo mức Bồn 3 (Sim_IO) |
| `TT3214_Bon3` | `%ID144` | `Bon3.Nhiet_Do_PV` | `DB_Operation` | Cảm biến nhiệt độ Bồn 3 (Sim_IO) |
| `LT3218_Bon4` | `%ID156` | `Bon4.Muc_Dich_PV` | `DB_Operation` | Cảm biến báo mức Bồn 4 (Sim_IO) |
| `TT3219_Bon4` | `%ID160` | `Bon4.Nhiet_Do_PV` | `DB_Operation` | Cảm biến nhiệt độ Bồn 4 (Sim_IO) |
| `LT3302_BonChua1` | `%ID164` | `BonChua1.Muc_Dich_PV` | `DB_Operation` | Mức dịch Bồn chứa 1 (Sim_IO) |
| `LT3307_BonChua2` | `%ID176` | `BonChua2.Muc_Dich_PV` | `DB_Operation` | Mức dịch Bồn chứa 2 (Sim_IO) |
| `AGTR3260_Khuay_Bon1` | `%Q0.1` | `Bon1.Khuay_Chay` | `DB_Operation` | Cánh khuấy Bồn 1 (Sim_IO) |
| `V3232_Xa_Bon1` | `%Q0.2` | `Bon1.Van_Xa_Day_1` | `DB_Operation` | Van xả đáy 1 Bồn 1 (Sim_IO) |
| `V3235_Nuoc_Bon2` | `%Q0.5` | `Bon2.Van_Cap_Nuoc` | `DB_Operation` | Van nước cấp Bồn 2 (Sim_IO) |
| `CV3206_Hoi_Bon2` | `%QD108` | `Bon2.Van_Cap_Hoi` | `DB_Operation` | Độ mở van hơi Bồn 2 (Sim_IO) |
| `PID_Bon2_Enable` | `%M412.0` | `PID_Bon2.Enable` | `DB_Operation` | Kích hoạt PID Bồn 2 |
| `PID_Bon2_SP` | `%MD416` | `PID_Bon2.Setpoint` | `DB_Operation` | Setpoint nhiệt độ PID Bồn 2 |
| `PID_Bon2_PV` | `%MD420` | `PID_Bon2.PV` | `DB_Operation` | Phản hồi nhiệt độ PID Bồn 2 |
| `PID_Bon2_CV` | `%MD424` | `PID_Bon2.CV` | `DB_Operation` | Ngõ ra điều khiển PID Bồn 2 |
| `Nut_Khoi_Dong_HMI` | `%M110.0` | `HMI.Nut_Khoi_Dong` | `DB_HMI` | Nút nhấn khởi động từ HMI |
| `HMI_SP_PLC1_Nuoc_Bon1` | `%MD224` | `Recipe.SP_Nuoc_Bon1` | `DB_HMI` / `DB_Recipe` | Setpoint nước cấp Bồn 1 |
| `HMI_SP_PLC1_Toc_Do_Bon1`| `%MD240` | `Recipe.SP_Toc_Do_Bon1` | `DB_HMI` / `DB_Recipe` | Setpoint tốc độ Bồn 1 |

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
