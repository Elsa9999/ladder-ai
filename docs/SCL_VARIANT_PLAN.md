# KẾ HOẠCH 2 VARIANT DỰ ÁN SCL (SCL VARIANT PLAN)

Tài liệu này chốt chiến lược phát triển **2 biến thể** cho project SCL mới
`projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL`, làm cơ sở phê duyệt trước khi code.

> [!IMPORTANT]
> Bản LAD cũ (`projects/Mixing_Nuoc_Tuong_Maggi_2026`) **KHÔNG còn là bản thi chính**.
> Từ nay bản LAD chỉ đóng vai trò: backup/rollback, reference logic đã test,
> reference tag/address/HMI/watch table, reference hành vi ATV12, reference lỗi Modbus TCP cần tránh.

---

## 1. Tổng Quan 2 Variant

| Tiêu chí | **Variant A** — Automation 1 PLC | **Variant B** — Đấu Nối 2 PLC |
| :--- | :--- | :--- |
| **Mục đích** | Cuộc thi tự động hóa, chạy trên 1 CPU | Đấu nối thực tế tủ điện, 2 CPU vật lý |
| **Số CPU** | 1 (PLC1 duy nhất, ảo hoặc thật) | 2 (PLC1 + PLC2) |
| **Bồn** | Bồn 1–2–3–4 trên PLC1 | PLC1: Bồn 1–2; PLC2: Bồn 3–4 |
| **Grafcet** | Theo đầy đủ Grafcet đề thi | State machine SCL gọn, không bắt buộc Grafcet toàn quy trình |
| **PID_Compact_1** | OB30 trên PLC1 | OB30 trên PLC1 |
| **PID_Compact_2** | OB31 trên PLC1 (PV: tag mô phỏng) | OB31 trên **PLC2** (PV: cảm biến thật) |
| **ATV12 Modbus RTU** | Tuỳ chọn (tắt nếu mô phỏng thuần) | Bắt buộc — FB30 trên PLC1, Contactor `%Q0.0` |
| **Modbus TCP** | **Không dùng** | `MB_CLIENT` (PLC1) ↔ `MB_SERVER` (PLC2) |
| **GET/PUT** | **Cấm** | **Cấm** |
| **Mô phỏng cảm biến** | `FC_Sensor_Sim` (FC40) cho mức dịch | Không cần — cảm biến thật |
| **HMI** | Screen_1 + màn chi tiết — dùng chung | Screen_1 + màn chi tiết — dùng chung |
| **DB chung** | `DB_HmiData` (DB100), `DB_RecipeData` (DB102) | `DB_HmiData` (DB100), `DB_RecipeData` (DB102) |
| **DB riêng** | `DB_OperationData_A` nội bộ | `DB_OperationData_B` + `DB_CommsData` (DB103) |

---

## 2. Kiến Trúc Khối — Điểm Chung (Shared Core)

Các khối sau **có mặt ở cả 2 variant**, cần code một lần và dùng lại:

| Khối | Mô tả |
| :--- | :--- |
| `FB10 FB_MixingBranch` | State machine tuần tự cho 1 nhánh (Bồn A + Bồn B) |
| `FB20 FB_StorageFilter` | Cụm bồn chứa, màng lọc, chiết rót |
| `OB30 PID_Loop_Bon2` | Gọi `PID_Compact_1` — 100ms, Bồn 2 |
| `DB100 DB_HmiData` | Dữ liệu HMI: setpoint, trạng thái, cảnh báo |
| `DB101 DB_OperationData` | Trạng thái bước, cờ an toàn, kết quả đo lường |
| `DB102 DB_RecipeData` | Công thức mặc định Maggi, load tại FirstScan |
| Quy tắc đặt tên | Không `AI_`, tiếng Việt không dấu, Snake_case I/O |

---

## 3. Kiến Trúc Khối — Điểm Khác (Variant-Specific)

### 3.1. Variant A — Automation 1 PLC

