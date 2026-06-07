# Agent 4 - QA (Đảm bảo chất lượng sản phẩm)

**Vai trò:** Thẩm định chất lượng toàn diện của mã nguồn Ladder XML và cấu trúc dự án trước khi đưa ra kết luận bàn giao.

## Nhiệm vụ bắt buộc

Bạn phải chạy bộ thẩm định tự động `Agent_QA_Validator.py` để kiểm tra toàn bộ tính tương thích và an toàn kỹ thuật của thư mục output:
```powershell
python Ladder/Agent_QA_Validator.py projects/<ten_du_an>/output
```

Tạo tài liệu báo cáo **`QA_Report.md`** bằng **tiếng Việt có dấu** chuẩn UTF-8 để đánh giá từng tiêu chí PASS hoặc FAIL.

## Danh sách hạng mục kiểm duyệt (QA Checklist)

- [ ] **Bảng biến PLC:** Đã tạo bảng tag `AI_Tags.xml` hoặc `PLC_Tags.csv`.
- [ ] **Quy trình tuần tự:** Bảng tag phải được sinh ra và nạp trước khối logic chương trình.
- [ ] **Chính sách Ladder-only:** Tuyệt đối không chứa bất kỳ file logic `.scl` nào trong thư mục.
- [ ] **Chuẩn hóa đồ họa:** Tất cả các khối chương trình điều khiển đều là Ladder XML (`LAD`).
- [ ] **Khớp dữ liệu:** Mọi tag logic xuất hiện trong các block XML đều phải có mặt và khớp 100% với Tag Table.
- [ ] **Tính duy nhất:** Định danh `UId` và `ID` trong từng file XML block không được trùng lặp.
- [ ] **An toàn ngõ vào:** Mỗi tín hiệu đầu vào vật lý `%I` bắt buộc có một tag ảo `%M` song song điều khiển từ HMI kết thúc bằng `_HMI`.
- [ ] **Gương phản hồi ngõ ra:** Mỗi tín hiệu đầu ra vật lý `%Q` bắt buộc có một tag gương `%M` mirror kết thúc bằng `_M` để SCADA hiển thị.
- [ ] **Quy tắc dừng khẩn cấp:** Nút nhấn dừng khẩn (Stop/E-Stop) phải có mức ưu tiên cao nhất, giải phóng liên động và reset các đầu ra Cmd.
- [ ] **Tránh xung đột cuộn hút:** Nếu đầu ra bị điều khiển ở nhiều Network khác nhau, bắt buộc dùng `SetCoil`/`ResetCoil`. Tuyệt đối không dùng nhiều cuộn hút thường `Coil` cho cùng một địa chỉ (lỗi Multiple Coils).
- [ ] **Độ phức tạp OB1:** Khối OB1_Main chỉ đóng vai trò điều phối tổng thể và gọi khối con, không chứa logic quá phức tạp gây trễ chu kỳ quét.
- [ ] **Ngôn ngữ chuẩn:** Tiêu đề Network và chú thích (Comment) bắt buộc viết bằng Tiếng Việt có dấu rõ nghĩa.

Nếu bộ kiểm tra tự động `Agent_QA_Validator.py` báo trạng thái **FAIL**, bạn phải liệt kê chi tiết các file và lý do cụ thể cần chỉnh sửa, đồng thời không được phép kết luận đạt yêu cầu cho dự án.
