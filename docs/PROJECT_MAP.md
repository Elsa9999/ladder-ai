# BẢN ĐỒ THƯ MỤC CẤU TRÚC WORKSPACE (PROJECT MAP)

Tài liệu này mô tả chi tiết sơ đồ tổ chức thư mục của workspace `D:\AI_Agent_PLC_LADDER_ONLY` nhằm giúp các kỹ sư và AI Agent định vị nhanh chóng các công cụ và tài nguyên.

---

## 1. Các Tệp Tin Cốt Lõi Ở Thư Mục Gốc (Root Files)
*   **[AGENTS.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/AGENTS.md):** Chỉ dẫn nhanh dành cho Agent (ASCII-safe, đọc ngay khi mở repo).
*   **[AI_AGENT_START_HERE.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/AI_AGENT_START_HERE.md):** Tài liệu nhập môn bắt buộc cho AI Agent, quy định các tiêu chuẩn lập trình đồ họa và ngôn ngữ.
*   **[README.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/README.md):** Tổng quan về framework, quy trình phối hợp 5 Agent và quy tắc đặt tên.
*   **[Lessons_Learned_RealWorld_PLC.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/Lessons_Learned_RealWorld_PLC.md):** Đúc kết kinh nghiệm thực tế về E-Stop chốt, chống trễ chu kỳ quét PLC, và xử lý lỗi Openness.

---

## 2. Thư Mục Công Cụ Lập Trình & Openness (`Ladder/`)
Chứa thư viện sinh code, công cụ thẩm định chất lượng và các file thực thi C# Openness:
*   **[Agent_LAD_Library.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/Ladder/Agent_LAD_Library.py):** Thư viện Python chính dùng để dựng các khối đồ họa Ladder XML (OB, FB, FC) và HMI lists.
*   **[Agent_QA_Validator.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/Ladder/Agent_QA_Validator.py):** Công cụ thẩm định tự động chất lượng XML đầu ra (QA Pass gate).
*   **[Agent_TIA_LAD_Only_Guide.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/Ladder/Agent_TIA_LAD_Only_Guide.md):** Cẩm nang hướng dẫn cú pháp vẽ Ladder XML.
*   **Các công cụ C# Openness (`.exe` và `.cs`):**
    *   `Agent_TIA_Importer_Generic.exe`: Nạp tự động tags, blocks, và HMI lists vào TIA Portal.
    *   `Export_Device_ByName.exe`: Xuất ngược blocks, tags, UDTs từ TIA Portal ra XML.
    *   `Agent_TIA_Tag_Lister.exe`: Liệt kê các tag hiện hữu của PLC.
    *   `Agent_TIA_HMI_Exporter.exe`: Xuất Text/Graphic Lists HMI ra XML.
*   **Các thư viện tham chiếu:** `Siemens.Engineering.dll`, `Siemens.Engineering.Hmi.dll` (Openness API).
*   **`Siemens_Block_Dictionary.json`:** Từ điển tra cứu tham số khối Siemens.

---

## 3. Thư Mục Hướng Dẫn Vai Trò Agent (`prompts/`)
Chứa các tài liệu chỉ dẫn chi tiết cho từng vai trò trong chuỗi 5 AI Agent:
*   [Master_Ladder_Only_5_Agent_Prompt.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/prompts/Master_Ladder_Only_5_Agent_Prompt.md) (Prompt tổng hợp)
*   [Agent1_Analyst.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/prompts/Agent1_Analyst.md) (Phân tích công nghệ & IO Map)
*   [Agent2_Tag_Builder.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/prompts/Agent2_Tag_Builder.md) (Thiết kế bảng biến)
*   [Agent3_Ladder_Coder.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/prompts/Agent3_Ladder_Coder.md) (Sinh code đồ họa & HMI list)
*   [Agent4_QA.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/prompts/Agent4_QA.md) (Thẩm định an toàn)
*   [Agent5_HMI_Executor.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/prompts/Agent5_HMI_Executor.md) (Tích hợp TIA Portal & WinCC)

---

## 4. Thư Mục Mẫu & Tài Liệu Tham Khảo (`templates/` & `examples/`)
*   **`templates/`:** Chứa các mẫu khai báo bảng biến, hướng dẫn vận hành (`Manual_Steps_Template.md`) và checklist chất lượng bàn giao.
*   **`examples/`:** Chứa dự án tham khảo và hướng dẫn lập trình Modbus TCP tiêu chuẩn.

---

## 5. Thư Mục Lưu Trữ Dự Án (`projects/`)
Nơi lưu trữ các dự án sinh thực tế. Ví dụ dự án chính:
*   **`projects/Mixing_Nuoc_Tuong_Maggi_2026/`:**
    *   `generate_mixing_project.py`: Script Python để sinh toàn bộ UDT, Tags, Blocks, và HMI lists của dự án.
    *   `prepare_tia_import_sets.py`: Script sắp xếp và chuẩn bị sẵn các bộ tệp tin cần import theo đúng thứ tự phụ thuộc.
    *   `tia_import/`: Thư mục chứa các file XML đã phân phối, sẵn sàng nạp vào TIA Portal cho PLC1 và PLC2.
    *   `post_import_export/`: Thư mục chứa code XML xuất ngược từ TIA Portal sau khi import để đối chiếu kiểm chứng.
    *   `walkthrough.md`: Báo cáo chi tiết kết quả tích hợp và kiểm thử.
    *   `DEMO_80_PERCENT_CHECKLIST.md` & `TIA_IMPORT_80_PERCENT_CHECKLIST.md`: Hướng dẫn vận hành/import.

---

## 6. Thư Mục Chứa Tệp Tạm & Kịch Bản Kiểm Thử (`scratch/` & `harness/`)
*   **`scratch/`:** Lưu trữ các script nghiên cứu, kiểm tra nhanh (ví dụ: `validate_tia_imports.py`, `verify_clean.py`, `verify_post_import_export.py`) và đặc biệt là bộ mô phỏng offline chu kỳ quét PLC [test_plc_logic.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/test_plc_logic.py).
*   **`harness/`:** Chứa bộ điều khiển kiểm thử tự động [run_acceptance.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/harness/run_acceptance.py) nhằm tự động hóa quy trình đánh giá offline.
