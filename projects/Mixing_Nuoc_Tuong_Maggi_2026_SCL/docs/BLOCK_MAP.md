# Bản Đồ Khối Chương Trình (BLOCK_MAP.md)

Tài liệu này liệt kê danh sách toàn bộ các khối chương trình (Organization Blocks, Function Blocks, Functions, Data Blocks) dự kiến phát triển cho dự án Mixing Nước Tương Maggi 2026 SCL.

---

## 1. Bảng Phân Bổ Khối Chương Trình Tổng Quan

| Tên Khối | Loại Khối | Số Hiệu | Ngôn ngữ | Vai Trò & Mô Tả | Variant A (1 PLC) | Variant B (2 PLC) |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **OB1_Main** | OB | 1 | SCL | Khối tổ chức chính, gọi điều phối các khối chức năng theo chu kỳ. | Có (PLC1) | Có (PLC1 & PLC2) |
| **OB100_Startup** | OB | 100 | SCL | Khối khởi chạy khi PLC khởi động, dùng gán động TCON Modbus TCP hoặc thông số recipe. | Có (PLC1) | Có (PLC1 & PLC2) |
| **OB30_PID_Bon2** | OB | 30 | SCL | Khối ngắt chu kỳ (Cyclic Interrupt), trực tiếp gọi điều phối `PID_Compact` cho Bồn 2. | Có (PLC1) | Có (PLC_1) |
| **OB31_PID_Bon4** | OB | 31 | SCL | Khối ngắt chu kỳ (Cyclic Interrupt), trực tiếp gọi điều phối `PID_Compact` cho Bồn 4. | Có (PLC1) | Có (PLC_2) |
| **FB_Grafcet_Bon1_2** | FB | 10 | SCL | Khối điều khiển chu trình tuần tự (Grafcet) cho Bồn 1 và Bồn 2. | Có (PLC1) | Có (PLC_1) |
| **FB_Grafcet_Bon3_4** | FB | 11 | SCL | Khối điều khiển chu trình tuần tự (Grafcet) cho Bồn 3 và Bồn 4. | Có (PLC1) | Có (PLC_2) |
| **FB_ATV12_Modbus_RTU**| FB | 12 | SCL | Khối State Machine điều khiển tuần tự biến tần ATV12 qua RS485 (Modbus RTU). | Không | Có (PLC_1) |
| **FB_ModbusTCP_Client** | FB | 13 | SCL | Khối điều phối truyền thông Modbus TCP Client (giao tiếp chéo với PLC2). | Không | Có (PLC_1) |
| **FB_ModbusTCP_Server** | FB | 14 | SCL | Khối điều phối truyền thông Modbus TCP Server (nhận yêu cầu từ PLC1). | Không | Có (PLC_2) |
| **FC_HMI_Mirror** | FC | 20 | SCL | Khối nhân bản trạng thái tag (mirroring) để tương thích bảng tag ảo HMI SCADA. | Có (PLC1) | Có (PLC1 & PLC2) |
| **FC_HMI_Animation** | FC | 21 | SCL | Khối tính toán logic hiển thị hình động mức dịch bồn chứa trên WinCC. | Có (PLC1) | Có (PLC1 & PLC2) |
| **FC_Manual_Control** | FC | 22 | SCL | Khối xử lý lệnh điều khiển bằng tay (Manual Mode) cho các thiết bị chấp hành. | Có (PLC1) | Có (PLC1 & PLC2) |
| **DB_HMI** | DB | 100 | Cấu trúc | Khối dữ liệu chứa toàn bộ giao tiếp đọc/ghi với màn hình WinCC HMI. | Có (PLC1) | Có (PLC1 & PLC2) |
| **DB_Recipe** | DB | 101 | Cấu trúc | Khối dữ liệu lưu trữ các setpoint nhiệt độ, thời gian và công thức pha chế. | Có (PLC1) | Có (PLC1 & PLC2) |
| **DB_Operation** | DB | 102 | Cấu trúc | Khối dữ liệu chứa các biến trạng thái trung gian, bước Grafcet và liên động. | Có (PLC1) | Có (PLC1 & PLC2) |
| **DB_Comms** | DB | 103 | Cấu trúc | Khối dữ liệu đệm truyền nhận cho Modbus TCP và Modbus RTU. | Không | Có (PLC1 & PLC2) |

---

## 2. Chi Tiết Các Khối Công Nghệ Hệ Thống (Siemens System Blocks)

Các khối dưới đây là khối thư viện tích hợp sẵn của hãng Siemens, không viết lại mã nguồn, chỉ được gọi và cấu hình tham số thông qua SCL:

1.  **PID_Compact (Version 1.2):**
    *   **Khối gọi:** `PID_Compact_DB` (gọi trong `OB30_PID_Bon2` và `OB31_PID_Bon4`).
    *   **Nhiệm vụ:** Điều khiển tuyến tính nhiệt độ Bồn 2 và Bồn 4.
    *   **Lưu ý lập trình SCL:** Giao tiếp chế độ thông qua chân `sRet.i_Mode`. Tránh ghi đè trực tiếp các tham số cấu hình tĩnh của khối để không xảy ra lỗi Lock-mode.

2.  **MB_CLIENT / MB_SERVER (Version 3.1):**
    *   **Khối gọi:** `MB_CLIENT_DB` và `MB_SERVER_DB` (gọi trong các FB truyền thông tương ứng của Variant B).
    *   **Nhiệm vụ:** Thiết lập kênh truyền dữ liệu Modbus TCP qua Ethernet giữa PLC1 và PLC2.
    *   **Lưu ý lập trình SCL:** Không khai báo cứng kiểu kết nối trong DB. Sử dụng cấu trúc `TCON_IP_v4` gán động IP và Port ở OB100.

3.  **Modbus RTU Blocks (MB_COMM_LOAD & MB_MASTER):**
    *   **Khối gọi:** `MB_COMM_LOAD_DB` và `MB_MASTER_DB` (gọi trong `FB_ATV12_Modbus_RTU`).
    *   **Nhiệm vụ:** Khởi tạo cổng truyền thông RS485 và thực hiện các lệnh đọc/ghi thanh ghi tần số/lệnh của biến tần ATV12.
