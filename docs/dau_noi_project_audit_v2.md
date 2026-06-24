# BÁO CÁO AUDIT DỰ ÁN TIA PORTAL ĐẤU NỐI - PHIÊN BẢN V2
**Dự án:** Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD
**Thời gian thực hiện:** 24/06/2026

> [!NOTE]
> Báo cáo này ghi nhận kết quả đánh giá cấu hình phần cứng mới cập nhật của dự án đấu nối Maggi, sau khi User đã thao tác thủ công thêm trạm HMI/SCADA vào PC-System_1 và thêm module RS485 cho PLC_1.

---

## 1. Thông Tin TIA Portal Instance Đang Kết Nối
- **TIA Portal Version:** V18
- **Project Name:** `Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD`
- **Project Path:** `C:\Users\lienb\Downloads\PLC-PID-Level-Control-main\Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD\Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD.ap18`
- **TIA Portal Process PID:** `7652`
- **Số lượng TIA Portal instance trên hệ thống:** 1 (PID `7652`).

---

## 2. Danh Sách Thiết Bị & Cấu Hình Chi Tiết (Devices Inventory v2)

### 2.1. PLC_1 (S7-1200 station_1)
- **Tên thiết bị (Device Name):** `PLC_1`
- **Dòng CPU (CPU Type):** CPU 1214C DC/DC/DC
- **Mã sản phẩm (Article Number):** `6ES7 214-1AG40-0XB0`
- **Phiên bản Firmware:** `V4.0`
- **Vị trí Slot/Position:** Slot 1
- **Cấu hình địa chỉ IP:**
  - **Địa chỉ IP:** `192.168.0.1`
  - **Subnet Mask:** `255.255.255.0`
  - **Subnet kết nối:** `PN/IE_1`
- **Cấu hình Clock Memory Byte:** Đã bật (Enabled) tại `%MB0` (`Clock_1Hz` = `%M0.5`, `Clock_0.5Hz` = `%M0.7`).
- **Cấu hình System Memory Byte:** Đã bật (Enabled) tại `%MB1` (`FirstScan` = `%M1.0`, `AlwaysTRUE` = `%M1.2`, `AlwaysFALSE` = `%M1.3`).
- **Cấu hình Module RS485:**
  - **Tên module:** `CB 1241 (RS485)`
  - **Mã sản phẩm (Article Number):** `6ES7 241-1CH30-1XB0`
  - **Phiên bản Firmware:** `V1.0`
  - **Vị trí lắp đặt (Slot/Position):** Position 3 (Lắp trên bo mạch tích hợp phía trước CPU - Signal Board).

### 2.2. PLC_2 (S7-1200 station_2)
- **Tên thiết bị (Device Name):** `PLC_2`
- **Dòng CPU (CPU Type):** CPU 1214C DC/DC/DC
- **Mã sản phẩm (Article Number):** `6ES7 214-1AG40-0XB0`
- **Phiên bản Firmware:** `V4.0`
- **Vị trí Slot/Position:** Slot 1
- **Cấu hình địa chỉ IP:**
  - **Địa chỉ IP:** `192.168.0.2`
  - **Subnet Mask:** `255.255.255.0`
  - **Subnet kết nối:** `PN/IE_1`
- **Cấu hình Clock Memory Byte:** Đã bật (Enabled) tại `%MB0` (`Clock_1Hz` = `%M0.5`, `Clock_0.5Hz` = `%M0.7`).
- **Cấu hình System Memory Byte:** Đã bật (Enabled) tại `%MB1` (`FirstScan` = `%M1.0`, `AlwaysTRUE` = `%M1.2`, `AlwaysFALSE` = `%M1.3`).
- **Kiểm tra RS485:** Xác nhận **PLC_2 không cấu hình bất kỳ module RS485 nào**.

### 2.3. HMI / SCADA Target (PC-System_1)
- **Tên thiết bị:** `PC-System_1`
- **Kiểu thiết bị (Type):** System:Device.PC
- **Tên cấu hình SCADA (HMI Target Name):** `HMI_RT_1` (WinCC Runtime target)
- **Cấu hình địa chỉ IP mạng (IE General):**
  - **Địa chỉ IP:** `192.168.0.3`
  - **Subnet Mask:** `255.255.255.0`
  - **Subnet kết nối:** `PN/IE_1`
