# Danh sách kiểm tra chất lượng đầu ra (Ladder Output Checklist)

Sử dụng danh sách kiểm tra này trước khi bàn giao và kết luận dự án.

- [ ] Output được đặt chính xác trong thư mục `projects/<ten_du_an>/output/`.
- [ ] Có đầy đủ file `IO_Map.json`.
- [ ] Có đầy đủ file bảng tag `AI_Tags.xml` hoặc `PLC_Tags.csv`.
- [ ] Có đầy đủ file khối chính `OB1_Main.xml`.
- [ ] Có đầy đủ các file khối Logic Ladder chính (ví dụ: `FB_Main_Ladder.xml`).
- [ ] Có đầy đủ các file XML danh sách HMI (Text List / Graphic List) nếu dự án có yêu cầu chẩn đoán trạng thái/cảnh báo lỗi (ví dụ: `Hmi.TextList.TL_Chuan_Doan_AnToan.xml`).
- [ ] Tên các danh sách HMI (HMI List Name) và các liên kết đảm bảo viết không dấu (ASCII, ví dụ: `TL_Chuan_Doan_AnToan`).
- [ ] Các chuỗi ký tự hiển thị (Text translations) trong Text List bắt buộc viết bằng tiếng Việt có dấu chuẩn UTF-8 để vận hành trực quan.
- [ ] Tuyệt đối KHÔNG có bất kỳ file logic `.scl` nào dùng làm chương trình PLC.
- [ ] Chạy bộ thẩm định QA tự động và đảm bảo đạt 100% (Trạng thái PASS):
  ```powershell
  python Ladder/Agent_QA_Validator.py projects/<ten_du_an>/output
  ```
- [ ] Mọi UId và ID trong từng file XML là duy nhất, không bị trùng lặp (kể cả trong các file XML HMI).
- [ ] Tất cả các biến logic sử dụng trong block XML đều đã được khai báo đầy đủ trong Tag Table.
- [ ] Mỗi tín hiệu vật lý đầu vào `%I` đều có một tag ảo `%M` song song kết thúc bằng `_HMI`.
- [ ] Mỗi tín hiệu vật lý đầu ra `%Q` đều có một tag gương `%M` mirror kết thúc bằng `_M`.
- [ ] Lệnh Stop/E-Stop được ưu tiên cao nhất, reset các đầu ra quan trọng.
- [ ] Các đầu ra xuất hiện ở nhiều Network bắt buộc sử dụng SetCoil/ResetCoil thay vì Coil thường.
- [ ] Tiêu đề Network (Network Title) bắt buộc sử dụng tiếng Việt có dấu chuẩn UTF-8.
- [ ] Chú thích (Comment) và mô tả (Description) trong code/tài liệu bắt buộc sử dụng tiếng Việt có dấu chuẩn UTF-8.
- [ ] Đã tạo đầy đủ tài liệu `Tag_Binding.md` hướng dẫn WinCC.
- [ ] Đã tạo đầy đủ hướng dẫn vận hành và import `MANUAL_STEPS.md` (bao gồm các bước import HMI Lists).
- [ ] Đã tạo báo cáo thẩm định tự động `QA_Report.md` dạng Tiếng Việt có dấu nằm trong thư mục output.
