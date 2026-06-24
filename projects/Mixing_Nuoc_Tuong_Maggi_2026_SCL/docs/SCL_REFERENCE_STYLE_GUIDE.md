# HƯỚNG DẪN QUY CHUẨN LẬP TRÌNH SCL TIA PORTAL V18 (SCL REFERENCE STYLE GUIDE)

Tài liệu này đúc kết các quy chuẩn lập trình, cấu trúc tệp tin, giao diện khối và cú pháp Structured Control Language (SCL) từ việc phân tích trực tiếp các tệp nguồn XML được export từ dự án mẫu **Filling Tank V18**. Mục tiêu là thiết lập quy chuẩn áp dụng cho dự án **Mixing Nước Tương Maggi 2026 SCL-first**.

---

## 1. Phân Tích Cách TIA Portal Export SCL Trong XML

Khi export một khối chương trình SCL qua TIA Portal Openness API, tệp XML sinh ra có cấu trúc như sau:

*   **Thuộc tính ngôn ngữ định dạng:** 
    Ngôn ngữ lập trình được khai báo tại thẻ `<ProgrammingLanguage>SCL</ProgrammingLanguage>` bên trong danh sách thuộc tính `<AttributeList>` của khối (FB/FC).
*   **Vị trí của StructuredText:**
    Mã nguồn SCL thực tế không được lưu dưới dạng văn bản thuần (plaintext) trực tiếp, mà được phân tách thành cây cú pháp trừu tượng (Abstract Syntax Tree - AST) nằm trong thẻ:
    `<SW.Blocks.CompileUnit>` $\rightarrow$ `<AttributeList>` $\rightarrow$ `<NetworkSource>` $\rightarrow$ `<StructuredText xmlns="...">`
*   **Cấu trúc AST của SCL trong XML:**
    *   Các từ khóa, toán tử và dấu phân cách được bọc trong các thẻ `<Token Text="..."/>` (ví dụ: `:=`, `IF`, `THEN`, `;`).
    *   Các khoảng trắng và xuống dòng được định nghĩa bằng `<Blank Num="n"/>` và `<NewLine Num="m"/>`.
    *   Truy cập biến local/global được định nghĩa bằng thẻ `<Access Scope="LocalVariable|GlobalVariable|Call|LiteralConstant">` chứa thẻ `<Symbol>` và các thẻ `<Component Name="..."/>` chỉ tên biến.
    *   Các chú thích được lưu trong thẻ `<LineComment>` hoặc `<Comment>`.

> [!IMPORTANT]
> **Nhận xét quan trọng cho dự án Maggi:**
> Vì cấu trúc XML chứa mã nguồn SCL của TIA Openness rất phức tạp và chứa nhiều chỉ số tự sinh (`ID`, `UId`), chúng ta **không tự soạn thảo SCL dưới dạng XML bằng tay**. 
> Thay vào đó, chúng ta viết mã SCL dưới dạng tệp văn bản thuần `.scl` chuẩn (External Source Files), sau đó sử dụng tính năng **"Generate blocks from source"** của TIA Portal để biên dịch thành các khối chương trình thực tế.

---

## 2. Cấu Trúc Interface Khối FB / FC

Interface của các khối SCL được khai báo trong XML tại thẻ `<Interface><Sections xmlns="...">`:

*   **Các Section chính:**
    *   `Input`: Các tham số đầu vào (đọc ghi chỉ trong khối, không lưu trạng thái qua chu kỳ quét tiếp theo).
    *   `Output`: Các tham số đầu ra (trả kết quả từ khối ra ngoài).
    *   `InOut`: Tham biến truyền qua con trỏ (đọc và ghi trực tiếp vào biến bên ngoài).
    *   `Static` *(chỉ có ở FB)*: Các biến tĩnh lưu trữ trạng thái giữa các chu kỳ quét (ví dụ: dữ liệu tích phân, bộ lọc nhiễu, các biến nhớ trung gian).
    *   `Temp`: Các biến tạm thời trong ngăn xếp (stack), bị xóa sau khi khối thực thi xong chu kỳ.
    *   `Constant`: Các hằng số cục bộ của khối.
    *   `Return` *(chỉ có ở FC)*: Kiểu dữ liệu trả về của hàm (nếu không trả về giá trị thì mặc định là `Void`).

*   **Thuộc tính của Member:**
    Mỗi biến trong section được khai báo qua thẻ `<Member Name="..." Datatype="..." Remanence="..." Accessibility="...">` và có thể kèm theo giá trị khởi tạo thông qua thẻ `<StartValue>value</StartValue>`.

---

## 3. Cách Instance DB Phản Ánh FB SCL

