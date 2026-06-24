# PHƯƠNG ÁN QUY HOẠCH BIẾN (TAGS) VÀ KHỐI DỮ LIỆU (DBS) CHO BẢN ĐẤU NỐI
**Dự án:** Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD
**Thời gian cập nhật:** 24/06/2026

> [!NOTE]
> Tài liệu này mô tả chi tiết phương án quy hoạch bảng biến (PLC Tag Tables) và khối dữ liệu đệm (Data Blocks/Buffers) phục vụ cho bài đấu nối, giải quyết triệt để lỗi biên dịch ánh xạ HMI và thực hiện kiểm tra không chồng lấn bộ nhớ (No-Overlap Check) theo yêu cầu kiểm duyệt.

---

## 1. Phân Tích Hiện Trạng HMI Tags & Ánh Xạ Biến (HMI Tag Mapping)
Đã xuất và phân tích toàn bộ 80 biến của bảng tag HMI `Screen1_HMI_Tags` để đối chiếu với yêu cầu biến nền PLC. Chi tiết báo cáo ánh xạ được ghi nhận trong tệp tin:
👉 [hmi_missing_tag_mapping.csv](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/hmi_missing_tag_mapping.csv)

### Tóm tắt thống kê ánh xạ:
- **Tổng số HMI Tags:** 80 tags.
- **Biến nội bộ (Internal Tags):** 4 tags (không kết nối PLC, dùng cho mục đích hiển thị giao diện).
- **Biến đã sẵn sàng map (Exists):** 3 tags (`TT3208_Bon2_Eff`, `HMI_SP_PLC1_Nhiet_Do_Bon2`, `HMI_SP_PLC2_Nhiet_Do_Bon4`).
- **Biến thiếu trong PLC (Missing):** 73 tags. Các tag này tương ứng với các van (V3230, V3232,...), bơm (Pump3264, Pump3265,...), cảm biến (LT3203, LT3209, TT3204,...), và các biến phụ trợ động tác/xung nhịp khuấy chưa được khai báo ở PLC Tag Table.
- **Đề xuất phân bổ thiết bị:** 
  - 51 HMI tags liên quan đến nhánh 1 (Bồn 1, Bồn 2, Bồn chứa 1, Bồn chứa 2, lọc) đề xuất gán cho **PLC_1** (IP 192.168.0.1).
  - 22 HMI tags liên quan đến nhánh 2 (Bồn 3, Bồn 4) đề xuất gán cho **PLC_2** (IP 192.168.0.2).

---

## 2. Đề Xuất Bảng Biến Nền Tối Giản (Proposed PLC Tag Tables)
Để giải quyết lỗi biên dịch tượng trưng (Symbolic Assignment) trên HMI và tạo cấu trúc cho các thuật toán PID, Modbus, chúng ta đề xuất khai báo các bảng tag sau:

### 2.1. PLC_1 Tag Table (Khai báo 93 tags bao gồm core và HMI compatibility tags)
- Tệp tin cấu hình đề xuất (XML Openness): [proposed_plc1_tags.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/proposed_plc1_tags.xml)
- Tệp tin xem nhanh (CSV): [proposed_plc1_tags.csv](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/proposed_plc1_tags.csv)

*Các biến chính được quy hoạch tại M-Area:*
- **Điều khiển & Hệ thống:** `HMI_Run_Enable` (%M20.0), `HMI_Reset_Alarm` (%M20.1), `HMI_Che_Do_Thi` (%M20.2), `HMI_Sim_Mode` (%M20.3), `PLC1_State` (%MW12), `PLC1_Loi_Tong` (%M20.4), `PLC1_Stop_Active` (%M20.5), `PLC1_EStop_Latch` (%M20.6), `PLC1_SP_Valid` (%M20.7).
- **Tín hiệu HMI:** `Nut_Khoi_Dong_HMI` (%M21.0), `Nut_Dung_HMI` (%M21.1), `Nut_Reset_HMI` (%M21.2).
- **Bộ PID Bồn 2:** `HMI_PID_Bon2_Dau_Noi_Enable` (%M21.5), `PID_Bon2_Enable` (%M21.6), `PID_Bon2_Enable_Eff` (%M21.7), `PID_Bon2_SP` (%MD30 - Real), `PID_Bon2_PV_Eff` (%MD34 - Real), `PID_Bon2_CV` (%MD38 - Real).
- **Tham số & Nhiệt độ Bồn 2:** `HMI_SP_PLC1_Nhiet_Do_Bon2` (%MD42), `HMI_SP_PLC1_Toc_Do_Bon2_Main` (%MD46), `TT3208_Bon2_Eff` (%MD50), `TT3208_Bon2_HMI` (%MD54), `VFD_Bon2_Toc_Do_Cmd` (%MD58), `TT3208_Bon2_Use_HMI` (%M22.0).
- **Biến tần Bồn 2 (Modbus RTU):**
  - Khối giao tiếp Modbus: `VFD_Bon2_MB_Error` (%M22.1), `VFD_Bon2_MB_Busy` (%M22.2), `VFD_Bon2_MB_Done` (%M22.3), `VFD_Bon2_MB_Status` (%MW70).
  - Từ lệnh/Từ trạng thái: `VFD_Bon2_MB_ControlWord` (%MW62), `VFD_Bon2_MB_StatusWord` (%MW64).
  - Tần số đặt/thực tế: `VFD_Bon2_MB_FreqSetpoint` (%MW66), `VFD_Bon2_MB_FreqActual` (%MW68).
