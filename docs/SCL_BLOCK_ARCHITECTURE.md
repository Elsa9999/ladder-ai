# KIẾN TRÚC KHỐI CHƯƠNG TRÌNH SCL (SCL BLOCK ARCHITECTURE)

Tài liệu này đặc tả cấu trúc phân bổ khối (OB, FB, FC, DB) cho phiên bản SCL mới, quy định rõ ngôn ngữ lập trình cho từng khối và phương thức gọi các thư viện công nghệ của Siemens.

---

## 1. Bản Đồ Phân Phổ Khối Chương Trình (Program Block Map)

| Ký Hiệu | Tên Khối | Ngôn Ngữ | Loại Khối | Vai Trò & Chức Năng |
| :--- | :--- | :--- | :--- | :--- |
| **OB1** | `Main` | SCL | Tổ chức (OB) | Điều phối quét chu kỳ chính, gọi các FB/FC điều khiển nhánh và bồn chứa. |
| **OB30** | `PID_Loop_PLC1` | SCL | Ngắt chu kỳ | Quét định kỳ 100ms cho bộ điều khiển nhiệt độ PID Bồn 2 (PLC1). |
| **OB31** | `PID_Loop_PLC2` | SCL | Ngắt chu kỳ | Quét định kỳ 100ms cho bộ điều khiển nhiệt độ PID Bồn 4 (PLC2). |
| **FB10** | `FB_Mixing_Branch` | SCL | Hàm chức năng | Chứa logic chạy tuần tự (CASE) cho một nhánh (Bồn A + Bồn B). Dùng chung instance cho Nhánh 1 và Nhánh 2. |
| **FB20** | `FB_Storage_Filter` | SCL | Hàm chức năng | Quản lý phân xử quyền sở hữu bồn chứa, logic giải nhiệt, bơm chuyển qua màng lọc và chiết rót. |
| **FC30** | `FC_Modbus_ATV12` | SCL | Hàm chức năng | Chạy State Machine điều khiển tuần tự Modbus RTU ghi Control Word/Tần số và đọc Status Word từ ATV12. |
| **FC40** | `FC_Sensor_Simulation`| SCL | Hàm chức năng | Giả lập dâng mức, tăng nhiệt bồn dựa trên trạng thái van/bơm/gia nhiệt để test offline. |
| **DB10** | `Inst_Mixing_Branch_1`| DB | Instance DB | Dữ liệu làm việc cho Nhánh 1 (PLC1). |
| **DB11** | `Inst_Mixing_Branch_2`| DB | Instance DB | Dữ liệu làm việc cho Nhánh 2 (PLC2 hoặc truyền thông nội bộ). |
| **DB20** | `Inst_Storage_Filter` | DB | Instance DB | Dữ liệu làm việc cho cụm bồn chứa thành phẩm. |
| **DB_HMI** | `DB_HMI_Data` | DB | Global DB | Vùng nhớ lưu trữ các cờ lệnh, cài đặt và giám sát liên kết trực tiếp với WinCC. |
| **DB_Comms**| `DB_Comms_Buffer` | DB | Global DB | Vùng đệm dữ liệu truyền thông Modbus TCP/RTU. |

---

## 2. Các Khối Công Nghệ & Thư Viện Giữ Nguyên Dạng Mặc Định

Các khối điều khiển công nghệ đặc thù của Siemens sẽ không được viết lại bằng SCL mà được gọi (Call) trực tiếp dưới dạng **Technology Object** hoặc các khối thư viện hệ thống đóng gói sẵn:

1.  **`PID_Compact` (Version 1.2):** Khối điều khiển PID nhiệt độ hệ thống cấp hơi Bồn 2 và Bồn 4.
2.  **`Modbus_Comm_Load` (Version 2.1) & `Modbus_Master` (Version 2.2):** Các khối thư viện phục vụ truyền thông Modbus RTU điều khiển biến tần ATV12.
3.  **`MB_CLIENT` (Version 3.1) & `MB_SERVER` (Version 3.1):** Các khối thư viện phục vụ truyền thông Modbus TCP trao đổi dữ liệu giữa PLC1 và PLC2.

---

## 3. Cú Pháp Gọi PID_Compact trong SCL

Để tránh lỗi mode-locking (PID bị kẹt ở chế độ không mong muốn khi khởi động/lỗi), cú pháp gọi `PID_Compact` trong SCL phải tuân thủ nghiêm ngặt việc cập nhật biến InOut `sRet.i_Mode`:

