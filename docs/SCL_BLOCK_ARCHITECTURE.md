# KIẾN TRÚC KHỐI CHƯƠNG TRÌNH SCL (SCL BLOCK ARCHITECTURE)

Tài liệu này đặc tả cấu trúc phân bổ khối (OB, FB, FC, DB) cho phiên bản SCL mới, quy định rõ ngôn ngữ lập trình cho từng khối và phương thức gọi các thư viện công nghệ của Siemens.

---

## 1. Bản Đồ Phân Phổ Khối Chương Trình (Program Block Map)

| Ký Hiệu | Tên Khối | Ngôn Ngữ | Loại Khối | Vai Trò & Chức Năng |
| :--- | :--- | :--- | :--- | :--- |
| **OB1** | `Main` | SCL | Tổ chức (OB) | Điều phối quét chu kỳ chính, gọi các FB/FC điều khiển nhánh và bồn chứa. |
| **OB30** | `PID_Loop_Bon2` | SCL | Ngắt chu kỳ | Quét định kỳ 100ms cho `PID_Compact_1` điều khiển nhiệt độ Bồn 2. Có mặt trên **cả bản A (1 PLC) và bản B (PLC1)**. |
| **OB31** | `PID_Loop_Bon4` | SCL | Ngắt chu kỳ | Quét định kỳ 100ms cho `PID_Compact_2` điều khiển nhiệt độ Bồn 4. **Bản A:** OB31 nằm trên PLC1 duy nhất. **Bản B:** OB31 nằm trên PLC2. |
| **FB10** | `FB_Mixing_Branch` | SCL | Function Block | Chứa logic chạy tuần tự (CASE) cho một nhánh (Bồn A + Bồn B). Dùng chung instance cho Nhánh 1 và Nhánh 2. |
| **FB20** | `FB_Storage_Filter` | SCL | Function Block | Quản lý phân xử quyền sở hữu bồn chứa, logic giải nhiệt, bơm chuyển qua màng lọc và chiết rót. |
| **FB30** | `FB_VFD_ATV12_ModbusRTU` | SCL | Function Block | **Thay thế FC30.** Chứa toàn bộ State Machine + timer nội bộ + retry counter + buffer + edge flag điều khiển tuần tự Modbus RTU cho biến tần ATV12. Phải có Instance DB riêng để lưu trạng thái giữa các chu kỳ quét. |
| **FC40** | `FC_Sensor_Sim` | SCL | Function | **Chỉ dùng cho bản A (mô phỏng 1 PLC):** Giả lập dâng/hạ mức dịch theo trạng thái van/bơm. **KHÔNG tự viết thuật toán PID.** PV nhiệt độ mô phỏng là tag nội bộ; `PID_Compact_1/_2` vẫn là bộ điều khiển chuẩn Siemens sinh CV thật. |
| **DB10** | `Inst_Mixing_Branch_1` | DB | Instance DB | Dữ liệu làm việc cho Nhánh 1 (PLC1). |
| **DB11** | `Inst_Mixing_Branch_2` | DB | Instance DB | Dữ liệu làm việc cho Nhánh 2 (PLC2 — bản B; hoặc PLC1 nội bộ — bản A). |
| **DB20** | `Inst_Storage_Filter` | DB | Instance DB | Dữ liệu làm việc cho cụm bồn chứa thành phẩm. |
| **DB30** | `Inst_VFD_ATV12` | DB | Instance DB | Dữ liệu làm việc của `FB_VFD_ATV12_ModbusRTU`: state machine step, timer, retry counter, MB buffer, last status word, edge flag. |
| **DB_HMI** | `DB_HMI_Data` | DB | Global DB | Vùng nhớ lưu trữ các cờ lệnh, cài đặt và giám sát liên kết trực tiếp với WinCC. |
| **DB_Comms** | `DB_Comms_Buffer` | DB | Global DB | Vùng đệm dữ liệu truyền thông Modbus TCP (bản B). Modbus RTU buffer nằm trong `DB30` (Instance DB của FB30). |

---