- **Truyền thông PLC1-PLC2 (Modbus TCP Client):** `MB_TCP_ERROR` (%M22.4), `MB_TCP_BUSY` (%M22.5), `MB_TCP_DONE` (%M22.6), `MB_TCP_STATUS` (%MW72), `MB_TCP_iStep` (%MW74).
- **Nhịp tim kiểm tra (Heartbeat):** `PLC1_Heartbeat` (%MW76), `PLC2_Heartbeat_Recv` (%MW78), `PLC1_Heartbeat_Timeout` (%M22.7).
- **Đầu ra vật lý điều lực (Real_IO):** `VFD_Bon2_Contactor` (%Q0.0).

### 2.2. PLC_2 Tag Table (Khai báo 45 tags bao gồm core và HMI compatibility tags)
- Tệp tin cấu hình đề xuất (XML Openness): [proposed_plc2_tags.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/proposed_plc2_tags.xml)
- Tệp tin xem nhanh (CSV): [proposed_plc2_tags.csv](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/proposed_plc2_tags.csv)

*Các biến chính được quy hoạch tại M-Area:*
- **Điều khiển & Hệ thống:** `HMI_Run_Enable` (%M20.0), `HMI_Reset_Alarm` (%M20.1), `HMI_Sim_Mode` (%M20.2), `PLC2_State` (%MW12), `PLC2_Loi_Tong` (%M20.3), `PLC2_Stop_Active` (%M20.4), `PLC2_EStop_Latch` (%M20.5).
- **Bộ PID Bồn 4:** `PID_Bon4_Enable` (%M20.6), `PID_Bon4_SP` (%MD30 - Real), `PID_Bon4_PV` (%MD34 - Real), `PID_Bon4_CV` (%MD38 - Real), `HMI_SP_PLC2_Nhiet_Do_Bon4` (%MD42), `TT3219_Bon4_Sim` (%MD46), `CV3216_Hoi_Bon4` (%MD50).
- **Truyền thông PLC1-PLC2 (Modbus TCP Server):** `MB_TCP_Server_Error` (%M20.7), `MB_TCP_Server_Busy` (%M21.0), `MB_TCP_Server_NDR` (%M21.1), `MB_TCP_Server_DR` (%M21.2), `PLC2_Heartbeat_Timeout` (%M21.3), `MB_TCP_Server_Status` (%MW54).
- **Nhịp tim kiểm tra (Heartbeat):** `PLC2_Heartbeat` (%MW56), `PLC1_Heartbeat_Recv` (%MW58).

---

## 3. Khối Dữ Liệu Đệm Truyền Thông (Proposed Communication DBs - Proposed Only)
> [!IMPORTANT]
> Toàn bộ các khối dữ liệu (DB) dưới đây hiện tại ở trạng thái **Đề xuất lập kế hoạch (Proposed Only / Dry-Run)**. Chưa thực hiện tạo thực tế hoặc import vào TIA Portal để đảm bảo không can thiệp khi chưa được phê duyệt.

Để trao đổi dữ liệu an toàn và đúng quy tắc (không truyền trực tiếp kiểu phức tạp Struct/Real/Bool qua thanh ghi Modbus), chúng ta cấu hình các khối dữ liệu standard non-optimized (để có địa chỉ Offset thanh ghi Modbus cố định):

