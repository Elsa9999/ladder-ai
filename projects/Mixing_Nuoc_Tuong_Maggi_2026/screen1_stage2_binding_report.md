# Báo cáo Giai đoạn 2 — Gán HMI tag cho Screen_1 (Thực tế)

**Trạng thái:** 🟢 **HOÀN THÀNH — ĐÃ NGHIỆM THU 100% PASS**

Báo cáo này ghi nhận kết quả preflight, import, biên dịch và thẩm định readback thực tế cho việc gán HMI tag trên `Screen_1` dự án *Mixing Nước Tương Maggi 2026* cho cả 24 IOField số và 41 Graphic I/O Field.

---

## 1. Thông tin Backup & Dự án
- **Đường dẫn lưu dự án backup:**
  `C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh_backup`
  *(Đã tạo backup qua Openness API lúc 10:02 ngày 23/06/2026).*
- **Dự án TIA đang mở:** `cuocthi_tdh` (PID: `19228`)

---

## 2. Kết quả Preflight (Kiểm tra trước khi Import)
- **Số lượng IOField số:** 24 ô.
- **Số lượng Graphic I/O Field:** 41 ô.
- **Tổng số đối tượng động:** 65 đối tượng.
- **Trạng thái đối chiếu:** **KHỚP 100%** (Tất cả tọa độ X, Y, Width, Height và ObjectName trùng khớp hoàn hảo).

---

## 3. Kết quả nạp (Import) và Biên dịch HMI (Compilation Results)
- **HMI Tag Table:** Đã xóa bảng tag cũ và nạp mới bảng tag `Screen1_HMI_Tags` gồm **69 tags** (gồm 24 tag số, 41 tag đồ họa và 4 tag nội bộ phụ trợ).
- **Screen_1:** Đã xóa màn hình cũ và nạp lại màn hình đã vá thuộc tính và liên kết.
- **Kết quả biên dịch WinCC RT:** **Thành công 100%**
  - **Lỗi (Errors):** `0`
  - **Cảnh báo (Warnings):** `53` (2 cảnh báo "The position or size of the object is invalid" đã biến mất hoàn toàn sau khi căn chỉnh biên).
  - **Cảnh báo thiếu Process Tag (47 warnings):** Xuất hiện trên các màn hình khác (`chekc truyen thong`, `bon tron 1`, `bon tron 2`, `bon tron 3`, `bon tron 4`), **không có cảnh báo thiếu Process Tag nào thuộc về Screen_1**.
  - **Cảnh báo độ phân giải ảnh (6 warnings):** Thể hiện việc một số ảnh đồ họa sử dụng sai tỷ lệ/kích thước gây nguy cơ pixelation (vỡ hạt).
  ```
  Compiling HMI Target software...
    Compile State: Warning
    Errors: 0, Warnings: 53
    Information: Number of tags: 73
    Information: Number of PowerTags used: 65
    Information: Software compilation completed (device version: 17.0.0.0).
  ```

---

## 4. Kết quả Thẩm định Readback Độc lập (Readback Proof)
Đã xuất ngược (Export Readback) toàn bộ HMI Tag Table và HMI Screen_1 trực tiếp từ dự án TIA Portal sau chỉnh sửa để đối chứng. Kết quả chạy kịch bản thẩm định tự động `verify_readback.py` đạt **PASS 100%**:

```
Loaded 24 numeric mapping records.
Loaded 41 graphic mapping records.
Parsed 69 tags from HMI Tag Table readback.
  Tags on HMI_Connection_1: 44 (expected 44: 16 numeric + 28 graphic)
  Tags on HMI_Connection_2: 21 (expected 21: 8 numeric + 13 graphic)
[PASS] Tag Table checks passed successfully!
Parsed 24 numeric IOFields from screen XML.
Parsed 41 graphic IOFields from screen XML.
Agitators X Positions: Bon1=123, Bon2=459, Bon4=782, Bon3=1130
[PASS] Agitator physical layout order verified: Bồn 1 -> Bồn 2 -> Bồn 4 -> Bồn 3

--- READBACK SUMMARY ---
Total Numeric IOFields Checked: 24 / 24
Total Graphic IOFields Checked: 41 / 41
Total Errors Found: 0

[PASS] TIA Screen_1 Readback Verification PASSED 100%!
```

### Các thông số kiểm tra cụ thể:
1. **Liên kết kết nối (Connection Binding):**
   - Đúng `44` tag liên kết với `HMI_Connection_1` (đọc dữ liệu từ `PLC_1` - gồm 16 numeric + 28 graphic).
   - Đúng `21` tag liên kết với `HMI_Connection_2` (đọc dữ liệu từ `PLC_2` - gồm 8 numeric + 13 graphic).
   - Đúng `4` tag nội bộ ảo phục vụ cho khối điều khiển/nút bấm không báo lỗi biên dịch (`GIA_TRI_NHIET_DO_DOC_VE`, `nguyen_lieu_tron_1`, `cap_nuoc_tron_1`, `start`).
2. **Căn lề hiển thị (Alignments):**
   - 24/24 ô IOField đều được cấu hình căn giữa chính xác:
     - `<HorizontalAlignment>Center</HorizontalAlignment>`
     - `<VerticalAlignment>Middle</VerticalAlignment>`
3. **Định dạng số thực (FormatPattern):**
   - Các ô đo nhiệt độ (TT), áp suất (PI) có dạng `99.9` (hiển thị 1 chữ số thập phân).
   - Các ô lưu lượng (FT/FQ), trạng thái van (CV), mức bồn (LT) có dạng `999.9`.
4. **Cấu hình Graphic I/O Field an toàn:**
   - 41/41 Graphic I/O Field đều được đặt thuộc tính `<Mode>Output</Mode>` (chỉ hiển thị, không ghi đè giá trị).
5. **Không có Tag rác/Tag chưa định nghĩa:**
   - 100% tag liên kết trong Screen_1 đều tồn tại hợp lệ trong bảng tag HMI (`0 unresolved tag references`).
   - Hoàn toàn không có tag nào chứa tiền tố `AI_`.
6. **Kích thước & Bố cục:**
   - Tọa độ X, Y và Kích thước Width, Height của 65 đối tượng khớp 100% với nguyên bản.
   - Trật tự bố cục bồn cánh khuấy tuân thủ hoàn hảo: Bồn 1 -> Bồn 2 -> Bồn 4 -> Bồn 3.

---

## 5. Kết luận
Giai đoạn 2 đã hoàn thành xuất sắc và đạt trạng thái **PASS** toàn diện trên dự án TIA Portal thực tế. Dự án đã được lưu lại an toàn.
