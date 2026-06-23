# Báo cáo Pre-flight kiểm tra HMI Tổng quan (Read-Only Pre-flight Report)

Dự án: `cuocthi_tdh`  
Phiên TIA Portal PID: `14620`  
Đường dẫn Project: `C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18`  
Màn hình XML: `D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml`  

---

## 1. Thiết bị và HMI Connection hiện có

| Tên Thiết bị | Loại Thiết bị | Trạng thái Software |
| :--- | :--- | :--- |
| `PLC_1` | S7-1200 | PlcSoftware |
| `PLC_2` | S7-1200 | PlcSoftware |
| `HMI_RT_1` | PC-System (WinCC Prof) | HmiTarget |

**Danh sách HMI Connection trong `HMI_RT_1`:**
- *Không tìm thấy HMI Connection trực tiếp trong `hmi.Connections`.* (Do WinCC Professional quản lý kết nối tích hợp trong Topology mạng).

---

## 2. Kiểm tra tính đúng đắn của tệp XML `Man Tong Quan`

- **Tính hợp lệ cú pháp (Well-formed):** XML hợp lệ và được parse thành công.
- **Trùng lặp ID (Duplicate IDs):** 0 ID bị trùng. Không phát hiện ID trùng.
- **Số lượng các ô IOField:**
  - `IOField` (ô số): 27 ô (2 gốc đã bị xóa, 25 ô do AI sinh mới).
  - `GraphicIOField` (van/bơm/bồn hoạt hình): 41 ô.
  - `TextField` (nhãn tĩnh/đơn vị): 81 ô (81 ô do AI sinh mới).