### 3.1. Truyền thông PLC1 - PLC2 (Modbus TCP)
- **Thiết lập phía PLC_2 (Modbus Server):**
  - Tạo khối `DB_Modbus_TCP_Server_Buffer` (DB10) - Non-optimized.
  - Cấu trúc dữ liệu chứa 1 mảng từ thanh ghi: `MB_Holding_Registers` : `Array[0..15] of Word`.
  - **Bản đồ thanh ghi Modbus (Holding Register Map):**

| Thanh ghi Modbus | Kiểu dữ liệu | Tên biến đệm | Mô tả | Hướng truyền |
| :---: | :---: | :--- | :--- | :---: |
| **40001 (Offset 0.0)** | Word | `PLC2_State_Register` | Lưu bước quy trình `PLC2_State` (Int) | PLC2 -> PLC1 |
| **40002 (Offset 2.0)** | Word | `PLC2_Status_Bits` | Chứa các cờ trạng thái Bool (Bit 0: Run_Enable, Bit 1: Loi_Tong, Bit 2: EStop_Latch) | PLC2 -> PLC1 |
| **40003 (Offset 4.0)** | Word | `PLC2_Heartbeat_Register` | Lưu nhịp tim `PLC2_Heartbeat` (Int) | PLC2 -> PLC1 |
| **40004 (Offset 6.0)** | Word | `PID_Bon4_PV_Word1` | Word cao của giá trị thực `PID_Bon4_PV` (Real) | PLC2 -> PLC1 |
| **40005 (Offset 8.0)** | Word | `PID_Bon4_PV_Word2` | Word thấp của giá trị thực `PID_Bon4_PV` (Real) | PLC2 -> PLC1 |
| **40006 (Offset 10.0)** | Word | `PID_Bon4_CV_Word1` | Word cao của giá trị thực `PID_Bon4_CV` (Real) | PLC2 -> PLC1 |
| **40007 (Offset 12.0)** | Word | `PID_Bon4_CV_Word2` | Word thấp của giá trị thực `PID_Bon4_CV` (Real) | PLC2 -> PLC1 |
| **40008 (Offset 14.0)** | Word | `PLC1_State_Recv` | Bước quy trình PLC1 gửi sang | PLC1 -> PLC2 |
| **40009 (Offset 16.0)** | Word | `PLC1_Status_Bits_Recv` | Các cờ trạng thái PLC1 gửi sang (Bit 0: Run_Enable, Bit 1: Che_Do_Thi) | PLC1 -> PLC2 |
| **40010 (Offset 18.0)** | Word | `PLC1_Heartbeat_Recv` | Nhịp tim PLC1 gửi sang | PLC1 -> PLC2 |

- **Thiết lập phía PLC_1 (Modbus Client):**
  - Sử dụng khối `DB_Modbus_TCP_Client_Buffer` (DB10) - Non-optimized chứa:
    - `Send_Data` : `Array[0..2] of Word` (Lưu State, Status Bits, Heartbeat để ghi sang Server từ thanh ghi 40008).
    - `Recv_Data` : `Array[0..6] of Word` (Lưu dữ liệu đọc về từ Server bắt đầu từ thanh ghi 40001).
  - Sử dụng logic tách/ghép Word thành kiểu Real (cho PV, CV) và kiểu Bool (cho Status Bits).

### 3.2. Truyền thông PLC1 - ATV12 VFD (Modbus RTU)
- Tạo khối `DB_ATV12_Modbus_Buffer` (DB11) - Non-optimized trên PLC_1.
- Cấu trúc dữ liệu đệm chứa:
  - `Control_Word` : Word (Thanh ghi lệnh CMD - Địa chỉ Modbus 8501)
  - `Freq_Setpoint` : Word (Thanh ghi tần số đặt LFRD - Địa chỉ Modbus 8502)
  - `Status_Word` : Word (Thanh ghi trạng thái ETA - Địa chỉ Modbus 3201)
  - `Freq_Actual` : Word (Thanh ghi tần số thực tế rfrd - Địa chỉ Modbus 3202)
- Khối `MB_MASTER` trên PLC_1 sẽ thực hiện đọc/ghi trực tiếp vào các biến này theo bước chu trình lập lịch truyền thông.

---

## 4. Kiểm Tra Tránh Chồng Lấn Bộ Nhớ (Mandatory No-Overlap Check)
Để đảm bảo độ tin cậy của hệ thống, một quy trình kiểm tra chồng lấn địa chỉ (Overlap Check) tự động bằng mã nguồn đã được thực hiện.