```
PLC1 (duy nhất)
├── OB1  Main
├── OB30 PID_Loop_Bon2     (PID_Compact_1)
├── OB31 PID_Loop_Bon4     (PID_Compact_2, PV từ FC_Sensor_Sim)
├── FB10 FB_MixingBranch   (Inst: DB10 Nhánh1, DB11 Nhánh2 — nội bộ)
├── FB20 FB_StorageFilter  (Inst: DB20)
├── FC40 FC_Sensor_Sim     (Mô phỏng mức dịch — KHÔNG viết PID)
├── DB100 DB_HmiData
├── DB101 DB_OperationData
├── DB102 DB_RecipeData
└── [FB30 FB_VFD_ATV12_ModbusRTU — tuỳ chọn nếu có ATV12]
```

**Đặc điểm riêng Variant A:**
- OB31 (`PID_Loop_Bon4`) nằm trên PLC1.
- `FC_Sensor_Sim` cung cấp PV nhiệt độ mô phỏng cho Bồn 4 vào PID_Compact_2.
- Nhánh 1 và Nhánh 2 trao đổi qua DB nội bộ, không dùng Modbus TCP.
- Tuân theo đầy đủ Grafcet đề thi (xem `SCL_GRAFCET_MAPPING.md`).

### 3.2. Variant B — Đấu Nối 2 PLC

```
PLC1
├── OB1  Main
├── OB30 PID_Loop_Bon2         (PID_Compact_1)
├── FB10 FB_MixingBranch       (Inst: DB10 Nhánh1)
├── FB20 FB_StorageFilter      (Inst: DB20)
├── FB30 FB_VFD_ATV12_ModbusRTU (Inst: DB30) — Bắt buộc
├── DB100 DB_HmiData
├── DB101 DB_OperationData
├── DB102 DB_RecipeData
└── DB103 DB_CommsData          (Modbus TCP buffer)

PLC2
├── OB1  Main
├── OB31 PID_Loop_Bon4         (PID_Compact_2, PV từ cảm biến thật)
├── FB10 FB_MixingBranch       (Inst: DB11 Nhánh2)
├── DB100 DB_HmiData           (đồng bộ qua Modbus TCP)
└── DB101 DB_OperationData
```

**Đặc điểm riêng Variant B:**
- OB31 nằm trên PLC2.
- FB30 bắt buộc — ATV12 Contactor `%Q0.0` thật.
- Modbus TCP dùng `TCON_IP_v4` + Word buffer cố định. **Tránh lỗi `16#80B6`** bằng cách:
  - Không gọi `MB_CLIENT` khi `Busy = TRUE`.
  - Connection block dạng `MB_CLIENT` V3.1, không dùng PUT/GET.
  - Kiểm tra `Done / Error / Status` mỗi chu kỳ quét trước khi phát REQ mới.
- PLC2 `MB_SERVER` V3.1, `MB_HOLD_REG` trỏ vào `DB_CommsData` (Standard DB).

---

## 4. Quy Tắc DB Chung

> [!IMPORTANT]
> `DB_HmiData` (DB100) **phải có cấu trúc giống nhau** ở cả 2 variant để HMI Screen_1 không bị vỡ liên kết.
> Chỉ được **thêm** trường mới vào DB100; không được đổi tên hoặc xóa trường đã có.

| DB | Variant A | Variant B | Ghi chú |
| :--- | :--- | :--- | :--- |
| `DB100 DB_HmiData` | ✅ Dùng | ✅ Dùng | Cấu trúc đồng nhất |
| `DB101 DB_OperationData` | ✅ Dùng | ✅ Dùng | Bồn 3–4 field chỉ có ở Variant B |
| `DB102 DB_RecipeData` | ✅ Dùng | ✅ Dùng | Chung công thức |
| `DB103 DB_CommsData` | ❌ Không dùng | ✅ Dùng | Buffer Modbus TCP (chỉ Variant B) |
| `DB30 Inst_VFD_ATV12` | Tuỳ chọn | ✅ Bắt buộc | Instance DB của FB30 |

---

## 5. Thứ Tự Phát Triển Ưu Tiên

1. **Variant A trước** — dễ test trên PLC Sim, không phụ thuộc phần cứng.
2. **Shared core** (FB10, FB20, OB30, DB100–102) code chung, dùng cho cả 2 variant.
3. **Variant B** thêm: FB30, DB103, Modbus TCP config.
4. **Không code bước nào khi chưa có Codex duyệt docs**.
