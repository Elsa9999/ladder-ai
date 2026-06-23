# Báo Cáo Kết Quả Xuất XML & Trích Xuất Raw Patterns (TIA Portal V18)

**Thời gian thực hiện:** 2026-06-09T00:18:00+07:00  
**Tác giả:** AI Agent Antigravity  
**Trạng thái chung:** THÀNH CÔNG (Đã trích xuất, đối chiếu trùng lặp từ cả S7-1200 và S7-300)

---

## 1. Thử Nghiệm Trên Dự Án `Project1` (Chưa Biên Dịch)
*   **Mục tiêu:** Kiểm tra xem TIA Portal V18 Openness có hỗ trợ xuất XML từ các khối chương trình đang bị lỗi biên dịch (Inconsistent) hay không.
*   **Kết quả:** **THẤT BẠI**.
*   **Lỗi Openness nguyên văn:**
    ```text
    Error when calling method 'Export' of type 'Siemens.Engineering.SW.Blocks.OB'.
    Inconsistent blocks and PLC data types (UDT) cannot be exported.
    ```
*   **Kết luận kỹ thuật:** TIA Openness strictly chặn mọi thao tác xuất XML đối với các khối chương trình ở trạng thái Inconsistent (chưa compile hoặc compile lỗi).

---

## 2. Các Dự Án Biên Dịch Thành Công Được Sử Dụng Để Trích Xuất
Chúng tôi đã thực hiện xuất XML thành công trên sáu dự án mẫu V18 của bạn:
1.  **Dự án `PLSP_THEO_CHIEU_CAO_V18` (S7-1200 - PLC_1)**: Xuất thành công các khối chương trình và bảng tags (lưu tại `PLC_1_PLSP_PID`).
2.  **Dự án `PID_MAYSAY_V18` (S7-1200 - PLC_1)**: Xuất thành công các khối chương trình và bảng tags (lưu tại `PLC_1_PLSP_PID`).
3.  **Dự án `Automated-Production-Line-Simulation_V18` (S7-300 - PLC_2)**: Xuất thành công 32 khối chương trình và bảng tags (lưu tại `PLC_2`).
4.  **Dự án `New_V16_PID_Project_V5.5_V18` (S7-1200 - PLC_1)**: Compile thành công và xuất ngược thành công khối (lưu tại `PLC_1_Smoker`).
5.  **Dự án `final_assignment_V18` (S7-1200 - PLC_1)**: Compile thành công và xuất ngược thành công 19 khối chương trình và tag tables (lưu tại `PLC_1_Assignment`).
6.  **Dự án `PLC_Mixing_system` (S7-1200 - PLC)**: Compile thành công và xuất ngược thành công khối `Main.xml` và tag tables (lưu tại `PLC`).

