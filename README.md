# AI Agent PLC SCL-First Workspace (Legacy Ladder Reference)

> [!NOTE]
> **THAY ĐỔI ĐỊNH HƯỚNG DỰ ÁN (SCL-FIRST):**
> Kể từ mốc `lad-cleaned-before-scl-20260623`, repository này đã chuyển dịch sang chiến lược phát triển **SCL-first** (logic PLC mới ưu tiên viết bằng ngôn ngữ SCL source/import được vào TIA Portal).
> Các quy tắc Ladder-only cũ bên dưới được giữ lại làm **Legacy Reference (Tham khảo lịch sử)** phục vụ đối chiếu và rollback.
> Quy tắc đặt tên tag mới: **KHÔNG dùng tiền tố `AI_`** (tiền tố `AI_` chỉ là tên lịch sử trước migration).

Workspace này là framework chuyên biệt dùng để thiết kế và sinh tự động dự án PLC Siemens TIA Portal V18.

## Mục tiêu chính của Framework (Chiến lược mới)

- Tự động hóa việc sinh cấu trúc dự án PLC bằng ngôn ngữ SCL sạch, cấu trúc hóa, dễ bảo trì.
- Các khối hàm tổ chức OB, FB, FC mới ưu tiên viết bằng ngôn ngữ SCL.
- Bản Ladder đồ họa (LAD) cũ được lưu giữ làm legacy để đối chiếu hoặc rollback khi cần.
- Vẫn duy trì các bộ công cụ nạp TIA Portal Openness API, HMI XML patcher và validators để hỗ trợ triển khai.
- Tuyệt đối cấm sử dụng lệnh truyền thông S7 GET/PUT, sử dụng Modbus TCP/RTU làm giải pháp truyền thông chính thức.
- Sử dụng Siemens PID_Compact Version 1.2 chuẩn cho các bồn nhiệt độ, không tự viết PID giả lập.
- Quy tắc đặt tên biến mới: sử dụng ký tự ASCII tiếng Việt không dấu, không dùng tiền tố `AI_`. Tiền tố `AI_` chỉ là lịch sử trước migration.
- HMI Styling & Formatting giữ nguyên các quy chuẩn hiển thị số thực, căn giữa và khoảng cách nhãn đơn vị.

## Cấu trúc thư mục chi tiết

```text
D:\AI_Agent_PLC_LADDER_ONLY
|-- AI_AGENT_START_HERE.md          # Điểm xuất phát bắt buộc của AI Agent
|-- README.md                       # Tài liệu tổng quan dự án (File này)
|-- Lessons_Learned_RealWorld_PLC.md # Đúc kết kinh nghiệm thiết kế PLC thực tế
|-- Ladder/
|   |-- Agent_LAD_Library.py        # Thư viện Python sinh mã Ladder XML & HMI Lists (Legacy Reference)
|   |-- Agent_QA_Validator.py       # Bộ thẩm định chất lượng tự động mới (QA Validator - Legacy Reference)
|   |-- Agent_TIA_LAD_Only_Guide.md # Hướng dẫn lập trình 100% Ladder XML (Legacy Reference)
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
|   |-- Master_Ladder_Only_5_Agent_Prompt.md # Prompt tổng hợp cho chuỗi 5 Agent cũ (Legacy Reference)
|   |-- Agent1_Analyst.md           # Hướng dẫn tác vụ của Agent 1 cũ (Legacy Reference)
|   |-- Agent2_Tag_Builder.md       # Hướng dẫn tác vụ của Agent 2 cũ (Legacy Reference)
|   |-- Agent3_Ladder_Coder.md      # Hướng dẫn tác vụ của Agent 3 cũ (Legacy Reference)
|   |-- Agent4_QA.md                # Hướng dẫn tác vụ của Agent 4 cũ (Legacy Reference)
|   |-- Agent5_HMI_Executor.md      # Hướng dẫn tác vụ của Agent 5 cũ (Legacy Reference)
|   |-- scl/                        # Thư mục Prompts cho SCL-First mới
|   |   |-- Master_SCL_5_Agent_Prompt.md     # Prompt tổng hợp cho chuỗi 5 Agent SCL
|   |   |-- Agent1_SCL_Analyst.md            # Prompt cho Agent 1 (Analyst)
|   |   |-- Agent2_SCL_Tag_DB_Builder.md    # Prompt cho Agent 2 (Tag & DB Builder)
|   |   |-- Agent3_SCL_Coder.md             # Prompt cho Agent 3 (SCL Coder)
|   |   |-- Agent4_SCL_QA_Reviewer.md        # Prompt cho Agent 4 (SCL QA Reviewer)
|   |   |-- Agent5_HMI_TIA_Executor.md      # Prompt cho Agent 5 (HMI & TIA Executor)
|-- templates/
|   |-- AI_Tags_Template.md         # Mẫu khai báo bảng biến XML (Legacy Reference)
|   |-- Ladder_Output_Checklist.md  # Danh sách kiểm tra chất lượng bàn giao (Legacy Reference)
|   |-- Manual_Steps_Template.md    # Mẫu tài liệu hướng dẫn vận hành hệ thống
|-- examples/                       # Các ví dụ tham khảo
|-- projects/                       # Nơi lưu trữ các dự án sinh thực tế
```

