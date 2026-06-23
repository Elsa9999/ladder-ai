# ÁNH XẠ GRAFCET → SCL STATE MACHINE (VARIANT A)

Tài liệu này chuyển đổi Grafcet đề thi tự động hóa sang cấu trúc SCL `CASE...OF`
dùng cho **Variant A (1 PLC)**. Đây là tài liệu thiết kế — **chưa phải code compile-ready**.

> [!CAUTION]
> Tài liệu này dựa trên Grafcet tham chiếu từ đề thi. Khi có đề chính thức,
> cần đối chiếu lại từng bước và cập nhật trước khi code.

---

## 1. Tổng Quan Quy Trình Mixing Nước Tương Maggi

### 1.1. Cấu Trúc Hệ Thống

```
Nhánh 1 (PLC1 — Variant A)        Nhánh 2 (PLC1 — Variant A)
├── Bồn 1: Dosing nước              ├── Bồn 3: Dosing nước
│   Van CV3201 (tuyến tính)         │   Van CV3301 (tuyến tính)
│   Cảm biến FT3200, LT3203, TT3204 │   Cảm biến FT3300, LT3303, TT3304
│                                   │
└── Bồn 2: Gia nhiệt + Khuấy       └── Bồn 4: Gia nhiệt + Khuấy
    Van hơi CV3206 (PID_Compact_1)      Van hơi CV3216 (PID_Compact_2)
    Biến tần ATV12 (khuấy)              [Mô phỏng khi Variant A]
    Cảm biến TT3208_Bon2_Eff

Cụm Bồn Chứa + Lọc + Chiết Rót (chung)
```

### 1.2. Các Giai Đoạn Chính (Master Steps)

| Giai đoạn | Mã bước | Mô tả |
| :--- | :---: | :--- |
| Chờ / Nghỉ | `0` | Idle, chờ lệnh Start |
| Cấp nguyên liệu | `10` | Dosing nước, tương, gia vị vào Bồn 1/3 |
| Khuấy | `20` | Khuấy trộn theo thời gian cài đặt |
| Gia nhiệt | `30` | PID_Compact điều nhiệt Bồn 2/4 |
| Giữ nhiệt (Thanh trùng) | `40` | Duy trì SP nhiệt độ theo thời gian |
| Xả đáy chuyển bồn | `50` | Mở van xả, bơm sang bồn chứa |
| Nghỉ chờ mẻ tiếp | `60` | Reset đếm, chờ confirm mẻ mới |

---

## 2. Grafcet Bồn 1 → SCL State Machine

### 2.1. Mã Bước — Bồn 1 (`DB_OperationData.Bon1.state`)

| State | Tên Bước Grafcet | Điều kiện CHUYỂN (Transition) | Hành động (Action) |
| :---: | :--- | :--- | :--- |
| `0` | S0 — Idle | `Auto_Enable AND Start_Cmd` → `10` | Tắt tất cả |
| `10` | S1 — Cấp nước | `FQ3200_Bon1 >= sp_nuoc_bon1` → `20` | Mở `CV3201_Nuoc_Bon1` (tuyến tính), đặt Flow SP |
| `20` | S2 — Khuấy | `Timer_Khuay_Bon1.Q` → `30` | Bật `AGTR3260_Khuay_Bon1`, chạy timer |
| `30` | S3 — Idle chờ Bồn 2 | `Bon2.state = 40` → `50` | Dừng khuấy, giữ nguyên |
| `50` | S4 — Xả Bồn 1 | `LT3203_Bon1 <= LT_Empty_Threshold` → `60` | Mở `V3232/V3233/V3234_Xa_Bon1`, bật `Pump3264` |
| `60` | S5 — Hoàn thành | `Operator_Confirm_Next_Batch` → `0` | Đóng tất cả, reset bộ đếm |

### 2.2. Cú Pháp SCL CASE Tương Ứng (DRAFT)

