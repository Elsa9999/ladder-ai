# AI Agent Guidance & Repository Rules (LAD-Only)

This repository is a framework for generating Siemens TIA Portal V18 PLC projects using 100% graphical Ladder XML (LAD).

## 1. Core Rules
- **LAD ONLY**: All PLC program blocks (OBs, FBs, FCs) must be 100% Ladder XML. Absolutely no SCL code (no SCL blocks, SCL networks, or .scl source files) is allowed in PLC logic. Python/C# are only used for tooling/generation.
- **NO GET/PUT**: S7 GET/PUT communication is prohibited. Use Modbus TCP for PLC-to-PLC communication.
- **PID Compact**: Use PID_Compact Version 1.2. Always write/move 3 (Auto) to sRet.i_Mode when enabled, and move 0 (Inactive) when disabled to prevent mode-locking.
- **Modbus TCP**: Use MB_CLIENT / MB_SERVER Version 3.1 for S7-1200 V4.5.
- **Quality Gates**: Always validate XML, backup/export before TIA import, and ensure 0 errors on compile.

## 2. Naming & Language Conventions
- **Variable/Tag Names, DB Names, HMI Tags**: Vietnamese WITHOUT accents (ASCII-only, A-Z, a-z, 0-9, underscores). Must start with "AI_" prefix (e.g., Nut_Khoi_Dong).
- **Network Titles, Comments, Descriptions**: UTF-8 Vietnamese WITH accents (Tieng Viet co dau) for operator understanding.
- **Documentation (.md, .json, .csv)**: UTF-8 Vietnamese WITH accents.

## 3. Directory Layout
- **docs/**: Project map, acceptance criteria, and CLI commands documentation.
- **Ladder/**: Python libraries (Agent_LAD_Library.py) and compiled Openness C# utilities.
- **projects/**: Code generation projects (e.g., Mixing_Nuoc_Tuong_Maggi_2026).
- **scratch/**: Temporary test scripts and offline verification codes.
- **prompts/**: Prompt specifications for Agent roles (Analyst, Tag Builder, Coder, QA, SCADA).

## 4. Quick Verification Commands
See docs/COMMANDS.md for detailed command usage.
To run offline checks, execute the automated harness:
  python harness/run_acceptance.py

## 5. HMI Styling & Formatting Rules
- **IO Field Alignment**: Cấu hình các ô nhập xuất dữ liệu (IO Field) luôn căn giữa: `<HorizontalAlignment>Center</HorizontalAlignment>` và `<VerticalAlignment>Middle</VerticalAlignment>`.
- **IO Field Numeric Format**: Cấu hình hiển thị số thực có 1 chữ số thập phân sau dấu phẩy:
  - Giá trị < 100 (như Nhiệt độ, Áp suất, Tần số): Dùng định dạng `<FormatPattern>99.9</FormatPattern>`.
  - Giá trị >= 100 (như Lưu lượng, Phần trăm): Dùng định dạng `<FormatPattern>999.9</FormatPattern>` để tránh tràn chữ dẫn tới lỗi hiển thị `###`.
- **Nhãn đơn vị đo lường (Unit Labels)**:
  - Đặt nhãn đơn vị (TextField tĩnh chứa `°C`, `bar`, `Hz`, `L/h`, `%`) cách lề phải của ô IO Field **8 pixel** (ví dụ: `tf_left = left + width + 8`) để không bị chồng lấn.
  - Sử dụng kích thước chữ cỡ **13, kiểu chữ Bold** (in đậm, font Arial hoặc Tahoma) để nhãn rõ ràng, cân xứng với ô số.

