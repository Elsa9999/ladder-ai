# PLC2 Watch Table - Nhận Lệnh & Phản Hồi Modbus TCP Với PLC1

| Tên Biến (Tag Name) | Mô Tả / Chú Thích (Comment) |
| --- | --- |
| `"DB_Modbus_Holding_Register_DB".CmdSeq` | Sequence lệnh gửi từ PLC1 |
| `"DB_Modbus_Holding_Register_DB".Cmd_Start` | Lệnh Start từ PLC1 |
| `"DB_Modbus_Holding_Register_DB".Cmd_Stop` | Lệnh Stop từ PLC1 |
| `"DB_Modbus_Holding_Register_DB".Cmd_Reset` | Lệnh Reset từ PLC1 |
| `"DB_Modbus_Holding_Register_DB".Cmd_EStop` | Lệnh EStop từ PLC1 |
| `"DB_Modbus_Holding_Register_DB".Cmd_Load_Recipe` | Lệnh yêu cầu nạp Recipe mặc định từ PLC1 |
| `"DB_Modbus_Holding_Register_DB".Heartbeat_Client` | Heartbeat gửi từ PLC1 |
| `"DB_Modbus_Holding_Register_DB".AckSeq` | Sequence phản hồi báo nhận lệnh của PLC2 |
| `"DB_Modbus_Holding_Register_DB".Done_Branch2` | Nhánh 2 hoàn thành mẻ |
| `"DB_Modbus_Holding_Register_DB".Done_Discharge2` | Bồn 4 đã xả xong |
| `"DB_Modbus_Holding_Register_DB".Alarm` | Cảnh báo lỗi tổng từ PLC2 |
| `"DB_Modbus_Holding_Register_DB".State` | Trạng thái bước chu trình PLC2 |
