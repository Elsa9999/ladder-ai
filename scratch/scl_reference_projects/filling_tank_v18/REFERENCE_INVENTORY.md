# DANH MỤC TÀI LIỆU THAM KHẢO SCL (REFERENCE_INVENTORY.md)

Dự án tham chiếu: **Filling Tank_V18**  
Đường dẫn dự án TIA: `C:\Users\lienb\Downloads\PLC-PID-Level-Control-main\Filling Tank_V18\Filling Tank_V18.ap18`  
Thư mục lưu trữ: `D:\AI_Agent_PLC_LADDER_ONLY\scratch\scl_reference_projects\filling_tank_v18\`

Tài liệu này kiểm kê toàn bộ các khối chương trình (Blocks) và bảng biến (Tags) đã được export từ project mẫu "Filling Tank" để sử dụng làm tài liệu tham chiếu cú pháp SCL và LAD trên TIA Portal V18.

---

## 1. Danh Mục Các Khối Chương Trình (Program Blocks Inventory)

Dưới đây là danh sách chi tiết các block được trích xuất trong thư mục [Blocks/](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Blocks/):

| Tên Khối (Block Name) | Loại Khối & Số Hiệu | Ngôn Ngữ (Language) | File Export Tương Ứng | Phân Loại Cú Pháp | Liên Quan PID | Vai Trò & Mô Tả |
| :--- | :--- | :---: | :--- | :---: | :---: | :--- |
| **Main** | OB 1 | **LAD** | [Main.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Blocks/Main.xml) | LAD/FBD | Không trực tiếp | Khối tổ chức chính chạy theo chu kỳ. Gọi hàm mô phỏng và bộ điều khiển PID. |
| **Cyclic interrupt** | OB 30 | **LAD** | [Cyclic interrupt.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Blocks/Cyclic%20interrupt.xml) | LAD/FBD | Có (Gọi PID) | Khối ngắt chu kỳ (100ms) dùng để gọi bộ PID để giải thuật tích phân hoạt động ổn định. |
| **PID** | FB 1 | **SCL** | [PID.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Blocks/PID.xml) | **SCL thật** | **Có (Lõi PID)** | Khối chức năng thực hiện thuật toán điều khiển PID tự viết bằng SCL. |
| **MHJ-PLC-Lab-Function-S71200** | FC 9000 | **SCL** | [MHJ-PLC-Lab-Function-S71200.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Blocks/MHJ-PLC-Lab-Function-S71200.xml) | **SCL thật** | Không | Khối chức năng SCL phục vụ giao tiếp mô phỏng với phần mềm PLC-Lab. |
| **PI_DB** | DB 3 | **DB** | [PI_DB.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Blocks/PI_DB.xml) | DB Instance | Có (Instance) | Khối dữ liệu Instance của khối `PID` [FB1] (Dùng cho một vòng lặp PI). |
| **PID_DB** | DB 6 | **DB** | [PID_DB.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Blocks/PID_DB.xml) | DB Instance | Có (Instance) | Khối dữ liệu Instance thứ hai của khối `PID` [FB1] (Dùng cho một vòng lặp PID đầy đủ). |
| **hmi** | DB 5 | **DB** | [hmi.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Blocks/hmi.xml) | DB Global | Không trực tiếp | Khối dữ liệu chứa các biến giao tiếp hiển thị/cài đặt với màn hình HMI. |

---

## 2. Bảng Biến PLC (PLC Tags)

Bảng biến vật lý và ký hiệu được trích xuất trong thư mục [Tags/](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Tags/):

*   **Standard-Variablentabelle.xml:** Chứa các khai báo địa chỉ I/O thực tế (nhập xuất cảm biến mức, van xả, van bơm, các nút nhấn điều khiển và các kênh Analog IO của CPU S7-1200).
    *   *Liên kết file:* [Standard-Variablentabelle.xml](file:///d:/AI_Agent_PLC_LADDER_ONLY/scratch/scl_reference_projects/filling_tank_v18/Tags/Standard-Variablentabelle.xml)

---

## 3. Phân Tích Cú Pháp Tham Khảo Quan Trọng

1.  **Cấu trúc SCL thật (SCL Block Structure):**
    *   Khối **`PID` [FB1]** và **`MHJ-PLC-Lab-Function-S71200` [FC9000]** chứa mã nguồn SCL nguyên bản dưới dạng `<StructuredText>` trong phần CompileUnits.
    *   Đây là tài liệu tham khảo tuyệt vời cho cú pháp gán biến SCL, cấu trúc rẽ nhánh `IF-THEN-ELSE`, tính toán số thực `Real` cho bộ điều khiển tỷ lệ/tích phân/vi phân, giới hạn ngõ ra (anti-windup), và các phép tính tỷ lệ analog.
2.  **Khối ngắt chu kỳ Gọi PID:**
    *   Khối **`Cyclic interrupt` [OB30]** được cấu hình kiểu quét định kỳ để gọi khối FB `PID`. Đây là cấu hình mẫu chuẩn công nghiệp cho tất cả các bài toán điều khiển PID.
3.  **Khối Dữ Liệu Instance (Instance Data Block):**
    *   **`PID_DB`** và **`PI_DB`** chỉ rõ cấu trúc tự động tạo khi gọi một Block FB có tham số đầu vào/ra. Cấu trúc này ánh xạ trực tiếp các biến Input, Output, Static của FB1 vào vùng nhớ DB tĩnh.
