# PHÂN TÍCH MÀN HÌNH GỐC (WinCC Pro cũ) - MAPPING TAG ĐÚNG
# Dựa trên ảnh chụp màn hình gốc và file XML hmi_export_actual/Hmi.Screen.Screen_2.xml

"""
MÀN HÌNH GỐC LAYOUT (CIP-MIXING, 1920x1080):
==============================================

Tiêu đề: CIP-MIXING
4 bồn (BON TRON 1, 2, 3, 4) từ trái sang phải

PHÂN TÍCH IO FIELDS TỪ XML GỐC:
  I/O field_1   L=1653  T=536   → Tag: 1400_TT32_PV    (°C)
  I/O field_2   L=651   T=766   → Tag: 1400_FS51_PV    (Hz)
  I/O field_3   L=124   T=828   → Tag: 1400_LGFE01_PV  (%)
  I/O field_4   L=805   T=697   → Tag: 1406_TX35_PV    (°C)
  I/O field_7   L=746   T=327   → Tag: 1400_FT101_PV   (Bar)
  I/O field_8   L=481   T=270   → Tag: 1400_FT115_PV   (°C)
  I/O field_9   L=1189  T=265   → Tag: 1400_1_02_PV    (°C)
  I/O field_10  L=1201  T=887   → Tag: 1400_FY301_PV   (%)
  I/O field_11  L=1385  T=537   → Tag: 1400_TT64_PV    (°C)

NHẬN XÉT VỀ VỊ TRÍ (trên màn hình 1920x1080):
  - field_7  (L=746,  T=327): Vùng trên-giữa    → áp suất FT101 (Bar)
  - field_8  (L=481,  T=270): Vùng trên-trái    → nhiệt độ FT115 (°C)
  - field_9  (L=1189, T=265): Vùng trên-phải    → cảm biến 1-02 (°C)
  - field_1  (L=1653, T=536): Vùng giữa-phải    → nhiệt độ TT32 (°C)
  - field_4  (L=805,  T=697): Vùng giữa         → áp suất/nhiệt TX35 (°C)
  - field_2  (L=651,  T=766): Vùng giữa-trái    → tần số FS51 (Hz)
  - field_3  (L=124,  T=828): Vùng dưới-trái    → lưu lượng LGFE01 (%)
  - field_10 (L=1201, T=887): Vùng dưới-phải    → điều chỉnh FY301 (%)
  - field_11 (L=1385, T=537): Vùng giữa-phải    → nhiệt độ TT64 (°C)

MAPPING ĐÚNG CHO ACTIVE SCREEN (các field do user đặt thủ công):
  Khi bạn chỉnh xong vị trí trong TIA Portal, mở file:
  D:\\AI_Agent_PLC_LADDER_ONLY\\scratch\\fix_active_screen_io.py
  và cập nhật FIELD_MAPPINGS theo đúng IO field name + tag.

BẢNG THAM CHIẾU TAG:
=====================
Tag Name            | Đơn vị | Dải giá trị | Mô tả
--------------------|--------|-------------|-------------------
1400_TT32_PV        | °C     | 60-80       | Nhiệt độ TT32
1400_FS51_PV        | Hz     | 45-55       | Tần số bơm FS51
1400_LGFE01_PV      | %      | 200-500     | Lưu lượng LGFE01
1406_TX35_PV        | °C     | 2-8         | Áp suất/Nhiệt TX35
1400_FT101_PV       | Bar    | 1-5         | Áp suất FT101
1400_FY301_PV       | %      | 10-90       | Điều chỉnh FY301
1400_FT115_PV       | °C     | 50-75       | Nhiệt độ FT115
1400_TT64_PV        | °C     | 55-70       | Nhiệt độ TT64
1400_TT101_PV       | °C     | 58-72       | Nhiệt độ TT101
1400_FTT02_PV       | °C     | 48-68       | Nhiệt độ FTT02
1400_1_02_PV        | °C     | 60-85       | Cảm biến 1-02
"""
