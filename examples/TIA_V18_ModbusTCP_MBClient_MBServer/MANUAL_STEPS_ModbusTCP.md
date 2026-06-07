# Hướng dẫn tạo và xuất XML mẫu Modbus TCP trên TIA Portal V18

Tài liệu này hướng dẫn chi tiết từng bước cho người vận hành để xây dựng một dự án TIA Portal V18 cấu hình mẫu truyền thông Modbus TCP giữa 2 PLC S7-1200, sau đó dùng công cụ xuất dữ liệu nội bộ `Export_Device_ByName.exe` để xuất cấu trúc XML SimaticML chuẩn. Các XML này được sử dụng làm mẫu (reference) cho AI generator sinh mã tự động.

---

## 1. Cấu hình phần cứng & IP trên TIA Portal V18

1. **Khởi tạo dự án mới:**
   * Mở TIA Portal V18, tạo dự án đặt tên là `TIA_V18_ModbusTCP_Test`.
2. **Thêm PLC 1 (Modbus Client):**
   * Add new device: PLC S7-1200 (ví dụ: CPU 1214C DC/DC/DC, mã `6ES7 214-1AG40-0XB0`).
   * Đặt tên thiết bị trong TIA Portal là: `PLC_1`.
   * Cấu hình IP cho cổng PROFINET interface: `192.168.0.1`, subnet mask: `255.255.255.0`.
   * Ghi nhận ID phần cứng của cổng Ethernet (thường là `64` hoặc xem tại System constants: `Local~PROFINET_interface`).
3. **Thêm PLC 2 (Modbus Server):**
   * Add new device: PLC S7-1200 tương tự.
   * Đặt tên thiết bị trong TIA Portal là: `PLC_2`.
   * Cấu hình IP cho cổng PROFINET interface: `192.168.0.2`, subnet mask: `255.255.255.0`.
   * Ghi nhận ID phần cứng của cổng Ethernet (thường là `64`).

---

## 2. Cấu hình tại PLC_1 (Modbus TCP Client)

### Bước 2.1: Tạo DB cấu hình kết nối (Connection DB)
1. Thêm một Global DB mới: đặt tên là `DB_MB_TCP_Client_Conn`.
2. Chuột phải vào DB -> **Properties** -> mục **Attributes** -> **Bỏ chọn** `Optimized block access` (để DB ở dạng **Standard / Non-Optimized** layout).
3. Định nghĩa biến kết nối bên trong DB:
   * Tên biến: `MB_TCP`
   * Kiểu dữ liệu: `TCON_IP_v4`
   * *Lưu ý:* Không cần nhập giá trị Start Value cho các trường con của `TCON_IP_v4` trong DB vì công cụ sinh code sẽ gán động qua các lệnh `MOVE` ở network khởi tạo.

### Bước 2.2: Tạo các DB gửi/nhận dữ liệu
1. Tạo DB gửi: đặt tên là `DB_PLC1_Send_To_PLC2`. **Bỏ chọn** `Optimized block access`.
   * Khai báo các biến:
     * `CmdSeq`: kiểu `Int` (chứa số thứ tự lệnh).
     * Các bit lệnh (tổng cộng 6 lệnh): `Cmd_Start`, `Cmd_Stop`, `Cmd_Reset`, `Cmd_EStop`, `Cmd_Pump_Branch2_To_SubTanks`, `Cmd_Load_Recipe` (kiểu `Bool`).
     * `Heartbeat_Client`: kiểu `Int`.
2. Tạo DB nhận: đặt tên là `DB_PLC1_Recv_From_PLC2`. **Bỏ chọn** `Optimized block access`.
   * Khai báo các biến nhận tương ứng với cấu trúc thanh ghi của Server (xem tài liệu chi tiết).

### Bước 2.3: Viết Logic gọi khối MB_CLIENT
1. Mở `Main [OB1]` của `PLC_1`.
2. Trong thư viện lệnh (Instruction tab), tìm đường dẫn: `Communication` -> `Others` -> `Modbus TCP` -> kéo khối `MB_CLIENT` vào một Network mới.
3. Khi TIA yêu cầu tạo Instance DB cho `MB_CLIENT`, đặt tên DB mặc định là `MB_CLIENT_DB`.
4. Điền các tham số cho khối `MB_CLIENT`:
   * `REQ`: Bit kích hoạt (ví dụ: `AI_MB_TCP_Write_Req` hoặc `AI_MB_TCP_Read_Req`).
   * `DISCONNECT`: `FALSE` (duy trì kết nối).
   * `CONNECT`: Trỏ tới `DB_MB_TCP_Client_Conn`.`MB_TCP` (kiểu dữ liệu `TCON_IP_v4`).
   * `MB_MODE`: Chế độ đọc/ghi (`1` để ghi, `0` để đọc).
   * `MB_DATA_ADDR`: Địa chỉ Modbus (`40001` cho ghi lệnh, `40004` cho đọc trạng thái).
   * `MB_DATA_LEN`: Độ dài word (`3` cho ghi lệnh, `10` cho đọc trạng thái).
   * `MB_DATA_PTR`: Trỏ tới vùng nhớ dữ liệu (`DB_PLC1_Send_To_PLC2` hoặc `DB_PLC1_Recv_From_PLC2`).

