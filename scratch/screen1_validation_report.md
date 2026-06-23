# Báo cáo Validation Giai đoạn 1 — Screen_1 (v3)

**Dự án:** `cuocthi_tdh`  
**TIA Portal PID:** `14620` (attach-only, READ-ONLY trong suốt Giai đoạn 1)  
**Project path:** `C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18`  
**Screen target:** `Screen_1` (HMI_RT_1)  
**Export timestamp:** `20260622_220027`  
**Phiên bản báo cáo:** v3 — corrections 2026-06-22 22:21 (ICT)

---

## 1. Thông tin Export

| Hạng mục | Giá trị |
|---|---|
| File export | `scratch\screen1_export_20260622_220027\Screen_1.xml` |
| **SHA256** | `DBB6A80586A1E3DBDAAC6079BCCF912209C54677FC28B991C4739FE62108B995` |
| Kích thước | 514,427 bytes |
| Kích thước màn hình | 1440 × 900 px |
| Screen Name | `Screen_1` |
| So sánh export cũ (`hmi_export_actual`) | SHA256 KHÁC → bản export hôm nay là mới nhất từ TIA |

---

## 2. Inventory Screen_1

| Loại phần tử | Số lượng |
|---|---|
| `Hmi.Screen.IOField` | **24** |
| `Hmi.Screen.GraphicIOField` | 41 |
| `Hmi.Screen.TextField` | 87 |
| `Hmi.Screen.GraphicView` | 128 |

> **Quan sát:** Toàn bộ 24 IOField và 87 TextField **chưa có tag binding nào** (ProcessValue = rỗng, không có PropertyBinding). Đây là màn hình khung thiết kế — chưa được gán tag từ trước.

---

## 3. Layout Screen_1

Screen_1 là **Màn hình Chi tiết Bồn (Tank Detail)** — 4 bồn trộn + 2 bồn chứa + thiết bị phụ trợ.

```
Layout 4 cột:
  Col1 (x≈133–387)  : Bồn 1 → PLC_1
  Col2 (x≈486–740)  : Bồn 2 → PLC_1
  Col3 (x≈804–1058) : Bồn 4 → PLC_2  ← Bồn 4 thuộc PLC_2
  Col4 (x≈1143–1410): Bồn 3 → PLC_2  ← Bồn 3 thuộc PLC_2

4 hàng đo lường:
  Hàng FQ  (y≈61–65,  fmt=999.9): Lưu lượng tích lũy (L)
  Hàng LT  (y≈127–130, fmt=999.9): Mức lỏng (%)
  Hàng TT  (y≈190–195, fmt=99.9):  Nhiệt độ (°C)
  Hàng CV  (y≈293–300, fmt=999.9): Van tuyến tính (%)

Vùng phụ:
  BonChua1 (x≈412):     LT3302 (999.9), TT3301 (99.9) → PLC_1
  BonChua2 (x≈1134):    LT3307 (999.9), TT3306 (99.9) → PLC_1
  Trao đổi nhiệt (x≈791, y≈589):   TT3303 (99.9)      → PLC_1
  Van nước làm mát (x≈832, y≈741): CV3304 (999.9)      → PLC_1
  Áp suất filter (x≈1280, y≈616):  PI3308 (99.9)       → PLC_1
  FT xa thành phẩm (x≈1280, y≈670): FT3309 (999.9)     → PLC_1
```

---

## 4. Quy tắc Format Pattern

| Loại đo lường | Format | Đơn vị điển hình |
|---|---|---|
| FQ (lưu lượng tích lũy), LT (mức lỏng), CV (van %), FT (lưu lượng tức thời) | `999.9` | L, %, L/h |
| TT (nhiệt độ), PI (áp suất) | `99.9` | °C, bar |

---

## 5. Mapping Đầy Đủ 24 IOField

