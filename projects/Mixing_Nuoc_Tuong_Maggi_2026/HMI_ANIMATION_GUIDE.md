# Hướng Dẫn Cấu Hình Animation Cánh Khuấy Trên HMI (WinCC)

Tài liệu này hướng dẫn cách cấu hình hiển thị chuyển động (animation) cho 4 cánh khuấy của Bồn 1, Bồn 2, Bồn 3 và Bồn 4 sử dụng dữ liệu từ các tag đếm frame của PLC.

> **Ghi chú kiến trúc**: Logic animation nằm trong hai FC riêng biệt:
> - **`FC_HMI_Animation_PLC1`** (block ID 60, PLC1) — Bồn 1 & Bồn 2, được gọi cuối OB30 (cyclic 100 ms).
> - **`FC_HMI_Animation_PLC2`** (block ID 61, PLC2) — Bồn 3 & Bồn 4, được gọi cuối OB31 (cyclic 100 ms).
> - OB30/OB31 chỉ chứa lệnh `CALL_FC` animation, không chứa trực tiếp logic ADD/SUB/reset frame.


---

## 1. Tạo Graphic List Trên HMI

Để tạo hiệu ứng cánh khuấy đang quay, chúng ta sử dụng một **Graphic List** chứa 8 ảnh cánh khuấy ở các góc xoay khác nhau.

1. Trong cây thư mục dự án HMI, mở rộng **Text and graphic lists** và chọn tab **Graphic lists**.
2. Thêm một Graphic List mới đặt tên là: **`GL_Agitator_8Frame`**.
3. Cấu hình bảng giá trị cho list như sau:
   - **Giá trị 0**: Chọn ảnh cánh khuấy ở vị trí tĩnh/bắt đầu (Frame 0).
   - **Giá trị 1**: Chọn ảnh cánh khuấy xoay góc thứ 1 (Frame 1).
   - **Giá trị 2**: Chọn ảnh cánh khuấy xoay góc thứ 2 (Frame 2).
   - **Giá trị 3**: Chọn ảnh cánh khuấy xoay góc thứ 3 (Frame 3).
   - **Giá trị 4**: Chọn ảnh cánh khuấy xoay góc thứ 4 (Frame 4).
   - **Giá trị 5**: Chọn ảnh cánh khuấy xoay góc thứ 5 (Frame 5).
   - **Giá trị 6**: Chọn ảnh cánh khuấy xoay góc thứ 6 (Frame 6).
   - **Giá trị 7**: Chọn ảnh cánh khuấy xoay góc thứ 7 (Frame 7).

---

## 2. Tạo Và Cấu Hình Graphic I/O Field Cho Các Bồn

Trên giao diện vận hành (Screen HMI), đặt các đối tượng hiển thị trạng thái quay tương ứng:

1. Kéo thả đối tượng **Graphic I/O Field** vào vị trí bồn tương ứng trên Screen.
2. Cấu hình thuộc tính chung cho Graphic I/O Field:
   - **Mode (Chế độ)**: Chọn **`Output`** (Chỉ xuất hình ảnh).
   - **Graphic list**: Gán danh sách vừa tạo **`GL_Agitator_8Frame`**.
3. Gán tag dữ liệu (Process Tag) tương ứng cho từng bồn:
   - **Bồn 1**: Gán tag **`HMI_Anim_Bon1_Frame`** (PLC1)
   - **Bồn 2**: Gán tag **`HMI_Anim_Bon2_Frame`** (PLC1)
   - **Bồn 3**: Gán tag **`HMI_Anim_Bon3_Frame`** (PLC2)
   - **Bồn 4**: Gán tag **`HMI_Anim_Bon4_Frame`** (PLC2)

---

## 3. Quy Tắc Định Dạng Và Thẩm Mỹ HMI (Styling & Formatting Rules)

Để đảm bảo giao diện HMI hiển thị cân đối, chuyên nghiệp và rõ ràng, toàn bộ các ô nhập/xuất dữ liệu (IO Field) và nhãn đơn vị phải tuân thủ các nguyên tắc thiết kế sau:

### Căn Lề Ô Nhập/Xuất (IO Field Alignment)
- Các ô dữ liệu số luôn luôn phải căn giữa theo cả hai chiều:
  - `<HorizontalAlignment>Center</HorizontalAlignment>`
  - `<VerticalAlignment>Middle</VerticalAlignment>`

### Định Dạng Hiển Thị Số Thực (IO Field Numeric Format)
- Các thông số kiểu thực hiển thị **1 chữ số thập phân** sau dấu phẩy:
  - **Giá trị < 100** (ví dụ: Nhiệt độ, Áp suất, Tần số): Sử dụng định dạng **`99.9`** (`<FormatPattern>99.9</FormatPattern>`).
  - **Giá trị >= 100** (ví dụ: Lưu lượng, Phần trăm): Sử dụng định dạng **`999.9`** (`<FormatPattern>999.9</FormatPattern>`) để tránh hiện tượng tràn ô dẫn đến hiển thị lỗi ký tự `###`.

### Nhãn Đơn Vị Đo Lường (Unit Labels)
- Nhãn đơn vị (ví dụ: `°C`, `bar`, `Hz`, `L/h`, `%`) được hiển thị bằng một Static TextField riêng biệt.
- **Vị trí**: Đặt cách lề phải của ô IO Field đúng **`8 pixel`** (ví dụ: `tf_left = left + width + 8`) để tránh bị chồng chéo ký tự khi hiển thị trên các kích thước màn hình khác nhau.
- **Định dạng chữ**: Sử dụng cỡ chữ **`13`**, kiểu chữ **`Bold`** (in đậm), sử dụng font **Arial** hoặc **Tahoma** để bảo đảm sự rõ ràng và cân xứng tối đa.