### A. Kiểm tra tràn biên màn hình (X: 0-1440, Y: 0-900)
| Tên phần tử | Loại | Vị trí (Left, Top) | Kích thước (W x H) | Tọa độ kết thúc (X/Y) | Lỗi cụ thể |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Graphic I/O field_27` | Hmi.Screen.GraphicIOField | (725, 829) | 51x78 | X=776, Y=907 | Vượt biên dưới Y=907 (> 900). |

### B. Kiểm tra chồng lấn phần tử (Overlaps)
| Phần tử 1 | Loại | Phần tử 2 | Loại | Tọa độ phần tử 1 | Tọa độ phần tử 2 | Diện tích đè nhau (px²) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `Graphic I/O field_24` | Hmi.Screen.GraphicIOField | (430, 521, 275x288) | (554, 759, 51x78) | 2550 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `Graphic I/O field_25` | Hmi.Screen.GraphicIOField | (430, 521, 275x288) | (672, 597, 51x78) | 2574 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `Graphic I/O field_34` | Hmi.Screen.GraphicIOField | (430, 521, 275x288) | (587, 792, 90x71) | 1530 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `Graphic I/O field_30` | Hmi.Screen.GraphicIOField | (430, 521, 275x288) | (467, 804, 83x47) | 415 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_24` | Hmi.Screen.TextField | (430, 521, 275x288) | (549, 737, 60x20) | 1200 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_25` | Hmi.Screen.TextField | (430, 521, 275x288) | (667, 575, 60x20) | 760 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `AI_IO_LT3302` | Hmi.Screen.IOField | (430, 521, 275x288) | (580, 570, 72x26) | 1872 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3302` | Hmi.Screen.TextField | (430, 521, 275x288) | (580, 545, 72x20) | 1440 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3302` | Hmi.Screen.TextField | (430, 521, 275x288) | (660, 570, 45x26) | 1170 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `AI_IO_TT3301` | Hmi.Screen.IOField | (430, 521, 275x288) | (580, 640, 72x26) | 1872 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3301` | Hmi.Screen.TextField | (430, 521, 275x288) | (580, 615, 72x20) | 1440 |
| `Graphic I/O field_9` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3301` | Hmi.Screen.TextField | (430, 521, 275x288) | (660, 640, 45x26) | 1170 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `Graphic I/O field_5` | Hmi.Screen.GraphicIOField | (154, 90, 233x295) | (189, 70, 51x78) | 2958 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `Graphic I/O field_8` | Hmi.Screen.GraphicIOField | (154, 90, 233x295) | (220, 339, 51x78) | 2346 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | (154, 90, 233x295) | (123, 84, 292x298) | 68036 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `I/O field_1` | Hmi.Screen.IOField | (154, 90, 233x295) | (113, 69, 67x32) | 286 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `I/O field_2` | Hmi.Screen.IOField | (154, 90, 233x295) | (300, 127, 67x28) | 1876 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_8` | Hmi.Screen.TextField | (154, 90, 233x295) | (215, 317, 60x20) | 1200 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_IO_FT3200` | Hmi.Screen.IOField | (154, 90, 233x295) | (114, 70, 72x26) | 192 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3200` | Hmi.Screen.TextField | (154, 90, 233x295) | (194, 70, 45x26) | 270 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_IO_CV3201` | Hmi.Screen.IOField | (154, 90, 233x295) | (114, 105, 72x26) | 832 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_CV3201` | Hmi.Screen.TextField | (154, 90, 233x295) | (114, 80, 72x20) | 320 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3201` | Hmi.Screen.TextField | (154, 90, 233x295) | (194, 105, 45x26) | 1170 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_IO_LT3203` | Hmi.Screen.IOField | (154, 90, 233x295) | (300, 130, 72x26) | 1872 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3203` | Hmi.Screen.TextField | (154, 90, 233x295) | (300, 105, 72x20) | 1440 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3203` | Hmi.Screen.TextField | (154, 90, 233x295) | (380, 130, 45x26) | 182 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_IO_TT3204` | Hmi.Screen.IOField | (154, 90, 233x295) | (300, 200, 72x26) | 1872 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3204` | Hmi.Screen.TextField | (154, 90, 233x295) | (300, 175, 72x20) | 1440 |
| `Graphic I/O field_10` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3204` | Hmi.Screen.TextField | (154, 90, 233x295) | (380, 200, 45x26) | 182 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `Graphic I/O field_28` | Hmi.Screen.GraphicIOField | (904, 517, 275x288) | (1030, 754, 51x78) | 2601 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `Graphic I/O field_35` | Hmi.Screen.GraphicIOField | (904, 517, 275x288) | (1108, 764, 90x71) | 2911 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `Graphic I/O field_37` | Hmi.Screen.GraphicIOField | (904, 517, 275x288) | (1156, 541, 60x42) | 966 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `Graphic I/O field_31` | Hmi.Screen.GraphicIOField | (904, 517, 275x288) | (930, 792, 83x47) | 1079 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_37` | Hmi.Screen.TextField | (904, 517, 275x288) | (1156, 585, 60x20) | 460 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_28` | Hmi.Screen.TextField | (904, 517, 275x288) | (1025, 732, 60x20) | 1200 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_IO_LT3307` | Hmi.Screen.IOField | (904, 517, 275x288) | (1054, 566, 72x26) | 1872 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3307` | Hmi.Screen.TextField | (904, 517, 275x288) | (1054, 541, 72x20) | 1440 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3307` | Hmi.Screen.TextField | (904, 517, 275x288) | (1134, 566, 45x26) | 1170 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_IO_TT3306` | Hmi.Screen.IOField | (904, 517, 275x288) | (1054, 636, 72x26) | 1872 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3306` | Hmi.Screen.TextField | (904, 517, 275x288) | (1054, 611, 72x20) | 1440 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3306` | Hmi.Screen.TextField | (904, 517, 275x288) | (1134, 636, 45x26) | 1170 |
| `Graphic I/O field_2` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_PI3308` | Hmi.Screen.TextField | (904, 517, 275x288) | (970, 795, 72x20) | 720 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `Graphic I/O field_12` | Hmi.Screen.GraphicIOField | (486, 90, 233x295) | (533, 70, 51x78) | 2958 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `Graphic I/O field_15` | Hmi.Screen.GraphicIOField | (486, 90, 233x295) | (556, 341, 51x78) | 2244 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | (486, 90, 233x295) | (459, 83, 292x298) | 67803 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_15` | Hmi.Screen.TextField | (486, 90, 233x295) | (551, 319, 60x20) | 1200 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_IO_FT3205` | Hmi.Screen.IOField | (486, 90, 233x295) | (446, 70, 72x26) | 192 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3205` | Hmi.Screen.TextField | (486, 90, 233x295) | (526, 70, 45x26) | 270 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_IO_CV3206` | Hmi.Screen.IOField | (486, 90, 233x295) | (446, 105, 72x26) | 832 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_CV3206` | Hmi.Screen.TextField | (486, 90, 233x295) | (446, 80, 72x20) | 320 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3206` | Hmi.Screen.TextField | (486, 90, 233x295) | (526, 105, 45x26) | 1170 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_IO_LT3209` | Hmi.Screen.IOField | (486, 90, 233x295) | (632, 130, 72x26) | 1872 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3209` | Hmi.Screen.TextField | (486, 90, 233x295) | (632, 105, 72x20) | 1440 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3209` | Hmi.Screen.TextField | (486, 90, 233x295) | (712, 130, 45x26) | 182 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_IO_TT3208` | Hmi.Screen.IOField | (486, 90, 233x295) | (632, 200, 72x26) | 1872 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3208` | Hmi.Screen.TextField | (486, 90, 233x295) | (632, 175, 72x20) | 1440 |
| `Graphic I/O field_3` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3208` | Hmi.Screen.TextField | (486, 90, 233x295) | (712, 200, 45x26) | 182 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `Graphic I/O field_13` | Hmi.Screen.GraphicIOField | (811, 89, 233x295) | (860, 69, 51x78) | 2958 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `Graphic I/O field_18` | Hmi.Screen.GraphicIOField | (811, 89, 233x295) | (857, 346, 51x78) | 1938 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | (811, 89, 233x295) | (782, 86, 292x298) | 68735 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_18` | Hmi.Screen.TextField | (811, 89, 233x295) | (852, 324, 60x20) | 1200 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_IO_FT3215` | Hmi.Screen.IOField | (811, 89, 233x295) | (771, 69, 72x26) | 192 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3215` | Hmi.Screen.TextField | (811, 89, 233x295) | (851, 69, 45x26) | 270 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_IO_CV3216` | Hmi.Screen.IOField | (811, 89, 233x295) | (771, 104, 72x26) | 832 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_CV3216` | Hmi.Screen.TextField | (811, 89, 233x295) | (771, 79, 72x20) | 320 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3216` | Hmi.Screen.TextField | (811, 89, 233x295) | (851, 104, 45x26) | 1170 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_IO_LT3219` | Hmi.Screen.IOField | (811, 89, 233x295) | (957, 129, 72x26) | 1872 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3219` | Hmi.Screen.TextField | (811, 89, 233x295) | (957, 104, 72x20) | 1440 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3219` | Hmi.Screen.TextField | (811, 89, 233x295) | (1037, 129, 45x26) | 182 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_IO_TT3218` | Hmi.Screen.IOField | (811, 89, 233x295) | (957, 199, 72x26) | 1872 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3218` | Hmi.Screen.TextField | (811, 89, 233x295) | (957, 174, 72x20) | 1440 |
| `Graphic I/O field_4` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3218` | Hmi.Screen.TextField | (811, 89, 233x295) | (1037, 199, 45x26) | 182 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `Graphic I/O field_14` | Hmi.Screen.GraphicIOField | (1160, 89, 233x295) | (1193, 67, 51x78) | 2856 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `Graphic I/O field_19` | Hmi.Screen.GraphicIOField | (1160, 89, 233x295) | (1214, 347, 51x78) | 1887 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | (1160, 89, 233x295) | (1130, 89, 292x298) | 68735 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_19` | Hmi.Screen.TextField | (1160, 89, 233x295) | (1209, 325, 60x20) | 1200 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_IO_FT3210` | Hmi.Screen.IOField | (1160, 89, 233x295) | (1120, 69, 72x26) | 192 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3210` | Hmi.Screen.TextField | (1160, 89, 233x295) | (1200, 69, 45x26) | 270 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_IO_CV3211` | Hmi.Screen.IOField | (1160, 89, 233x295) | (1120, 104, 72x26) | 832 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_CV3211` | Hmi.Screen.TextField | (1160, 89, 233x295) | (1120, 79, 72x20) | 320 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3211` | Hmi.Screen.TextField | (1160, 89, 233x295) | (1200, 104, 45x26) | 1170 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_IO_LT3214` | Hmi.Screen.IOField | (1160, 89, 233x295) | (1306, 129, 72x26) | 1872 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3214` | Hmi.Screen.TextField | (1160, 89, 233x295) | (1306, 104, 72x20) | 1440 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3214` | Hmi.Screen.TextField | (1160, 89, 233x295) | (1386, 129, 45x26) | 182 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_IO_TT3213` | Hmi.Screen.IOField | (1160, 89, 233x295) | (1306, 199, 72x26) | 1872 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3213` | Hmi.Screen.TextField | (1160, 89, 233x295) | (1306, 174, 72x20) | 1440 |
| `Graphic I/O field_6` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3213` | Hmi.Screen.TextField | (1160, 89, 233x295) | (1386, 199, 45x26) | 182 |
| `Graphic I/O field_5` | Hmi.Screen.GraphicIOField | `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | (189, 70, 51x78) | (123, 84, 292x298) | 3264 |
| `Graphic I/O field_5` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3200` | Hmi.Screen.TextField | (189, 70, 51x78) | (194, 70, 45x26) | 1170 |
| `Graphic I/O field_5` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3201` | Hmi.Screen.TextField | (189, 70, 51x78) | (194, 105, 45x26) | 1170 |
| `Graphic I/O field_12` | Hmi.Screen.GraphicIOField | `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | (533, 70, 51x78) | (459, 83, 292x298) | 3315 |
| `Graphic I/O field_12` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3205` | Hmi.Screen.TextField | (533, 70, 51x78) | (526, 70, 45x26) | 988 |
| `Graphic I/O field_12` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3206` | Hmi.Screen.TextField | (533, 70, 51x78) | (526, 105, 45x26) | 988 |
| `Graphic I/O field_13` | Hmi.Screen.GraphicIOField | `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | (860, 69, 51x78) | (782, 86, 292x298) | 3111 |
| `Graphic I/O field_13` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3215` | Hmi.Screen.TextField | (860, 69, 51x78) | (851, 69, 45x26) | 936 |
| `Graphic I/O field_13` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3216` | Hmi.Screen.TextField | (860, 69, 51x78) | (851, 104, 45x26) | 936 |
| `Graphic I/O field_14` | Hmi.Screen.GraphicIOField | `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | (1193, 67, 51x78) | (1130, 89, 292x298) | 2856 |
| `Graphic I/O field_14` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3210` | Hmi.Screen.TextField | (1193, 67, 51x78) | (1200, 69, 45x26) | 1144 |
| `Graphic I/O field_14` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3211` | Hmi.Screen.TextField | (1193, 67, 51x78) | (1200, 104, 45x26) | 1144 |
| `Graphic I/O field_8` | Hmi.Screen.GraphicIOField | `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | (220, 339, 51x78) | (123, 84, 292x298) | 2193 |
| `Graphic I/O field_8` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_11` | Hmi.Screen.TextField | (220, 339, 51x78) | (215, 407, 60x20) | 510 |
| `Graphic I/O field_15` | Hmi.Screen.GraphicIOField | `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | (556, 341, 51x78) | (459, 83, 292x298) | 2040 |
| `Graphic I/O field_15` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_16` | Hmi.Screen.TextField | (556, 341, 51x78) | (553, 395, 60x20) | 1020 |
| `Graphic I/O field_18` | Hmi.Screen.GraphicIOField | `Graphic I/O field_20` | Hmi.Screen.GraphicIOField | (857, 346, 51x78) | (857, 412, 51x78) | 612 |
| `Graphic I/O field_18` | Hmi.Screen.GraphicIOField | `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | (857, 346, 51x78) | (782, 86, 292x298) | 1938 |
| `Graphic I/O field_18` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_20` | Hmi.Screen.TextField | (857, 346, 51x78) | (852, 390, 60x20) | 1020 |
| `Graphic I/O field_19` | Hmi.Screen.GraphicIOField | `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | (1214, 347, 51x78) | (1130, 89, 292x298) | 2040 |
| `Graphic I/O field_19` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_21` | Hmi.Screen.TextField | (1214, 347, 51x78) | (1208, 397, 60x20) | 1020 |
| `Graphic I/O field_24` | Hmi.Screen.GraphicIOField | `Graphic I/O field_34` | Hmi.Screen.GraphicIOField | (554, 759, 51x78) | (587, 792, 90x71) | 810 |
| `Graphic I/O field_22` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_20` | Hmi.Screen.TextField | (903, 387, 83x47) | (852, 390, 60x20) | 180 |
| `Graphic I/O field_23` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_21` | Hmi.Screen.TextField | (1257, 394, 83x47) | (1208, 397, 60x20) | 220 |
| `Graphic I/O field_1` | Hmi.Screen.GraphicIOField | `Graphic I/O field_34` | Hmi.Screen.GraphicIOField | (608, 851, 60x42) | (587, 792, 90x71) | 720 |
| `Graphic I/O field_1` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_34` | Hmi.Screen.TextField | (608, 851, 60x42) | (602, 865, 60x20) | 1080 |
| `Graphic I/O field_25` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3301` | Hmi.Screen.TextField | (672, 597, 51x78) | (660, 640, 45x26) | 858 |
| `Graphic I/O field_27` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_1` | Hmi.Screen.TextField | (725, 829, 51x78) | (676, 862, 72x20) | 460 |
| `Graphic I/O field_26` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_27` | Hmi.Screen.TextField | (725, 757, 51x78) | (720, 807, 60x20) | 1020 |
| `Graphic I/O field_28` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_PI3308` | Hmi.Screen.TextField | (1030, 754, 51x78) | (970, 795, 72x20) | 240 |
| `Graphic I/O field_28` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_PI3308` | Hmi.Screen.TextField | (1030, 754, 51x78) | (1050, 820, 45x26) | 372 |
| `Graphic I/O field_35` | Hmi.Screen.GraphicIOField | `Graphic I/O field_36` | Hmi.Screen.GraphicIOField | (1108, 764, 90x71) | (1123, 820, 60x42) | 900 |
| `Graphic I/O field_36` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_35` | Hmi.Screen.TextField | (1123, 820, 60x42) | (1123, 837, 60x20) | 1200 |
| `Graphic I/O field_29` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_FT3309` | Hmi.Screen.TextField | (1191, 655, 51x78) | (1190, 715, 72x20) | 918 |
| `Graphic I/O field_37` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3307` | Hmi.Screen.TextField | (1156, 541, 60x42) | (1134, 566, 45x26) | 391 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `I/O field_1` | Hmi.Screen.IOField | (123, 84, 292x298) | (113, 69, 67x32) | 969 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `I/O field_2` | Hmi.Screen.IOField | (123, 84, 292x298) | (300, 127, 67x28) | 1876 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_8` | Hmi.Screen.TextField | (123, 84, 292x298) | (215, 317, 60x20) | 1200 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_IO_FT3200` | Hmi.Screen.IOField | (123, 84, 292x298) | (114, 70, 72x26) | 756 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3200` | Hmi.Screen.TextField | (123, 84, 292x298) | (194, 70, 45x26) | 540 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_IO_CV3201` | Hmi.Screen.IOField | (123, 84, 292x298) | (114, 105, 72x26) | 1638 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_CV3201` | Hmi.Screen.TextField | (123, 84, 292x298) | (114, 80, 72x20) | 1008 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3201` | Hmi.Screen.TextField | (123, 84, 292x298) | (194, 105, 45x26) | 1170 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_IO_LT3203` | Hmi.Screen.IOField | (123, 84, 292x298) | (300, 130, 72x26) | 1872 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3203` | Hmi.Screen.TextField | (123, 84, 292x298) | (300, 105, 72x20) | 1440 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3203` | Hmi.Screen.TextField | (123, 84, 292x298) | (380, 130, 45x26) | 910 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_IO_TT3204` | Hmi.Screen.IOField | (123, 84, 292x298) | (300, 200, 72x26) | 1872 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3204` | Hmi.Screen.TextField | (123, 84, 292x298) | (300, 175, 72x20) | 1440 |
| `Graphic I/O field_38` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3204` | Hmi.Screen.TextField | (123, 84, 292x298) | (380, 200, 45x26) | 910 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_15` | Hmi.Screen.TextField | (459, 83, 292x298) | (551, 319, 60x20) | 1200 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_IO_FT3205` | Hmi.Screen.IOField | (459, 83, 292x298) | (446, 70, 72x26) | 767 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3205` | Hmi.Screen.TextField | (459, 83, 292x298) | (526, 70, 45x26) | 585 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_IO_CV3206` | Hmi.Screen.IOField | (459, 83, 292x298) | (446, 105, 72x26) | 1534 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_CV3206` | Hmi.Screen.TextField | (459, 83, 292x298) | (446, 80, 72x20) | 1003 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3206` | Hmi.Screen.TextField | (459, 83, 292x298) | (526, 105, 45x26) | 1170 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_IO_LT3209` | Hmi.Screen.IOField | (459, 83, 292x298) | (632, 130, 72x26) | 1872 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3209` | Hmi.Screen.TextField | (459, 83, 292x298) | (632, 105, 72x20) | 1440 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3209` | Hmi.Screen.TextField | (459, 83, 292x298) | (712, 130, 45x26) | 1014 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_IO_TT3208` | Hmi.Screen.IOField | (459, 83, 292x298) | (632, 200, 72x26) | 1872 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3208` | Hmi.Screen.TextField | (459, 83, 292x298) | (632, 175, 72x20) | 1440 |
| `Graphic I/O field_39` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3208` | Hmi.Screen.TextField | (459, 83, 292x298) | (712, 200, 45x26) | 1014 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_18` | Hmi.Screen.TextField | (782, 86, 292x298) | (852, 324, 60x20) | 1200 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_IO_FT3215` | Hmi.Screen.IOField | (782, 86, 292x298) | (771, 69, 72x26) | 549 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3215` | Hmi.Screen.TextField | (782, 86, 292x298) | (851, 69, 45x26) | 405 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_IO_CV3216` | Hmi.Screen.IOField | (782, 86, 292x298) | (771, 104, 72x26) | 1586 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_CV3216` | Hmi.Screen.TextField | (782, 86, 292x298) | (771, 79, 72x20) | 793 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3216` | Hmi.Screen.TextField | (782, 86, 292x298) | (851, 104, 45x26) | 1170 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_IO_LT3219` | Hmi.Screen.IOField | (782, 86, 292x298) | (957, 129, 72x26) | 1872 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3219` | Hmi.Screen.TextField | (782, 86, 292x298) | (957, 104, 72x20) | 1440 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3219` | Hmi.Screen.TextField | (782, 86, 292x298) | (1037, 129, 45x26) | 962 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_IO_TT3218` | Hmi.Screen.IOField | (782, 86, 292x298) | (957, 199, 72x26) | 1872 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3218` | Hmi.Screen.TextField | (782, 86, 292x298) | (957, 174, 72x20) | 1440 |
| `Graphic I/O field_40` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3218` | Hmi.Screen.TextField | (782, 86, 292x298) | (1037, 199, 45x26) | 962 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_Lbl_Graphic I/O field_19` | Hmi.Screen.TextField | (1130, 89, 292x298) | (1209, 325, 60x20) | 1200 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_IO_FT3210` | Hmi.Screen.IOField | (1130, 89, 292x298) | (1120, 69, 72x26) | 372 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_FT3210` | Hmi.Screen.TextField | (1130, 89, 292x298) | (1200, 69, 45x26) | 270 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_IO_CV3211` | Hmi.Screen.IOField | (1130, 89, 292x298) | (1120, 104, 72x26) | 1612 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_CV3211` | Hmi.Screen.TextField | (1130, 89, 292x298) | (1120, 79, 72x20) | 620 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_CV3211` | Hmi.Screen.TextField | (1130, 89, 292x298) | (1200, 104, 45x26) | 1170 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_IO_LT3214` | Hmi.Screen.IOField | (1130, 89, 292x298) | (1306, 129, 72x26) | 1872 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_LT3214` | Hmi.Screen.TextField | (1130, 89, 292x298) | (1306, 104, 72x20) | 1440 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_LT3214` | Hmi.Screen.TextField | (1130, 89, 292x298) | (1386, 129, 45x26) | 936 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_IO_TT3213` | Hmi.Screen.IOField | (1130, 89, 292x298) | (1306, 199, 72x26) | 1872 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_TT3213` | Hmi.Screen.TextField | (1130, 89, 292x298) | (1306, 174, 72x20) | 1440 |
| `Graphic I/O field_41` | Hmi.Screen.GraphicIOField | `AI_Unit_AI_IO_TT3213` | Hmi.Screen.TextField | (1130, 89, 292x298) | (1386, 199, 45x26) | 936 |
| `Graphic I/O field_31` | Hmi.Screen.GraphicIOField | `AI_IO_PI3308` | Hmi.Screen.IOField | (930, 792, 83x47) | (970, 820, 72x26) | 817 |
| `Graphic I/O field_31` | Hmi.Screen.GraphicIOField | `AI_Lbl_AI_IO_PI3308` | Hmi.Screen.TextField | (930, 792, 83x47) | (970, 795, 72x20) | 860 |
| `I/O field_1` | Hmi.Screen.IOField | `AI_IO_FT3200` | Hmi.Screen.IOField | (113, 69, 67x32) | (114, 70, 72x26) | 1716 |
| `I/O field_1` | Hmi.Screen.IOField | `AI_Lbl_AI_IO_CV3201` | Hmi.Screen.TextField | (113, 69, 67x32) | (114, 80, 72x20) | 1320 |
| `I/O field_2` | Hmi.Screen.IOField | `AI_IO_LT3203` | Hmi.Screen.IOField | (300, 127, 67x28) | (300, 130, 72x26) | 1675 |
| `AI_Lbl_Graphic I/O field_37` | Hmi.Screen.TextField | `AI_Unit_AI_IO_LT3307` | Hmi.Screen.TextField | (1156, 585, 60x20) | (1134, 566, 45x26) | 161 |
| `AI_Lbl_Graphic I/O field_25` | Hmi.Screen.TextField | `AI_Unit_AI_IO_LT3302` | Hmi.Screen.TextField | (667, 575, 60x20) | (660, 570, 45x26) | 760 |
| `AI_Lbl_Graphic I/O field_31` | Hmi.Screen.TextField | `AI_IO_PI3308` | Hmi.Screen.IOField | (941, 841, 60x20) | (970, 820, 72x26) | 155 |
| `AI_IO_FT3200` | Hmi.Screen.IOField | `AI_Lbl_AI_IO_CV3201` | Hmi.Screen.TextField | (114, 70, 72x26) | (114, 80, 72x20) | 1152 |
| `AI_IO_FT3205` | Hmi.Screen.IOField | `AI_Lbl_AI_IO_CV3206` | Hmi.Screen.TextField | (446, 70, 72x26) | (446, 80, 72x20) | 1152 |
| `AI_IO_FT3215` | Hmi.Screen.IOField | `AI_Lbl_AI_IO_CV3216` | Hmi.Screen.TextField | (771, 69, 72x26) | (771, 79, 72x20) | 1152 |
| `AI_IO_FT3210` | Hmi.Screen.IOField | `AI_Lbl_AI_IO_CV3211` | Hmi.Screen.TextField | (1120, 69, 72x26) | (1120, 79, 72x20) | 1152 |

