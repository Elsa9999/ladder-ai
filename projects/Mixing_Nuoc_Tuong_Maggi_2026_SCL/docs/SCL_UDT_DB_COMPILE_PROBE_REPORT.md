# BÁO CÁO KIỂM CHỨNG BIÊN DỊCH THỰC TẾ TRÊN TIA PORTAL (SCL_UDT_DB_COMPILE_PROBE_REPORT.md)

Tài liệu này ghi lại kết quả kiểm chứng thực tế quá trình import và biên dịch (Compile Probe) các file cấu trúc SCL (UDT/DB skeletons) của dự án **Mixing Nước Tương Maggi 2026 SCL-first** trên phần mềm **TIA Portal V18**.

---

## 1. Môi Trường Kiểm Chứng (Test Environment)
*   **Phiên bản TIA Portal:** Siemens Totally Integrated Automation Portal V18 (Openness API V18).
*   **Dự án kiểm chứng (Probe Project):** `Maggi_SCL_Compile_Probe_20260624` (Được nhân bản an toàn từ dự án gốc `cuocthi_tdh` để đảm bảo độc lập, tránh ảnh hưởng đến logic Ladder hiện tại).
*   **Cấu hình CPU S7-1200 kiểm thử:**
    *   **PLC_1:** CPU 1214C DC/DC/DC (Mã đặt hàng: `6ES7 214-1AG40-0XB0` / Firmware V4.5).
    *   **PLC_2:** CPU 1214C DC/DC/DC (Mã đặt hàng: `6ES7 214-1AG40-0XB0` / Firmware V4.5).

---

## 2. Kết Quả Import & Biên Dịch Chi Tiết

Tất cả 12 file nguồn SCL (7 UDTs và 5 DBs) đều được import và sinh khối thành công (**[SUCCESS]**) trong thư mục External Sources của cả hai PLC.

### 2.1. Kết quả trên PLC_2 (Biên dịch thành công 100%)
*   **Số lượng Errors:** 0
*   **Số lượng Warnings:** 1 (Cảnh báo về địa chỉ I/O không tồn tại trong cấu hình phần cứng vật lý hiện tại của PLC2).
*   **Trạng thái phần mềm:** **COMPILED SUCCESSFULLY** (Biên dịch thành công sạch sẽ).
*   **Danh sách file SCL đã nạp và biên dịch thành công:**
    *   **UDTs:** `UDT_HMI_Data`, `UDT_ModbusTCP_Link`, `UDT_PID_Channel`, `UDT_Recipe`, `UDT_SystemStatus`, `UDT_Tank`, `UDT_VFD_ATV12`.
    *   **DBs:** `DB_Comms`, `DB_HMI`, `DB_Operation`, `DB_RealIO_Map`, `DB_Recipe`.

### 2.2. Kết quả trên PLC_1 (Lỗi khối cũ / SCL mới thành công)
*   **Số lượng Errors:** 41
*   **Số lượng Warnings:** 1
*   **Trạng thái phần mềm:** Có lỗi biên dịch.
*   **Phân tích nguyên nhân lỗi:**
    *   Các lỗi biên dịch này **không nằm trong các khối SCL mới import** (`UDT` và `DB` Maggi), mà nằm trong các khối logic điều khiển Ladder cũ của dự án `cuocthi_tdh` (ví dụ: các lỗi không khớp kiểu dữ liệu `Int` và `Real` trên tham số khối, tag `#Temp_Pack_Word` chưa định nghĩa).
    *   Các khối UDT và DB Maggi SCL mới import vẫn được tạo ra và kiểm chứng cú pháp nội bộ thành công, không gặp bất kỳ lỗi parser hay biên dịch nào thuộc về bản thân chúng.

---

## 3. Đánh Giá Các Điểm Rủi Ro Đã Nêu Trong Style Guide

### 3.1. Cú pháp khởi tạo `BEGIN` trong `DB_Recipe.scl`
*   **Cú pháp khai báo:**
    ```pascal
    BEGIN
       Default_Recipe.SP_Nuoc_Bon1 := 100.0;
       Default_Recipe.SP_Nuoc_Bon2 := 120.0;
       ...
    END_DATA_BLOCK
    ```
*   **Kết quả thực tế:** **THÀNH CÔNG**. Trình biên dịch TIA Portal V18 SCL chấp nhận hoàn toàn cú pháp gán giá trị con của Struct lồng trong khối `BEGIN`.
*   **Xác nhận qua XML Readback:** Thẻ `<StartValue>` tương ứng trong XML của `DB_Recipe` đã được cập nhật chính xác các giá trị khởi tạo (ví dụ: `<StartValue>100.0</StartValue>` cho `SP_Nuoc_Bon1`).
*   **Kết luận:** Giữ nguyên cú pháp `BEGIN` hiện tại của `DB_Recipe.scl` mà không cần chỉnh sửa hay lược bỏ.

### 3.2. Cấu trúc kiểu dữ liệu hệ thống `TCON_IP_v4` trong `DB_Comms.scl`
*   **Cú pháp khai báo:** Khai báo cấu trúc kiểu `TCON_IP_v4` cho truyền thông Modbus TCP.
*   **Kết quả thực tế:** **THÀNH CÔNG**. Không có lỗi thiếu kiểu dữ liệu do dự án gốc `cuocthi_tdh` đã sử dụng khối truyền thông Modbus TCP (`MB_CLIENT` / `MB_SERVER`) từ trước, giúp CPU nhận dạng ngay kiểu hệ thống này.
*   **Kết luận:** Việc sử dụng cấu trúc `TCON_IP_v4` tường minh trong SCL DB là an toàn và biên dịch tốt.

---

## 4. Đường Dẫn Dữ Liệu Readback Compile
Dữ liệu khối và kiểu dữ liệu sau khi biên dịch thành công trên PLC_2 đã được export ngược ra XML thành công để lưu vết:
*   **Thư mục chứa:** [projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/readback_compile_probe/PLC_2/](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/readback_compile_probe/PLC_2/)
    *   **Thư mục UDTs:** [Types/](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/readback_compile_probe/PLC_2/Types/) (chứa `UDT_Recipe.xml`, `UDT_Tank.xml`, v.v.)
    *   **Thư mục DBs:** [Blocks/](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/readback_compile_probe/PLC_2/Blocks/) (chứa `DB_Recipe.xml`, `DB_Comms.xml`, v.v.)
