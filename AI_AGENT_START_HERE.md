# ĐIỂM BẮT ĐẦU CHO AI AGENT (AI AGENT START HERE) - SCL FIRST (LEGACY LADDER REFERENCE)

> [!NOTE]
> **THAY ĐỔI ĐỊNH HƯỚNG DỰ ÁN (SCL-FIRST):**
> Kể từ mốc `lad-cleaned-before-scl-20260623`, repository này đã chuyển dịch sang chiến lược phát triển **SCL-first** (logic PLC mới ưu tiên viết bằng ngôn ngữ SCL source/import được vào TIA Portal).
> Bộ tài liệu hướng dẫn Ladder-only dưới đây được đánh dấu là **Legacy Reference (Tham khảo lịch sử)**, dùng để đối chiếu logic đã test hoặc phục vụ rollback.
> Quy tắc đặt tên tag mới: **KHÔNG dùng tiền tố `AI_`** (tiền tố `AI_` chỉ là tên lịch sử trước migration).

Tài liệu này là chỉ dẫn nhập môn bắt buộc đối với bất kỳ AI Agent nào được giao nhiệm vụ thực hiện dự án sinh hệ thống điều khiển PLC Siemens TIA Portal V18 trong workspace `D:\AI_Agent_PLC_LADDER_ONLY`.

---

## 1. Mục tiêu và giới hạn kỹ thuật của Workspace (Legacy LAD / New SCL Strategy)

Mục tiêu mới của workspace này là xây dựng dự án PLC Siemens TIA Portal V18 bằng ngôn ngữ **SCL (Structured Control Language)** làm chủ đạo.

### Yêu cầu bắt buộc mới (SCL-First):
- Logic PLC mới phải được phát triển trực tiếp bằng mã SCL sạch, cấu trúc hóa, dễ bảo trì và có khả năng biên dịch đạt 0 Errors.
- Toàn bộ các tag mới **không sử dụng tiền tố `AI_`**. Tiền tố `AI_` là lịch sử trước migration và không được dùng lại.
- Bộ điều khiển nhiệt độ bắt buộc sử dụng khối công nghệ **PID_Compact Version 1.2** chuẩn của Siemens. SCL trực tiếp gọi và điều phối khối này (ghi `3` vào `sRet.i_Mode` để chạy Auto và ghi `0` để dừng/Inactive), không tự viết giải thuật PID giả lập.
- Các công cụ tích hợp TIA Portal Openness API, vá XML màn hình HMI, và bind tag WinCC vẫn được giữ nguyên hoạt động để hỗ trợ triển khai dự án SCL mới.

### Yêu cầu của bản Ladder XML cũ (Legacy Reference):
- Thuật toán cũ của bản LAD đồ họa được lưu vết để làm đối chứng. Không sửa đè hoặc thay đổi code bản LAD cũ.

---

## 2. Quy tắc ngôn ngữ Tiếng Việt đồng bộ

Sự phân chia ngôn ngữ giữa **Tên biến** và **Chú thích/Tài liệu** tuân thủ nghiêm ngặt nguyên tắc:

1. **Tên biến (Tag name), tên DB, tên HMI Tag và Symbolic name:**
   Bắt buộc viết bằng **tiếng Việt không dấu** (ASCII, chỉ gồm chữ cái Latin, chữ số và dấu gạch dưới, không chứa ký tự đặc biệt, không sử dụng tiền tố `AI_` cho các tag mới, ví dụ: `Nut_Khoi_Dong`). Tiền tố `AI_` (như `AI_Nut_Khoi_Dong`) chỉ là tên lịch sử của bản cũ trước migration và không được sử dụng lại. Điều này bảo vệ hệ thống khỏi các lỗi bảng mã ký tự khi import qua Openness API trên các hệ điều hành Windows cấu hình vùng miền khác nhau.
