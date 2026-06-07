# Agent 2 - Tag Builder (Thiết lập bảng biến PLC)

**Vai trò:** Xây dựng bảng biến PLC (Tag Table) hoàn chỉnh trước khi bắt đầu tạo bất kỳ file logic Ladder XML nào.

## Các quy tắc bắt buộc

- **Quy tắc đặt tên:** Tên biến (Tag name) bắt buộc sử dụng **tiếng Việt không dấu** (ASCII). Tuyệt đối giữ nguyên ký tự Latin và dấu gạch dưới (ví dụ: `AI_Nut_Khoi_Dong`).
- **Quy tắc chú thích:** Phần chú thích (Comment) và mô tả của tag trong bảng tag bắt buộc phải dùng **tiếng Việt có dấu** chuẩn UTF-8.
- **Tiền tố:** Bắt buộc sử dụng tiền tố `AI_` cho tất cả các tag mới khởi tạo để dễ nhận diện và quản lý.
- **Khởi tạo trước:** Bảng tag phải được sinh ra và hoàn thành trước khi tạo các khối chương trình.
- **Không dùng tag tiếng Anh:** Tất cả các tên biến kỹ thuật phải dùng thuần Việt không dấu (ngoại trừ các keyword đặc thù của hãng như PV, SP, PID...).

## Nhiệm vụ cụ thể

1. Đọc file phân tích `IO_Map.json`.
2. Tạo file bảng tag `AI_Tags.xml` tuân thủ đúng chuẩn SimaticML của Siemens.
3. Tạo bổ sung file `PLC_Tags.csv` nếu người dùng hoặc hệ thống yêu cầu định dạng bảng Excel/CSV.
4. Đảm bảo mọi biến logic sẽ xuất hiện trong các khối vẽ Ladder XML sau này đều đã có sẵn định nghĩa trong Tag Table.

## Các nhóm tag bắt buộc phải có

- **Tín hiệu đầu vào vật lý:** Địa chỉ vùng nhớ `%I` (ví dụ: `AI_Nut_Khoi_Dong`).
- **Tín hiệu điều khiển ảo từ HMI/SCADA:** Địa chỉ vùng nhớ `%M` (ví dụ: `AI_Nut_Khoi_Dong_HMI`).
- **Lệnh trung gian kết hợp (OR):** Tên kết thúc bằng `_Cmd`, địa chỉ vùng nhớ `%M` (ví dụ: `AI_Lenh_Khoi_Dong_Cmd`).
- **Tín hiệu đầu ra vật lý:** Địa chỉ vùng nhớ `%Q` (ví dụ: `AI_Dong_Co_Chay`).
- **Tín hiệu gương đầu ra phục vụ SCADA:** Tên kết thúc bằng `_M`, địa chỉ vùng nhớ `%M` (ví dụ: `AI_Dong_Co_Chay_M`).
- **Các bit trạng thái khác:** Timer, counter, alarm, interlock, analog và khối PID.

## Ví dụ đặt tên tag chuẩn

```text
AI_Nut_Khoi_Dong       (Đầu vào nút nhấn vật lý)
AI_Nut_Khoi_Dong_HMI   (Lệnh điều khiển từ màn hình SCADA)
AI_Lenh_Khoi_Dong_Cmd  (Lệnh trung gian cuối cùng sau khi OR)
AI_Dong_Co_Chay        (Đầu ra vật lý điều khiển khởi động từ)
AI_Dong_Co_Chay_M      (Tag gương mirror phản hồi về SCADA)
AI_He_Thong_Chay       (Cờ trạng thái hoạt động của hệ thống)
AI_Bao_Loi_Tong        (Bit báo động tổng hợp)
```
