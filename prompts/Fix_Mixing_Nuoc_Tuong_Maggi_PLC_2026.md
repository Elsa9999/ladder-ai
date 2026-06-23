# PROMPT SỬA PLC/LAD - MIXING NƯỚC TƯƠNG MAGGI 2026

Bạn là kỹ sư PLC Siemens TIA Portal V18 và lập trình viên Python chuyên sinh Ladder XML. Hãy trực tiếp sửa mã nguồn trong workspace:

`D:\AI_Agent_PLC_LADDER_ONLY`

Dự án cần sửa:

`D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026`

## 1. Mục tiêu

Sửa phần PLC/LAD để hai PLC có thể chạy ổn định một mẻ hoàn chỉnh từ Bồn 1/Bồn 3 đến cụm bồn chứa và lọc.

Không làm HMI trong nhiệm vụ này.

Không chỉ viết kế hoạch hoặc báo cáo. Phải đọc mã hiện tại, sửa mã nguồn sinh XML, sinh lại toàn bộ output/import set, cập nhật test và chạy kiểm tra.

## 2. Quy tắc bắt buộc

1. Đọc và tuân thủ tuyệt đối `D:\AI_Agent_PLC_LADDER_ONLY\AGENTS.md`.
2. Toàn bộ OB, FB, FC phải là 100% Ladder XML. Không tạo SCL, không chèn SCL vào Network.
3. Không dùng S7 GET/PUT. PLC-to-PLC chỉ dùng Modbus TCP.
4. Dùng PID_Compact Version 1.2:
   - Enable: MOVE `3` vào `sRet.i_Mode`.
   - Disable: MOVE `0` vào `sRet.i_Mode`.
5. Dùng MB_CLIENT/MB_SERVER Version 3.1 cho S7-1200 V4.5.
6. Tên tag/DB mới phải là ASCII, bắt đầu bằng `AI_`.
7. Network Title và mô tả phải là tiếng Việt có dấu UTF-8.
8. Không sửa HMI, màn hình, layout hoặc style HMI.
9. Không xóa, reset hoặc hoàn tác thay đổi đang có trong worktree. Chỉ sửa đúng phạm vi cần thiết.
10. Không chỉnh trực tiếp file XML sinh ra để che lỗi. Nguồn sự thật là các generator Python và thư viện LAD; sau đó phải sinh lại XML.
11. Không được kết luận hoàn thành chỉ vì XML parse được hoặc TIA compile được. Phải kiểm tra hành vi tuần tự và liên động chạy thật.

## 3. Tệp cần đọc trước khi sửa

- `AGENTS.md`
- `ĐỀ THI VÒNG SƠ KHẢO.pdf`
- `projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py`
- `projects/Mixing_Nuoc_Tuong_Maggi_2026/prepare_tia_import_sets.py`
- `Ladder/Agent_LAD_Library.py`
- `scratch/test_plc_logic.py`
- `scratch/validate_tia_imports.py`
- `scratch/verify_post_import_export.py`
- `projects/Mixing_Nuoc_Tuong_Maggi_2026/post_import_export`
- `examples/TIA_V18_ModbusTCP_ManualExport`

Đọc logic hiện tại trước khi chọn giải pháp. Giữ cấu trúc và quy ước sẵn có nếu chúng vẫn phù hợp.

## 4. Các lỗi bắt buộc phải sửa

### P0. Bơm chuyển Nhánh 2 chỉ nhận xung một vòng quét

Hiện tại PLC1 gửi lệnh chuyển Nhánh 2 qua CmdSeq. PLC2 tạo:

`AI_Pump3265_Chuyen_Nhanh2_Cmd_Nhan`

chỉ trong một scan rồi dùng trực tiếp tín hiệu này để điều khiển:

`AI_Pump3265_Chuyen_Nhanh2`

Hậu quả: bơm chuyển Nhánh 2 chỉ chạy một vòng quét.

Yêu cầu:

