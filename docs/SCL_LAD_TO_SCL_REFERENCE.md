# BẢNG THAM CHIẾU LAD → SCL (SCL LAD-TO-SCL REFERENCE)

Tài liệu này ánh xạ từng thành phần của bản LAD cũ
(`projects/Mixing_Nuoc_Tuong_Maggi_2026`) sang thiết kế SCL mới,
chủ yếu phục vụ **Variant B (2 PLC đấu nối thực tế)**.

> [!NOTE]
> Bản LAD cũ **KHÔNG bị sửa hay xóa**. Đây chỉ là bảng ánh xạ tham chiếu.
> Tất cả địa chỉ I/O vật lý giữ nguyên — KHÔNG đổi địa chỉ `%I`, `%Q`, `%ID`, `%QD`.

---

## 1. Ánh Xạ Khối Chương Trình LAD → SCL

| Khối LAD Cũ | Ngôn ngữ | Vai trò | Khối SCL Mới | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| `OB1 Main` | LAD | Điều phối chính | `OB1 Main` (SCL) | Gọi FB10, FB20, FB30, safety |
| `OB30 PID_Cycle` | LAD | OB ngắt PID Bồn 2 | `OB30 PID_Loop_Bon2` (SCL) | Giữ nguyên OB number |
| `FB_Mixing` | LAD | Sequencer nhánh | `FB10 FB_MixingBranch` (SCL) | Gom cả 2 nhánh vào 1 FB |
| `FC_VFD_Control` | LAD | Điều khiển ATV12 | `FB30 FB_VFD_ATV12_ModbusRTU` (SCL) | **FC → FB** vì cần Static Var |
| `FC_Safety` | LAD | An toàn, E-Stop | Logic inline trong `OB1` (SCL) | Đơn giản hóa, không cần FC riêng |
| `DB_Global` (M-area) | — | Biến M-area toàn cục | `DB100–DB103` (SCL DB) | **Dứt khoát xóa M-area** |
| `Inst_PID_Bon2` | — | Instance PID | `Inst_PID_Compact_1` (trong TIA TO) | Giữ nguyên cấu hình PID |

---

## 2. Ánh Xạ Tag/Biến LAD → SCL (Bảng Đầy Đủ)

### 2.1. Biến I/O Vật Lý — Giữ Nguyên Địa Chỉ

| Tag LAD Cũ | Địa chỉ | Tag SCL Mới | Địa chỉ | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| `AI_Nut_Khoi_Dong` | `%I0.0` | `Nut_Khoi_Dong` | `%I0.0` | Bỏ tiền tố `AI_` |
| `AI_Nut_Dung` | `%I0.1` | `Nut_Dung` | `%I0.1` | |
| `AI_Nut_Reset` | `%I0.2` | `Nut_Reset` | `%I0.2` | |
| `AI_Nut_EStop` | `%I0.3` | `Nut_EStop` | `%I0.3` | |
| `AI_LS3202_Bon1_Cao` | `%I0.4` | `LS3202_Bon1_Cao` | `%I0.4` | |
| `AI_FT3200_Bon1` | `%ID100` | `FT3200_Bon1` | `%ID100` | |
| `AI_FQ3200_Bon1` | `%ID104` | `FQ3200_Bon1` | `%ID104` | |
| `AI_LT3203_Bon1` | `%ID108` | `LT3203_Bon1` | `%ID108` | |
| `AI_TT3204_Bon1` | `%ID112` | `TT3204_Bon1` | `%ID112` | |
| `AI_VFD_Bon2_Contactor` | `%Q0.0` | `VFD_Bon2_Contactor` | `%Q0.0` | Contactor ATV12 |
| `AI_AGTR3260_Khuay_Bon1` | `%Q0.1` | `AGTR3260_Khuay_Bon1` | `%Q0.1` | |
| `AI_V3232_Xa_Bon1` | `%Q0.2` | `V3232_Xa_Bon1` | `%Q0.2` | |
| `AI_V3233_Xa_Bon1` | `%Q0.3` | `V3233_Xa_Bon1` | `%Q0.3` | |
| `AI_V3234_Xa_Bon1` | `%Q0.4` | `V3234_Xa_Bon1` | `%Q0.4` | |
| `AI_V3235_Nuoc_Bon2` | `%Q0.5` | `V3235_Nuoc_Bon2` | `%Q0.5` | |
| `AI_V3237_Xa_Bon2` | `%Q0.6` | `V3237_Xa_Bon2` | `%Q0.6` | |
| `AI_V3238_Xa_Bon2` | `%Q0.7` | `V3238_Xa_Bon2` | `%Q0.7` | |
| `AI_V3239_Xa_Bon2` | `%Q1.0` | `V3239_Xa_Bon2` | `%Q1.0` | |
| `AI_Pump3264_Chuyen_Nhanh1` | `%Q1.1` | `Pump3264_Chuyen_Nhanh1` | `%Q1.1` | |
| `AI_CV3201_Nuoc_Bon1` | `%QD100` | `CV3201_Nuoc_Bon1` | `%QD100` | AO tuyến tính |
| `AI_AGTR3260_Toc_Do_AO` | `%QD104` | `AGTR3260_Toc_Do_AO` | `%QD104` | AO tốc độ khuấy |
| `AI_CV3206_Hoi_Bon2` | `%QD108` | `CV3206_Hoi_Bon2` | `%QD108` | AO van hơi PID output |