## Quy tắc sử dụng ngôn ngữ Tiếng Việt thống nhất

Để đảm bảo tính tương thích phần mềm tối đa và hiển thị rõ ràng, chuyên nghiệp:
- **Tên biến (Tag Name), tên DB, tên HMI Tag:** Bắt buộc viết bằng **tiếng Việt không dấu** (ASCII, ký tự chữ, số và dấu gạch dưới, KHÔNG sử dụng tiền tố `AI_` cho các biến mới, ví dụ: `Nut_Khoi_Dong`). Tiền tố `AI_` chỉ là lịch sử trước migration và không được dùng lại. Điều này ngăn ngừa lỗi font/bảng mã hệ thống khi import tự động qua Openness API.
- **Tiêu đề mạng (Network Title), Chú thích (Comment) và Mô tả (Description) trong code/tài liệu:** Bắt buộc sử dụng **tiếng Việt có dấu** chuẩn UTF-8 để đảm bảo thông tin an toàn công nghệ hiển thị trực quan và chính xác trên WinCC SCADA/HMI.

### Ví dụ đặt tên chuẩn (Không chứa tiền tố AI_):
- Biến vật lý: `Nut_Khoi_Dong`
- Biến ảo HMI: `Nut_Khoi_Dong_HMI`
- Chú thích: `Nút khởi động hệ thống an toàn`
- Tiêu đề mạng: `Khởi động chu kỳ chưng cất tự động`

## Quy trình làm việc cho mỗi dự án mới

1. Đọc kỹ tài liệu chỉ dẫn [AI_AGENT_START_HERE.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/AI_AGENT_START_HERE.md) và tuân thủ thiết kế an toàn trong [Lessons_Learned_RealWorld_PLC.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/Lessons_Learned_RealWorld_PLC.md).
2. Phân tích đề bài và sinh sơ đồ ngõ vào ra đặt trong `IO_Map.json`.
3. Sinh bảng tag PLC đầy đủ và lưu tại `PLC_Tags.xml` hoặc SCL tag table (không chứa tiền tố `AI_`).
4. Lập trình logic OB/FB/FC trực tiếp dưới dạng mã SCL (file `.scl`) và định nghĩa các khối dữ liệu DB/UDT cho dự án SCL mới. (Thư viện Python `Agent_LAD_Library.py` chỉ dùng để tham khảo vẽ Ladder XML cũ).
5. Đảm bảo biên dịch không lỗi (0 Errors) khi nạp qua Openness. Bộ validator kiểm duyệt Ladder-only và `Agent_QA_Validator.py` chỉ áp dụng cho phiên bản Ladder cũ (legacy reference), không dùng cho SCL mới.
6. Hoàn thiện tài liệu WinCC và hướng dẫn import thực tế bàn giao tại thư mục `projects/<ten_du_an>/output/`.

## Bộ công cụ hỗ trợ phát triển PLC

- `Ladder/Agent_LAD_Library.py`: Thư viện lõi Python để lập trình vẽ khối Ladder XML và thiết lập HMI lists.
- `Ladder/Agent_QA_Validator.py`: Script tự động thẩm định và đánh giá chất lượng sản phẩm đầu ra.
- `Ladder/Agent_TIA_Importer_Generic.exe`: Bộ nạp tự động tích hợp trực tiếp bảng tag, blocks và các Text/Graphic Lists của HMI vào dự án TIA Portal.
- `Ladder/Agent_TIA_HMI_Exporter.exe`: Bộ xuất tự động các Text List và Graphic List hiện hành từ dự án HMI của TIA Portal ra file XML.
- `Ladder/Agent_TIA_Tag_Lister.exe`: Bộ liệt kê và kết xuất nhanh các tag hiện hữu từ dự án TIA Portal.