| # | ObjectName | L | T | Fmt | PLC | Proposed Tag | Connection | Conf | Conn2? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | I/O field_1 | 133 | 61 | 999.9 | PLC_1 | `FQ3200_Bon1_Eff` | HMI_Connection_1 | HIGH | — |
| 2 | I/O field_7 | 486 | 65 | 999.9 | PLC_1 | `FQ3205_Bon2_Eff` | HMI_Connection_1 | HIGH | — |
| 3 | I/O field_11 | 804 | 61 | 999.9 | **PLC_2** | `FQ3215_Bon4_Eff` | HMI_Connection_2 | HIGH | ❌ BLOCKER |
| 4 | I/O field_15 | 1143 | 62 | 999.9 | **PLC_2** | `FQ3210_Bon3_Eff` | HMI_Connection_2 | HIGH | ❌ BLOCKER |
| 5 | I/O field_2 | 300 | 127 | 999.9 | PLC_1 | `LT3203_Bon1_Eff` | HMI_Connection_1 | HIGH | — |
| 6 | I/O field_8 | 636 | 129 | 999.9 | PLC_1 | `LT3209_Bon2_Eff` | HMI_Connection_1 | HIGH | — |
| 7 | I/O field_12 | 965 | 127 | 999.9 | **PLC_2** | `LT3218_Bon4_Eff` | HMI_Connection_2 | HIGH | ❌ BLOCKER |
| 8 | I/O field_16 | 1318 | 130 | 999.9 | **PLC_2** | `LT3213_Bon3_Eff` | HMI_Connection_2 | HIGH | ❌ BLOCKER |
| 9 | I/O field_5 | 353 | 195 | 99.9 | PLC_1 | `TT3204_Bon1_Eff` | HMI_Connection_1 | HIGH | — |
| 10 | I/O field_9 | 689 | 192 | 99.9 | PLC_1 | `TT3208_Bon2_Eff` | HMI_Connection_1 | HIGH | — |
| 11 | I/O field_13 | 1016 | 190 | 99.9 | **PLC_2** | `TT3219_Bon4_Eff` | HMI_Connection_2 | HIGH | ❌ BLOCKER |
| 12 | I/O field_17 | 1365 | 193 | 99.9 | **PLC_2** | `TT3214_Bon3_Eff` | HMI_Connection_2 | HIGH | ❌ BLOCKER |
| 13 | I/O field_6 | 354 | 296 | 999.9 | PLC_1 | `CV3201_Nuoc_Bon1_M` | HMI_Connection_1 | HIGH | — |
| 14 | I/O field_10 | 688 | 294 | 999.9 | PLC_1 | `CV3206_Hoi_Bon2_M` | HMI_Connection_1 | HIGH | — |
| 15 | I/O field_14 | 1015 | 293 | 999.9 | **PLC_2** | `CV3216_Hoi_Bon4_M` | HMI_Connection_2 | HIGH | ❌ BLOCKER |
| 16 | I/O field_18 | 1367 | 293 | 999.9 | **PLC_2** | `CV3211_Nuoc_Bon3_M` | HMI_Connection_2 | HIGH | ❌ BLOCKER |
| 17 | I/O field_19 | 412 | 586 | 999.9 | PLC_1 | `LT3302_BonChua1_Eff` | HMI_Connection_1 | HIGH | — |
| 18 | I/O field_20 | 417 | 713 | 99.9 | PLC_1 | `TT3301_BonChua1_Eff` | HMI_Connection_1 | HIGH | — |
| 19 | I/O field_22 | 1135 | 589 | 999.9 | PLC_1 | `LT3307_BonChua2_Eff` | HMI_Connection_1 | HIGH | — |
| 20 | I/O field_21 | 1134 | 711 | 99.9 | PLC_1 | `TT3306_BonChua2_Eff` | HMI_Connection_1 | HIGH | — |
| 21 | I/O field_23 | 1280 | 616 | 99.9 | PLC_1 | `PI3308_Truoc_Filter_Eff` | HMI_Connection_1 | HIGH | — |
| 22 | I/O field_24 | 1280 | 670 | 999.9 | PLC_1 | `FT3309_Xa_Thanh_Pham_Eff` | HMI_Connection_1 | HIGH | — |
| 23 | I/O field_3 | 832 | 741 | 999.9 | PLC_1 | `CV3304_Nuoc_Lam_Mat_M` | HMI_Connection_1 | HIGH | — |
| 24 | I/O field_4 | 791 | 589 | 99.9 | PLC_1 | `TT3303_TraoDoiNhiet_Eff` | HMI_Connection_1 | HIGH | — |