### 2.2. Biến M-Area LAD → DB SCL

| Biến LAD Cũ (M-area) | Địa chỉ | Biến SCL Mới (DB) | Kiểu | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| `AI_Auto_Enable` | `%M110.0` | `DB_OperationData.Sys.auto_enable` | Bool | |
| `AI_EStop_Latch` | `%M110.1` | `DB_OperationData.Sys.estop_latch` | Bool | |
| `AI_Loi_Tong` | `%M110.2` | `DB_OperationData.Sys.loi_tong` | Bool | |
| `AI_Loi_Dry_Run` | `%M110.3` | `DB_OperationData.Sys.loi_dry_run` | Bool | |
| `AI_Bon1_State` | `%MW120` | `DB_OperationData.Bon1.state` | Int | Bước tuần tự |
| `AI_Bon2_State` | `%MW122` | `DB_OperationData.Bon2.state` | Int | |
| `AI_PID_Enable_Bon2` | `%M124.0` | `DB_OperationData.Bon2.pid_enable` | Bool | |
| `AI_PID_CV_Bon2` | `%MD130` | `DB_OperationData.Bon2.pid_cv` | Real | Cần xác nhận tên chân |
| `AI_SP_NhietDo_Bon2` | `%MD200` | `DB_HmiData.Setpoint.sp_nhiet_do_bon2` | Real | HMI setpoint |
| `AI_SP_NhietDo_Bon4` | `%MD204` | `DB_HmiData.Setpoint.sp_nhiet_do_bon4` | Real | HMI setpoint |
| `AI_SP_Nuoc_Bon1` | `%MD208` | `DB_HmiData.Setpoint.sp_nuoc_bon1` | Real | |
| `AI_SP_Nuoc_Bon2` | `%MD212` | `DB_HmiData.Setpoint.sp_nuoc_bon2` | Real | |
| `AI_Alarm_Status` | `%MW250` | `DB_HmiData.Status.alarm_status` | Int | WinCC TextList |
| `AI_VFD_Comm_Fault` | `%M260.0` | `DB_OperationData.Sys.VFD_Comm_Fault` | Bool | Lỗi Modbus RTU |

---

## 3. Ánh Xạ Hành Vi ATV12 LAD → FB30 SCL

### 3.1. Hành Vi Đã Test Thật (từ bản LAD)

| Hành vi LAD | Trình tự đã xác nhận | Tương đương SCL |
| :--- | :--- | :--- |
| Bật Contactor | `Q0.0 = TRUE` trước khi gửi Control Word | `VFD_Bon2_Contactor := TRUE; // chờ 500ms` |
| Gửi Control Word RUN | Modbus RTU ghi `8501h = 047Fh` | `Step 2 — ghi Control Word` |
| Gửi tần số đặt | Ghi `8502h = Hz * 10` | `Step 3 — ghi Freq Setpoint` |
| Đọc Status Word | Đọc `3201h` | `Step 0 — đọc Status Word` |
| Đọc tần số thực | Đọc `3202h` | `Step 1 — đọc Freq Actual` |
| Dừng VFD | Control Word = `0006h` | `Bước dừng — kèm kiểm tra Busy` |
| Ngắt Contactor | `Q0.0 = FALSE` **sau khi** VFD báo dừng | `Sau khi VFD_StatusWord.bit0 = 0` |

### 3.2. Lỗi Modbus RTU Đã Gặp — Cần Tránh Ở SCL

