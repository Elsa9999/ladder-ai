# Quy Hoạch Bảng Biến Và Khối Dữ Liệu (TAG_PLAN.md)

Tài liệu này quy hoạch các nguyên tắc đặt tên tag, cấu trúc các khối dữ liệu (DB), và lộ trình dịch chuyển vùng nhớ từ M-area sang DB-area cho dự án Mixing Nước Tương Maggi 2026 SCL.

---

## 1. Nguyên Tắc Đặt Tên Biến (Tag Naming Rules)

Để đảm bảo hệ thống SCL mới hoạt động ổn định và tương thích hoàn toàn với bảng mã Unicode UTF-8 và ASCII trên TIA Portal:

1.  **Symbolic Name (Tên Tag / Tên DB / Tên Biến):**
    *   Bắt buộc viết bằng **tiếng Việt không dấu** (ASCII, chỉ gồm chữ cái Latinh `A-Z`, `a-z`, chữ số `0-9` và dấu gạch dưới `_`).
    *   Tuyệt đối **KHÔNG sử dụng tiền tố `AI_`** cho bất kỳ biến mới nào. (Ví dụ đặt: `Nut_Khoi_Dong`, `Nut_Dung`, `Dong_Co_Chay`).
    *   Tiền tố `AI_` chỉ là tên lịch sử của bản cũ trước migration (như `AI_Nut_Khoi_Dong`) và **tuyệt đối không được dùng lại** trong logic SCL mới.

2.  **Chú thích (Comment) và Mô tả (Description):**
    *   Bắt buộc viết bằng **tiếng Việt có dấu** chuẩn Unicode UTF-8 để đảm bảo người vận hành đọc hiểu chính xác trên màn hình WinCC HMI.

---

## 2. Chiến Lược Tổ Chức Vùng Nhớ (DB-Area vs. M-Area)

Bản Ladder cũ lạm dụng vùng nhớ M-area toàn cục (`%M`, `%MW`), gây khó khăn cho việc quản lý cấu trúc dữ liệu trong SCL.

### Thiết kế ưu tiên DB có cấu trúc:
Logic SCL mới sẽ chuyển toàn bộ dữ liệu nội bộ và dữ liệu giao tiếp sang các khối dữ liệu (Data Blocks) có cấu trúc để mã nguồn trực quan hơn:

1.  **`DB_HMI` (Giao tiếp HMI):** Chứa các nút nhấn ảo từ SCADA, các trạng thái phản hồi hiển thị đèn, số thực nhiệt độ, mức dịch.
2.  **`DB_Recipe` (Tham số công nghệ):** Chứa các giá trị cài đặt (Setpoint) thời gian trộn, thời gian xả dosing, nhiệt độ mục tiêu cho PID.
3.  **`DB_Operation` (Trạng thái vận hành):** Chứa các biến điều phối bước Grafcet (Step), cờ khóa liên động liên hoàn giữa các bồn, cờ báo lỗi lỗi thiết bị.
4.  **`DB_Comms` (Vùng đệm truyền thông):** Chứa mảng dữ liệu đệm đọc/ghi Modbus TCP và Modbus RTU.

### Xử lý tương thích M-area cũ (Compatibility Strategy):
*   Do màn hình WinCC HMI cũ và các Watch Table kiểm thử offline vẫn liên kết trực tiếp với một số địa chỉ `%M` cụ thể, chúng ta **giữ lại các tag M-area cũ** làm lớp đệm tương thích.
*   **Cơ chế liên kết:** Sử dụng khối mirror `FC_HMI_Mirror` viết bằng SCL để ánh xạ hai chiều giữa các tag M-area cũ và các cấu trúc biến trong DB mới:
    *   *Ví dụ (HMI ghi xuống M):* `DB_HMI.Nut_Khoi_Dong := M_Nut_Khoi_Dong_HMI;`
    *   *Ví dụ (PLC phản hồi lên M):* `M_Dong_Co_Chay_HMI := DB_HMI.Dong_Co_Chay;`
*   Lớp đệm này sẽ được loại bỏ hoàn toàn (Migration toàn diện) sau khi HMI Screen XML được cập nhật liên kết sang tag DB thông qua công cụ patch tag.

---

## 3. Bản Đồ I/O Vật Lý Bắt Buộc Giữ Nguyên (Physical I/O Preservation)

Để đảm bảo không cần đấu nối lại dây điện trên tủ điều khiển thực tế, các địa chỉ ngõ vào vật lý (`%I`) và ngõ ra vật lý (`%Q`) phải được giữ nguyên chính xác từ bản cũ:

### Ngõ vào số (Digital Inputs - %I):
*   Cảm biến báo mức cạn Bồn 1: `%I0.0`
*   Cảm biến báo mức đầy Bồn 1: `%I0.1`
*   Cảm biến báo mức cạn Bồn 2: `%I0.2`
*   Cảm biến báo mức đầy Bồn 2: `%I0.3`
*   Cảm biến báo mức cạn Bồn 3: `%I0.4`
*   Cảm biến báo mức đầy Bồn 3: `%I0.5`
*   Cảm biến báo mức cạn Bồn 4: `%I0.6`
*   Cảm biến báo mức đầy Bồn 4: `%I0.7`

### Ngõ ra số (Digital Outputs - %Q):
*   Van cấp liệu Dosing Bồn 1: `%Q0.0`
*   Van xả Bồn 1: `%Q0.1`
*   Van cấp liệu Dosing Bồn 2: `%Q0.2`
*   Van xả Bồn 2: `%Q0.3`
*   Van cấp liệu Dosing Bồn 3: `%Q0.4`
*   Van xả Bồn 3: `%Q0.5`
*   Van cấp liệu Dosing Bồn 4: `%Q0.6`
*   Van xả Bồn 4: `%Q0.7`