*   **Thư mục xuất ngược:**
    *   S7-1200 (PLSP/PID): [PLSP_export/PLC_1_PLSP_PID](file:///D:/AI_Agent_PLC_LADDER_ONLY/examples/TIA_V18_XML_Pattern_Library/raw_exports/PLSP_export/PLC_1_PLSP_PID/)
    *   S7-1200 (Smoker): [PLSP_export/PLC_1_Smoker](file:///D:/AI_Agent_PLC_LADDER_ONLY/examples/TIA_V18_XML_Pattern_Library/raw_exports/PLSP_export/PLC_1_Smoker/)
    *   S7-1200 (Assignment): [PLSP_export/PLC_1_Assignment](file:///D:/AI_Agent_PLC_LADDER_ONLY/examples/TIA_V18_XML_Pattern_Library/raw_exports/PLSP_export/PLC_1_Assignment/)
    *   S7-1200 (Mixing): [PLSP_export/PLC](file:///D:/AI_Agent_PLC_LADDER_ONLY/examples/TIA_V18_XML_Pattern_Library/raw_exports/PLSP_export/PLC/)
    *   S7-300: [PLSP_export/PLC_2](file:///D:/AI_Agent_PLC_LADDER_ONLY/examples/TIA_V18_XML_Pattern_Library/raw_exports/PLSP_export/PLC_2/)
*   **Trạng thái kiểm tra XML:** 100% Well-formed (Không gặp lỗi cú pháp).

---

## 3. Kết Quả Đối Chiếu Trùng Lặp & Bổ Sung Thư Viện
Chúng tôi đã đối chiếu đệ quy 14 raw patterns vừa trích xuất với thư viện chính (`patterns/`):

### A. Lệnh Bị Trùng Lặp (Đã Có Sẵn - Bỏ Qua):
*   **`TON`**: Đã tồn tại trong thư viện chính tại thư mục `patterns/timer_counter/ton`.
*   **`CTU`**: Đã tồn tại trong thư viện chính tại thư mục `patterns/timer_counter/ctu`.

### B. Các Lệnh Mới Hoàn Toàn (Được Bổ Sung Vào Raw Patterns):
Có **12 raw patterns mới** được lưu trữ thành công tại thư mục [raw_patterns](file:///D:/AI_Agent_PLC_LADDER_ONLY/examples/TIA_V18_XML_Pattern_Library/raw_patterns/):

| Tên Lệnh (Mapped Name) | Tên Part Trong XML | Dòng CPU Hỗ Trợ | File Nguồn | Vị Trí Mạng (Network Index) | Trạng Thái XML | Trạng Thái Thư Viện |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OR** | `O` | S7-1200 | `Main.xml` (Mixing) | Network 1 | Well-formed | **Mới (Chưa có)** |
| **P_TRIG** | `PBox` | S7-1200 | `FC_AUTO_MODE.xml` (PLSP) | Network 2 | Well-formed | **Mới (Chưa có)** |
| **N_TRIG** | `NBox` | S7-1200 | `FC_AUTO_MODE.xml` (PLSP) | Network 2 | Well-formed | **Mới (Chưa có)** |
| **TONR** | `TONR` | S7-1200 | `FC_SIMULATION.xml` (PLSP) | Network 3 | Well-formed | **Mới (Chưa có)** |
| **NORM_X** | `Normalize` | S7-1200 | `Main.xml` (PID) | Network 2 | Well-formed | **Mới (Chưa có)** |
| **SCALE_X** | `Scale_X` | S7-1200 | `Main.xml` (PID) | Network 2 | Well-formed | **Mới (Chưa có)** |
| **TOF** | `TOF` | S7-1200 | `M1_WIND_DOWN.xml` (Assignment) | Network 1 | Well-formed | **Mới (Chưa có)** |
| **R_TRIG** | `R_TRIG` | S7-1200 | `Main.xml` (Smoker) | Network 2 | Well-formed | **Mới (Chưa có)** |
| **TP** | `TP` | S7-1200 | `Main.xml` (Mixing) | Network 2 | Well-formed | **Mới (Chưa có)** |
| **F_TRIG** | `F_TRIG` | S7-1200 | `Main.xml` (Smoker) | Network 9 | Well-formed | **Mới (Chưa có)** |
| **SR** | `Sr` | S7-1200 | `Main.xml` (Mixing) | Network 1 | Well-formed | **Mới (Chưa có)** |
| **INVERT** | `Not` | S7-1200 | `base_production_fb.xml` (Sim) | Network 1 | Well-formed | **Mới (Chưa có)** |

> [!NOTE]
> **Lưu ý về khả năng tương thích:**  
> Nhờ việc nạp các dự án S7-1200 mới (`PLC_Mixing_system`), các lệnh như `OR`, `SR` và `TP` đã được cập nhật trực tiếp nguồn trích xuất từ các khối XML bản S7-1200 gốc. Điều này đảm bảo tính tương thích và độ chính xác cao nhất cho thư viện.

> [!WARNING]
> **RAW ONLY - DO NOT USE FOR GENERATION UNTIL COMPILE PASS.**  
> Mặc dù các mẫu này đều là XML hợp lệ (Well-formed), chúng được lưu dưới dạng `pattern.raw.xml` và `manifest.raw.json` để phục vụ nghiên cứu và đối chiếu. Cần chạy qua bộ QA/Validator và chuẩn hóa sang dạng template trước khi sử dụng để tự động phát sinh mã Ladder.
