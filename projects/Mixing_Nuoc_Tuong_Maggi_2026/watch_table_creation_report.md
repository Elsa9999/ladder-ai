# Báo cáo tạo lập Watch Table đấu nối TIA Portal

Báo cáo tự động ghi nhận kết quả tạo lập Watch Table chuẩn bị cho việc đấu nối thiết bị.

---

## 1. Thông tin lưu trữ và backup
- **Original Project Path:** `C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18`
- **Backup Project Path:** `C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh_backup_watchtables`
- **Trạng thái lưu trữ:** Đã backup trước khi tạo và lưu thành công sau khi hoàn tất.

## 2. Chi tiết số lượng và trạng thái các Watch Table

### PLC_1 Watch Tables
| Tên Watch Table | Yêu cầu | Thực tế tạo | Thiếu/Unresolved |
| :--- | :---: | :---: | :--- |
| `WT_DAU_NOI_01_MODE_SAFETY` | 21 | 21 | Không có |
| `WT_DAU_NOI_02_PID_VFD` | 25 | 25 | Không có |
| `WT_DAU_NOI_03_ATV12_MODBUS` | 18 | 18 | Không có |
| `WT_DAU_NOI_04_PLC_TO_PLC` | 13 | 13 | Không có |

### PLC_2 Watch Tables
| Tên Watch Table | Yêu cầu | Thực tế tạo | Thiếu/Unresolved |
| :--- | :---: | :---: | :--- |
| `WT_DAU_NOI_05_PLC2_SERVER` | 10 | 10 | Không có |

## 3. Kết quả biên dịch (Compile Check)
- **PLC_1 Compiler Status:** `Warning` | Errors: `0` | Warnings: `1`
- **PLC_2 Compiler Status:** `Warning` | Errors: `0` | Warnings: `1`
- **Đánh giá:** Compilation hoàn thành sạch sẽ, **0 lỗi (Errors)** trên cả 2 PLC.

## 4. Xác nhận thay đổi dự án
- Không có khối logic PLC nào bị thay đổi cấu trúc hoặc mã nguồn.
- Không có bảng PLC Tag nào bị sửa đổi hay bổ sung.
- Không có màn hình HMI hay cấu hình phần cứng/mạng nào bị tác động.
- **Bằng chứng lưu trữ (Project Save Proof):** TIA Portal Openness API `proj.Save()` đã hoàn tất thực thi thành công.

---
## 5. Kết luận
Tất cả Watch Table đã được cấu hình và nạp thành công vào TIA Portal phục vụ đấu nối thực nghiệm.
