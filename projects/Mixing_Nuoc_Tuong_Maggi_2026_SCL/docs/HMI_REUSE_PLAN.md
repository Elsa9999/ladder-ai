# Kế Hoạch Tái Sử Dụng Giao Diện HMI WinCC (HMI_REUSE_PLAN.md)

Tài liệu này đặc tả kế hoạch tái sử dụng, ánh xạ biến, và tự động vá lỗi (patch) giao diện màn hình điều khiển WinCC HMI cho dự án Mixing Nước Tương Maggi 2026 SCL.

---

## 1. Nguyên Tắc Bảo Toàn Giao Diện & Tự Động Hóa

*   **Không chỉnh sửa thủ công trên WinCC:** Tuyệt đối không tự kéo thả, chỉnh sửa tọa độ hay liên kết tag thủ công trên phần mềm TIA Portal/WinCC HMI để tránh sai lệch và tốn thời gian.
*   **Quy trình tự động hóa:**
    1.  **Export:** Xuất các màn hình giao diện WinCC (`Screen_1.xml` và các màn hình chi tiết) thành định dạng XML thông qua công cụ Openness `Agent_TIA_HMI_Exporter.exe`.
    2.  **Patch:** Chạy script Python để tự động dò tìm, thay thế địa chỉ tag cũ bằng tag mới dựa trên file ánh xạ `migration_map.csv` và căn chỉnh bố cục các đối tượng.
    3.  **Import & Readback:** Nạp lại file XML đã vá vào dự án WinCC, xuất ngược để kiểm tra bằng chứng (KEEP_EVIDENCE) và chạy script verify để đảm bảo tính chính xác.

---

## 2. Thứ Tự Bồn Trộn Trên Giao Diện Tổng Quan

Trên giao diện tổng quan màn hình SCADA (Screen_1), thứ tự sắp xếp đồ họa của các bồn trộn từ trái sang phải tuân thủ nghiêm ngặt thiết kế vật lý của nhà máy:
$$\text{Bồn 1} \rightarrow \text{Bồn 2} \rightarrow \text{Bồn 4} \rightarrow \text{Bồn 3}$$

*   **Lưu ý quan trọng:** Bồn 4 hiển thị trước Bồn 3. Tất cả các tag liên kết động, dữ liệu hoạt cảnh (Animation) và nhãn hiển thị của các bồn phải khớp chính xác với vị trí tương ứng này trên giao diện WinCC.

---

## 3. Quy Chuẩn Định Dạng Ô Nhập Xuất Số Liệu (IO Field Formatting)

Để đảm bảo hiển thị trực quan và không bị lỗi hiển thị tràn chữ (lỗi hiển thị `###`), các ô nhập xuất dữ liệu (IO Field) trên HMI WinCC phải tuân thủ các quy tắc định dạng XML sau:

1.  **Căn lề chữ (Alignment):**
    *   Cấu hình căn giữa ô nhập liệu cả chiều dọc và chiều ngang:
        ```xml
        <HorizontalAlignment>Center</HorizontalAlignment>
        <VerticalAlignment>Middle</VerticalAlignment>
        ```

2.  **Định dạng chữ số (Numeric Format):**
    *   **Giá trị < 100** (Nhiệt độ Bồn 2/Bồn 4, Áp suất, Tần số): Hiển thị 1 chữ số thập phân sau dấu phẩy. Sử dụng định dạng:
        ```xml
        <FormatPattern>99.9</FormatPattern>
        ```
    *   **Giá trị >= 100** (Lưu lượng nước, Phần trăm mức dịch, Tần số Max): Sử dụng định dạng rộng hơn để tránh tràn ký tự:
        ```xml
        <FormatPattern>999.9</FormatPattern>
        ```

---

## 4. Quy Chuẩn Bố Cục Nhãn Đơn Vị Đo Lường (Unit Labels)

Các nhãn đơn vị đo lường tĩnh (`°C`, `bar`, `Hz`, `%`, `L/h`) đặt cạnh các ô nhập xuất số liệu phải được căn chỉnh tọa độ chính xác:

*   **Vị trí lề (X-Coordinate):** Nhãn đơn vị tĩnh phải cách lề phải của ô IO Field tương ứng đúng **8 pixel** để tránh bị chồng đè ký tự khi số hiển thị lớn:
    $$\text{X}_{\text{Unit}} = \text{X}_{\text{IO\_Field}} + \text{Width}_{\text{IO\_Field}} + 8$$
*   **Kích thước & Kiểu chữ (Font):** Sử dụng cỡ chữ **13, kiểu in đậm (Bold)**, font chữ Arial hoặc Tahoma để nhãn rõ ràng và cân xứng với kích thước số trong ô IO Field.