## 2. Các Khối Công Nghệ & Thư Viện Giữ Nguyên Dạng Mặc Định

Các khối điều khiển công nghệ đặc thù của Siemens sẽ không được viết lại bằng SCL mà được gọi (Call) trực tiếp dưới dạng **Technology Object** hoặc các khối thư viện hệ thống đóng gói sẵn:

1.  **`PID_Compact` (Version 1.2) — Bồn 2 và Bồn 4:**
    *   **`PID_Compact_1` (OB30, 100ms):** PV = `TT3208_Bon2_Eff`; SP = `HMI_SP_PLC1_Nhiet_Do_Bon2`; CV → `CV3206_Hoi_Bon2`. Nằm trên **PLC1** (cả bản A và bản B).
    *   **`PID_Compact_2` (OB31, 100ms):** PV = `TT3219_Bon4_Eff` (cảm biến thật — bản B; hoặc tag nội bộ mô phỏng quá trình — bản A); SP = `HMI_SP_PLC2_Nhiet_Do_Bon4`; CV → `CV3216_Hoi_Bon4`. **Bản A:** nằm trên PLC1 duy nhất. **Bản B:** nằm trên PLC2.
    *   **Quy tắc bắt buộc:** SCL chỉ gọi và điều phối `PID_Compact`. PID_Compact **không mô phỏng nhiệt độ** — nó là bộ điều khiển chuẩn Siemens sinh CV. PV có thể lấy từ tag nội bộ thay cảm biến thật khi chạy offline.
    *   **Nghiêm cấm tự viết thuật toán PID riêng.**
2.  **`Modbus_Comm_Load` (Version 2.1) & `Modbus_Master` (Version 2.2):** Thư viện Modbus RTU điều khiển ATV12, được gọi bên trong `FB_VFD_ATV12_ModbusRTU` (FB30).
3.  **`MB_CLIENT` (Version 3.1) & `MB_SERVER` (Version 3.1):** Thư viện Modbus TCP — **chỉ sử dụng ở bản B (2 PLC thật)**. Bản A không dùng.

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

## 4. Thiết Kế FB_VFD_ATV12_ModbusRTU (FB30 thay thế FC30)

### 4.1. Lý Do Dùng FB Thay FC

ATV12 cần lưu trạng thái **liên tục giữa các chu kỳ quét** bao gồm: bước State Machine, timer retry, đếm lỗi, buffer Modbus, last status word, edge flag bật/tắt. FC không có Static Variables — không thể lưu các giá trị này. **Phải dùng FB30 với Instance DB30 (`Inst_VFD_ATV12`).**

### 4.2. Cấu Trúc Static Variables của FB30 (DB30)

| Biến | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `iStep` | Int | Bước State Machine hiện tại (0–3) |
| `CommLoad_Done` | Bool | Cờ Comm Load hoàn thành |
| `CommLoad_Req` | Bool | Yêu cầu chạy Comm Load |
| `MB_Req` | Bool | Yêu cầu giao dịch Modbus |
| `MB_Done` | Bool | Giao dịch Modbus hoàn thành |
| `MB_Busy` | Bool | Đang xử lý Modbus |
| `MB_Error` | Bool | Có lỗi giao dịch |
| `MB_Status` | Word | Mã trạng thái Modbus |
| `MB_ErrorCount` | Int | Đếm số lỗi liên tiếp |
| `MB_Buffer` | Array[0..3] of Word | Bộ đệm dữ liệu đọc/ghi |
| `VFD_StatusWord` | Word | Status Word đọc về từ ATV12 |
| `VFD_FreqActual` | Word | Tần số thực tế đọc về từ ATV12 |
| `R_TRIG_Enable` | R_TRIG | Edge flag phát hiện cạnh lên lệnh Enable VFD |
| `TON_Retry` | TON | Timer trễ retry sau lỗi (200ms) |

### 4.3. Yêu Cầu Bắt Buộc Trước Khi Viết SCL FB30