- Tạo cơ chế giữ lệnh tại PLC2 sau cạnh lệnh hợp lệ.
- Chỉ xóa lệnh khi Bồn 4 đã xả xong, có điều kiện dừng an toàn, có Stop/E-Stop/lỗi, hoặc có lệnh hủy rõ ràng.
- Không giữ lệnh bằng cách dựa vào HMI.
- CmdSeq/AckSeq phải chống thực thi lặp cùng một lệnh.
- Viết test chứng minh pulse một scan vẫn làm bơm chạy liên tục đến điều kiện hoàn thành.

Vị trí tham khảo:

- `prepare_tia_import_sets.py`, Network `Handshake Server - Transfer command pulse`.
- `generate_mixing_project.py`, Network điều khiển bơm chuyển Nhánh 2.

### P0. PID bị ghi CV về 0 trong bước thanh trùng

PID vẫn Enable trong State 31 nhưng mạng cleanup lại reset CV dựa trên Step PID đã bị xóa:

- `AI_CV3206_Hoi_Bon2`
- `AI_CV3216_Hoi_Bon4`

Yêu cầu:

- CV chỉ bị đưa về `0.0` khi PID thực sự Disable, Stop, E-Stop hoặc lỗi yêu cầu dừng.
- Trong toàn bộ State 31, PID phải tiếp tục giữ nhiệt và CV không bị OB1 ghi đè về 0.
- PID Bồn 2 giữ SP 75°C theo đề.
- PID mô phỏng Bồn 4 dùng SP 95°C theo đề và theo generator hiện tại.
- Test ít nhất ba scan liên tiếp trong State 31 và chứng minh CV không bị cleanup ghi đè.

### P0. Cụm bồn chứa chưa có phân xử hai nhánh

Hiện tại khi cả hai nhánh hoàn thành, hai bơm có thể cùng chạy vào Bồn chứa 01. Một nhánh cũng có thể khởi động bơm khi cụm bồn chứa đang giải nhiệt, chuyển bồn hoặc lọc.

Yêu cầu:

- Chỉ một nhánh được quyền chuyển dịch tại một thời điểm.
- Tạo trạng thái/chủ sở hữu mẻ rõ ràng, ví dụ `AI_BonChua_Nhan_Tu_Nhanh` hoặc hai cờ owner loại trừ nhau.
- Chỉ cấp quyền khi cụm bồn chứa đang rảnh và sẵn sàng nhận.
- Nếu hai nhánh hoàn thành cùng lúc, chọn một quy tắc ưu tiên xác định và giữ nhánh còn lại chờ; không làm mất cờ hoàn thành.
- Bơm Nhánh 1/Nhánh 2 phải được gate bởi bước nhận dịch và owner tương ứng.
- Không cho phép bắt đầu mẻ mới làm ghi đè sản phẩm chưa chuyển xong.
- Có test cho: chỉ Nhánh 1, chỉ Nhánh 2, cả hai cùng hoàn thành, nhánh đến khi bồn chứa đang bận.

### P0. Dừng xả bình thường và bảo vệ dry-run đang xung đột

Dry-run hiện có thể latch đúng lúc mức bồn xuống thấp trong quá trình xả bình thường.

Yêu cầu:

- Có điều kiện hoàn thành xả dựa trên mức thấp/cạn hoặc điều kiện quá trình hợp lý.
- Dừng bơm và đóng van theo đường hoàn thành bình thường trước khi đánh giá dry-run.
- Dry-run phải phát hiện bơm chạy khi không có dịch bất thường, không báo lỗi chỉ vì quá trình vừa xả hết.
- Dùng timer/debounce nếu cần; không dùng HMI làm điều kiện bắt buộc để kết thúc xả.
- Stop/E-Stop/lỗi phải dừng bơm và đóng van ngay.
- Có test cho xả hết bình thường không lỗi và chạy bơm khi bồn đã cạn thì có lỗi.

### P1. Cách gọi instance Modbus không an toàn

Hiện tại:

- Hai lệnh MB_CLIENT Write/Read dùng chung `MB_CLIENT_DB` và đều được gọi trong một scan.
- Bốn lệnh MB_MASTER cho biến tần dùng chung `MB_MASTER_DB` và đều được gọi trong một scan.