```scl
// Gán chân đầu vào hiệu dụng cho bộ PID Bồn 2
"Inst_PID_Bon2".Setpoint := "DB_HMI_Data".Setpoint.NhietDo_Bon2;
"Inst_PID_Bon2".Input := "DB_Operation_Data".Bon2.NhietDo_Eff;
"Inst_PID_Bon2".Reset := "DB_Operation_Data".Sys.Reset_Active;

// Xử lý cờ cho phép PID hoạt động
IF "DB_Operation_Data".Bon2.PID_Enable THEN
    // MOVE 3 (Auto Mode) vào i_Mode để kích hoạt bộ PID
    "Inst_PID_Bon2".sRet.i_Mode := 3;
    "Inst_PID_Bon2".ManualEnable := FALSE;
ELSE
    // MOVE 0 (Inactive Mode) vào i_Mode để tắt bộ PID an toàn
    "Inst_PID_Bon2".sRet.i_Mode := 0;
    "Inst_PID_Bon2".ManualEnable := FALSE;
END_IF;

// Thực hiện gọi khối PID_Compact (OB30 quét định kỳ 100ms)
"Inst_PID_Bon2"(
    Setpoint := "Inst_PID_Bon2".Setpoint,
    Input := "Inst_PID_Bon2".Input,
    Reset := "Inst_PID_Bon2".Reset,
    ManualEnable := "Inst_PID_Bon2".ManualEnable,
    OutputValue => "DB_Operation_Data".Bon2.PID_CV
);

// Gán ngõ ra PID điều khiển van hơi gia nhiệt
"CV3206_Hoi_Bon2" := "DB_Operation_Data".Bon2.PID_CV;
```

---

## 4. Thiết Kế Sequencer Điều Khiển Modbus RTU ATV12

Để loại bỏ hoàn toàn rủi ro gọi một instance `Modbus_Master` nhiều lần trong cùng một chu kỳ quét (gây xung đột và lỗi Bus), chúng ta sẽ thiết kế một State Machine (CASE) tuần tự duy nhất trong `FC_Modbus_ATV12`:

```scl
// Khởi tạo khối Comm Load tại First Scan
IF "FirstScan" THEN
    "DB_Comms_Buffer".ATV12.Comm_Load_Req := TRUE;
END_IF;

"Inst_Modbus_Comm_Load"(
    REQ := "DB_Comms_Buffer".ATV12.Comm_Load_Req,
    "PORT" := 260, // Hardware ID của CB1241
    BAUD := 19200,
    PARITY := 1,
    RESP_TO := 1000,
    DONE => "DB_Comms_Buffer".ATV12.Comm_Load_Done,
    ERROR => "DB_Comms_Buffer".ATV12.Comm_Load_Error,
    STATUS => "DB_Comms_Buffer".ATV12.Comm_Load_Status
);

IF "DB_Comms_Buffer".ATV12.Comm_Load_Done THEN
    "DB_Comms_Buffer".ATV12.Comm_Load_Req := FALSE;
END_IF;

// Nếu Comm Load đã cấu hình xong, chạy State Machine Modbus Master
IF NOT "DB_Comms_Buffer".ATV12.Comm_Load_Req THEN
    
    // Tạo trễ 200ms để Retry nếu có lỗi xảy ra
    "Timer_MB_Retry"(IN := "DB_Comms_Buffer".ATV12.MB_Error, PT := T#200MS);
    
    // Kích hoạt REQ khi không bận, không lỗi hoặc khi hết thời gian chờ retry
    IF NOT "Inst_Modbus_Master".BUSY AND (NOT "DB_Comms_Buffer".ATV12.MB_Error OR "Timer_MB_Retry".Q) THEN
        "DB_Comms_Buffer".ATV12.MB_Req := TRUE;
    END_IF;

    // Chỉ thực hiện thiết lập tham số khi rảnh
    IF NOT "Inst_Modbus_Master".BUSY THEN
        CASE "DB_Comms_Buffer".ATV12.iStep OF
            0: // ĐỌC Status Word (Địa chỉ 3201)
                "DB_Comms_Buffer".ATV12.MB_Mode := 0;
                "DB_Comms_Buffer".ATV12.MB_DataAddr := 43202; // Modbus 4x Address
                "DB_Comms_Buffer".ATV12.MB_DataLen := 1;
            
            1: // ĐỌC Tần số thực tế (Địa chỉ 3202)
                "DB_Comms_Buffer".ATV12.MB_Mode := 0;
                "DB_Comms_Buffer".ATV12.MB_DataAddr := 43203;
                "DB_Comms_Buffer".ATV12.MB_DataLen := 1;
            
            2: // GHI Control Word (Địa chỉ 8501)
                "DB_Comms_Buffer".ATV12.MB_Mode := 1;
                "DB_Comms_Buffer".ATV12.MB_DataAddr := 48502;
                "DB_Comms_Buffer".ATV12.MB_DataLen := 1;
            
            3: // GHI Tần số cài đặt (Địa chỉ 8502)
                "DB_Comms_Buffer".ATV12.MB_Mode := 1;
                "DB_Comms_Buffer".ATV12.MB_DataAddr := 48503;
                "DB_Comms_Buffer".ATV12.MB_DataLen := 1;
        END_CASE;
    END_IF;

    // Chỉ gọi instance duy nhất của Modbus_Master
    "Inst_Modbus_Master"(
        REQ := "DB_Comms_Buffer".ATV12.MB_Req,
        MB_ADDR := 1, // Node ID của ATV12
        MODE := "DB_Comms_Buffer".ATV12.MB_Mode,
        DATA_ADDR := "DB_Comms_Buffer".ATV12.MB_DataAddr,
        DATA_LEN := "DB_Comms_Buffer".ATV12.MB_DataLen,
        DATA_PTR := "DB_Comms_Buffer".ATV12.MB_Buffer, // Con trỏ mảng đệm
        DONE => "DB_Comms_Buffer".ATV12.MB_Done,
        BUSY => "DB_Comms_Buffer".ATV12.MB_Busy,
        ERROR => "DB_Comms_Buffer".ATV12.MB_Error,
        STATUS => "DB_Comms_Buffer".ATV12.MB_Status
    );

    // Xử lý sau khi kết thúc giao dịch
    IF "DB_Comms_Buffer".ATV12.MB_Done THEN
        "DB_Comms_Buffer".ATV12.MB_Req := FALSE;
        "DB_Comms_Buffer".ATV12.MB_Error_Counter := 0; // Reset đếm lỗi
        
        // Cập nhật dữ liệu tương ứng từ Buffer vào tag nội bộ
        CASE "DB_Comms_Buffer".ATV12.iStep OF
            0: "DB_Operation_Data".Bon2.VFD_StatusWord := "DB_Comms_Buffer".ATV12.MB_Buffer[0];
            1: "DB_Operation_Data".Bon2.VFD_ActualSpeed := "DB_Comms_Buffer".ATV12.MB_Buffer[0];
        END_CASE;
        
        // Chuyển sang bước tiếp theo
        "DB_Comms_Buffer".ATV12.iStep := ("DB_Comms_Buffer".ATV12.iStep + 1) MOD 4;
    
    ELSIF "DB_Comms_Buffer".ATV12.MB_Error THEN
        "DB_Comms_Buffer".ATV12.MB_Req := FALSE;
        "DB_Comms_Buffer".ATV12.MB_Error_Counter := "DB_Comms_Buffer".ATV12.MB_Error_Counter + 1;
        
        // Nếu lỗi quá 3 lần liên tiếp, chốt lỗi truyền thông
        IF "DB_Comms_Buffer".ATV12.MB_Error_Counter >= 3 THEN
            "DB_Operation_Data".Sys.VFD_Comm_Fault := TRUE;
        END_IF;
    END_IF;
END_IF;
```

---

## 5. Kế Hoạch Truyền Thông Modbus TCP PLC1 ↔ PLC2 (Giai Đoạn Sau)

*   **Nguyên tắc:** Việc trao đổi dữ liệu mẻ và phân xử cụm bồn chứa giữa 2 PLC vật lý sẽ được thực hiện thông qua liên kết Modbus TCP ở giai đoạn sau của dự án.
*   **Giải pháp:**
    *   `PLC2` hoạt động như một Modbus TCP Server (`MB_SERVER` V3.1) mở cổng 502, trỏ vùng Holding Registers vào DB chia sẻ dữ liệu.
    *   `PLC1` hoạt động như một Modbus TCP Client (`MB_CLIENT` V3.1), gọi tuần tự các lệnh đọc/ghi để kéo dữ liệu trạng thái Bồn 3, Bồn 4 và đẩy lệnh đồng bộ, lệnh bắt tay xuống `PLC2`.
    *   Tất cả các thông số kết nối IP (Struct `TCON_IP_v4`) sẽ được gán động tại hàm khởi tạo `FirstScan` trong SCL để bảo toàn tính độc lập dữ liệu.
