# Báo cáo ánh xạ HMI (Dry-Run Mapping Report) - Màn hình Tổng quan

Dự án: `Mixing_Nuoc_Tuong_Maggi_2026`  
Màn hình sửa đổi: `Hmi.Screen.Man Tong Quan.xml`  

## 1. Danh sách cảm biến đo lường và van tuyến tính (25 IOFields mới sinh)

| Ký hiệu màn hình | Tag PLC liên kết | Đơn vị | Định dạng | Vị trí HMI (X, Y) |
| :--- | :--- | :--- | :--- | :--- |
| FT 32.00 | `FQ3200_Bon1_Eff` | L | `999.9` | (114, 70) |
| CV 32.01 | `CV3201_Nuoc_Bon1_M` | % | `999.9` | (114, 105) |
| LT 32.03 | `LT3203_Bon1_Eff` | % | `999.9` | (300, 130) |
| TT 32.04 | `TT3204_Bon1_Eff` | °C | `99.9` | (300, 200) |
| FT 32.05 | `FQ3205_Bon2_Eff` | L | `999.9` | (446, 70) |
| CV 32.06 | `CV3206_Hoi_Bon2_M` | % | `999.9` | (446, 105) |
| LT 32.09 | `LT3209_Bon2_Eff` | % | `999.9` | (632, 130) |
| TT 32.08 | `TT3208_Bon2_Eff` | °C | `99.9` | (632, 200) |
| FT 32.15 | `FQ3215_Bon4_Eff` | L | `999.9` | (771, 69) |
| CV 32.16 | `CV3216_Hoi_Bon4_M` | % | `999.9` | (771, 104) |
| LT 32.18 | `LT3218_Bon4_Eff` | % | `999.9` | (957, 129) |
| TT 32.19 | `TT3219_Bon4_Eff` | °C | `99.9` | (957, 199) |
| FT 32.10 | `FQ3210_Bon3_Eff` | L | `999.9` | (1120, 69) |
| CV 32.11 | `CV3211_Nuoc_Bon3_M` | % | `999.9` | (1120, 104) |
| LT 32.13 | `LT3213_Bon3_Eff` | % | `999.9` | (1306, 129) |
| TT 32.14 | `TT3214_Bon3_Eff` | °C | `99.9` | (1306, 199) |
| LT 33.02 | `LT3302_BonChua1_Eff` | % | `999.9` | (580, 570) |
| TT 33.01 | `TT3301_BonChua1_Eff` | °C | `99.9` | (580, 640) |
| LT 33.07 | `LT3307_BonChua2_Eff` | % | `999.9` | (1054, 566) |
| TT 33.06 | `TT3306_BonChua2_Eff` | °C | `99.9` | (1054, 636) |
| TT 33.03 | `TT3303_TraoDoiNhiet_Eff` | °C | `99.9` | (1270, 636) |
| CV 33.04 | `CV3304_Nuoc_Lam_Mat_M` | % | `999.9` | (1270, 706) |
| PI 33.08 | `PI3308_Truoc_Filter_Eff` | bar | `99.9` | (970, 820) |
| FT 33.09 | `FT3309_Xa_Thanh_Pham_Eff` | L/h | `999.9` | (1190, 740) |
| CV Filler | `CV_Filler_Cap_Dich_M` | % | `999.9` | (1290, 820) |

## 2. Danh sách thiết bị dạng đồ họa hoạt hình (GraphicIOFields gốc - 41 thiết bị)