Yêu cầu:

- Mỗi instance asynchronous không được bị gọi nhiều lần trong cùng vòng quét với bộ tham số khác nhau.
- Chọn một kiến trúc Siemens hợp lệ:
  - Một call duy nhất với scheduler/state machine chọn tham số; hoặc
  - Các instance DB độc lập và connection/transaction được cấu hình không xung đột.
- Không tạo nhiều yêu cầu mới khi BUSY.
- DONE/ERROR phải kết thúc giao dịch và chuyển bước hợp lệ.
- Giữ MB_CLIENT/MB_SERVER Version 3.1.
- Đối chiếu cấu trúc XML đã được TIA export trong `examples/TIA_V18_ModbusTCP_ManualExport`.
- Thêm kiểm tra tĩnh hoặc test để ngăn một instance bị gọi nhiều lần trong cùng scan.

### P1. Heartbeat chưa đúng một nhịp mỗi giây

Hiện tại heartbeat cộng liên tục trong mọi scan mà `AI_Clock_1Hz` đang ở mức TRUE.

Yêu cầu:

- Bắt cạnh lên `AI_Clock_1Hz`, chỉ tăng heartbeat một lần mỗi chu kỳ.
- Có timeout theo dõi heartbeat nhận từ PLC đối tác.
- Lỗi thực tế của MB_CLIENT/MB_SERVER và timeout heartbeat phải đưa vào lỗi truyền thông.
- Tín hiệu giả lập mất kết nối vẫn được giữ để test nhưng không phải nguồn lỗi duy nhất.

### P1. Lỗi PID và Modbus chưa được đưa vào lỗi tổng

Yêu cầu:

- Lỗi PID Bồn 2/Bồn 4, MB_CLIENT, MB_SERVER và MB_MASTER liên quan phải được tổng hợp vào lỗi phù hợp.
- Lỗi nghiêm trọng phải khóa hoặc dừng đúng phần quá trình liên quan.
- Reset chỉ xóa lỗi khi nguyên nhân cho phép reset; không tạo reset liên tục che lỗi đang tồn tại.

### P1. Dosing Bồn 2 và Bồn 3 đang so sánh lưu lượng tức thời với số lít

Hiện tại một số bước so sánh `FT..._Eff` trực tiếp với setpoint thể tích lít.

Yêu cầu:

- Xác định rõ tag nào là lưu lượng tức thời và tag nào là tổng lượng.
- Bồn 1–4 phải dùng cùng một mô hình đại lượng hợp lý.
- Nếu chỉ có flow rate, tạo totalizer LAD bằng chu kỳ thời gian xác định hoặc dùng tag FQ/tổng lượng phù hợp.
- Reset tổng lượng khi bắt đầu mẻ mới.
- Không so sánh đơn vị L/h hoặc L/min trực tiếp với setpoint L.
- Cập nhật IO map/mô tả tag nếu tạo tag mới.

### P1. Bộ test Python không khớp Ladder thật

Các sai lệch đã biết:

- Test đang dùng SP Bồn 4 là 75°C thay vì 95°C.
- Có các tag không khớp generator như `AI_FQ3210_Bon3_Eff`, `AI_FT3215_Bon4_Eff`, `AI_LT3217_Bon4_Eff`.
- Test tự giữ lệnh bơm Nhánh 2 nên không phát hiện lỗi pulse.
- Test mô hình hóa một số chuyển bước không tồn tại trong Ladder.

Yêu cầu:

- Đồng bộ tên tag, setpoint, state và chuyển tiếp với Ladder được sinh.
- Không được tạo một simulator “đẹp” nhưng khác chương trình PLC.
- Bổ sung test cho storage arbitration, pulse command, PID State 31, dry-run, heartbeat, lỗi truyền thông và Modbus scheduler.
- Nếu vẫn dùng mô hình Python thủ công, thêm kiểm tra cấu trúc XML để chứng minh Ladder sinh ra chứa đúng network/coil/contact mong đợi.

### P2. Gia cố thư viện và QA

Yêu cầu:

- `TIALadderBuilder` phải fail fast khi gặp `ctype` không hỗ trợ; không được âm thầm bỏ qua operation.
- Validator phải phát hiện:
  - Operation không được hỗ trợ.
  - Coil thường nối thẳng Powerrail ngoài các trường hợp được whitelist rõ ràng.
  - Một instance FB bất đồng bộ bị gọi nhiều lần trong cùng OB/FC scan với tham số khác nhau.
  - GET/PUT trong output/import set.
- Không dùng phần hỗ trợ GET/PUT của thư viện trong dự án này.
- Không mở rộng phạm vi thành refactor toàn bộ thư viện nếu không cần.

## 5. Tiêu chí hành vi sau khi sửa

1. PLC1 chạy Bồn 1 → Bồn 2 → PID 75°C → thanh trùng → chờ quyền chuyển.
2. PLC2 chạy Bồn 3 → Bồn 4 → PID mô phỏng 95°C → thanh trùng → chờ quyền chuyển.
3. PID tiếp tục điều khiển van hơi trong suốt thời gian thanh trùng.
4. Một pulse chuyển Nhánh 2 đủ để PLC2 giữ bơm đến khi Bồn 4 xả xong.
5. Cụm bồn chứa chỉ nhận một nhánh tại một thời điểm.
6. Nhánh còn lại chờ và được phục vụ sau khi cụm bồn chứa trở về trạng thái sẵn sàng.
7. Xả hết bình thường không gây dry-run.
8. Chạy bơm khi nguồn đã cạn bất thường phải gây dry-run.
9. Không có instance MB_CLIENT/MB_MASTER bị gọi nhiều lần với bộ tham số khác nhau trong cùng scan.
10. Heartbeat tăng đúng một lần trên mỗi cạnh 1 Hz và mất heartbeat gây lỗi truyền thông.
11. Mọi lỗi PID/Modbus quan trọng đi vào lỗi tổng và interlock phù hợp.
12. Không cần HMI để hoàn thành chuyển dịch/xả trong test PLC.

## 6. Quy trình kiểm tra bắt buộc

Sau khi sửa, chạy từ thư mục gốc:

```powershell
python projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py
python projects\Mixing_Nuoc_Tuong_Maggi_2026\prepare_tia_import_sets.py
python scratch\validate_tia_imports.py
python scratch\verify_clean.py
python scratch\test_plc_logic.py
python harness\run_acceptance.py
```

Ngoài các lệnh trên:

- Parse tất cả XML mới sinh.
- Kiểm tra không có `.scl`, GET hoặc PUT.
- Kiểm tra PID_Compact Version 1.2 và mạng mode 3/0.
- Kiểm tra MB_CLIENT/MB_SERVER Version 3.1.
- So sánh danh sách Network chính giữa import set mới và post-import export cũ để phát hiện mất logic ngoài ý muốn.
- Nếu TIA Portal đang mở và công cụ Openness dùng được:
  - Backup/export trước khi import.
  - Import cả PLC1 và PLC2.
  - Compile cả hai PLC, yêu cầu 0 Errors.
  - Export ngược lại và chạy `scratch\verify_post_import_export.py`.
- Nếu không thể compile TIA trong phiên làm việc, phải nói rõ là chưa xác nhận compile TIA; không được giả vờ đã compile.

## 7. Yêu cầu báo cáo khi hoàn thành

Báo cáo ngắn gọn nhưng phải có:

1. Danh sách file đã sửa.
2. Mỗi lỗi P0/P1/P2 đã sửa bằng cơ chế nào.
3. Test mới đã thêm và tình huống được kiểm tra.
4. Kết quả từng lệnh kiểm tra.
5. Tình trạng compile TIA thực tế.
6. Các rủi ro còn lại hoặc phần chưa thể xác nhận.
7. `git diff --stat` và tóm tắt diff; không commit trừ khi được yêu cầu.

Không tự đánh giá “100% hoàn thành”. Sau khi bạn sửa xong, một AI khác sẽ review độc lập diff, XML sinh ra, test và liên động vận hành.
