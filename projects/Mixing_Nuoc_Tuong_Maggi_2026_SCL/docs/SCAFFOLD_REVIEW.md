# Báo Cáo Kiểm Duyệt Và Chuẩn Hóa Scaffold Project (SCAFFOLD_REVIEW.md)

Tài liệu này kiểm duyệt cấu trúc thư mục (Scaffold) và các tài liệu đặc tả thiết kế của dự án Mixing Nước Tương Maggi 2026 SCL.

---

## 1. Thành Phần Cấu Trúc Scaffold Hiện Có

Dự án đã được thiết lập đầy đủ khung thư mục và các tệp tin đặc tả tại thư mục `projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL`:
*   **Thư mục docs/ đặc tả thiết kế:**
    *   `VARIANT_SCOPE.md`: Đặc tả phạm vi Variant A (1 PLC mô phỏng) và Variant B (2 PLC phân tán).
    *   `BLOCK_MAP.md`: Sơ đồ phân bổ và số hiệu của OB, FB, FC, DB cùng các Siemens System Blocks.
    *   `TAG_PLAN.md`: Quy hoạch đặt tên tag ASCII không dấu, không prefix `AI_`, thiết lập cấu trúc DB và đệm M-area.
    *   `HMI_REUSE_PLAN.md`: Quy hoạch tái sử dụng màn hình WinCC, thứ tự bồn trộn và quy chuẩn hiển thị ô IO Field, đơn vị tĩnh.
*   **Các thư mục trống được Git track (chứa `.gitkeep`):**
    *   `src_scl/Variant_A_Automation_1PLC/`: Nơi lưu logic SCL cho Variant A.
    *   `src_scl/Variant_B_DauNoi_2PLC/`: Nơi lưu logic SCL cho Variant B.
    *   `db/` và `udt/`: Lưu trữ các định nghĩa DB và UDT toàn cục.
    *   `hmi_mapping/` và `tia_import/`: Lưu trữ bảng ánh xạ và dữ liệu chuẩn bị nạp TIA Portal.
    *   `tests/`: Chứa các script test offline.

---

## 2. Điểm Đúng (Đạt Tiêu Chuẩn SCL-First)

1.  **Chiến lược SCL-first rõ ràng:** Logic PLC hoàn toàn định hướng bằng ngôn ngữ SCL sạch, cấu trúc hóa. Bản Ladder cũ chỉ được dùng làm đối chiếu logic (Legacy Reference).
2.  **Không có mâu thuẫn tag:** Quy tắc tag không sử dụng tiền tố `AI_` được áp dụng triệt để ở tất cả các cấp độ.
3.  **Điều khiển PID Compact Siemens chuẩn:** Thống nhất gọi khối công nghệ chuẩn `PID_Compact` V1.2 của Siemens và phối hợp chế độ qua `sRet.i_Mode` (Auto = 3, Inactive = 0), không tự chế thuật toán PID.
4.  **Cấm GET/PUT:** Không sử dụng truyền thông S7 GET/PUT, thay thế hoàn toàn bằng Modbus TCP V3.1 và Modbus RTU cho biến tần.
5.  **Bố cục HMI chuẩn xác:** Giữ nguyên thứ tự bồn trộn tổng quan trên WinCC HMI: **Bồn 1 $\rightarrow$ Bồn 2 $\rightarrow$ Bồn 4 $\rightarrow$ Bồn 3** (Bồn 4 đặt trước Bồn 3) và áp dụng các quy chuẩn định dạng số thực `<FormatPattern>` để chống tràn chữ.

---

## 3. Điểm Sai / Mâu Thuẫn Đã Được Chỉnh Sửa

Trong quá trình rà soát, chúng tôi phát hiện và đã tiến hành sửa đổi 2 điểm mâu thuẫn lớn trong tài liệu scaffold:

1.  **Phân định Real_IO vs. Sim_IO:**
    *   *Mâu thuẫn cũ:* Trong `TAG_PLAN.md`, các cảm biến mức và van xả/van cấp của bồn được liệt kê dưới dạng "I/O vật lý bắt buộc giữ nguyên `%I` / `%Q`".
    *   *Chỉnh sửa:* Đã viết lại mục 3 của `TAG_PLAN.md` để phân biệt rõ: Các van, cảm biến mức, nhiệt độ và lưu lượng là **Sim_IO** (mô phỏng ảo qua DB/HMI), cấm tự ý gán địa chỉ `%I`/`%Q` vật lý. Nhóm **Real_IO** (đấu dây thật) chỉ bao gồm cổng RS485 biến tần ATV12, contactor cấp nguồn VFD Bồn 2 (`%Q0.0`), và nút nhấn Start/Stop/Reset/E-Stop vật lý (nếu có).
2.  **Cấu hình kết nối Modbus TCP (TCON_IP_v4):**
    *   *Mâu thuẫn cũ:* Tài liệu yêu cầu "TCON cấu hình kết nối bắt buộc phải được gán động ở `FirstScan` (OB100)".
    *   *Chỉnh sửa:* Đã cập nhật `VARIANT_SCOPE.md` và `BLOCK_MAP.md` để linh hoạt hơn: Yêu cầu chân `CONNECT` của khối Modbus TCP Client/Server trỏ vào DB kết nối kiểu `TCON_IP_v4` tường minh. Các thông số IP, Port, Connection ID có thể cấu hình thông qua Start Value của DB hoặc gán tại `OB100`/`FirstScan`, miễn là biên dịch đạt 0 Errors và được kiểm chứng qua readback (không bắt buộc duy nhất việc gán ở OB100).

---

## 4. Điểm Còn Chờ Duyệt (Pending Review)

*   Bảng ánh xạ tag ảo HMI SCADA từ M-area cũ sang DB mới phục vụ patch màn hình XML HMI tự động.
*   Cấu trúc chi tiết của các DB toàn cục (`DB_HMI`, `DB_Recipe`, `DB_Operation`, `DB_Comms`) sẽ được viết cụ thể khi bắt đầu giai đoạn code.

---

## 5. Đề Xuất Nhiệm Vụ Kế Tiếp Để Code SCL An Toàn

Để bắt đầu viết code logic SCL đạt chất lượng cao và an toàn:
1.  **Nhiệm vụ 1:** Thiết lập các kiểu dữ liệu người dùng UDT (`.scl`) và khai báo cấu trúc hoàn chỉnh của 4 DB toàn cục (`DB_HMI`, `DB_Recipe`, `DB_Operation`, `DB_Comms`).
2.  **Nhiệm vụ 2:** Lập trình logic SCL cho **Variant A (1 PLC mô phỏng)** để kiểm chứng toàn bộ quy trình Grafcet, liên động an toàn và thuật toán PID bằng kịch bản mô phỏng offline.
3.  **Nhiệm vụ 3:** Phát triển logic truyền thông Modbus TCP PLC1-PLC2 và bộ điều khiển Modbus RTU ATV12 cho **Variant B (2 PLC đấu nối)**.
4.  **Nhiệm vụ 4:** Chạy các công cụ Openness xuất WinCC XML, chạy script vá HMI dựa trên tag DB mới, import WinCC và readback thẩm định.
