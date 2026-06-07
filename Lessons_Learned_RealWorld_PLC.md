# KINH NGHIỆM THỰC TẾ & BÀI HỌC THIẾT KẾ PLC (Real-world Lessons Learned)

Tài liệu này đúc kết các kinh nghiệm kỹ thuật thực tế, nguyên tắc thiết kế an toàn hệ thống (Interlock/E-Stop), tối ưu hóa chu kỳ quét PLC (Scan Cycle) và xử lý môi trường tự động hóa TIA Openness đúc kết từ dự án Chưng cất tinh dầu Tràm gió. 

Mọi AI Agent hoặc kỹ sư làm việc trên workspace này **bắt buộc phải đọc và tuân thủ các nguyên tắc thiết kế dưới đây**.

---

## 1. NGUYÊN TẮC AN TOÀN VÀ KHÓA LIÊN ĐỘNG (Safety & Interlock Principles)

### 🔴 Chốt trạng thái E-Stop HMI (Emergency Stop Latching)
*   **Vấn đề thực tế:** Nút dừng khẩn cấp trên SCADA (HMI_EStop) là dạng nút nhấn ảo. Nếu chỉ gán trực tiếp tiếp điểm thường đóng (NC) thì khi người vận hành nhả tay ra trên giao diện, E-Stop sẽ tự động mất tác dụng. Điều này vi phạm nghiêm trọng tiêu chuẩn an toàn.
*   **Nguyên tắc thiết kế:** 
    *   Tạo ra một tag chốt nhớ trạng thái: `EStop_HMI_Latch` (%M).
    *   Khi nhấn E-Stop trên SCADA (`Nut_EStop_HMI` = TRUE) $\rightarrow$ Lập tức **SET** `EStop_HMI_Latch`.
    *   Cờ chốt `EStop_HMI_Latch` **chỉ được phép RESET** khi và chỉ khi: Nút nhấn E-Stop trên SCADA đã nhả ra (`NOT Nut_EStop_HMI`) **VÀ** người vận hành nhấn nút **Reset** (`bReset_Yeu_Cau`).

### 🔒 Không tự động xóa lỗi (No Auto-Clear Faults Policy)
*   **Vấn đề thực tế:** Hệ thống cũ tự động chuyển trạng thái chính (`Main_State`) từ trạng thái lỗi (State 90) về trạng thái chờ (State 0 - IDLE) ngay khi lỗi vật lý vừa biến mất (ví dụ: nhiệt độ giảm xuống dưới ngưỡng báo động). Hành vi này cực kỳ nguy hiểm vì lỗi có thể chập chờn gây hư hỏng thiết bị hoặc gây tai nạn cho người vận hành đang sửa máy.
*   **Nguyên tắc thiết kế:** 
    *   **Bắt buộc nhấn Reset thủ công:** Khi PLC đã trip vào trạng thái lỗi (`Main_State = 90`), hệ thống phải khóa cứng tại đây.
    *   Chỉ cho phép thoát trạng thái lỗi về IDLE khi: Người vận hành nhấn nút **Reset HMI** (`bReset_Yeu_Cau`) **VÀ** tất cả các lỗi hệ thống/liên động vật lý đã được giải quyết triệt để (`NOT Loi_He_Thong`).

### 🔑 Khóa trạng thái hoạt động của nút Reset (Reset State Lockout)
*   **Vấn đề thực tế:** Nút nhấn Reset trên SCADA có thể gửi xung lệnh bất kỳ lúc nào. Nếu không khóa trạng thái, xung Reset có thể làm xáo trộn các bước GRAFCET hoạt động bình thường (Step 1/2/3).
*   **Nguyên tắc thiết kế:** 
    *   Nút Reset giải phóng lỗi trạng thái hệ thống chỉ được phép hoạt động khi và chỉ khi hệ thống đang ở trạng thái lỗi (`Main_State = 90`).
    ```pascal
    // Logic an toàn trong FC_Control_Program
    IF Main_State = 90 AND bReset_Yeu_Cau AND NOT Loi_He_Thong THEN
        Main_State := 0; // Trở về IDLE an toàn
    END_IF;
    ```

---

## 2. TỐI ƯU HÓA CHU KỲ QUÉT PLC (Scan Cycle & Network Execution Order)

*   **Vấn đề thực tế:** Khi nhấn Reset để giải phóng E-Stop HMI, nếu network tính toán lệnh dừng khẩn cấp tổng hợp (`Nut_EStop_Cmd`) được đặt *trước* các network thực hiện SET/RESET cờ chốt `EStop_HMI_Latch`, hệ thống sẽ bị trễ đúng **1 chu kỳ quét (scan cycle)**. Điều này có thể gây ra hiện tượng xung đột tín hiệu tạm thời hoặc PLC trip giả ở chu kỳ đó.
*   **Nguyên tắc thiết kế:** Trong khối xử lý đầu vào (`FC_Input_Model`), thứ tự thực thi của các mạng (network) phải sắp xếp tuần tự và tối ưu như sau:
    1.  **Cập nhật lệnh Reset** (`bReset_Yeu_Cau = Nut_Reset_HMI`).
    2.  **SET cờ chốt** `EStop_HMI_Latch` khi kích hoạt dừng khẩn SCADA (`Nut_EStop_HMI` = TRUE).
    3.  **RESET cờ chốt** `EStop_HMI_Latch` khi có lệnh Reset và nút nhấn dừng khẩn đã nhả (`bReset_Yeu_Cau AND NOT Nut_EStop_HMI`).
    4.  **Tính toán lệnh dừng khẩn cấp tổng hợp cuối cùng** (`Nut_EStop_Cmd = (Nut_EStop OR bCheDoMoPhong) AND NOT EStop_HMI_Latch`).
    *   *Kết quả:* Lệnh `Nut_EStop_Cmd` luôn phản ánh trạng thái mới nhất của cờ chốt ngay trong cùng một chu kỳ quét mà không bị trễ.