> [!CAUTION]
> **Nghiêm cấm hard-code PORT (HW ID) của CB1241** vào bất kỳ dòng SCL nào (ví dụ: `"PORT" := 260` là SAI — giá trị HW ID thay đổi theo cấu hình TIA). **PORT/HW ID phải được lấy từ TIA device configuration readback** hoặc khai báo là hằng số `HW_IO` trong Symbol Table của TIA trước khi viết code compile-ready.

### 4.4. Mẫu Cấu Trúc SCL FB30 (DRAFT — chưa compile-ready)

> [!WARNING]
> Đoạn dưới đây là **mẫu ý định thiết kế**, chưa xác nhận compile. PORT phải được điền sau khi có readback HW ID. Tên chân `Modbus_Comm_Load` / `Modbus_Master` cần xác nhận phiên bản.

```scl
// === FB_VFD_ATV12_ModbusRTU — được gọi từ OB1 ===
// Static Variables nằm trong Instance DB30 (Inst_VFD_ATV12)

// Bước 0: Comm Load tại First Scan
IF #First_Scan AND NOT #CommLoad_Done THEN
    #CommLoad_Req := TRUE;
END_IF;

// [CHƯA COMPILE-READY] Gọi Modbus_Comm_Load
// PORT := <HW_ID_CB1241_tu_readback_TIA>  -- KHÔNG hard-code
// "Inst_Comm_Load"(
//     REQ   := #CommLoad_Req,
//     PORT  := <xac_nhan_tu_TIA_device_config>,
//     BAUD  := 19200,
//     PARITY := 1,
//     RESP_TO := 1000,
//     DONE  => #CommLoad_Done,
//     ERROR => #MB_Error,
//     STATUS => #MB_Status
// );
IF #CommLoad_Done THEN
    #CommLoad_Req := FALSE;
END_IF;

// Bước 1: State Machine (chỉ chạy sau khi Comm Load xong)
IF #CommLoad_Done THEN
    // Timer retry 200ms sau lỗi
    #TON_Retry(IN := #MB_Error, PT := T#200MS);

    IF NOT #MB_Busy AND (NOT #MB_Error OR #TON_Retry.Q) THEN
        #MB_Req := TRUE;
    END_IF;

    IF NOT #MB_Busy THEN
        CASE #iStep OF
            0: // ĐỌC Status Word ATV12
            1: // ĐỌC Tần số thực tế
            2: // GHI Control Word
            3: // GHI Tần số đặt
        END_CASE;
    END_IF;

    // [CHƯA COMPILE-READY] Gọi Modbus_Master instance duy nhất
    // "Inst_Modbus_Master"( REQ := #MB_Req, ... );

    IF #MB_Done THEN
        #MB_ErrorCount := 0;
        #iStep := (#iStep + 1) MOD 4;
    ELSIF #MB_Error THEN
        #MB_ErrorCount := #MB_ErrorCount + 1;
        IF #MB_ErrorCount >= 3 THEN
            // Chốt lỗi truyền thông VFD
        END_IF;
    END_IF;
END_IF;
```

---

## 5. Kế Hoạch Truyền Thông Modbus TCP PLC1 ↔ PLC2 (Chỉ Bản B)

> [!IMPORTANT]
> **Modbus TCP chỉ có trong bản B (2 PLC thật).** Bản A (1 PLC) không sử dụng `MB_CLIENT` / `MB_SERVER`. Bản A trao đổi dữ liệu giữa hai nhánh qua Internal Struct trong DB nội bộ.

*   **Bản B — Nguyên tắc phân vai:**
    *   `PLC2` hoạt động như Modbus TCP Server (`MB_SERVER` V3.1), mở cổng 502, trỏ Holding Registers vào DB chia sẻ dữ liệu Bồn 3–4.
    *   `PLC1` hoạt động như Modbus TCP Client (`MB_CLIENT` V3.1), đọc/ghi dữ liệu trạng thái Bồn 3, Bồn 4 và đẩy lệnh đồng bộ xuống `PLC2`.
    *   Tất cả thông số kết nối IP (Struct `TCON_IP_v4`) gán động tại `FirstScan` trong SCL.