---

## 3. Cấu hình tại PLC_2 (Modbus TCP Server)

### Bước 3.1: Tạo DB cấu hình kết nối
1. Thêm một Global DB mới: đặt tên là `DB_MB_TCP_Server_Conn`.
2. Chuột phải vào DB -> **Properties** -> mục **Attributes** -> **Bỏ chọn** `Optimized block access`.
3. Định nghĩa biến kết nối:
   * Tên biến: `MB_TCP_SERVER`
   * Kiểu dữ liệu: `TCON_IP_v4`.

### Bước 3.2: Tạo DB Holding Register
1. Tạo Global DB mới: đặt tên là `DB_Modbus_Holding_Register`. **Bỏ chọn** `Optimized block access`.
2. DB này đóng vai trò là bảng thanh ghi lưu trữ toàn bộ thông tin trao đổi. Cấu trúc khai báo các biến liên tiếp như sau:
   * `CmdSeq`: kiểu `Int` (Offset 0.0) -> Tương đương thanh ghi `40001`.
   * 6 Bools lệnh liên tiếp: `Cmd_Start`, `Cmd_Stop`, `Cmd_Reset`, `Cmd_EStop`, `Cmd_Pump_Branch2_To_SubTanks`, `Cmd_Load_Recipe` (Offset 2.0 đến 2.5) -> Tương đương thanh ghi `40002`.
   * `Heartbeat_Client`: kiểu `Int` (Offset 4.0) -> Tương đương thanh ghi `40003`.
   * `AckSeq`: kiểu `Int` (Offset 6.0) -> Tương đương thanh ghi `40004`.
   * 3 Bools trạng thái liên tiếp: `Done_Branch2`, `Done_Recipe`, `Alarm` (Offset 8.0 đến 8.2) -> Tương đương thanh ghi `40005`.
   * `State`: kiểu `Int` (Offset 10.0) -> Tương đương thanh ghi `40006`.
   * `PID_Bon4_SP`: kiểu `Real` (Offset 12.0) -> Tương đương thanh ghi `40007-40008`.
   * `PID_Bon4_PV`: kiểu `Real` (Offset 16.0) -> Tương đương thanh ghi `40009-40010`.
   * `PID_Bon4_CV`: kiểu `Real` (Offset 20.0) -> Tương đương thanh ghi `40011-40012`.
   * `Heartbeat_Server`: kiểu `Int` (Offset 24.0) -> Tương đương thanh ghi `40013`.

### Bước 3.3: Viết Logic gọi khối MB_SERVER
1. Mở `Main [OB1]` của `PLC_2`.
2. Kéo khối `MB_SERVER` từ tab `Communication` -> `Others` -> `Modbus TCP` vào một Network mới.
3. Đồng ý tạo Instance DB mặc định tên là `MB_SERVER_DB`.
4. Điền các tham số cho khối `MB_SERVER`:
   * `DISCONNECT`: `FALSE` (chấp nhận kết nối liên tục từ Client).
   * `CONNECT`: Trỏ tới `DB_MB_TCP_Server_Conn`.`MB_TCP_SERVER`.
   * `MB_HOLD_REG`: Trỏ tới toàn bộ DB Holding Register: `DB_Modbus_Holding_Register`.

---

## 4. Chạy công cụ Export để lấy XML chuẩn

Sau khi cấu hình và biên dịch không lỗi trên TIA Portal V18, giữ dự án mở và chạy các lệnh CLI sau ở terminal để xuất XML:

```powershell
# 1. Xuất dữ liệu từ PLC_1 (Modbus TCP Client)
& Ladder\Export_Device_ByName.exe TIA_V18_ModbusTCP_Test PLC_1 examples\TIA_V18_ModbusTCP_MBClient_MBServer\PLC_1

# 2. Xuất dữ liệu từ PLC_2 (Modbus TCP Server)
& Ladder\Export_Device_ByName.exe TIA_V18_ModbusTCP_Test PLC_2 examples\TIA_V18_ModbusTCP_MBClient_MBServer\PLC_2
```

### Kết quả thu được trong thư mục `examples\TIA_V18_ModbusTCP_MBClient_MBServer\`:
* Thư mục `PLC_1/Blocks` chứa `Main.xml` và `MB_CLIENT_DB.xml`.
* Thư mục `PLC_1/Tags` chứa bảng tag của PLC_1.
* Thư mục `PLC_2/Blocks` chứa `Main.xml` và `MB_SERVER_DB.xml`.
* Thư mục `PLC_2/Tags` chứa bảng tag của PLC_2.

Các XML này chứa định dạng chuẩn SimaticML của khối hệ thống `MB_CLIENT`, `MB_SERVER`, và định dạng struct kết nối `TCON_IP_v4` phục vụ cho việc sinh mã tự động bằng Python trong project Mixer.