---

## 3. CHUẨN ĐOÁN AN TOÀN TRÊN SCADA (WinCC Safety Diagnostics Mapping)

Để SCADA WinCC hiển thị chính xác và trực quan trạng thái liên động của hệ thống, bắt buộc tích hợp tag số nguyên chuyên dụng tên là **`HMI_AnToan_Status`** (%MW) kết hợp với bảng WinCC Text list `TL_Chuan_Doan_AnToan`.

### Bảng phân cấp ưu tiên (Priority Mapping):
Giá trị của tag được gán theo thứ tự ưu tiên từ cao xuống thấp như sau:
1.  **4** = `[ESTOP ACTIVE]`: Nút dừng khẩn cấp bị nhấn! Hệ thống bị khóa cứng! (Khi cờ chốt `Estop_Active` hoặc `EStop_HMI_Latch` = TRUE).
2.  **3** = `[KHÓA AN TOÀN]`: Liên động bảo vệ đã kích hoạt! Các thiết bị đã ngắt! (Khi có bất kỳ lỗi trip vật lý nào như mức nước quá cao, áp suất quá cao, nhiệt độ quá cao).
3.  **1** = `[CẢNH BÁO MỨC NƯỚC]`: Mức nước bình Florentine đang vượt ngưỡng đặt!
4.  **2** = `[CẢNH BÁO NHIỆT/ÁP]`: Nhiệt độ hoặc áp suất đang tăng cao, kiểm tra ngay!
5.  **0** = `[AN TOÀN]`: Hệ thống hoạt động bình thường, không có cảnh báo.

### Cách lập trình LAD tối ưu:
Sử dụng đặc điểm quét tuần tự của PLC (quét từ trên xuống dưới, giá trị cuối cùng ghi đè lên giá trị trước đó) để lập trình ưu tiên trong LAD của `FC_HMI_Animation_Status`:
*   *Network 1:* Gán mặc định `HMI_AnToan_Status = 0`.
*   *Network 2:* Nếu có cảnh báo Nhiệt/Áp $\rightarrow$ Gán `HMI_AnToan_Status = 2`.
*   *Network 3:* Nếu có cảnh báo Mức nước $\rightarrow$ Gán `HMI_AnToan_Status = 1`.
*   *Network 4:* Nếu có lỗi hệ thống liên động $\rightarrow$ Gán `HMI_AnToan_Status = 3`.
*   *Network 5:* Nếu E-Stop hoạt động $\rightarrow$ Gán `HMI_AnToan_Status = 4`.
*   *Ý nghĩa:* Cách viết này cực kỳ gọn, không cần dùng các tiếp điểm khóa chéo phức tạp, giá trị ưu tiên cao hơn sẽ tự động ghi đè lên giá trị thấp hơn vào cuối chu kỳ quét.

---

## 4. KHẮC PHỤC LỖI HỆ THỐNG VÀ PHẦN MỀM (Troubleshooting & TIA Openness Rules)

### 🧟 Tiến trình chạy ngầm TIA Portal (Zombie Processes Lockout)
*   **Vấn đề thực tế:** Khi chạy các công cụ C# kết nối Openness API (như `AddDiagnosticTags.exe` hay `Agent_TIA_Importer_Generic.exe`), chương trình có thể báo lỗi hoặc bị treo cứng không thể kết nối. Nguyên nhân thường do có các tiến trình TIA Portal zombie chạy ngầm trong Windows (không có cửa sổ hiển thị giao diện nhưng vẫn giữ lock file project).
*   **Giải pháp xử lý:**
    *   Mở PowerShell và chạy lệnh kiểm tra các tiến trình Siemens:
        ```powershell
        Get-Process | Where-Object {$_.ProcessName -like "*Siemens*"} | Select-Object Id, ProcessName, MainWindowTitle
        ```
    *   Nếu phát hiện các tiến trình không có `MainWindowTitle` (ID zombie), tiến hành tắt bằng Taskkill hoặc mở Task Manager tắt thủ công.
    *   Luôn đảm bảo chạy công cụ Openness với quyền **Administrator** nếu TIA Portal chính đang chạy dưới quyền Administrator để tránh lỗi từ chối truy cập (Access Denied).

### 🔠 Lỗi hiển thị Tiếng Việt có dấu trên Windows Console
*   **Vấn đề thực tế:** Khi chạy công cụ Python hoặc C# để đọc xuất bảng tag hoặc chỉnh sửa tài liệu, các ký tự Tiếng Việt có dấu có thể bị lỗi font hoặc báo lỗi encoding (ví dụ: lỗi biên dịch `cp1252.py` hay lỗi hiển thị dấu `?` trong đường dẫn thư mục `học tập`).
*   **Giải pháp xử lý:**
    *   Trong các script Python, luôn cấu hình lại chuẩn đầu ra `sys.stdout` ngay từ đầu:
        ```python
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        ```
    *   Trong các công cụ C#, luôn sử dụng `Encoding.UTF8` khi đọc viết file và đảm bảo cấu hình ngôn ngữ `en-US` hoặc `vi-VN` phù hợp trong project TIA Portal để giữ nguyên tính toàn vẹn của chuỗi ký tự Unicode có dấu.
