# Báo cáo tích hợp và nâng cấp công cụ TIA Tooling & Modbus TCP

Báo cáo này tóm tắt kết quả phân tích công nghệ từ các kho lưu trữ bên ngoài, nâng cấp bộ công cụ TIA Portal Openness nội bộ, thiết lập quy trình làm việc cho Modbus TCP, và áp dụng thực tế thành công cho dự án `Mixing_Nuoc_Tuong_Maggi_2026` đạt trạng thái QA PASS 100%.

---

## 1. Phân tích các kho lưu trữ mẫu (External Repositories)

### 1.1 Repo `cmariusz/TiaImportExport.VSExt` (MIT License)
* **Ý tưởng học hỏi:**
  * **Độ ưu tiên nạp dữ liệu (Import Dependency Order):** UDTs (PlcUserType/PlcStruct) phải được nạp trước tiên, sau đó đến Tag Tables, rồi mới đến các Blocks (OB/FB/FC/DB) vì các blocks và tags thường tham chiếu trực tiếp đến các kiểu dữ liệu UDT này. Nếu nạp sai thứ tự, TIA Portal sẽ báo lỗi thiếu kiểu dữ liệu và từ chối import XML.
  * **Tìm kiếm thực thể chính xác (Process Selection):** Thay vì tự động kết nối với tiến trình TIA Portal đầu tiên (`TiaPortal.GetProcesses()[0]`), công cụ duyệt qua tất cả các tiến trình đang chạy, tìm dự án đang mở khớp với tên hoặc đường dẫn dự án đích, sau đó tìm CPU theo tên thiết bị (ví dụ: `PLC_1`, `PLC_2`).
  * **Biên dịch & Chẩn đoán lỗi (Compilation & Diagnostics):** Sau khi hoàn thành việc nạp XML, gọi dịch vụ biên dịch thông qua giao diện `ICompilable` của TIA Openness, duyệt qua danh mục tin nhắn biên dịch (`CompilerResult.Messages`) và hiển thị định dạng lỗi chi tiết (Đường dẫn khối, cấp độ Error/Warning, và mô tả).

### 1.2 Repo `Parozzz/TiaUtilities` (GPL License)
* **Ý tưởng học hỏi:**
  * **Cấu trúc SimaticML:** Hiểu cách tổ chức các phân đoạn (Segments), mạng (Networks), các thành phần logic (`Part` như `Contact`, `Coil`, `Add`, `Mul`, `Move`, `MB_CLIENT`, `MB_SERVER`) và cách chúng kết nối dây tín hiệu qua các `Wire` và `IdentCon/NameCon`.
  * **Tham chiếu và Không sao chép:** Toàn bộ mã nguồn GPL được giữ riêng biệt để tham khảo ý tưởng xử lý XML. Không có bất kỳ dòng mã nguồn nào của `TiaUtilities` được sao chép trực tiếp vào thư mục công cụ nội bộ để tránh vi phạm bản quyền phần mềm nguồn mở.

---

## 2. Nâng cấp bộ công cụ nội bộ (Ladder-Only Tooling)

