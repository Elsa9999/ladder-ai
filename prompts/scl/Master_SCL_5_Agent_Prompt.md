# Master Prompt Cho Chuỗi 5 AI Agent (Master_SCL_5_Agent_Prompt.md)

Tài liệu này định nghĩa luồng phối hợp và quy định chung cho chuỗi 5 AI Agent chuyên trách phát triển dự án PLC Siemens TIA Portal V18 bằng ngôn ngữ **SCL (Structured Control Language)**.

---

## 1. Các Nguyên Tắc Bắt Buộc (Core Rules)

1.  **SCL-First:** Logic PLC mới bắt buộc viết bằng ngôn ngữ SCL sạch, cấu trúc hóa để import vào TIA Portal. Bộ mã Ladder XML cũ chỉ dùng làm cơ sở tham khảo đối chiếu.
2.  **Đặt Tên Tag Hợp Lệ:** Tên tag viết bằng tiếng Việt không dấu (ASCII, A-Z, a-z, 0-9, dấu gạch dưới). Tuyệt đối **KHÔNG sử dụng tiền tố `AI_`** cho các tag/biến mới. Tiền tố `AI_` chỉ là tên lịch sử và không được dùng lại.
3.  **Không Sử Dụng GET/PUT:** Cấm sử dụng truyền thông S7 GET/PUT. Sử dụng Modbus TCP (giữa các PLC) hoặc Modbus RTU (PLC với thiết bị ngoại vi).
4.  **Điều khiển PID Compact:** Sử dụng khối công nghệ **`PID_Compact` Version 1.2** chuẩn của Siemens. Cấm tự viết thuật toán PID giả lập. Lập trình SCL trực tiếp gọi và phối hợp chế độ qua `sRet.i_Mode` (ghi `3` khi chạy Auto, ghi `0` khi dừng/Inactive).
5.  **Chú thích & Tài liệu:** Comment trong code và các tài liệu bàn giao viết bằng **tiếng Việt có dấu** chuẩn UTF-8.

---

## 2. Đặc Tả Hai Biến Thể Thiết Kế (Variant Scope)

Hệ thống SCL mới được phát triển song song hai Variant:

*   **Variant A (Cuộc thi tự động hóa - 1 PLC):**
    *   Mô phỏng toàn bộ chu trình Grafcet/State Machine của cả 4 bồn trên một CPU duy nhất.
    *   Sử dụng hai khối PID công nghệ `PID_Compact` Siemens cho Bồn 2 và Bồn 4.
    *   Tái sử dụng giao diện HMI Screen_1 để hiển thị và tương tác tập trung.
*   **Variant B (Đấu nối thực tế - 2 PLC):**
    *   **PLC_1 (Client):** Điều khiển Bồn 1-2, giao tiếp điều khiển biến tần cánh khuấy ATV12 thực tế qua Modbus RTU.
    *   **PLC_2 (Server):** Điều khiển Bồn 3-4.
    *   **Truyền thông chéo (Modbus TCP V3.1):** PLC_1 làm Client kết nối với PLC_2 làm Server. Giao tiếp qua khối kết nối kiểu `TCON_IP_v4` tường minh (giống bài mẫu Siemens/bài 4). Chân `CONNECT` của `MB_CLIENT`/`MB_SERVER` phải trỏ vào DB `TCON_IP_v4`. Các thông số IP, Port, Connection ID có thể được cấu hình trực tiếp qua Start Value trong DB hoặc khởi tạo ở `OB100`/`FirstScan`, đảm bảo biên dịch (compile) và readback từ TIA Portal khớp chính xác (không dùng các shortcut CONNECT_ID/IP_OCTET mơ hồ). Sử dụng cơ chế bắt tay bằng các tag kiểu `Int` (`CmdSeq` và `AckSeq`). Giao tiếp S7 GET/PUT bị nghiêm cấm hoàn toàn.

---

## 3. Luồng Phối Hợp 5 Agent

*   **Agent 1 - SCL Analyst:** Phân tích quy trình công nghệ, bóc tách tín hiệu I/O và liên động an toàn. Xuất bản `IO_Map.json` và `Logic_Analysis.md`.
*   **Agent 2 - SCL Tag & DB Builder:** Đọc sơ đồ I/O để sinh bảng tag vật lý (không prefix `AI_`) và thiết kế cấu trúc các khối dữ liệu DB tập trung (`DB_HMI`, `DB_Recipe`, `DB_Operation`, `DB_Comms`).
*   **Agent 3 - SCL Coder:** Lập trình các khối OB, FB, FC bằng mã nguồn SCL sạch, cấu trúc hóa. Cấm nhồi nhét logic vào OB1, sử dụng cấu trúc `CASE State OF` rõ ràng.
*   **Agent 4 - SCL QA Reviewer:** Thẩm định chất lượng code, kiểm duyệt an toàn I/O, cấm GET/PUT, cấm dùng tag `AI_`, đảm bảo biên dịch 0 lỗi trong TIA.
*   **Agent 5 - HMI & TIA Executor:** Quản lý xuất/nhập HMI WinCC qua export/dry-run/patch/readback, giữ nguyên thứ tự bồn tổng quan: Bồn 1 $\rightarrow$ Bồn 2 $\rightarrow$ Bồn 4 $\rightarrow$ Bồn 3.
