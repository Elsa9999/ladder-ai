# HƯỚNG DẪN LẬP TRÌNH 100% LADDER XML TRÊN SIEMENS TIA PORTAL V18

Tài liệu này cung cấp các nguyên tắc thiết kế, quy tắc chuẩn hóa và cẩm nang kỹ thuật lập trình PLC bằng đồ họa **100% Ladder XML** cho các AI Agent hoạt động trong workspace `D:\AI_Agent_PLC_LADDER_ONLY`.

---

## 1. Mục tiêu tối thượng của dự án

- Sinh bảng tag và các khối chương trình (Block XML) tương thích hoàn toàn, import thành công vào phần mềm Siemens TIA Portal V18 thông qua Openness API.
- Toàn bộ thuật toán và logic điều khiển PLC bắt buộc nằm trong khối đồ họa OB/FC/FB Ladder.
- Tuyệt đối không sinh bất kỳ dạng logic mã nguồn SCL nào làm chương trình PLC.
- Các công cụ lập trình Python/C# chỉ dùng làm môi trường tự động hóa cấu trúc XML, không được nhồi nhét thuật toán PLC vào.

---

## 2. Quy tắc sử dụng ngôn ngữ Tiếng Việt thống nhất

Để đảm bảo tính tương thích và hiển thị chuyên nghiệp nhất trên hệ thống:

- **Tên biến (Tag Name), tên DB, tên HMI Tag:** Bắt buộc viết bằng **tiếng Việt không dấu** (ASCII, ký tự chữ, số và dấu gạch dưới, bắt đầu bằng `AI_`). Điều này tránh lỗi bảng mã ký tự khi import qua TIA Portal Openness chạy trên các máy tính Windows cấu hình khác nhau.
- **Tiêu đề mạng (Network Title), Chú thích (Comment) và Mô tả (Description) trong XML/CSV:** Bắt buộc sử dụng **tiếng Việt có dấu** chuẩn Unicode UTF-8 để phục vụ người vận hành giám sát thông tin trực quan trên WinCC SCADA/HMI.

### Ví dụ phân biệt đúng:
- Tag vật lý hợp lệ: `AI_Nut_Khoi_Dong`
- Tag ảo HMI hợp lệ: `AI_Nut_Khoi_Dong_HMI`
- Lệnh trung gian Cmd hợp lệ: `AI_Lenh_Khoi_Dong_Cmd`
- Tag gương phản hồi hợp lệ: `AI_Dong_Co_Chay_M`
- Comment hợp lệ: `Nút khởi động hệ thống an toàn`
- Tiêu đề Network hợp lệ: `Khởi động hệ thống chưng cất tự động`

---

## 3. Kiến trúc chương trình Ladder khuyến nghị

### Khối chính điều phối OB1 (`OB1_Main.xml`)
Khối tổ chức hệ thống OB1 nên giữ cấu trúc gọn gàng:
- Chỉ làm nhiệm vụ điều phối tổng thể và gọi các khối FB/FC chức năng lớn.
- Xử lý các lệnh Start/Stop hệ thống tổng hợp.
- Bản đồ hóa (Mapping) trực tiếp các biến Cmd trung gian ra ngõ ra vật lý `%Q`.
- Không nhồi nhét toàn bộ logic công nghệ phức tạp vào OB1 gây khó khăn cho việc bảo trì.

### Khối chức năng công nghệ chính FB (`FB_Main_Ladder.xml`)
Khối FB chính chứa logic cốt lõi bao gồm:
- Logic trạng thái tuần tự (State/Step logic).
- Bộ định thời (Timer) và bộ đếm (Counter) đa phân thể (Multi-instance).
- Các khóa liên động an toàn thiết bị (Interlocks).
- Quyết định các bit lệnh trung gian `_Cmd`.

### Khối quản lý lỗi FB (`FB_Fault_Ladder.xml`)
Nếu dự án có nhiều điều kiện cảnh báo bảo vệ:
- Nên tách riêng khối quản lý lỗi để chương trình mạch lạc.
- Tự động khóa trạng thái lỗi (Latch) bằng cuộn hút `SetCoil` khi có tác nhân.
- Chỉ giải phóng cờ lỗi bằng cuộn hút `ResetCoil` khi điều kiện an toàn đã hồi phục và có lệnh Reset chủ động từ người vận hành.

### Khối điều khiển ngắt chu kỳ OB30 (`OB30_PID.xml`)
Nếu hệ thống tích hợp bộ điều khiển nhiệt độ/áp suất PID:
- Bắt buộc gọi khối `PID_Compact` trong khối OB ngắt chu kỳ (OB30 Cyclic Interrupt).
- OB30 cũng được thiết lập và vẽ hoàn toàn bằng Ladder XML.
- Không tự ý gán các giá trị Kp, Ti, Td nếu đề bài chưa cung cấp. Cung cấp hướng dẫn tự chỉnh (Auto-tune) trong tài liệu hướng dẫn.