---

## 6. Xác minh Controller Tags

### 6.1 PLC_1 — 16 tags (HMI_Connection_1 AVAILABLE)

| Tag | DataType | Địa chỉ | Xác minh |
|---|---|---|---|
| `FQ3200_Bon1_Eff` | Real | %MD712 | ✅ |
| `FQ3205_Bon2_Eff` | Real | %MD744 | ✅ |
| `LT3203_Bon1_Eff` | Real | %MD720 | ✅ |
| `LT3209_Bon2_Eff` | Real | %MD752 | ✅ |
| `TT3204_Bon1_Eff` | Real | %MD728 | ✅ |
| `TT3208_Bon2_Eff` | Real | %MD760 | ✅ |
| `CV3201_Nuoc_Bon1_M` | Real | %MD1200 | ✅ |
| `CV3206_Hoi_Bon2_M` | Real | %MD1208 | ✅ |
| `LT3302_BonChua1_Eff` | Real | %MD832 | ✅ |
| `TT3301_BonChua1_Eff` | Real | %MD840 | ✅ |
| `LT3307_BonChua2_Eff` | Real | %MD856 | ✅ |
| `TT3306_BonChua2_Eff` | Real | %MD864 | ✅ |
| `TT3303_TraoDoiNhiet_Eff` | Real | %MD848 | ✅ |
| `CV3304_Nuoc_Lam_Mat_M` | Real | %MD1232 | ✅ |
| `PI3308_Truoc_Filter_Eff` | Real | %MD872 | ✅ |
| `FT3309_Xa_Thanh_Pham_Eff` | Real | %MD880 | ✅ |


### 6.2 PLC_2 — 8 tags (HMI_Connection_2 CHƯA TỒN TẠI)

| Tag | DataType | Địa chỉ | Xác minh trong PLC_2 |
|---|---|---|---|
| `FQ3215_Bon4_Eff` | Real | %MD808 | ✅ |
| `LT3218_Bon4_Eff` | Real | %MD816 | ✅ |
| `TT3219_Bon4_Eff` | Real | %MD824 | ✅ |
| `CV3216_Hoi_Bon4_M` | Real | %MD1224 | ✅ |
| `FQ3210_Bon3_Eff` | Real | %MD776 | ✅ |
| `LT3213_Bon3_Eff` | Real | %MD784 | ✅ |
| `TT3214_Bon3_Eff` | Real | %MD792 | ✅ |
| `CV3211_Nuoc_Bon3_M` | Real | %MD1216 | ✅ |

---

## 7. IOField Thiếu trong Screen_1

> **`CV_Filler_Cap_Dich_M`** — Tag tồn tại trong PLC_1 (`%MD1236`, Real, fmt=`999.9`, unit=`%`) nhưng **không có IOField tương ứng** trong Screen_1 (chỉ có 24 ô hiện có).  
> **Hành động:** Chờ người dùng đặt thủ công IOField mới trong TIA. Agent **không tự tạo ô hoặc sửa layout**.

---

## 8. Kiểm tra HMI Connection

| Connection | Partner | Trạng thái |
|---|---|---|
| `HMI_Connection_1` | PLC_1 (192.168.0.1) | ✅ Tồn tại |
| `HMI_Connection_2` | PLC_2 (192.168.0.2) | ❌ Chưa tồn tại |

### Vai trò của HMI_Connection_2

