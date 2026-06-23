# DANH SÁCH CÁC CÔNG CỤ BẮT BUỘC GIỮ LẠI (REPO CLEANUP KEEP LIST)

Tài liệu này đặc tả danh sách các tệp tin, công cụ và tài liệu đặc tả bắt buộc phải giữ lại (KEEP) để phục vụ cho việc phát triển và tích hợp hệ thống SCL mới. 

> [!IMPORTANT]
> **Quy định nghiêm ngặt:**
> Tuyệt đối không xóa, di chuyển hoặc đổi tên các tệp tin nằm trong danh sách này để tránh phá hỏng quy trình kiểm thử tự động, tích hợp Openness và liên kết HMI.

---

## 1. Công cụ tích hợp TIA Portal & Openness API (TIA Openness Tooling)
Đây là các công cụ viết bằng C# sử dụng API của Siemens để tự động hóa việc nạp (import), xuất (export) chương trình và thiết bị trong dự án TIA Portal V18.

- **[update_tia_project.cs](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/update_tia_project.cs) / [update_tia_project.exe](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/update_tia_project.exe):** Công cụ cốt lõi để nạp tự động các XML blocks vào TIA Portal.
- **[inspect_current_project.cs](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/inspect_current_project.cs) / [inspect_current_project.exe](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/inspect_current_project.exe):** Công cụ chẩn đoán và kiểm tra cấu trúc dự án TIA hiện tại.
- **[list_all_blocks.cs](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/list_all_blocks.cs) / [list_all_blocks.exe](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/list_all_blocks.exe):** Liệt kê toàn bộ các khối chương trình đang tồn tại trong CPU PLC.
- **[Siemens.Engineering.dll](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/Siemens.Engineering.dll) & [Siemens.Engineering.Hmi.dll](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/Siemens.Engineering.Hmi.dll):** Thư viện liên kết động của Siemens, bắt buộc phải nằm chung thư mục với các tệp `.exe` để Openness hoạt động.

---

## 2. Công cụ liên kết biến HMI WinCC (HMI Tag Binding)
Các script đảm nhận việc quét biến PLC và tự động map địa chỉ với WinCC HMI.

- **[add_missing_hmi_tags.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/add_missing_hmi_tags.py):** Tự động phát hiện và thêm các tag HMI còn thiếu.
- **[generate_all_scada_tags.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/generate_all_scada_tags.py):** Sinh bảng tag HMI hoàn chỉnh cho WinCC.
- **[smart_import_hmi_tags.cs](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/smart_import_hmi_tags.cs) / [smart_import_hmi_tags.exe](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/smart_import_hmi_tags.exe):** Tự động nạp bảng tag HMI đã xử lý vào dự án WinCC.

---

## 3. Công cụ sửa đổi giao diện XML (Screen XML Patching)
Bộ công cụ tự động căn lề ô nhập xuất dữ liệu (IO Field), định dạng số thực (`99.9` hoặc `999.9`) và căn chỉnh lề nhãn đơn vị đo lường cách ô số 8 pixel theo Rule 5 của `AGENTS.md`.

- **[patch_all_screens.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/patch_all_screens.py):** Script tổng chạy vá lỗi trên toàn bộ các tệp XML màn hình WinCC.
- **[patch_detail_screens.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/patch_detail_screens.py):** Vá lỗi riêng cho các màn hình chi tiết Bồn 1, 2, 3, 4.
- **[patch_man_tong_quan.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/patch_man_tong_quan.py):** Vá lỗi riêng cho giao diện Màn hình Tổng quan.
- **[apply_correct_units.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/apply_correct_units.py):** Căn chỉnh khoảng cách và kích thước font chữ cho nhãn đơn vị (°C, bar, Hz, %).
- **[format_hmi_io_fields.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/format_hmi_io_fields.py):** Căn giữa và định dạng số thực hiển thị.

---

## 4. Công cụ sinh bảng giám sát (Watch Table Generator)
Tự động tạo các bảng Watch Table của TIA Portal để hỗ trợ việc debug/ép giá trị ngoại tuyến.

- **[generate_watch_tables.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/generate_watch_tables.py):** Sinh file XML Watch Table từ file cấu hình.
- **[create_watch_tables.cs](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/create_watch_tables.cs) / [create_watch_tables.exe](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/create_watch_tables.exe):** Tự động nạp Watch Table trực tiếp vào dự án PLC.

---

## 5. Công cụ kiểm thử tự động & Thẩm định (Harness & Validators)
Các chốt kiểm soát chất lượng (Quality Gates) để Agent tự chạy xác minh trước khi commit.

- **[run_acceptance.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/harness/run_acceptance.py):** Script điều khiển chạy toàn bộ quy trình test của repo.
- **[validate_plc_overlaps.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/validate_plc_overlaps.py):** Kiểm tra trùng lặp vùng nhớ M-area hoặc I/O vật lý.
- **[validate_tia_imports.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/validate_tia_imports.py):** Thẩm định chất lượng XML import (kiểm tra luật Ladder-only đối với bản cũ, cấu trúc XML hợp lệ).
- **[test_plc_logic.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/test_plc_logic.py):** Bộ mô phỏng offline toàn diện scan-cycle của PLC để test logic sequencer và liên động an toàn.
- **[verify_post_import_export_manual.py](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/verify_post_import_export_manual.py):** Đối chiếu readback thực tế sau nạp.

---

## 6. Bản đồ dịch biến và báo cáo readback (Migration Map & Readback Reports)
Cơ sở dữ liệu đối chiếu và kết quả nghiệm thu trước đó.

- **[migration_map.csv](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026/migration_map.csv):** Tệp ánh xạ tag từ LAD cũ sang SCL mới không chứa tiền tố `AI_`.
- **[TIA_Tooling_Integration_Report.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/TIA_Tooling_Integration_Report.md):** Báo cáo tích hợp nạp thành công trước đó.

---

## 7. Bộ tài liệu đặc tả thiết kế SCL (SCL Planning Docs)
Toàn bộ các tài liệu hướng dẫn và chiến lược rewrite SCL vừa tạo:
- [SCL_REWRITE_STRATEGY.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/SCL_REWRITE_STRATEGY.md)
- [SCL_BLOCK_ARCHITECTURE.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/SCL_BLOCK_ARCHITECTURE.md)
- [SCL_TAG_DB_PLAN.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/SCL_TAG_DB_PLAN.md)
- [SCL_MIGRATION_RISK.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/SCL_MIGRATION_RISK.md)
- [SCL_VARIANT_PLAN.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/SCL_VARIANT_PLAN.md)
- [SCL_GRAFCET_MAPPING.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/SCL_GRAFCET_MAPPING.md)
- [SCL_LAD_TO_SCL_REFERENCE.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/SCL_LAD_TO_SCL_REFERENCE.md)
- [SCL_TEST_VERIFICATION_PLAN.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/docs/SCL_TEST_VERIFICATION_PLAN.md)