| Ký hiệu thiết bị | Tên đối tượng gốc | Tag PLC liên kết | Loại thiết bị | Vị trí HMI (X, Y) |
| :--- | :--- | :--- | :--- | :--- |
| Pump 33.62 | `Graphic I/O field_1` | `Pump3362_Xa_BonChua1_M` | Bơm | (608, 851) |
| N/A | `Graphic I/O field_10` | `HMI_Anim_Bon1_MucDich` | Mức dịch bồn | (154, 90) |
| V32.33 | `Graphic I/O field_11` | `V3233_Xa_Bon1_M` | Van ON/OFF | (220, 429) |
| V32.35 | `Graphic I/O field_12` | `V3235_Nuoc_Bon2_M` | Van ON/OFF | (533, 70) |
| V32.45 | `Graphic I/O field_13` | `V3245_Nuoc_Bon4_M` | Van ON/OFF | (860, 69) |
| V32.40 | `Graphic I/O field_14` | `V3240_Nuoc_Bon3_M` | Van ON/OFF | (1193, 67) |
| V32.37 | `Graphic I/O field_15` | `V3237_Xa_Bon2_M` | Van ON/OFF | (556, 341) |
| V32.38 | `Graphic I/O field_16` | `V3238_Xa_Bon2_M` | Van ON/OFF | (558, 417) |
| V32.39 | `Graphic I/O field_17` | `V3239_Xa_Bon2_M` | Van ON/OFF | (471, 394) |
| V32.47 | `Graphic I/O field_18` | `V3247_Xa_Bon4_M` | Van ON/OFF | (857, 346) |
| V32.42 | `Graphic I/O field_19` | `V3242_Xa_Bon3_M` | Van ON/OFF | (1214, 347) |
| N/A | `Graphic I/O field_2` | `HMI_Anim_BonChua2_MucDich` | Mức dịch bồn | (904, 517) |
| V32.48 | `Graphic I/O field_20` | `V3248_Xa_Bon4_M` | Van ON/OFF | (857, 412) |
| V32.43 | `Graphic I/O field_21` | `V3243_Xa_Bon3_M` | Van ON/OFF | (1213, 419) |
| V32.49 | `Graphic I/O field_22` | `V3249_Xa_Bon4_M` | Van ON/OFF | (903, 387) |
| V32.44 | `Graphic I/O field_23` | `V3244_Xa_Bon3_M` | Van ON/OFF | (1257, 394) |
| V33.31 | `Graphic I/O field_24` | `V3331_Xa_BonChua1_M` | Van ON/OFF | (554, 759) |
| V33.33 | `Graphic I/O field_25` | `V3333_DieuHuong_BonChua1_M` | Van ON/OFF | (672, 597) |
| V33.34 | `Graphic I/O field_26` | `V3334_DieuHuong_BonChua1_M` | Van ON/OFF | (725, 757) |
| V33.35 | `Graphic I/O field_27` | `V3335_DieuHuong_BonChua1_M` | Van ON/OFF | (725, 829) |
| V33.38 | `Graphic I/O field_28` | `V3338_Xa_BonChua2_M` | Van ON/OFF | (1030, 754) |
| V33.40 | `Graphic I/O field_29` | `V3340_Duong_Filter_M` | Van ON/OFF | (1191, 655) |
| N/A | `Graphic I/O field_3` | `HMI_Anim_Bon2_MucDich` | Mức dịch bồn | (486, 90) |
| V33.32 | `Graphic I/O field_30` | `V3332_Xa_BonChua1_M` | Van ON/OFF | (467, 804) |
| V33.39 | `Graphic I/O field_31` | `V3339_Xa_BonChua2_M` | Van ON/OFF | (930, 792) |
| V33.41 | `Graphic I/O field_32` | `V3341_Duong_Filter_M` | Van ON/OFF | (1346, 558) |
| Pump 32.64 | `Graphic I/O field_33` | `Pump3264_Chuyen_Nhanh1_M` | Bơm | (282, 542) |
| Pump 33.61 | `Graphic I/O field_34` | `Pump3361_LuanChuyen_BonChua1_M` | Bơm | (587, 792) |
| Pump 33.64 | `Graphic I/O field_35` | `Pump3364_Filter_M` | Bơm | (1108, 764) |
| Pump 33.65 | `Graphic I/O field_36` | `Pump3365_Filter_M` | Bơm | (1123, 820) |
| Pump 32.69 | `Graphic I/O field_37` | `Pump3265_Chuyen_Nhanh2_M` | Bơm | (1156, 541) |
| N/A | `Graphic I/O field_38` | `HMI_Anim_Bon1_Frame` | Động cơ cánh khuấy | (123, 84) |
| N/A | `Graphic I/O field_39` | `HMI_Anim_Bon2_Frame` | Động cơ cánh khuấy | (459, 83) |
| N/A | `Graphic I/O field_4` | `HMI_Anim_Bon4_MucDich` | Mức dịch bồn | (811, 89) |
| N/A | `Graphic I/O field_40` | `HMI_Anim_Bon4_Frame` | Động cơ cánh khuấy | (782, 86) |
| N/A | `Graphic I/O field_41` | `HMI_Anim_Bon3_Frame` | Động cơ cánh khuấy | (1130, 89) |
| V32.30 | `Graphic I/O field_5` | `V3230_Nuoc_Bon1_M` | Van ON/OFF | (189, 70) |
| N/A | `Graphic I/O field_6` | `HMI_Anim_Bon3_MucDich` | Mức dịch bồn | (1160, 89) |
| V32.34 | `Graphic I/O field_7` | `V3234_Xa_Bon1_M` | Van ON/OFF | (133, 396) |
| V32.32 | `Graphic I/O field_8` | `V3232_Xa_Bon1_M` | Van ON/OFF | (220, 339) |
| N/A | `Graphic I/O field_9` | `HMI_Anim_BonChua1_MucDich` | Mức dịch bồn | (430, 521) |