# HƯỚNG DẪN IMPORT VÀ VẬN HÀNH (MANUAL_STEPS.md Template)

## Mục tiêu

Tài liệu này hướng dẫn người vận hành thực hiện nhập (Import) các file XML vào TIA Portal V18 và kiểm tra chất lượng chương trình logic Ladder.

## Bước 1 - Mở TIA Portal và Dự án

1. Mở phần mềm **Siemens TIA Portal V18**.
2. Mở dự án cần làm việc.
3. Đảm bảo cấu hình phần cứng PLC (CPU) đã được tạo sẵn trong cấu trúc dự án.

## Bước 2 - Thẩm định QA tự động trước khi nhập

Trước khi bắt đầu quy trình import, hãy chạy bộ công cụ thẩm định tự động để chắc chắn không có lỗi logic hoặc vi phạm chính sách Ladder-only:
```powershell
python Ladder/Agent_QA_Validator.py D:\AI_Agent_PLC_LADDER_ONLY\projects\<ten_du_an>\output
```
Đảm bảo kết quả thẩm định báo trạng thái **ĐẠT (PASS)**.

## Bước 3 - Nhập bảng Tag và Block Logic

Sử dụng bộ công cụ Importer Openness tự động để đẩy tài liệu vào dự án:
```powershell
D:\AI_Agent_PLC_LADDER_ONLY\Ladder\Agent_TIA_Importer_Generic.exe D:\AI_Agent_PLC_LADDER_ONLY\projects\<ten_du_an>\output
```

*Lưu ý thứ tự tự động của công cụ:*
1. Nạp bảng biến vật lý (Tag Table) trước để tạo danh nghĩa các biến.
2. Nạp các danh sách HMI (Text/Graphic Lists XML) để tạo tài nguyên hiển thị cho HMI/SCADA.
3. Nạp các khối chương trình PLC (Block XML) để tự động biên dịch logic Ladder.
4. Tiến hành biên dịch lại (Compile) toàn bộ Hardware và Software trên TIA Portal để kiểm tra không có lỗi cú pháp.

## Bước 4 - Kiểm tra trực quan bảng Tag

- Mở mục **PLC Tags** -> **Show all tags**.
- Kiểm tra các tag có tiền tố `AI_`.
- Xác thực địa chỉ của tín hiệu vật lý `%I`, `%Q` và đảm bảo các tín hiệu ảo song song `%M` được phân cấp địa chỉ hợp lệ.

## Bước 5 - Xác thực Logic Ladder

- Mở khối chương trình chính **OB1**.
- Mở các khối hàm chức năng nâng cao (FB/FC).
- Đảm bảo toàn bộ tiêu đề mạng (Network Title) và chú thích (Comment) hiển thị Tiếng Việt có dấu chính xác, rõ ràng.
- Đảm bảo không tồn tại bất kỳ cảnh báo hoặc lỗi biên dịch đỏ nào.

## Bước 6 - Liên kết giao diện WinCC/SCADA
 
Sử dụng tài liệu liên kết `Tag_Binding.md` để cấu hình giao diện HMI:
- Mở rộng mục HMI trong cấu trúc dự án TIA Portal -> **Text and graphic lists** -> kiểm tra các danh sách Text List (ví dụ: `TL_Chuan_Doan_AnToan`) đã được tạo và chứa đầy đủ các hàng dịch tiếng Việt có dấu UTF-8 chuẩn xác.
- Liên kết nút nhấn ảo trên màn hình với các tag `_HMI` (%M).
- Liên kết trạng thái đèn báo, cờ hoạt động với các tag mirror `_M` (%M) hoặc tag Cmd.
- Áp dụng WinCC Text List cho các tag chẩn đoán an toàn (ví dụ: `HMI_AnToan_Status` %MW hoặc các tag lưu trữ mã cảnh báo) bằng cách đặt thuộc tính của đối tượng **Symbolic IO Field** sử dụng Text List vừa nhập.
- Áp dụng WinCC Graphic List cho đối tượng **Graphic I/O Field** để hiển thị trạng thái bằng hình ảnh động nếu có.

## Bước 7 - Chạy thử nghiệm trên PLCSIM

- Khởi động bộ giả lập **S7-PLCSIM**.
- Đổ chương trình xuống PLC giả lập.
- Sử dụng Watch Table để mô phỏng tác động các tiếp điểm vật lý `%I` và kiểm soát tín hiệu điều khiển HMI `%M`.
- Xác nhận các liên động an toàn và dừng khẩn cấp (E-Stop) hoạt động chính xác theo đúng kịch bản chu kỳ quét.