### 4.1. Khắc phục lỗi chồng lấn bộ nhớ PLC_1
1. **Lỗi chồng lấn vùng nhớ trạng thái `%MW12`:**
   - Trong phiên bản trước, biến `PLC1_State` (%MW12, chiếm byte %MB12 và %MB13) bị chồng chéo với các biến Bool hệ thống và Modbus vốn đặt ở `%M12.0` đến `%M12.7`.
   - **Giải pháp:** Toàn bộ các biến Bool hệ thống và truyền thông đã được chuyển dịch hoàn toàn sang vùng `%M20.0` đến `%M22.7` (thuộc %MB20, %MB21, %MB22). Vùng nhớ `%MW12` hiện tại hoàn toàn độc lập và không bị chồng lấn.
2. **Tránh chồng lấn địa chỉ đầu ra vật lý `%Q0.0`:**
   - Đã phát hiện sự trùng lặp địa chỉ `%Q0.0` giữa ngõ ra vật lý điều khiển contactor biến tần bồn 2 `VFD_Bon2_Contactor` và van ảo `V3230_Nuoc_Bon1` (được thừa kế từ bảng tag cũ).
   - **Giải pháp (Nguyên tắc Sim_IO):** Vì van `V3230_Nuoc_Bon1` là van mô phỏng (Sim_IO) không có thiết bị vật lý thực tế trên bảng đấu nối, van này được cấu hình lại địa chỉ thành biến ảo `%M100.6` thuộc vùng nhớ HMI Compatibility. Địa chỉ `%Q0.0` được giải phóng hoàn toàn để phục vụ riêng cho ngõ ra điều khiển contactor thực tế `VFD_Bon2_Contactor`.
3. **Tránh chồng lấn vùng nhớ xung nhịp/hệ thống:**
   - Không sử dụng các địa chỉ `%MB0` (Clock byte của CPU) và `%MB1` (System byte của CPU) cho các tag trong bảng import đề xuất để tránh xung đột với cấu hình phần cứng CPU.

### 4.2. Kết quả chạy script kiểm tra chồng lấn địa chỉ
Đã thực thi kiểm tra chồng lấn địa chỉ toàn diện cho cả hai bảng tag đề xuất thông qua script `scratch/generate_final_proposed_tags.py`.
Kết quả phân tích:
- **PLC_1 (93 tags):** `[PASS] Overlap check passed for PLC_1 (0 overlaps detected).`
- **PLC_2 (45 tags):** `[PASS] Overlap check passed for PLC_2 (0 overlaps detected).`

---

## 5. Tính Tương Thích HMI (HMI Compatibility & Connection Rules)
*   **Độ bao phủ của bảng tag:** Các proposed PLC tag tables đã bao phủ 73/73 process tags bị thiếu với kiểu dữ liệu phù hợp. Kết quả hết lỗi HMI chỉ được xác nhận sau khi kiểm tra HMI_Connection_1/2, import tag, compile HMI và readback thực tế.
*   **Tên biến không có dấu chấm:** Tất cả các tên biến trong bảng tag đề xuất đều tuân thủ đúng quy định ASCII, không chứa dấu chấm (các tag xung nhịp cũ có chứa dấu chấm như `Clock_2.5Hz` đã được loại bỏ hoàn toàn khỏi bảng tag import, thay vào đó ghi chú cấu hình trực tiếp trên CPU).
*   **Điều kiện kết nối bắt buộc (Connection Rules):**
    *   `HMI_Connection_1` bắt buộc phải trỏ sang thiết bị **PLC_1**.
    *   `HMI_Connection_2` bắt buộc phải trỏ sang thiết bị **PLC_2**.
    *   **Quy định an toàn:** Nếu bất kỳ kết nối nào (connection) chưa tồn tại hoặc bị sai trỏ trên TIA Portal, điều này sẽ được coi là lỗi chặn mức cao (Blocker). Tuyệt đối không tự ý tạo mới hay sửa đổi connection khi chưa được Codex và người dùng phê duyệt trực tiếp.

---

## 6. Hiện Trạng Git & Quyết Định Tiếp Theo
- **Trạng thái Git:** Chỉ stage các file đề xuất (`docs/proposed_plc1_tags.*`, `docs/proposed_plc2_tags.*` và báo cáo `docs/dau_noi_tag_db_plan.md`). Không stage các script thử nghiệm scratch hay file trung gian `HMI_Tags_Exported.xml`.
- **Hành động tiếp theo:** Không thực hiện import phần mềm, không tải xuống (download) PLC. Hệ thống dừng lại để chờ Codex và người sử dụng duyệt phương án quy hoạch này.