```scl
// === FB_MixingBranch — State Machine Bồn 1 ===
// Chạy từ OB1 (Main) mỗi chu kỳ quét

CASE #Bon1_State OF
    0: // ===== IDLE =====
        // Đóng tất cả output Bồn 1
        CV3201_Nuoc_Bon1 := 0.0;
        AGTR3260_Khuay_Bon1 := FALSE;
        V3232_Xa_Bon1 := FALSE;
        // Điều kiện chuyển bước
        IF #Auto_Enable AND #Start_Cmd THEN
            #Bon1_State := 10;
        END_IF;

    10: // ===== CẤP NƯỚC =====
        CV3201_Nuoc_Bon1 := #SP_DoSing_Flow; // AO tuyến tính
        IF FQ3200_Bon1 >= #sp_nuoc_bon1 THEN
            CV3201_Nuoc_Bon1 := 0.0;
            #Bon1_State := 20;
        END_IF;

    20: // ===== KHUẤY =====
        AGTR3260_Khuay_Bon1 := TRUE;
        #Timer_Khuay_Bon1(IN := TRUE, PT := #sp_time_khuay_bon1);
        IF #Timer_Khuay_Bon1.Q THEN
            AGTR3260_Khuay_Bon1 := FALSE;
            #Timer_Khuay_Bon1(IN := FALSE, PT := #sp_time_khuay_bon1);
            #Bon1_State := 30;
        END_IF;

    30: // ===== CHỜ BỒN 2 XONG GIA NHIỆT =====
        // Chờ Bồn 2 hoàn thành bước 40 (Giữ nhiệt)
        IF #Bon2_State = 40 THEN
            #Bon1_State := 50;
        END_IF;

    50: // ===== XẢ ĐÁY =====
        V3232_Xa_Bon1 := TRUE;
        V3233_Xa_Bon1 := TRUE;
        V3234_Xa_Bon1 := TRUE;
        Pump3264_Chuyen_Nhanh1 := TRUE;
        IF LT3203_Bon1 <= #LT_Empty_Threshold THEN
            V3232_Xa_Bon1 := FALSE; V3233_Xa_Bon1 := FALSE; V3234_Xa_Bon1 := FALSE;
            Pump3264_Chuyen_Nhanh1 := FALSE;
            #Bon1_State := 60;
        END_IF;

    60: // ===== CHỜ XÁC NHẬN MẺ TIẾP =====
        IF #Operator_Confirm_Next_Batch THEN
            #Bon1_State := 0;
        END_IF;

    ELSE: // Bước không hợp lệ — về Idle an toàn
        #Bon1_State := 0;
END_CASE;
```

---

## 3. Grafcet Bồn 2 → SCL State Machine (Có PID)

### 3.1. Mã Bước — Bồn 2 (`DB_OperationData.Bon2.state`)

| State | Tên Bước Grafcet | Điều kiện CHUYỂN | Hành động |
| :---: | :--- | :--- | :--- |
| `0` | S0 — Idle | `Bon1.state = 20` → `10` | Tắt tất cả Bồn 2 |
| `10` | S1 — Nhận dịch từ Bồn 1 | `LT3208_Bon2 >= LT_Fill_Threshold` → `20` | Chờ van xả Bồn 1 chuyển sang |
| `20` | S2 — Cấp nước bổ sung | `FQ3206_Bon2 >= sp_nuoc_bon2` → `30` | Mở `V3235_Nuoc_Bon2` |
| `30` | S3 — Gia nhiệt (PID) | `TT3208_Bon2_Eff >= SP_NhietDo - 2°C` → `40` | Enable `PID_Compact_1`, bật ATV12 khuấy |
| `40` | S4 — Giữ nhiệt | `Timer_ThanhTrung_Bon2.Q` → `50` | Duy trì PID, đếm thời gian |
| `50` | S5 — Xả đáy | `LT3208_Bon2 <= LT_Empty_Threshold` → `0` | Disable PID, mở `V3237/V3238/V3239_Xa_Bon2` |

### 3.2. Cú Pháp SCL PID + State Machine Bồn 2 (DRAFT)

```scl
// === OB30 (100ms) — PID_Compact_1 điều khiển Bồn 2 ===
// Bước 1: Điều phối chế độ (phải chạy mỗi chu kỳ OB30)
IF DB_OperationData.Bon2.pid_enable THEN
    "Inst_PID_Compact_1".sRet.i_Mode := 3;  // Auto
ELSE
    "Inst_PID_Compact_1".sRet.i_Mode := 0;  // Inactive
END_IF;

// Bước 2: Gọi PID_Compact (tên chân xác nhận từ readback TIA)
// "Inst_PID_Compact_1"(
//     Setpoint := DB_HmiData.Setpoint.sp_nhiet_do_bon2,
//     Input    := TT3208_Bon2_Eff,
//     Reset    := DB_OperationData.Sys.estop_latch,
//     <CV_pin_from_readback> => DB_OperationData.Bon2.pid_cv
// );
// CV3206_Hoi_Bon2 := DB_OperationData.Bon2.pid_cv;

// === OB1 — State Machine Bồn 2 ===
CASE #Bon2_State OF
    0:  // IDLE — PID tắt
        DB_OperationData.Bon2.pid_enable := FALSE;
        IF DB_OperationData.Bon1.state = 20 THEN #Bon2_State := 10; END_IF;

    10: // NHẬN DỊCH
        IF LT3208_Bon2 >= #LT_Fill_Threshold THEN #Bon2_State := 20; END_IF;

    20: // CẤP NƯỚC BỔ SUNG
        V3235_Nuoc_Bon2 := TRUE;
        IF FQ3206_Bon2 >= #sp_nuoc_bon2 THEN
            V3235_Nuoc_Bon2 := FALSE;
            #Bon2_State := 30;
        END_IF;

    30: // GIA NHIỆT (kích hoạt PID)
        DB_OperationData.Bon2.pid_enable := TRUE;
        // ATV12 khuấy — gọi qua FB30 nếu có phần cứng
        IF TT3208_Bon2_Eff >= (DB_HmiData.Setpoint.sp_nhiet_do_bon2 - 2.0) THEN
            #Bon2_State := 40;
        END_IF;

    40: // GIỮ NHIỆT (đếm thời gian thanh trùng)
        DB_OperationData.Bon2.pid_enable := TRUE;
        #Timer_ThanhTrung_Bon2(IN := TRUE, PT := #sp_time_thanh_trung_bon2);
        IF #Timer_ThanhTrung_Bon2.Q THEN
            #Timer_ThanhTrung_Bon2(IN := FALSE, PT := T#0S);
            #Bon2_State := 50;
        END_IF;

    50: // XẢ ĐÁY
        DB_OperationData.Bon2.pid_enable := FALSE;
        V3237_Xa_Bon2 := TRUE;
        V3238_Xa_Bon2 := TRUE;
        V3239_Xa_Bon2 := TRUE;
        IF LT3208_Bon2 <= #LT_Empty_Threshold THEN
            V3237_Xa_Bon2 := FALSE; V3238_Xa_Bon2 := FALSE; V3239_Xa_Bon2 := FALSE;
            #Bon2_State := 0;
        END_IF;

    ELSE: #Bon2_State := 0;
END_CASE;
```