Chúng tôi đã hoàn thành nâng cấp hai công cụ CLI chính tương thích hoàn toàn với TIA Portal V18 Openness và .NET Framework 4.8 (C# 5):

1. **`Agent_TIA_Importer_Generic.cs` / `.exe`:**
   * Tự động quét và kết nối với đúng TIA process chứa PLC cần nạp thông qua tham số CLI.
   * Phân loại tự động các tệp XML trong thư mục nguồn: UDTs, Tag Tables, Blocks, HMI Text/Graphic Lists.
   * Thực hiện nạp theo thứ tự ổn định: **UDTs (Types) -> Tags -> Blocks -> HMI Lists**.
   * Hỗ trợ cờ `"compile"` kích hoạt biên dịch PLC và in lỗi dạng UTF-8 dễ đọc.
   * Có bộ lọc kiểm tra nghiêm ngặt ngăn chặn SCL (Ladder-only policy).

2. **`Export_Device_ByName.cs` / `.exe`:**
   * Lọc và xuất dữ liệu từ đúng dự án đang mở và đúng PLC mục tiêu thông qua tham số dòng lệnh.
   * Giải quyết triệt để lỗi đường dẫn tương đối của TIA Openness bằng cách chuyển đổi thư mục đầu ra thành đường dẫn tuyệt đối thông qua `Path.GetFullPath()`.
   * Xuất các khối blocks, tags, và UDTs ra các thư mục con riêng biệt (`Blocks`, `Tags`, `Types`) rõ ràng.

---

## 3. Tạo tài liệu hướng dẫn xuất XML mẫu Modbus TCP

Chúng tôi đã tạo tài liệu hướng dẫn từng bước cấu hình dự án mẫu Modbus TCP trên TIA Portal V18 tại:
* [MANUAL_STEPS_ModbusTCP.md](file:///d:/AI_Agent_PLC_LADDER_ONLY/examples/TIA_V18_ModbusTCP_MBClient_MBServer/MANUAL_STEPS_ModbusTCP.md)

Tài liệu hướng dẫn chi tiết cách tạo kết nối Client (`MB_CLIENT`), Server (`MB_SERVER`), cấu hình kiểu dữ liệu `TCON_IP_v4`, tổ chức DB Holding Register Standard layout (Non-Optimized), và cách chạy công cụ export để trích xuất XML SimaticML chuẩn làm tham chiếu cho AI.

---

## 4. Áp dụng cho dự án chính (Mixing Nuoc Tuong Maggi 2026)

Toàn bộ truyền thông giữa **PLC1** và **PLC2** đã được chuyển đổi từ S7 GET/PUT sang Modbus TCP:
* **PLC1 (Client):** IP `192.168.0.1`, gọi khối `MB_CLIENT` thông qua một sequencer điều khiển tuần tự bằng biến bước `AI_MB_TCP_iStep` (0: Ghi dữ liệu lệnh sang Server; 1: Đọc dữ liệu trạng thái từ Server về).
* **PLC2 (Server):** IP `192.168.0.2`, lắng nghe ở cổng `502`, gọi khối `MB_SERVER` kết nối trực tiếp với DB Holding Register thô `DB_Modbus_Holding_Register_DB` dạng Standard layout (13 Words).
* **Cơ chế bắt tay chống chồng lệnh (CmdSeq/AckSeq Handshake):** 
  * Khi Client (PLC1) phát hiện cạnh lên của bất kỳ lệnh nào, nó tăng số thứ tự lệnh `CmdSeq` lên 1 và tự động chốt bit lệnh gửi.
  * Server (PLC2) phát hiện `CmdSeq` thay đổi, tạo xung lệnh hiệu dụng 1 scan cho các biến nội bộ, sau đó phản hồi lại số thứ tự lệnh qua `AckSeq = CmdSeq`.
  * Khi Client nhận được `AckSeq == CmdSeq`, nó tự động xóa các cờ chốt lệnh gửi, kết thúc chu trình bắt tay an toàn.
* **Cấu hình động:** Toàn bộ thông số cấu hình của struct `TCON_IP_v4` được gán động bằng lệnh `MOVE` trong mạng khởi tạo (`AI_FirstScan`) của cả hai PLC để đảm bảo tính an toàn của cấu trúc XML khi import vào TIA Portal.
* **Định kiểu So sánh Handshake (Sửa lỗi Type-Mismatch):** Tích hợp từ khóa `"Seq"` vào bộ nhận diện kiểu của thư viện sinh Ladder `Agent_LAD_Library.py`. Nhờ đó, các phép so sánh handshake như `AckSeq == CmdSeq` và `CmdSeq <> Last_CmdSeq` được xuất dưới dạng `SrcType` là `Int` thay vì `Real`, đảm bảo biên dịch chính xác 100%.
* **Định kiểu Hằng số MB_CLIENT (Sửa lỗi Type Constant):** Cập nhật ánh xạ chân hằng số cho khối `MB_CLIENT` trong thư viện sinh mã. Các hằng số điều khiển giờ đây được định kiểu chuẩn xác:
  * `MB_MODE` sử dụng kiểu `USInt` (ví dụ: `0`, `1`).
  * `MB_DATA_ADDR` sử dụng kiểu `UDInt` (ví dụ: `40001`, `40004`).
  * `MB_DATA_LEN` sử dụng kiểu `UInt` (ví dụ: `3`, `10`).
  * Triệt tiêu hoàn toàn cảnh báo ép kiểu hằng số khi biên dịch khối.

---

## 5. Kết quả kiểm tra bắt buộc (QA Status)

Sau khi sinh lại code và phân phối import sets, chúng tôi đã tiến hành kiểm tra bắt buộc:

1. **Khử hoàn toàn GET/PUT:**
   * Tìm kiếm trong toàn bộ các tệp logic XML của `tia_import`: **Không phát hiện bất kỳ khối hoặc biến GET/PUT nào** giữa PLC1 và PLC2.
2. **Khai báo Modbus TCP:**
   * Tìm kiếm trong `PLC_1_Mixing_Import\Main.xml`: **Có sự xuất hiện của khối `MB_CLIENT`** với phiên bản 4.0 và gọi instance `MB_CLIENT_DB`.
   * Tìm kiếm trong `PLC_2_Mixing_Import\Main.xml`: **Có sự xuất hiện của khối `MB_SERVER`** với phiên bản 4.0 và gọi instance `MB_SERVER_DB`.
3. **Kết quả QA Validator:**
   * Thư mục flat output: **QA PASS 100%**
   * Thư mục CPU-level `PLC_1_Mixing_Import`: **QA PASS 100%**
   * Thư mục CPU-level `PLC_2_Mixing_Import`: **QA PASS 100%**
   * Toàn bộ cấu trúc XML đều hợp lệ, không có tag chưa khai báo, đảm bảo an toàn tín hiệu I/O và tính duy nhất của ID/UId.
4. **Dọn dẹp tệp tin dư thừa & tệp tạm:**
   * Đã tích hợp thư viện `shutil` vào phương thức khởi tạo dự án trong `generate_mixing_project.py` để tự động dọn sạch thư mục `output` trước mỗi lần tạo mới. Điều này loại bỏ hoàn toàn các tệp tin dư thừa của cơ chế GET/PUT cũ (`DB_PLC2_Recv_From_PLC1.xml` và `DB_PLC2_Send_To_PLC1.xml`).
   * Xóa bỏ tệp tin tạm không liên quan `scratch/search_exe_calls.py` để giữ trạng thái Git Repo sạch sẽ (Working Tree Clean).
