# AI Agent PLC Ladder Only Workspace

Workspace này là framework chuyên biệt dùng để thiết kế và sinh tự động dự án PLC Siemens TIA Portal V18 bằng **100% đồ họa Ladder XML**.

## Mục tiêu chính của Framework

- Tự động hóa việc sinh cấu trúc dự án PLC hoàn chỉnh từ mô tả công nghệ thực tế bằng ngôn ngữ tự nhiên.
- Vận hành chuỗi liên kết phối hợp nhịp nhàng giữa 5 AI Agent như quy trình trước đây.
- Xuất bản bảng tag biểu diễn biến, khối tổ chức OB1, và các khối hàm chức năng FB/FC hoàn toàn bằng định dạng đồ họa Ladder XML.
- Tuyệt đối tuân thủ chính sách **Ladder-only**: không sinh bất kỳ dạng logic SCL nào làm chương trình chạy trên PLC CPU.

## Cấu trúc thư mục chi tiết

```text
D:\AI_Agent_PLC_LADDER_ONLY
|-- AI_AGENT_START_HERE.md          # Điểm xuất phát bắt buộc của AI Agent
|-- README.md                       # Tài liệu tổng quan dự án (File này)
|-- Lessons_Learned_RealWorld_PLC.md # Đúc kết kinh nghiệm thiết kế PLC thực tế
|-- Ladder/
|   |-- Agent_LAD_Library.py        # Thư viện Python sinh mã Ladder XML & HMI Lists
|   |-- Agent_QA_Validator.py       # Bộ thẩm định chất lượng tự động mới (QA Validator)
|   |-- Agent_TIA_LAD_Only_Guide.md # Hướng dẫn lập trình 100% Ladder XML
|   |-- Agent_TIA_Importer_Generic.exe # Công cụ tự động nạp XML và HMI lists vào TIA Portal
|   |-- Agent_TIA_Importer_Generic.cs  # Mã nguồn C# của bộ nạp tự động
|   |-- Agent_TIA_HMI_Exporter.exe  # Công cụ xuất Text/Graphic List của HMI ra XML
|   |-- Agent_TIA_HMI_Exporter.cs   # Mã nguồn C# của bộ xuất HMI
|   |-- Agent_TIA_Tag_Lister.exe    # Công cụ liệt kê tag từ dự án TIA Portal
|   |-- Agent_TIA_Tag_Lister.cs     # Mã nguồn C# của bộ liệt kê tag
|   |-- Siemens.Engineering.dll     # Thư viện Siemens Openness API chính
|   |-- Siemens.Engineering.Hmi.dll # Thư viện Siemens Openness HMI API
|   |-- Siemens_Block_Dictionary.json # Từ điển tra cứu cấu trúc block Siemens
|-- prompts/
|   |-- Master_Ladder_Only_5_Agent_Prompt.md # Prompt tổng hợp cho chuỗi 5 Agent
|   |-- Agent1_Analyst.md           # Hướng dẫn tác vụ của Agent 1
|   |-- Agent2_Tag_Builder.md       # Hướng dẫn tác vụ của Agent 2
|   |-- Agent3_Ladder_Coder.md      # Hướng dẫn tác vụ của Agent 3
|   |-- Agent4_QA.md                # Hướng dẫn tác vụ của Agent 4
|   |-- Agent5_HMI_Executor.md      # Hướng dẫn tác vụ của Agent 5
|-- templates/
|   |-- AI_Tags_Template.md         # Mẫu khai báo bảng biến XML
|   |-- Ladder_Output_Checklist.md  # Danh sách kiểm tra chất lượng bàn giao
|   |-- Manual_Steps_Template.md    # Mẫu tài liệu hướng dẫn vận hành hệ thống
|-- examples/                       # Các ví dụ tham khảo
|-- projects/                       # Nơi lưu trữ các dự án sinh thực tế
```

## Quy tắc sử dụng ngôn ngữ Tiếng Việt thống nhất

Để đảm bảo tính tương thích phần mềm tối đa và hiển thị rõ ràng, chuyên nghiệp:
- **Tên biến (Tag Name), tên DB, tên HMI Tag:** Bắt buộc viết bằng **tiếng Việt không dấu** (ASCII, ký tự chữ, số và dấu gạch dưới, bắt đầu bằng `AI_`, ví dụ: `AI_Nut_Khoi_Dong`). Điều này ngăn ngừa lỗi font/bảng mã hệ thống khi import tự động qua Openness API.
- **Tiêu đề mạng (Network Title), Chú thích (Comment) và Mô tả (Description) trong code/tài liệu:** Bắt buộc sử dụng **tiếng Việt có dấu** chuẩn UTF-8 để đảm bảo thông tin an toàn công nghệ hiển thị trực quan và chính xác trên WinCC SCADA/HMI.

### Ví dụ đặt tên chuẩn:
- Biến vật lý: `AI_Nut_Khoi_Dong`
- Biến ảo HMI: `AI_Nut_Khoi_Dong_HMI`
- Chú thích: `Nút khởi động hệ thống an toàn`
- Tiêu đề mạng: `Khởi động chu kỳ chưng cất tự động`

## Quy trình làm việc cho mỗi dự án mới

1. Đọc kỹ tài liệu chỉ dẫn [AI_AGENT_START_HERE.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/AI_AGENT_START_HERE.md) và tuân thủ thiết kế an toàn trong [Lessons_Learned_RealWorld_PLC.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/Lessons_Learned_RealWorld_PLC.md).
2. Phân tích đề bài và sinh sơ đồ ngõ vào ra đặt trong `IO_Map.json`.
3. Sinh bảng tag PLC đầy đủ và lưu tại `AI_Tags.xml`.
4. Viết mã Python gọi thư viện `Agent_LAD_Library.py` để kết xuất các khối logic OB/FB/FC và HMI Text/Graphic Lists dưới dạng XML.
5. Chạy bộ thẩm định tự động `Agent_QA_Validator.py` để chắc chắn chương trình không vi phạm chính sách Ladder-only và đạt 100% tiêu chí an toàn ngõ vào ra.
6. Hoàn thiện tài liệu WinCC và hướng dẫn import thực tế bàn giao tại thư mục `projects/<ten_du_an>/output/`.

## Bộ công cụ hỗ trợ phát triển PLC

- `Ladder/Agent_LAD_Library.py`: Thư viện lõi Python để lập trình vẽ khối Ladder XML và thiết lập HMI lists.
- `Ladder/Agent_QA_Validator.py`: Script tự động thẩm định và đánh giá chất lượng sản phẩm đầu ra.
- `Ladder/Agent_TIA_Importer_Generic.exe`: Bộ nạp tự động tích hợp trực tiếp bảng tag, blocks và các Text/Graphic Lists của HMI vào dự án TIA Portal.
- `Ladder/Agent_TIA_HMI_Exporter.exe`: Bộ xuất tự động các Text List và Graphic List hiện hành từ dự án HMI của TIA Portal ra file XML.
- `Ladder/Agent_TIA_Tag_Lister.exe`: Bộ liệt kê và kết xuất nhanh các tag hiện hữu từ dự án TIA Portal.