Instance DB (khối dữ liệu thực thể) được tạo ra khi một FB được gọi. Trong XML:
*   Được định nghĩa bởi thẻ `<SW.Blocks.InstanceDB ID="...">`.
*   Chỉ rõ FB gốc qua thẻ `<InstanceOfName>Tên_FB</InstanceOfName>` và `<InstanceOfType>FB</InstanceOfType>`.
*   Cấu trúc `<Interface><Sections>` của Instance DB **sao chép y hệt** cấu trúc của FB gốc bao gồm tất cả các thành phần `Input`, `Output`, `InOut`, và `Static`.
*   Giá trị hiện tại hoặc giá trị khởi động riêng của Instance DB có thể được định cấu hình bằng thẻ `<StartValue>` trên từng member tương ứng của DB đó mà không làm ảnh hưởng đến FB gốc.

---

## 4. Cách OB LAD Gọi FB SCL Bằng Instance DB

Từ tệp `Cyclic interrupt.xml` (OB30 viết bằng LAD), chúng ta quan sát thấy cách một mạng LAD gọi khối FB viết bằng SCL:

1.  **Khai báo Call:**
    Sử dụng thẻ `<Call UId="...">` chứa phần `<CallInfo Name="Tên_FB" BlockType="FB">` và chỉ định thực thể DB liên kết qua thẻ `<Instance Scope="GlobalVariable"><Component Name="Tên_Instance_DB"/></Instance>`.
2.  **Đấu nối chân tham số (Wiring):**
    Mỗi chân tham số đầu vào (`Input`) và đầu ra (`Output`) của FB được liệt kê thành các phần tử `<Parameter Name="..." Section="..." Type="..." />`. Các kết nối dây (Wire) trong LAD sẽ liên kết các cổng này với các biến vật lý hoặc biến nhớ toàn cục (ví dụ: nối biến hệ thống `"hmi".startfromhmi` vào chân điều khiển).

---

## 5. Cú Pháp SCL Rút Ra Từ Dự Án Mẫu

Dựa trên việc giải mã và phân tích các mạng StructuredText trong `PID.xml` và `MHJ-PLC-Lab-Function-S71200.xml`, các cú pháp SCL chuẩn của TIA Portal V18 gồm:

*   **Phép gán (Assignment):**
    `Biến := Biểu_thức;`
    *   Gán biến cục bộ: `err2 := error;`
    *   Gán biến toàn cục (DB): `"PI_DB".kp := 1.0;` (Tên DB toàn cục phải đặt trong dấu nháy kép `""`).
*   **Cấu trúc điều kiện IF-THEN-END_IF:**
    ```pascal
    IF điều_kiện THEN
        // Logic thực thi khi đúng
    ELSIF điều_kiện_khác THEN
        // Logic thực thi khi điều kiện khác đúng
    ELSE
        // Logic thực thi khi sai
    END_IF;
    ```
*   **Vòng lặp FOR-TO-BY-DO-END_FOR:**
    ```pascal
    FOR biến_chạy := giá_trị_đầu TO giá_trị_cuối DO
        // Logic lặp
    END_FOR;
    ```
*   **Gọi hàm hệ thống và chuyển đổi kiểu:**
    *   Hàm trị tuyệt đối: `ABS(giá_trị)`
    *   Chuyển kiểu Real sang DInt: `REAL_TO_DINT(giá_trị_real)`
*   **Ngắt thực thi hàm:**
    *   Lệnh `RETURN;` dùng để thoát sớm khỏi FC/FB/OB.

---

## 6. Cảnh Báo Quan Trọng Khi Phát Triển Dự Án Maggi

> [!WARNING]
> **Không sao chép thuật toán PID thủ công từ `PID.xml`:**
> Tệp `PID.xml` trong dự án mẫu chứa thuật toán PID tự tính toán bằng công thức toán học rời rạc (`u := (error * kp) + (integralop * (ki / 10)) ...`). 
> Đối với dự án Maggi SCL-first, **bắt buộc** phải sử dụng khối công nghệ chuẩn **`PID_Compact` Version 1.2** của Siemens. Ta chỉ dùng `PID.xml` để học cú pháp viết SCL, tuyệt đối không copy thuật toán toán học này vào code chính.

> [!CAUTION]
> **Không sử dụng PEEK và POKE:**
> Khối `MHJ-PLC-Lab-Function-S71200.xml` sử dụng các lệnh đọc ghi trực tiếp bộ nhớ vật lý `PEEK` và `POKE` (ví dụ: `PEEK(area := 16#82, dbNumber := 0, byteOffset := 511)`). 
> Phương pháp này truy cập gián tiếp qua địa chỉ con trỏ thô, phá vỡ tính bao đóng và an toàn kiểu dữ liệu của PLC. Trong dự án Maggi, cấu trúc dữ liệu đã được hoạch định rõ ràng qua UDT và DB, do đó **nghiêm cấm** sử dụng `PEEK`/`POKE` để tránh lỗi tràn bộ nhớ và khó giải trình trong nghiệm thu.

---

## 7. Các Điểm Áp Dụng Và Không Áp Dụng Cho Dự Án Maggi SCL