---

## 4. Grafcet Bồn 3 & Bồn 4 (Nhánh 2 — Variant A Nội Bộ)

### 4.1. Nguyên Tắc

- Bồn 3 và Bồn 4 trong Variant A **dùng cùng FB10 `FB_MixingBranch`**, chỉ khác Instance DB.
- Instance DB11 (Nhánh 2) giữ state riêng cho Bồn 3 và Bồn 4.
- Bồn 4 dùng `PID_Compact_2` (OB31 trên PLC1), PV là **tag mô phỏng** từ `FC_Sensor_Sim`.

### 4.2. Mô Phỏng Quá Trình (FC40 `FC_Sensor_Sim`)

```
FC_Sensor_Sim cung cấp:
- LT_Bon3_Sim: Mức dịch Bồn 3 mô phỏng (dâng khi van cấp mở, hạ khi van xả mở)
- LT_Bon4_Sim: Mức dịch Bồn 4 mô phỏng
- TT3219_Bon4_Sim: Nhiệt độ Bồn 4 mô phỏng (tăng khi PID_CV > 0)

KHÔNG tự tính PID. PID_Compact_2 nhận TT3219_Bon4_Sim làm PV và sinh CV thật.
```

---

## 5. Safety Logic (Chạy Mỗi Chu Kỳ Quét OB1)

> [!WARNING]
> Safety logic phải chạy **trước** khi gọi FB_MixingBranch, không được đặt sau.

```scl
// === SAFETY CHECK (ưu tiên cao nhất) ===
// E-Stop chốt (latch)
IF NOT Nut_EStop THEN  // NC contact
    DB_OperationData.Sys.estop_latch := TRUE;
END_IF;

// Khóa tổng khi E-Stop hoặc lỗi tổng
IF DB_OperationData.Sys.estop_latch OR DB_OperationData.Sys.loi_tong THEN
    // Tắt toàn bộ output nguy hiểm
    CV3206_Hoi_Bon2 := 0.0;
    CV3216_Hoi_Bon4 := 0.0;
    // Reset PID
    DB_OperationData.Bon2.pid_enable := FALSE;
    DB_OperationData.Bon4.pid_enable := FALSE;
END_IF;

// Reset E-Stop (chỉ khi Nut_Reset + xác nhận an toàn)
IF Nut_Reset AND Nut_EStop THEN  // EStop đã nhả
    DB_OperationData.Sys.estop_latch := FALSE;
END_IF;
```

---

## 6. Checklist Ánh Xạ Grafcet → SCL (Cần Xác Nhận Trước Khi Code)

- [ ] Xác nhận số bước Grafcet đầy đủ từ đề thi chính thức
- [ ] Xác nhận điều kiện chuyển bước cho Bồn 3 và Bồn 4
- [ ] Xác nhận tên chân PID_Compact_1 và PID_Compact_2 từ readback TIA
- [ ] Xác nhận địa chỉ I/O Bồn 3, Bồn 4 từ `generate_mixing_project.py`
- [ ] Xác nhận thời gian khuấy, thời gian thanh trùng từ công thức Maggi
- [ ] Xác nhận ngưỡng mức dịch LT_Fill và LT_Empty từ datasheets cảm biến
