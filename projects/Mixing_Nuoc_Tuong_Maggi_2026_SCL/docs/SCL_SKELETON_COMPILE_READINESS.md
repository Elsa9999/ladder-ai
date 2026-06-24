# BÁO CÁO KIỂM TRA SCL SKELETON COMPILE-READINESS (SCL_SKELETON_COMPILE_READINESS.md)

Tài liệu này báo cáo chi tiết quá trình kiểm tra tĩnh và hiệu chỉnh các tệp UDT/DB skeleton SCL nhằm tối ưu hóa khả năng import và biên dịch thành công trong TIA Portal V18.

---

## 1. Kết Luận Chung
*   **Compile-readiness static check (Kiểm tra tĩnh tính sẵn sàng):** **PASS**
*   **TIA compile thật (Biên dịch thực tế trên TIA):** **CHƯA CHẠY** *(Do lượt này chỉ thực hiện kiểm tra tĩnh offline, không import vào TIA Portal và không tải xuống PLC thật/mô phỏng)*.

---

## 2. Danh Sách Các File Đã Kiểm Tra
Chúng tôi đã kiểm tra tĩnh toàn bộ 12 tệp SCL trong dự án:

### Thư mục UDT (`udt/`)
1.  [UDT_Tank.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_Tank.scl)
2.  [UDT_PID_Channel.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_PID_Channel.scl)
3.  [UDT_VFD_ATV12.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_VFD_ATV12.scl)
4.  [UDT_ModbusTCP_Link.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_ModbusTCP_Link.scl)
5.  [UDT_HMI_Data.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_HMI_Data.scl)
6.  [UDT_Recipe.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_Recipe.scl)
7.  [UDT_SystemStatus.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_SystemStatus.scl)

### Thư mục DB (`db/`)
8.  [DB_HMI.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_HMI.scl)
9.  [DB_Recipe.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_Recipe.scl)
10. [DB_Operation.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_Operation.scl)
11. [DB_Comms.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_Comms.scl)
12. [DB_RealIO_Map.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/DB_RealIO_Map.scl)

---

## 3. Các Hiệu Chỉnh Và Lỗi Cú Pháp Đã Sửa

### Hiệu chỉnh trong `DB_Comms.scl` (Rủi ro cao nhất):
*   *Lỗi cú pháp gốc:* Khối `BEGIN ... END_DATA_BLOCK` của `DB_Comms.scl` trước đó chứa các lệnh gán tĩnh cho struct `TCON_IP_v4` (ví dụ: `MB_TCP_Client_Conn.RemoteAddress.ADDR[1] := 192;`). Trong cú pháp Siemens SCL cho Data Block, việc gán giá trị khởi đầu cho các kiểu dữ liệu phức tạp hoặc mảng lồng nhau trong phần `BEGIN` thường không được hỗ trợ bởi trình biên dịch SCL của TIA Portal và sẽ báo lỗi cú pháp khi import file SCL tĩnh.
*   *Giải pháp:* 
    1. Loại bỏ toàn bộ phần gán tĩnh của `MB_TCP_Client_Conn` và `MB_TCP_Server_Conn` khỏi khối `BEGIN` của `DB_Comms.scl`.
    2. Giữ nguyên khai báo kiểu dữ liệu `TCON_IP_v4` trong phần `STRUCT`.
    3. Thêm chú thích chi tiết kèm mẫu mã nguồn gán động tại hàm khởi tạo `FirstScan` (OB1/OB100). Cách tiếp cận này giảm rủi ro lỗi parser khi import SCL, nhưng chưa được xác nhận compile thật trên TIA Portal. Bắt buộc import/compile/readback TIA để kết luận compile sạch.

---

## 4. Các Điểm Rủi Ro Chưa Chắc Cần TIA Portal Kiểm Chứng Thực Tế

Mặc dù các tệp SCL đã vượt qua hoàn toàn bộ lọc kiểm tra tĩnh (Static Checks), vẫn còn một số điểm rủi ro phụ thuộc vào quá trình import/biên dịch thực tế trong TIA Portal V18:

1.  **Nhận diện Kiểu Dữ Liệu `TCON_IP_v4`:**
    *   *Rủi ro:* `TCON_IP_v4` là kiểu dữ liệu hệ thống tích hợp sẵn của Siemens. Nếu tệp SCL chứa kiểu này được import vào một project TIA Portal trống chưa từng sử dụng bất kỳ khối truyền thông Modbus TCP nào (như `MB_CLIENT`), TIA Portal có thể tạm thời không nhận diện được kiểu dữ liệu này và báo lỗi import.
    *   *Khắc phục:* Trong TIA Portal, cần kéo một khối `MB_CLIENT` hoặc `MB_SERVER` vào chương trình trước để TIA tự động nạp kiểu dữ liệu hệ thống `TCON_IP_v4` vào danh mục kiểu dữ liệu của CPU, sau đó tiến hành import `DB_Comms.scl`.
2.  **Độ lệch Offset trong DB Non-Optimized (`DB_Comms.scl`):**
    *   *Rủi ro:* `DB_Comms` được cấu hình `{ S7_Optimized_Access := 'False' }` để phục vụ Modbus TCP và RTU. Khi biên dịch thực tế, TIA Portal sẽ tự động tính toán byte offset cho từng biến trong DB.
    *   *Cần kiểm chứng:* Cần thực hiện compile và readback từ TIA Portal để xác nhận chính xác các byte offset của mảng `MB_Hold_Reg` và các struct liên quan không bị lệch do căn chỉnh dữ liệu tự động (data alignment) của CPU S7-1200.
3.  **Tương thích UDT lồng trong DB:**
    *   *Cần lưu ý:* Các DB chứa các biến kiểu UDT (ví dụ: `Bon1 : "UDT_Tank"`). Thứ tự import vào TIA Portal bắt buộc phải là: **Import tất cả các UDT trước, sau đó mới import các DB**. Nếu import DB trước khi các UDT được định nghĩa trong hệ thống, TIA Portal sẽ báo lỗi biên dịch thiếu kiểu dữ liệu.
4.  **Start value cho field lồng trong UDT ở DB_Recipe.scl:**
    *   *Rủi ro:* `DB_Recipe.scl` hiện đang gán giá trị khởi tạo cho các thuộc tính con của struct `Default_Recipe` (kiểu `UDT_Recipe`) trong khối `BEGIN ... END_DATA_BLOCK` (ví dụ: `Default_Recipe.SP_Nuoc_Bon1 := 100.0;`).
    *   *Cần kiểm chứng:* Cú pháp gán giá trị cho trường con của struct lồng trong DB thông qua khối `BEGIN` có thể được một số phiên bản TIA Portal chấp nhận, nhưng chưa được xác nhận qua việc compile thật trên TIA Portal V18. Cần thực hiện import thử các UDT trước DB, tiến hành compile và readback để xác nhận tính đúng đắn.

---

## 5. Xác Nhận Logic Và Tiền Tố
*   **Tiền tố `AI_`:** Xác nhận quét toàn bộ 12 file SCL, hoàn toàn không có bất kỳ identifier (tên biến, tên DB, tên UDT) nào chứa tiền tố `AI_`.
*   **Logic vận hành:** Xác nhận không có bất kỳ logic điều khiển, sequencer, Grafcet, vòng quét hay lệnh gọi khối công nghệ Modbus/PID nào được sinh ra trong các file skeleton.