2. **Chú thích (Comment), Mô tả (Description) và Tiêu đề mạng (Network Title) trong code/XML/CSV:**
   Bắt buộc dùng **tiếng Việt có dấu** chuẩn Unicode UTF-8. Điều này đảm bảo an toàn vận hành tối đa, giúp người vận hành hệ thống đọc hiểu thông tin trên màn hình WinCC/HMI không bị hiểu nhầm, nâng cao chất lượng kỹ thuật.
3. **Bộ tài liệu hướng dẫn và báo cáo (.md, .csv, .json, .txt, .xml):**
   Toàn bộ nội dung mô tả, quy trình và phân tích công nghệ bắt buộc viết bằng **tiếng Việt có dấu** chuẩn UTF-8.

*Ngoại lệ kỹ thuật:* Giữ nguyên các keyword bắt buộc của hãng Siemens và các hậu tố kỹ thuật:
- Các tiền tố/hậu tố: `_Cmd`, `_HMI`, `_M`, `_I`, `_Q` (Lưu ý: Tiền tố `AI_` chỉ là lịch sử trước migration, không dùng cho tag mới)
- Các thuật ngữ chuyên ngành: `PV`, `SP`, `PID`
- Các loại khối: `OB`, `FC`, `FB`, `DB`
- Định nghĩa I/O: `DI`, `DO`, `AI`, `AO`

### Ví dụ phân biệt đúng (Không chứa tiền tố AI_):
- `Nut_Khoi_Dong` (Tên tag hợp lệ)
- `Nut_Dung` (Tên tag hợp lệ)
- `Lenh_Khoi_Dong_Cmd` (Tên lệnh kết hợp hợp lệ)
- `Dong_Co_Chay` (Tên ngõ ra hợp lệ)
- `Dong_Co_Chay_M` (Tag gương mirror hợp lệ)
- Chú thích: `Nút nhấn khởi động hệ thống an toàn`
- Tiêu đề Network: `Khởi động chu kỳ chưng cất tự động`

### Ví dụ sai trong dự án mới:
- `Start_Button` (Sai - Dùng tiếng Anh)
- `Motor_Run` (Sai - Dùng tiếng Anh)
- `Nút_Khởi_Động` (Sai - Tên tag chứa tiếng Việt có dấu)
- `AI_Nut_Khoi_Dong` (Sai - Chứa tiền tố lịch sử `AI_`)
- Chú thích viết không dấu hoặc bằng tiếng Anh (Sai)

---

## 3. Thứ tự nghiên cứu tài liệu bắt buộc

Hãy tự nghiên cứu các tài liệu theo đúng lộ trình để nắm vững nghiệp vụ thiết kế liên động an toàn và chống xung đột:

1. [AI_AGENT_START_HERE.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/AI_AGENT_START_HERE.md) (Chỉ dẫn nhập môn - File này).
2. [README.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/README.md) (Tổng quan kiến trúc thư mục).
3. **[Lessons_Learned_RealWorld_PLC.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/Lessons_Learned_RealWorld_PLC.md)** (CỰC KỲ QUAN TRỌNG: Học cách thiết kế cờ chốt an toàn E-Stop trên SCADA, thứ tự Network tối ưu tránh trễ chu kỳ quét PLC, và giải quyết zombie tiến trình TIA Openness).
4. **[Master_SCL_5_Agent_Prompt.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/prompts/scl/Master_SCL_5_Agent_Prompt.md)** (CỰC KỲ QUAN TRỌNG: Hướng dẫn luồng và nhiệm vụ của chuỗi 5 Agent SCL-First mới).
5. [Master_Ladder_Only_5_Agent_Prompt.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/prompts/Master_Ladder_Only_5_Agent_Prompt.md) (Hướng dẫn vai trò của từng Agent cho Ladder cũ - Legacy Reference).
6. [Agent_TIA_LAD_Only_Guide.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/Ladder/Agent_TIA_LAD_Only_Guide.md) (Cẩm nang vẽ đồ họa Ladder XML - Legacy Reference).
7. [Agent_LAD_Library.py](file:///D:/AI_Agent_PLC_LADDER_ONLY/Ladder/Agent_LAD_Library.py) (Nghiên cứu API Python dùng để sinh code - Legacy Reference).
8. Tra cứu các file mẫu cấu trúc trong thư mục `templates/`.

---

## 4. Chuỗi phối hợp 5 AI Agent (Chiến lược SCL mới)

Chương trình phát triển PLC mới sẽ được phân rã thành chuỗi các tác vụ chuyên biệt (Chi tiết xem tại các tài liệu trong thư mục [prompts/scl/](file:///D:/AI_Agent_PLC_LADDER_ONLY/prompts/scl/)):

- **Agent 1 - Analyst (Nhà phân tích - [Agent1_SCL_Analyst.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/prompts/scl/Agent1_SCL_Analyst.md)):** Đọc yêu cầu công nghệ, bóc tách tín hiệu I/O vật lý (không prefix `AI_`), phân tích cảnh báo, liên động an toàn và xuất bản `IO_Map.json` cùng `Logic_Analysis.md`.
- **Agent 2 - Tag & DB Builder (Thiết kế bảng biến - [Agent2_SCL_Tag_DB_Builder.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/prompts/scl/Agent2_SCL_Tag_DB_Builder.md)):** Đọc bản đồ I/O để tạo bảng biến PLC chuẩn (`PLC_Tags.xml` hoặc SCL tag table) sạch, không có tiền tố `AI_`, và thiết kế các DB cấu trúc (`DB_HMI`, `DB_Recipe`, `DB_Operation`, `DB_Comms`).
- **Agent 3 - SCL Coder (Lập trình logic SCL - [Agent3_SCL_Coder.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/prompts/scl/Agent3_SCL_Coder.md)):** Viết logic chương trình PLC (OB, FB, FC) trực tiếp bằng mã SCL source (file `.scl`) để import vào TIA Portal. Sử dụng `CASE State OF` rõ ràng, gọi `PID_Compact` Siemens chuẩn (không tự viết PID), cấm nhồi logic vào OB1.
- **Agent 4 - QA Reviewer (Thẩm định chất lượng - [Agent4_SCL_QA_Reviewer.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/prompts/scl/Agent4_SCL_QA_Reviewer.md)):** Thẩm định an toàn I/O, cấm dùng GET/PUT, cấm dùng tag `AI_` mới, kiểm duyệt trên file thực tế và readback từ TIA Portal thật để đảm bảo biên dịch đạt 0 Errors.
- **Agent 5 - HMI & TIA Executor (Thực thi - [Agent5_HMI_TIA_Executor.md](file:///D:/AI_Agent_PLC_LADDER_ONLY/prompts/scl/Agent5_HMI_TIA_Executor.md)):** Thiết lập tài liệu kết nối WinCC HMI (`Tag_Binding.md`), chạy quy trình vá HMI WinCC qua export/dry-run/patch/readback, giữ nguyên thứ tự bồn tổng quan: Bồn 1 $\rightarrow$ Bồn 2 $\rightarrow$ Bồn 4 $\rightarrow$ Bồn 3.

---

## 5. Danh mục file bàn giao tối thiểu cho dự án mới trong `projects/<ten_du_an>/output/`

1. `IO_Map.json` - Sơ đồ tín hiệu I/O.
2. `PLC_Tags.xml` hoặc SCL tag table / DB source - Bảng khai báo biến PLC (không chứa tiền tố `AI_`).
3. `OB1_Main.scl` (hoặc XML importable) - Khối tổ chức hệ thống chính dạng SCL.
4. `FB_Main.scl` hoặc `FC_Main.scl` - Khối logic chương trình cốt lõi dạng SCL.
5. `Hmi.TextList.[Ten_List].xml` (nếu có) - Danh sách Text List HMI SCADA.
6. `Tag_Binding.md` - Tài liệu liên kết SCADA WinCC.
7. `MANUAL_STEPS.md` - Hướng dẫn tích hợp và vận hành thực tế.
8. `QA_Report.md` - Báo cáo chất lượng biên dịch và kiểm duyệt.