> **Làm rõ:** `HMI_Connection_2` là kết nối **HMI đọc dữ liệu từ PLC_2** — đây là kết nối giám sát SCADA/HMI tiêu chuẩn (SIMATIC HMI Connection, S7 Communication).  
> **Đây KHÔNG PHẢI** thay đổi kiến trúc PLC-to-PLC (GET/PUT hay Modbus TCP giữa hai PLC). Kiến trúc PLC_1 ↔ PLC_2 không bị ảnh hưởng.  
> Việc thêm HMI_Connection_2 chỉ cho phép HMI_RT_1 đọc thêm tag từ PLC_2 thông qua mạng PROFINET hiện có (192.168.0.x/24).

**Phương án tạo HMI_Connection_2:**

| Phương án | Khả thi | Khuyến nghị |
|---|---|---|
| A) TIA UI thủ công: `HMI_RT_1 > Connections > Add > SIMATIC S7 1200 > PLC_2` | ✅ | **Khuyến nghị** |
| B) XML import (sửa HmiTarget XML) | ⚠️ Rủi ro cao | Không dùng |
| C) Openness API `hmiTarget.Connections.Create()` | ❌ Không khả dụng | Không dùng |

---

## 9. HMI Tag Readback Hiện Tại

| Tag HMI | Loại | Connection | Ghi chú |
|---|---|---|---|
| `Logged_In` | Internal | `<Internal>` | ✅ Hợp lệ |
| `HMI_SP_PLC2_Nhiet_Do_Bon4` | External | `None` | ⚠️ Connection=None (lần import thử trước, không xóa/sửa) |
| `HMI_SP_PLC2_Nuoc_Bon3` | External | `None` | ⚠️ Connection=None (lần import thử trước, không xóa/sửa) |

---

## 10. Blockers và Điều kiện Giai đoạn 2

| # | Blocker | Mức | Hành động |
|---|---|---|---|
| B1 | `HMI_Connection_2` → PLC_2 chưa tồn tại | **P0** | Tạo thủ công TIA UI trước khi import |
| B2 | 8/24 IOField (Bon3+Bon4) cần Connection_2 | **P0** | Phụ thuộc B1 |
| B3 | `CV_Filler_Cap_Dich_M` không có IOField trong Screen_1 | **P1** | Người dùng thêm IOField thủ công |
| B4 | `HMI_SP_PLC2_*` tags có Connection=None | **P2** | Sẽ tự giải quyết sau khi B1 hoàn thành |

---

## 11. Deliverables Giai đoạn 1 (đầy đủ)

| File | Đường dẫn | Trạng thái |
|---|---|---|
| Original Screen_1 XML | `scratch\screen1_export_20260622_220027\Screen_1.xml` | ✅ |
| SHA256 | `DBB6A80586A1E3DBDAAC6079BCCF912209C54677FC28B991C4739FE62108B995` | ✅ |
| `screen1_inventory.csv` | `scratch\screen1_inventory.csv` | ✅ |
| `screen1_mapping_dry_run.csv` | `scratch\screen1_mapping_dry_run.csv` | ✅ v3 |
| `screen1_validation_report.md` | *(file này)* | ✅ v3 |
| HMI Tag readback | Mục 9 | ✅ |

---

## 12. Kết luận

**GIAI ĐOẠN 1 HOÀN THÀNH — DỪNG.**

Không có thay đổi nào được thực hiện trên TIA Portal (không import, không save, không compile, không sửa connection, không xóa hoặc sửa HMI tag).

Giai đoạn 2 **CHỈ ĐƯỢC THỰC HIỆN** sau khi:
1. `HMI_Connection_2` được tạo thủ công trong TIA UI
2. `PI3308_Truoc_Filter_Eff` được xác nhận tên chính xác trong PLC_1
3. `CV_Filler_Cap_Dich_M` được người dùng thêm IOField thủ công (nếu cần)
4. Codex/người dùng phê duyệt Giai đoạn 2
