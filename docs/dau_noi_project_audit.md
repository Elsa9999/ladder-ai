# BÁO CÁO AUDIT DỰ ÁN TIA PORTAL ĐẤU NỐI MỚI
**Dự án:** Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD
**Thời gian thực hiện:** 24/06/2026

> [!NOTE]
> Báo cáo này ghi nhận hiện trạng phần cứng, kết nối mạng và cấu hình bộ nhớ hệ thống của dự án TIA Portal V18 đấu nối mới trước khi thực hiện viết hoặc import logic chương trình.

---

## 1. Thông Tin TIA Portal Instance Đang Kết Nối
- **TIA Portal Version:** V18
- **Project Name:** `Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD`
- **Project Path:** `C:\Users\lienb\Downloads\PLC-PID-Level-Control-main\Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD\Mixing_Nuoc_Tuong_Maggi_2026_DauNoi_LAD.ap18`
- **TIA Portal Process PID:** `7652`
- **Số lượng TIA Portal instance phát hiện trên hệ thống:** 2 (gồm PID `7652` - dự án đấu nối mới Maggi và PID `27364` - dự án `cuocthi_tdh`). Hệ thống đã kết nối chính xác vào PID `7652`.

---

## 2. Danh Sách Thiết Bị & Cấu Hình Chi Tiết (Devices Inventory)

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
- **Cấu hình Clock Memory Byte:**
  - **Trạng thái:** Đã bật (Enabled) tại `%MB0`
  - **Địa chỉ tag chi tiết:**
    - `Clock_Byte` = `%MB0`
    - `Clock_1Hz` = `%M0.5`
    - `Clock_0.5Hz` = `%M0.7`
    - (Các clock khác từ `%M0.0` đến `%M0.6` được map đầy đủ)
- **Cấu hình System Memory Byte:**
  - **Trạng thái:** Đã bật (Enabled) tại `%MB1`
  - **Địa chỉ tag chi tiết:**
    - `System_Byte` = `%MB1`
    - `FirstScan` = `%M1.0`
    - `AlwaysTRUE` = `%M1.2`
    - `AlwaysFALSE` = `%M1.3`
- **Kiểm tra Module RS485 (CB 1241 / CM 1241):** Không có module/board RS485 nào được cấu hình trên `PLC_1`.

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
- **Cấu hình Clock Memory Byte:**
  - **Trạng thái:** Đã bật (Enabled) tại `%MB0`
  - **Địa chỉ tag chi tiết:**
    - `Clock_Byte` = `%MB0`
    - `Clock_1Hz` = `%M0.5`
    - `Clock_0.5Hz` = `%M0.7`
- **Cấu hình System Memory Byte:**
  - **Trạng thái:** Đã bật (Enabled) tại `%MB1`
  - **Địa chỉ tag chi tiết:**
    - `System_Byte` = `%MB1`
    - `FirstScan` = `%M1.0`
    - `AlwaysTRUE` = `%M1.2`
    - `AlwaysFALSE` = `%M1.3`

### 2.3. HMI / PC Station (PC-System_1)
- **Tên thiết bị:** `PC-System_1`
- **Kiểu thiết bị (Type):** System:Device.PC (Trạm PC chạy WinCC Runtime)
- **Cấu hình địa chỉ IP mạng (IE General):**
  - **Địa chỉ IP:** `192.168.0.3`
  - **Subnet Mask:** `255.255.255.0`
  - **Subnet kết nối:** `PN/IE_1`
- **Hiện trạng phần mềm HMI:** Thiết bị `PC-System_1` chỉ được cấu hình phần cứng mạng (Ethernet Card), **không chứa bất kỳ phần mềm HMI Target nào** (không có WinCC RT Professional/Advanced hay các màn hình HMI được cấu hình trong cây thư mục dự án này).

---

## 3. Danh Sách Kết Nối (Logical Connections)

> [!WARNING]
> Quy định dự án cấm sử dụng truyền thông S7 GET/PUT. Bắt buộc truyền thông giữa PLC_1 và PLC_2 qua Modbus TCP.

- **Kết nối S7 (S7 Connections):** Không có kết nối S7 nào được cấu hình trong dự án. Không phát hiện kết nối tên `S7_Connection_1` hay các kết nối tương tự.
- **Kết nối HMI (HMI Connections):** Không có kết nối HMI nào được cấu hình (do dự án chưa có HMI Target).
- **Đánh giá chung:** Cấu hình kết nối trống, hoàn toàn tuân thủ quy định không sử dụng GET/PUT trong phần cấu hình tĩnh. Quá trình truyền thông giữa hai PLC sẽ được triển khai hoàn toàn bằng code logic SCL gọi các khối truyền thông Modbus TCP (`MB_CLIENT` / `MB_SERVER`).

---

## 4. Kết Quả Biên Dịch Thử Nghiệm (Compilation Audit)
Đã thực hiện biên dịch phần cứng trống và phần mềm trống (chương trình chưa có logic tùy biến, chỉ có mặc định `Main [OB1]` trống) để kiểm tra tính toàn vẹn của dự án mới:

| Thiết bị | Loại biên dịch | Trạng thái | Lỗi (Errors) | Cảnh báo (Warnings) | Chi tiết |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **PLC_1** | Cấu hình phần cứng (HW) | Success | 0 | 0 | Biên dịch thành công |
| **PLC_1** | Khối logic (Blocks) | Success | 0 | 0 | Khối `Main [OB1]` trống biên dịch thành công |
| **PLC_2** | Cấu hình phần cứng (HW) | Success | 0 | 0 | Biên dịch thành công |
| **PLC_2** | Khối logic (Blocks) | Success | 0 | 0 | Khối `Main [OB1]` trống biên dịch thành công |

---

## 5. Kết Luận & Khuyến Nghị
1. **Sự phù hợp của bộ nhớ hệ thống:** Clock memory byte (`%MB0`) và System memory byte (`%MB1`) đã được kích hoạt và gán tag chính xác cho cả `PLC_1` và `PLC_2`, tuân thủ hoàn toàn quy định phần cứng mới (không dùng `%MB100` / `%MB101`).
2. **Không có module RS485:** Xác nhận không có module RS485 trên `PLC_1` (và cả `PLC_2`). Truyền thông giữa `PLC_1` và `PLC_2` bắt buộc dùng Modbus TCP qua cổng PROFINET tích hợp sẵn trên CPU.
3. **Hiện trạng kết nối S7:** Không có kết nối S7 cũ, đáp ứng yêu cầu an toàn thông tin và kiến trúc mạng.
4. **Trạng thái sẵn sàng:** Dự án đấu nối mới có cấu hình phần cứng sạch, không có lỗi biên dịch, đã sẵn sàng để Codex/User phê duyệt cho các bước phát triển logic SCL tiếp theo.