---

## 4. Quy tắc an toàn I/O & Ladder XML

- **Mỗi %I có %M song song:**
  ```text
  AI_Nut_Khoi_Dong      %I0.0  (Nút nhấn vật lý)
  AI_Nut_Khoi_Dong_HMI  %M0.0  (Lệnh bấm ảo WinCC)
  AI_Lenh_Khoi_Dong_Cmd %M20.0 (Xung lệnh kết hợp: AI_Nut_Khoi_Dong OR AI_Nut_Khoi_Dong_HMI)
  ```
- **Mỗi %Q có %M mirror:**
  ```text
  AI_Dong_Co_Chay       %Q0.0  (Đầu ra vật lý khởi động từ)
  AI_Dong_Co_Chay_M     %M10.0 (Tag gương mirror gửi phản hồi cho SCADA giám sát)
  ```
- **Quản lý UId duy nhất:** Mỗi phân đoạn vẽ `Part`, `Wire`, `Access`, `Instance` trong cấu trúc XML bắt buộc có một định danh `UId` duy nhất được sinh tự động từ bộ đếm của thư viện `Agent_LAD_Library.py`.
- **Tránh ghi đè cuộn hút:** Nếu một đầu ra bị chi phối ở nhiều mạng (Network) khác nhau, bắt buộc dùng `SetCoil` và `ResetCoil`. Tuyệt đối không dùng nhiều cuộn hút thường `Coil` cho cùng một tag (lỗi ghi đè).

---

## 5. Thư viện sinh Ladder XML (Agent_LAD_Library.py)

AI Agent thực hiện viết mã sinh logic thông qua API cực kỳ tường minh của thư viện:

### Ví dụ 1: Tạo mạch tự giữ OR trong Ladder
```python
builder.add_network("Khởi động hệ thống chưng cất", [
    ("NO", "AI_Nut_Khoi_Dong"),
    ("OR2", "AI_Nut_Khoi_Dong", "AI_Nut_Khoi_Dong_HMI", "AI_Lenh_Khoi_Dong_Cmd"),
    ("SetCoil", "AI_He_Thong_Chay")
])
```

### Ví dụ 2: Gọi bộ định thời TON (Timer On-Delay) an toàn (Không dùng Dummy Tag)
```python
# Gọi khối TON "T_Mo_Van" với thời gian trễ 5 giây, kết hợp hở tiếp điểm Q và ET bằng OpenCon
builder.add_network("Trễ mở van xả tinh dầu", [
    ("NO", "AI_He_Thong_Chay"),
    ("TON", "T_Mo_Van", "T#5S"),
    ("SetCoil", "AI_Van_Xa_Mo")
])
```

### Ví dụ 3: Tạo danh sách Text List và Graphic List tự động cho SCADA/HMI
```python
from Agent_LAD_Library import TIAHmiListBuilder

# 1. Tạo Text List cho chẩn đoán hệ thống an toàn
tl_builder = TIAHmiListBuilder("TL_Chuan_Doan_AnToan", "TextList", "Cảnh báo an toàn hệ thống")
tl_builder.add_item(0, "Hệ thống an toàn", "Bình thường")
tl_builder.add_item(3, "[KHOÁ AN TOÀN] Bảo vệ kích hoạt!", "Trip lỗi vật lý")
tl_builder.add_item(4, "[ESTOP ACTIVE] Dừng khẩn cấp!", "E-Stop")

with open("output/Hmi.TextList.TL_Chuan_Doan_AnToan.xml", "w", encoding="utf-8") as f:
    f.write(tl_builder.generate_xml())

# 2. Tạo Graphic List liên kết hình ảnh SCADA
gl_builder = TIAHmiListBuilder("GL_Van_Xa", "GraphicList", "Trạng thái van xả")
gl_builder.add_item(0, "valve_close_icon", "Van đóng")
gl_builder.add_item(1, "valve_open_icon", "Van mở")

with open("output/Hmi.GraphicList.GL_Van_Xa.xml", "w", encoding="utf-8") as f:
    f.write(gl_builder.generate_xml())
```

---

## 6. Bộ công cụ kiểm tra tự động trước khi bàn giao

Trước khi kết luận hoàn thành dự án, bắt buộc phải chạy bộ thẩm định chất lượng tự động:
```powershell
python Ladder/Agent_QA_Validator.py projects/<ten_du_an>/output
```
Đảm bảo báo cáo xuất ra `QA_Report.md` đạt trạng thái **ĐẠT (PASS)** ở 100% các tiêu chí kiểm duyệt.