### Các điểm ÁP DỤNG cho Maggi:
1.  **Viết SCL thuần túy cho logic nghiệp vụ:** Sử dụng đầy đủ các cú pháp gán `:=`, cấu trúc `IF-THEN`, vòng lặp `FOR`, và ngắt `RETURN` để xây dựng máy trạng thái (state machine/sequencer) cho quy trình trộn Maggi.
2.  **Truy cập DB toàn cục chuẩn tắc:** Sử dụng cú pháp `"Tên_DB".Tên_Biến` có nháy kép cho các DB toàn cục (`"DB_Operation"`, `"DB_Recipe"`, v.v.) để đảm bảo tính tường minh.
3.  **Khởi tạo biến rõ ràng:** Khai báo giá trị khởi động (`StartValue`) trực tiếp cho các biến cấu trúc trong tệp UDT.

### Các điểm KHÔNG ÁP DỤNG cho Maggi:
1.  **Không tự viết giải thuật PID:** Như đã nêu ở trên, phối hợp điều khiển gia nhiệt bồn 2 và bồn 4 phải gọi trực tiếp khối công nghệ `PID_Compact` Siemens.
2.  **Không dùng PEEK/POKE:** Toàn bộ bản đồ I/O vật lý được map tường minh qua `DB_RealIO_Map.scl`. Không sử dụng địa chỉ thô hay đọc ghi gián tiếp.
3.  **Không viết mã trực tiếp trong file XML:** Tất cả các khối được quản lý dưới dạng mã nguồn `.scl` thuần văn bản để thuận tiện cho việc kiểm soát phiên bản (Git) và biên dịch.

---

## 8. Đối Chiếu Với Hệ Thống Skeleton SCL Hiện Tại Của Maggi

Chúng tôi tiến hành đối chiếu cấu trúc hiện tại của các file `projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/*.scl` và `projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/db/*.scl` với các phát hiện từ dự án mẫu:

### Điểm skeleton đang giống style TIA thật:
1.  **Định dạng Source SCL:** Cấu trúc định nghĩa UDT (`TYPE ... END_TYPE`) và DB (`DATA_BLOCK ... END_DATA_BLOCK`) trong các file skeleton hoàn toàn khớp với định dạng mã nguồn SCL ngoài mà TIA Portal chấp nhận khi import.
2.  **Cấu hình tối ưu hóa:** Sử dụng thuộc tính `{ S7_Optimized_Access := 'True' }` cho các DB nội bộ (`DB_Recipe`, `DB_Operation`, `DB_HMI`) và `{ S7_Optimized_Access := 'False' }` cho `DB_Comms` đúng với quy tắc truyền thông Modbus TCP.

### Điểm vẫn cần TIA Portal import/compile kiểm chứng thực tế:
1.  **Khởi tạo kiểu truyền thông hệ thống:** Sự tồn tại của kiểu dữ liệu `TCON_IP_v4` trong `DB_Comms.scl` cần kiểm tra xem TIA Portal có nhận dạng được ngay khi import hay không (đòi hỏi phải kéo một block truyền thông Modbus vào trước).
2.  **Trình tự biên dịch:** Cần kiểm chứng quá trình biên dịch tuần tự trên TIA thực tế: Import UDT trước $\rightarrow$ DB $\rightarrow$ FB/FC.

### Đề xuất hiệu chỉnh giá trị khởi tạo trong `DB_Recipe.scl` (ĐỀ XUẤT - CHƯA SỬA):
Trong tệp `DB_Recipe.scl` hiện tại, phần khởi tạo giá trị được viết như sau:
```pascal
BEGIN
   Default_Recipe.SP_Nuoc_Bon1 := 100.0;
   Default_Recipe.SP_Nuoc_Bon2 := 120.0;
   ...
END_DATA_BLOCK
```
*   **Vấn đề rủi ro:** Gán giá trị khởi đầu cho từng trường con của một Struct lồng trong khối `BEGIN` của DB nguồn ngoài đôi khi bị trình biên dịch SCL của TIA Portal báo lỗi parser hoặc không áp dụng đúng giá trị mặc định.
*   **Đề xuất tối ưu:** 
    1. Do tất cả các thuộc tính của `UDT_Recipe` đã được gán sẵn giá trị mặc định lúc định nghĩa ở tệp [UDT_Recipe.scl](file:///d:/AI_Agent_PLC_LADDER_ONLY/projects/Mixing_Nuoc_Tuong_Maggi_2026_SCL/udt/UDT_Recipe.scl) (ví dụ: `SP_Nuoc_Bon1 : Real := 100.0;`), khi khai báo `Default_Recipe : "UDT_Recipe";` trong DB, TIA Portal sẽ tự động lấy các giá trị mặc định này làm giá trị khởi động.
    2. Ta có thể **lược bỏ hoàn toàn** các dòng gán thủ công này trong khối `BEGIN` của `DB_Recipe.scl` để mã nguồn sạch hơn và giảm thiểu tối đa lỗi khi import.
    3. Nếu cần nạp lại công thức mặc định lúc Runtime, việc gán này nên được thực hiện bằng lệnh gán cấu trúc động trong logic SCL (ví dụ: `"DB_Recipe".Active := "DB_Recipe".Default_Recipe;` hoặc gọi ở `FirstScan` (OB100)).
