# Dự án Mixing Nước Tương Maggi 2026 (SCL Version)

Dự án này là phiên bản phát triển bằng ngôn ngữ **SCL (Structured Control Language)** cho hệ thống pha trộn nước tương Maggi 2026, chuyển dịch từ định hướng Ladder-only cũ sang **SCL-first**.

## 1. Cấu trúc thư mục dự án

```text
projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/
├── README.md               # Tài liệu tổng quan (File này)
├── docs/                   # Tài liệu đặc tả và kế hoạch thiết kế
│   ├── VARIANT_SCOPE.md    # Phân định phạm vi Variant A (1 PLC) & Variant B (2 PLC)
│   ├── BLOCK_MAP.md        # Bản đồ phân bổ khối chương trình (OB, FB, FC, DB)
│   ├── TAG_PLAN.md         # Quy hoạch bảng biến Tag và Data Blocks
│   └── HMI_REUSE_PLAN.md   # Kế hoạch tái sử dụng giao diện HMI WinCC
├── src_scl/                # Thư mục mã nguồn SCL (.scl)
│   ├── Variant_A_Automation_1PLC/ # Mã nguồn logic cho Variant A
│   └── Variant_B_DauNoi_2PLC/     # Mã nguồn logic cho Variant B
├── db/                     # Các file định nghĩa Data Block (.scl)
├── udt/                    # Định nghĩa kiểu dữ liệu người dùng UDT (.scl)
├── hmi_mapping/            # Bảng ánh xạ tag và file patch HMI
├── tia_import/             # Thư mục chuẩn bị import vào TIA Portal
└── tests/                  # Kịch bản mô phỏng và test offline
```

## 2. Nguyên tắc thiết kế cốt lõi (SCL-First)

*   **SCL là ngôn ngữ chính:** Toàn bộ logic điều khiển mới phải viết bằng SCL. Bản Ladder cũ chỉ dùng làm cơ sở tham khảo đối chiếu logic (Legacy Reference).
*   **Quy tắc đặt tên Tag:** Tên tag viết bằng tiếng Việt không dấu (ASCII), tuyệt đối **KHÔNG sử dụng tiền tố `AI_`** cho các biến mới.
*   **Điều khiển nhiệt độ (PID):** Bắt buộc sử dụng khối công nghệ **`PID_Compact` Version 1.2** chuẩn của Siemens, không tự viết thuật toán PID giả lập. Việc điều phối PID được gọi trực tiếp bằng SCL (ghi `3` vào `sRet.i_Mode` để chạy Auto và ghi `0` để dừng/Inactive).
*   **Truyền thông:**
    *   Truyền thông PLC-PLC (Variant B): Sử dụng Modbus TCP thông qua thư viện `MB_CLIENT` và `MB_SERVER` (Version 3.1). Nghiêm cấm dùng S7 GET/PUT.
    *   Truyền thông điều khiển biến tần ATV12 (Variant B): Sử dụng Modbus RTU thông qua các khối chuẩn của Siemens.
*   **Quy hoạch dữ liệu:** Ưu tiên sử dụng các khối dữ liệu cấu trúc (`DB_HMI`, `DB_Operation`, `DB_Recipe`, `DB_Comms`) thay vì vùng nhớ M-area toàn cục nhằm nâng cao hiệu năng và tính cấu trúc của mã SCL.
