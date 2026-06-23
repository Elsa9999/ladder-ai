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
| **FC40** | `FC_Sensor_Sim` | SCL | Hàm chức năng | **Chỉ dùng cho bản mô phỏng 1 PLC:** Giả lập dâng/hạ mức dịch theo trạng thái van/bơm. **KHÔNG tự viết thuật toán PID.** Nhiệt độ bồn mô phỏng qua PID_Compact_2 chạy trong OB31 với PV từ tag nội bộ thay thế cảm biến thật. |
| **DB10** | `Inst_Mixing_Branch_1`| DB | Instance DB | Dữ liệu làm việc cho Nhánh 1 (PLC1). |
| **DB11** | `Inst_Mixing_Branch_2`| DB | Instance DB | Dữ liệu làm việc cho Nhánh 2 (PLC2 hoặc truyền thông nội bộ). |
| **DB20** | `Inst_Storage_Filter` | DB | Instance DB | Dữ liệu làm việc cho cụm bồn chứa thành phẩm. |
| **DB_HMI** | `DB_HMI_Data` | DB | Global DB | Vùng nhớ lưu trữ các cờ lệnh, cài đặt và giám sát liên kết trực tiếp với WinCC. |
| **DB_Comms**| `DB_Comms_Buffer` | DB | Global DB | Vùng đệm dữ liệu truyền thông Modbus TCP/RTU. |

---

## 2. Các Khối Công Nghệ & Thư Viện Giữ Nguyên Dạng Mặc Định

Các khối điều khiển công nghệ đặc thù của Siemens sẽ không được viết lại bằng SCL mà được gọi (Call) trực tiếp dưới dạng **Technology Object** hoặc các khối thư viện hệ thống đóng gói sẵn:

1.  **`PID_Compact` (Version 1.2) — Bồn 2 và Bồn 4:**
    *   **`PID_Compact_1` (PLC1/OB30, chu kỳ 100ms):** PV = `TT3208_Bon2_Eff` (hoặc tag nhiệt độ hiệu dụng Bồn 2); SP = `HMI_SP_PLC1_Nhiet_Do_Bon2`; Output = `CV3206_Hoi_Bon2`.
    *   **`PID_Compact_2` (PLC2/OB31, chu kỳ 100ms):** PV = `TT3219_Bon4_Eff` (nhiệt độ hiệu dụng Bồn 4 — có thể là cảm biến thật hoặc tag mô phỏng offline); SP = `HMI_SP_PLC2_Nhiet_Do_Bon4`; Output = `CV3216_Hoi_Bon4`.
    *   **Quy tắc bắt buộc:** SCL chỉ gọi và điều phối `PID_Compact`, **không được tự viết thuật toán PID riêng**.
2.  **`Modbus_Comm_Load` (Version 2.1) & `Modbus_Master` (Version 2.2):** Các khối thư viện phục vụ truyền thông Modbus RTU điều khiển biến tần ATV12.
3.  **`MB_CLIENT` (Version 3.1) & `MB_SERVER` (Version 3.1):** Các khối thư viện phục vụ truyền thông Modbus TCP trao đổi dữ liệu giữa PLC1 và PLC2.

---

## 3. Yêu Cầu Bắt Buộc Trước Khi Viết SCL Gọi PID_Compact

> [!CAUTION]
> **NGHIÊM CẤM** viết SCL call PID_Compact cho đến khi đã:
> 1. Export readback Technology Object `PID_Compact_1` và `PID_Compact_2` thực tế từ TIA Portal V18.
> 2. Lập đầy đủ bảng chân (I/O pin table) thực tế của PID_Compact V1.2 từ dữ liệu readback XML.
> 3. Xác nhận tên chính xác của từng chân (ví dụ: chân Output có thể là `Output`, `OutputValue`, hay cấu trúc khác — **không được bịa đặt**).

### 3.1. Cấu Hình PID Bồn 2 (PLC1 / OB30 / chu kỳ 100ms)

| Chân PID_Compact | Nguồn dữ liệu | Ghi chú |
| :--- | :--- | :--- |
| `Setpoint` (IN, Real) | `HMI_SP_PLC1_Nhiet_Do_Bon2` | Setpoint nhiệt độ Bồn 2 từ HMI |
| `Input` (IN, Real) | `TT3208_Bon2_Eff` | Nhiệt độ hiệu dụng Bồn 2 |
| `Reset` (IN, Bool) | Cờ reset hệ thống | Xóa trạng thái PID khi reset |
| `sRet.i_Mode` (InOut, Int) | Ghi `3` khi Enable / `0` khi Disable | **Bắt buộc** — chống mode-locking |
| `Output` / chân CV (OUT) | → `CV3206_Hoi_Bon2` | **Tên chân cần xác nhận từ readback TIA** |

### 3.2. Cấu Hình PID Bồn 4 (PLC2 / OB31 / chu kỳ 100ms)

| Chân PID_Compact | Nguồn dữ liệu | Ghi chú |
| :--- | :--- | :--- |
| `Setpoint` (IN, Real) | `HMI_SP_PLC2_Nhiet_Do_Bon4` | Setpoint nhiệt độ Bồn 4 từ HMI |
| `Input` (IN, Real) | `TT3219_Bon4_Eff` | Nhiệt độ hiệu dụng Bồn 4 (cảm biến thật hoặc tag mô phỏng offline) |
| `Reset` (IN, Bool) | Cờ reset hệ thống | Xóa trạng thái PID khi reset |
| `sRet.i_Mode` (InOut, Int) | Ghi `3` khi Enable / `0` khi Disable | **Bắt buộc** — chống mode-locking |
| `Output` / chân CV (OUT) | → `CV3216_Hoi_Bon4` | **Tên chân cần xác nhận từ readback TIA** |

### 3.3. Mẫu Cú Pháp SCL (DRAFT — chưa compile-ready)

> [!WARNING]
> Đoạn code dưới đây là **mẫu tham khảo ý định gọi**, **CHƯA được xác nhận compile trong TIA Portal**. Các tên chân như `Output`, `Input`, `Reset` có thể sai so với chân thực tế của PID_Compact V1.2. Phải thay bằng tên chính xác lấy từ readback XML.

```scl
// === OB30 — PID Bồn 2 (PLC1) ===
// Bước 1: Điều phối chế độ PID (MOVE 3/0 vào sRet.i_Mode)
IF PID_Bon2_Enable THEN
    "Inst_PID_Compact_1".sRet.i_Mode := 3;   // Auto
ELSE
    "Inst_PID_Compact_1".sRet.i_Mode := 0;   // Inactive
END_IF;

// Bước 2: Gọi khối PID_Compact (tên chân cần xác nhận từ TIA readback)
// "Inst_PID_Compact_1"(
//     Setpoint := HMI_SP_PLC1_Nhiet_Do_Bon2,
//     Input    := TT3208_Bon2_Eff,
//     Reset    := Reset_Active,
//     <Output_pin_confirmed_from_readback> => PID_Bon2_CV
// );

// Bước 3: Gán ngõ ra (sau khi xác nhận tên chân)
// CV3206_Hoi_Bon2 := PID_Bon2_CV;
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