---

## 3. Đối chiếu XML với TIA Portal (Tag References)

Tổng số HMI Tag màn hình XML tham chiếu: **66**
- Số tag HMI đã tồn tại trong TIA Portal: **3** (gồm Logged_In, HMI_SP_PLC2_Nhiet_Do_Bon4, HMI_SP_PLC2_Nuoc_Bon3)
- Số tag HMI thiếu (chưa được tạo/import): **63**

### Danh sách chi tiết ánh xạ 66 tag tham chiếu:

| Tên Tag màn hình | Tồn tại ở HMI TIA? | Vị trí thực tế ở PLC | Địa chỉ PLC | Trạng thái Pre-flight |
| :--- | :--- | :--- | :--- | :--- |
| `CV3201_Nuoc_Bon1_M` | CHƯA CÓ | `PLC_1` | `%MD1200` | MISSING IN HMI TAG TABLE |
| `CV3206_Hoi_Bon2_M` | CHƯA CÓ | `PLC_1` | `%MD1208` | MISSING IN HMI TAG TABLE |
| `CV3211_Nuoc_Bon3_M` | CHƯA CÓ | `PLC_2` | `%MD1216` | MISSING IN HMI TAG TABLE |
| `CV3216_Hoi_Bon4_M` | CHƯA CÓ | `PLC_2` | `%MD1224` | MISSING IN HMI TAG TABLE |
| `CV3304_Nuoc_Lam_Mat_M` | CHƯA CÓ | `PLC_1` | `%MD1232` | MISSING IN HMI TAG TABLE |
| `CV_Filler_Cap_Dich_M` | CHƯA CÓ | `PLC_1` | `%MD1236` | MISSING IN HMI TAG TABLE |
| `FQ3200_Bon1_Eff` | CHƯA CÓ | `PLC_1` | `%MD712` | MISSING IN HMI TAG TABLE |
| `FQ3205_Bon2_Eff` | CHƯA CÓ | `PLC_1` | `%MD744` | MISSING IN HMI TAG TABLE |
| `FQ3210_Bon3_Eff` | CHƯA CÓ | `PLC_2` | `%MD776` | MISSING IN HMI TAG TABLE |
| `FQ3215_Bon4_Eff` | CHƯA CÓ | `PLC_2` | `%MD808` | MISSING IN HMI TAG TABLE |
| `FT3309_Xa_Thanh_Pham_Eff` | CHƯA CÓ | `PLC_1` | `%MD880` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_Bon1_Frame` | CHƯA CÓ | `PLC_1` | `%MW542` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_Bon1_MucDich` | CHƯA CÓ | `None` | `None` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_Bon2_Frame` | CHƯA CÓ | `PLC_1` | `%MW544` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_Bon2_MucDich` | CHƯA CÓ | `None` | `None` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_Bon3_Frame` | CHƯA CÓ | `PLC_2` | `%MW546` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_Bon3_MucDich` | CHƯA CÓ | `None` | `None` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_Bon4_Frame` | CHƯA CÓ | `PLC_2` | `%MW548` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_Bon4_MucDich` | CHƯA CÓ | `None` | `None` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_BonChua1_MucDich` | CHƯA CÓ | `None` | `None` | MISSING IN HMI TAG TABLE |
| `HMI_Anim_BonChua2_MucDich` | CHƯA CÓ | `None` | `None` | MISSING IN HMI TAG TABLE |
| `LT3203_Bon1_Eff` | CHƯA CÓ | `PLC_1` | `%MD720` | MISSING IN HMI TAG TABLE |
| `LT3209_Bon2_Eff` | CHƯA CÓ | `PLC_1` | `%MD752` | MISSING IN HMI TAG TABLE |
| `LT3213_Bon3_Eff` | CHƯA CÓ | `PLC_2` | `%MD784` | MISSING IN HMI TAG TABLE |
| `LT3218_Bon4_Eff` | CHƯA CÓ | `PLC_2` | `%MD816` | MISSING IN HMI TAG TABLE |
| `LT3302_BonChua1_Eff` | CHƯA CÓ | `PLC_1` | `%MD832` | MISSING IN HMI TAG TABLE |
| `LT3307_BonChua2_Eff` | CHƯA CÓ | `PLC_1` | `%MD856` | MISSING IN HMI TAG TABLE |
| `PI3308_Truoc_Filter_Eff` | CHƯA CÓ | `PLC_1` | `%MD872` | MISSING IN HMI TAG TABLE |
| `Pump3264_Chuyen_Nhanh1_M` | CHƯA CÓ | `PLC_1` | `%M221.3` | MISSING IN HMI TAG TABLE |
| `Pump3265_Chuyen_Nhanh2_M` | CHƯA CÓ | `PLC_2` | `%M222.7` | MISSING IN HMI TAG TABLE |
| `Pump3361_LuanChuyen_BonChua1_M` | CHƯA CÓ | `PLC_1` | `%M223.2` | MISSING IN HMI TAG TABLE |
| `Pump3362_Xa_BonChua1_M` | CHƯA CÓ | `PLC_1` | `%M223.3` | MISSING IN HMI TAG TABLE |
| `Pump3364_Filter_M` | CHƯA CÓ | `PLC_1` | `%M224.1` | MISSING IN HMI TAG TABLE |
| `Pump3365_Filter_M` | CHƯA CÓ | `PLC_1` | `%M224.2` | MISSING IN HMI TAG TABLE |
| `TT3204_Bon1_Eff` | CHƯA CÓ | `PLC_1` | `%MD728` | MISSING IN HMI TAG TABLE |
| `TT3208_Bon2_Eff` | CHƯA CÓ | `PLC_1` | `%MD760` | MISSING IN HMI TAG TABLE |
| `TT3214_Bon3_Eff` | CHƯA CÓ | `PLC_2` | `%MD792` | MISSING IN HMI TAG TABLE |
| `TT3219_Bon4_Eff` | CHƯA CÓ | `PLC_2` | `%MD824` | MISSING IN HMI TAG TABLE |
| `TT3301_BonChua1_Eff` | CHƯA CÓ | `PLC_1` | `%MD840` | MISSING IN HMI TAG TABLE |
| `TT3303_TraoDoiNhiet_Eff` | CHƯA CÓ | `PLC_1` | `%MD848` | MISSING IN HMI TAG TABLE |
| `TT3306_BonChua2_Eff` | CHƯA CÓ | `PLC_1` | `%MD864` | MISSING IN HMI TAG TABLE |
| `V3230_Nuoc_Bon1_M` | CHƯA CÓ | `PLC_1` | `%M220.0` | MISSING IN HMI TAG TABLE |
| `V3232_Xa_Bon1_M` | CHƯA CÓ | `PLC_1` | `%M220.2` | MISSING IN HMI TAG TABLE |
| `V3233_Xa_Bon1_M` | CHƯA CÓ | `PLC_1` | `%M220.3` | MISSING IN HMI TAG TABLE |
| `V3234_Xa_Bon1_M` | CHƯA CÓ | `PLC_1` | `%M220.4` | MISSING IN HMI TAG TABLE |
| `V3235_Nuoc_Bon2_M` | CHƯA CÓ | `PLC_1` | `%M220.5` | MISSING IN HMI TAG TABLE |
| `V3237_Xa_Bon2_M` | CHƯA CÓ | `PLC_1` | `%M221.0` | MISSING IN HMI TAG TABLE |
| `V3238_Xa_Bon2_M` | CHƯA CÓ | `PLC_1` | `%M221.1` | MISSING IN HMI TAG TABLE |
| `V3239_Xa_Bon2_M` | CHƯA CÓ | `PLC_1` | `%M221.2` | MISSING IN HMI TAG TABLE |
| `V3240_Nuoc_Bon3_M` | CHƯA CÓ | `PLC_2` | `%M221.4` | MISSING IN HMI TAG TABLE |
| `V3242_Xa_Bon3_M` | CHƯA CÓ | `PLC_2` | `%M221.6` | MISSING IN HMI TAG TABLE |
| `V3243_Xa_Bon3_M` | CHƯA CÓ | `PLC_2` | `%M221.7` | MISSING IN HMI TAG TABLE |
| `V3244_Xa_Bon3_M` | CHƯA CÓ | `PLC_2` | `%M222.0` | MISSING IN HMI TAG TABLE |
| `V3245_Nuoc_Bon4_M` | CHƯA CÓ | `PLC_2` | `%M222.1` | MISSING IN HMI TAG TABLE |
| `V3247_Xa_Bon4_M` | CHƯA CÓ | `PLC_2` | `%M222.4` | MISSING IN HMI TAG TABLE |
| `V3248_Xa_Bon4_M` | CHƯA CÓ | `PLC_2` | `%M222.5` | MISSING IN HMI TAG TABLE |
| `V3249_Xa_Bon4_M` | CHƯA CÓ | `PLC_2` | `%M222.6` | MISSING IN HMI TAG TABLE |
| `V3331_Xa_BonChua1_M` | CHƯA CÓ | `PLC_1` | `%M223.0` | MISSING IN HMI TAG TABLE |
| `V3332_Xa_BonChua1_M` | CHƯA CÓ | `PLC_1` | `%M223.1` | MISSING IN HMI TAG TABLE |
| `V3333_DieuHuong_BonChua1_M` | CHƯA CÓ | `PLC_1` | `%M223.4` | MISSING IN HMI TAG TABLE |
| `V3334_DieuHuong_BonChua1_M` | CHƯA CÓ | `PLC_1` | `%M223.5` | MISSING IN HMI TAG TABLE |
| `V3335_DieuHuong_BonChua1_M` | CHƯA CÓ | `PLC_1` | `%M223.6` | MISSING IN HMI TAG TABLE |
| `V3338_Xa_BonChua2_M` | CHƯA CÓ | `PLC_1` | `%M223.7` | MISSING IN HMI TAG TABLE |
| `V3339_Xa_BonChua2_M` | CHƯA CÓ | `PLC_1` | `%M224.0` | MISSING IN HMI TAG TABLE |
| `V3340_Duong_Filter_M` | CHƯA CÓ | `PLC_1` | `%M224.3` | MISSING IN HMI TAG TABLE |
| `V3341_Duong_Filter_M` | CHƯA CÓ | `PLC_1` | `%M224.4` | MISSING IN HMI TAG TABLE |

---

## 4. Xác định nguyên nhân lỗi

> [!WARNING]
> **Lỗi:** *“The controller tag CV3211_Nuoc_Bon3_M was not found.”*
> 
> **Phân tích nguyên nhân:**
> 1. **Kiểu kết nối:** HMI `HMI_RT_1` chỉ có duy nhất **một kết nối tích hợp** kết nối trực tiếp đến **`PLC_1`** (được hiển thị là `HMI_Connection_1`). Không có kết nối trực tiếp từ HMI sang `PLC_2`.
> 2. **Vị trí của Tag:** Tag điều khiển `CV3211_Nuoc_Bon3_M` thực chất thuộc về **`PLC_2`** (station_2) và **không tồn tại** trong bảng tag của `PLC_1`.
> 3. **Cơ chế lỗi:** Khi chúng ta cố gắng tạo tag HMI `CV3211_Nuoc_Bon3_M` tham chiếu qua kết nối `HMI_Connection_1` (kết nối tới `PLC_1`), TIA Portal tìm kiếm tag này trong `PLC_1`. Vì tag này chỉ nằm ở `PLC_2`, TIA Portal ném ra ngoại lệ và dừng quá trình import tag.
> 4. **Trường hợp của `HMI_SP_PLC2_Nhiet_Do_Bon4`:** Tag này import thành công trước đó vì nó được khai báo trùng lặp (dual-defined) ở cả `PLC_1` (với địa chỉ `%MD932`) và `PLC_2` (với địa chỉ `%MD932`). Do đó, khi kết nối tới `PLC_1`, nó tìm thấy tag có tên này.
> 5. **Các biến Bồn 3 & Bồn 4 khác:** Các biến như `CV3211_Nuoc_Bon3_M`, `LT3213_Bon3_Eff`, `TT3214_Bon3_Eff`, `V3240_Nuoc_Bon3_M` đều nằm hoàn toàn ở `PLC_2` và không có bản sao ở `PLC_1` nên đều sẽ bị lỗi này nếu cố gắng liên kết trực tiếp.

---

## 5. Đề xuất kế hoạch sửa đổi tối thiểu (Chưa thực hiện)

Để import thành công màn hình và tag mà không làm thay đổi kiến trúc kết nối hoặc chương trình PLC, ta áp dụng phương án **ánh xạ toàn bộ 66 Tag HMI về PLC_1** theo các bước sau:

### Bước 1: Khai báo bổ sung các Tag của PLC_2 vào bảng Tag của PLC_1 dưới dạng địa chỉ Modbus / Bộ đệm truyền thông
- Đối với các giá trị Analog của Bồn 3 & Bồn 4:
  - Sử dụng các biến truyền nhận Modbus TCP hiện có của PLC_1 để làm ControllerTag nguồn cho HMI:
    - `LT3213_Bon3_Eff` -> Đổi thành HMI tham chiếu tới `PLC2_Tip_Bon3_Timer` hoặc ánh xạ trung gian qua `%MD1056`?
    - Không! Hãy xem các biến nhận thực tế trong PLC_1:
      - `PID_Bon4_SP_Recv` (%MD884) -> Ánh xạ cho setpoint của Bồn 4 (`TT3219_Bon4_Target`).
      - `PID_Bon4_PV_Recv` (%MD888) -> Ánh xạ cho mức dịch / cảm biến PV của Bồn 4.
      - `PID_Bon4_CV_Recv` (%MD892) -> Ánh xạ cho van tuyến tính CV của Bồn 4.
      - `PLC2_Tip_Bon3_Timer` (%MD1056) -> Cho Bồn 3.
      - `PLC2_Tip_Bon4_Timer` (%MD1060) -> Cho Bồn 4.
  - Đối với các van/bơm đồ họa hoặc các tag chưa được đồng bộ Modbus sang PLC_1:
    - Để HMI không bị lỗi compile/import, ta **tạo các tag này trong PLC_1** (trong bảng `PLC_Tags` của `PLC_1`) với cùng kiểu dữ liệu. Sau đó viết code chuyển đổi Modbus ở PLC (nếu cần), hoặc HMI sẽ tham chiếu trực tiếp đến địa chỉ vùng nhớ đệm đã đồng bộ trên PLC_1.
    - Cụ thể: Khai báo thêm 28 tag thiếu (ví dụ `CV3211_Nuoc_Bon3_M`, `V3240_Nuoc_Bon3_M`, `LT3213_Bon3_Eff`, v.v.) vào `PLC_1` dưới dạng các tag trung gian để TIA Portal nhận diện được khi import bảng Tag HMI qua `HMI_Connection_1`.

### Bước 2: Cập nhật hàm sinh Tag HMI trong script Python
- Cập nhật `patch_man_tong_quan.py` để tất cả 66 tag HMI đều sử dụng `HMI_Connection_1` và liên kết với các tag tương ứng đã tồn tại/khai báo ở `PLC_1`.

### Bước 3: Thực hiện Import Tag Table vào TIA Portal
- Chạy import tệp `AI_HMI_Tags.xml` sau khi PLC_1 đã có đủ các tag tương ứng.

### Bước 4: Kiểm tra màn hình và XML và bàn giao
- Chạy kiểm tra QA và acceptance test.

---

## 6. Kết luận

### **NOT READY FOR IMPORT**

*(Cần thực hiện khai báo bổ sung các tag của PLC_2 vào PLC_1 để làm cầu nối truyền thông, hoặc tạo các biến đệm tương ứng trên PLC_1 trước khi có thể chạy import bảng tag HMI)*