| Lỗi | Nguyên nhân LAD | Giải pháp FB30 SCL |
| :--- | :--- | :--- |
| Xung đột instance | Gọi `Modbus_Master` 2 lần/chu kỳ | 1 instance duy nhất trong FB30 Static |
| Timer drift | Dùng M-byte timer ngoài | Timer `TON_Retry` trong Static của FB30 |
| Bảng Comm Load mất | Comm Load chạy mỗi scan | `CommLoad_Done` flag chỉ chạy 1 lần FirstScan |
| PORT sai | Hard-code PORT := 260 | PORT từ TIA HW config readback |

---

## 4. Ánh Xạ Modbus TCP LAD → Variant B SCL

### 4.1. Lỗi `16#80B6` Đã Gặp — Cần Tránh

| Nguyên nhân | Giải pháp SCL Variant B |
| :--- | :--- |
| Gọi `MB_CLIENT` khi `Busy = TRUE` | Kiểm tra `NOT #MB_Busy` trước khi set `REQ := TRUE` |
| Connection parameters thay đổi trong khi Busy | Gán `TCON_IP_v4` 1 lần tại FirstScan, không gán lại |
| Buffer trỏ sai kiểu dữ liệu | Buffer = `Array[0..10] of Word` trong `DB_CommsData` (Standard DB) |
| Dùng GET/PUT thay MB_CLIENT | **Cấm tuyệt đối** — chỉ dùng `MB_CLIENT` V3.1 |

### 4.2. Cấu Hình Modbus TCP Đúng (Variant B)

```scl
// === Khởi tạo tại FirstScan — OB1 ===
// TCON_IP_v4 gán 1 lần, không thay đổi sau đó
IF #FirstScan THEN
    DB_CommsData.TCON_Params.InterfaceId := 64;       // PROFINET port — xác nhận từ TIA
    DB_CommsData.TCON_Params.ID          := 1;        // Connection ID
    DB_CommsData.TCON_Params.ConnectionType := 11;    // TCP
    DB_CommsData.TCON_Params.ActiveEstablished := TRUE; // PLC1 chủ động
    DB_CommsData.TCON_Params.RemoteAddress.ADDR[1] := 192;
    DB_CommsData.TCON_Params.RemoteAddress.ADDR[2] := 168;
    DB_CommsData.TCON_Params.RemoteAddress.ADDR[3] := 0;
    DB_CommsData.TCON_Params.RemoteAddress.ADDR[4] := 2;  // IP PLC2 — xác nhận
    DB_CommsData.TCON_Params.RemotePort := 502;       // Modbus TCP port
    DB_CommsData.TCON_Params.LocalPort  := 0;         // Auto
END_IF;

// === Gọi MB_CLIENT (chỉ khi không Busy) ===
IF NOT DB_CommsData.MB_Busy THEN
    DB_CommsData.MB_Req := TRUE;
END_IF;

// [CHƯA COMPILE-READY] MB_CLIENT call — tên chân xác nhận từ TIA
// "Inst_MB_CLIENT"(
//     REQ        := DB_CommsData.MB_Req,
//     MB_ADDR    := 1,
//     MODE       := 0,     // Đọc Holding Register
//     DATA_ADDR  := 40001,
//     DATA_LEN   := 10,
//     DATA_PTR   := DB_CommsData.plc2_recv_buffer,
//     DONE       => DB_CommsData.MB_Done,
//     BUSY       => DB_CommsData.MB_Busy,
//     ERROR      => DB_CommsData.MB_Error,
//     STATUS     => DB_CommsData.MB_Status,
//     CONNECT    := DB_CommsData.TCON_Params
// );
```

---

## 5. Checklist Tham Chiếu (Cần Xác Nhận Trước Khi Code Variant B)

- [ ] Export readback toàn bộ Tag Table LAD cũ để xác nhận địa chỉ M-area đầy đủ
- [ ] Xác nhận địa chỉ I/O PLC2 (Bồn 3, Bồn 4) từ `generate_mixing_project.py`
- [ ] Xác nhận HW ID CB1241 (PORT Modbus RTU) từ TIA device config readback
- [ ] Xác nhận IP PLC1 và PLC2 từ tủ điện thật
- [ ] Xác nhận tên chân `MB_CLIENT` V3.1 từ TIA readback (tránh giả định)
- [ ] Đối chiếu watch table LAD cũ với DB mới để không bỏ sót biến nào