- **Danh sách màn hình hiện có:**
  - `Login/out`
  - `chekc truyen thong`
  - `Screen_1`
  - `bon tron 1`
  - `bon tron 2`
  - `bon tron 3`
  - `bon tron 4`
- **Bảng HMI Tags:**
  - `Default tag table` (1 tag)
  - `Screen1_HMI_Tags` (80 tags)

---

## 3. Danh Sách Kết Nối (Logical Connections)
- **Kết nối S7 (S7 Connections):** Không phát hiện kết nối S7 nào được cấu hình tĩnh giữa các PLC. Không có `S7_Connection_1`.
- **Kết nối HMI (HMI Connections):** Kết nối HMI trong phần `HMI_RT_1` > `Connections` trống (0 connections). Các biến trong bảng tag HMI hiện tại trỏ tới các tag PLC qua gán ký hiệu tượng trưng (Symbolic Assignment) nhưng chưa liên kết kết nối tĩnh HMI.

---

## 4. Kết Quả Biên Dịch Thử Nghiệm (Compilation Audit)
Đã thực hiện biên dịch phần cứng và phần mềm để kiểm tra dự án sau khi User cập nhật thiết bị:

| Thiết bị | Loại biên dịch | Trạng thái | Lỗi (Errors) | Cảnh báo (Warnings) | Chi tiết |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **PLC_1** | Phần cứng & Phần mềm | Warning | 0 | 1 | Phần cứng biên dịch thành công. Cảnh báo: `PLC_1 does not contain a configured protection level` |
| **PLC_2** | Phần cứng & Phần mềm | Warning | 0 | 1 | Phần cứng biên dịch thành công. Cảnh báo: `PLC_2 does not contain a configured protection level` |
| **PC-System_1 (HMI_RT_1)** | Phần cứng & Phần mềm | **Fail** | **76** | **10** | Biên dịch phần cứng thành công. Biên dịch phần mềm HMI **Thất bại** với 76 lỗi `Invalid symbol assignment`. |

> [!IMPORTANT]
> **Giải thích lỗi biên dịch HMI (76 Errors):**
> Lỗi này xảy ra do bảng HMI Tag `Screen1_HMI_Tags` chứa 80 biến liên kết tượng trưng (Symbolic Assignment) đến các biến PLC như `V3230_Nuoc_Bon1`, `V3237_Xa_Bon2`, `Pump3264_Chuyen_Nhanh1`...
> Tuy nhiên, do chúng ta **chưa import bảng tag PLC và logic chương trình** (mặc định CPU chỉ có 14 biến Clock/System trống), các biến này chưa tồn tại trong PLC. TIA Portal báo lỗi ánh xạ ký hiệu không hợp lệ. Đây là hành vi hoàn toàn bình thường và đúng tiến trình tại giai đoạn audit đấu nối chưa import logic.

---

## 5. Kết Luận & Đề Xuất
1. **Module RS485:** Đã được cấu hình thành công trên `PLC_1` (CB 1241 tại slot 3). `PLC_2` hoàn toàn trống đúng thiết kế.
2. **Trạm HMI/SCADA:** SCADA Target `HMI_RT_1` và các màn hình bồn trộn, bảng tag HMI (80 tags) đã được tạo lập thành công trên trạm PC-System_1 (IP 192.168.0.3).
3. **Cấu hình IP & Memory Byte:** Hoàn toàn tuân thủ các quy định hardware của bài thi đấu nối (IP PLC1=192.168.0.1, PLC2=192.168.0.2, Clock=%MB0, System=%MB1).
4. **Trạng thái sẵn sàng:** Dự án đấu nối mới có cấu hình phần cứng đúng chuẩn. Trạng thái lỗi biên dịch HMI sẽ tự động hết khi các bước tiếp theo thực hiện import PLC tag table đầy đủ. Sẵn sàng báo cáo User duyệt để bắt đầu import logic.
