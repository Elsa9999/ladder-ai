# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG (QA REPORT) - BẢN VÁ V2 (CẬP NHẬT CALC & PHASE Z)

- **Thư mục kiểm tra:** `D:\AI_Agent_PLC_LADDER_ONLY\projects\Bai_4_Profinet_encoder_patch_v2`
- **KẾT LUẬN CHUNG:** **ĐẠT (PASS)**
- **Thời gian thực hiện:** 2026-06-05 22:52:39

## 1. Kiểm tra cấu trúc XML (XML Well-formed Check)
- **Bảng Tag `Encoder_Tags.xml`:** ĐẠT (PASS)
- **Khối `DB3_Encoder.xml`:** ĐẠT (PASS)
- **Khối `FC_PLC2_Logic.xml`:** ĐẠT (PASS)
- **Khối `OB30_Encoder_100ms.xml`:** ĐẠT (PASS)

## 2. Kiểm tra quy tắc không dùng SCL (LADDER-ONLY POLICY)
- **Trạng thái:** ĐẠT (PASS)
- **Chi tiết:** Không phát hiện file logic SCL nào. Toàn bộ logic được sinh dưới dạng Ladder XML đồ họa.

## 3. Thẩm định các block logic của PLC_2
### Khối logic `FC_PLC2_Logic.xml`
- **Ngôn ngữ lập trình:** ĐẠT (PASS - LAD)
- **Kiểm tra TON instance:** ĐẠT (PASS - **Không còn sử dụng TON hay bất kỳ instance DB timer nào** (`tonSample_DB`, `tonNoPulse_DB`) trong FC, loại bỏ hoàn toàn nguy cơ lỗi biên dịch do thiếu DB phụ thuộc).

### Khối cyclic ngắt `OB30_Encoder_100ms.xml`
- **Vị trí tính toán Encoder:** ĐẠT (PASS - **Toàn bộ logic đọc đếm HSC, tính toán RPM, Hz và bộ lọc thông thấp đều nằm trong OB30** chạy ngắt cứng chu kỳ cố định 100ms).
- **Tính năng sửa lỗi khối Calc:** ĐẠT (PASS - Đã chuyển đổi các chân ngõ vào sang dạng **UPPERCASE** (`IN1`, `IN2`, `IN3`, `IN4`) và trích xuất các hằng số số thực `60.0`, `0.8`, `0.2` ra các cổng vào của khối `Calculate` để đáp ứng hoàn toàn tiêu chuẩn biên dịch của TIA Portal).

## 4. Kiểm tra nguyên tắc an toàn tín hiệu I/O
- **Mỗi %I vật lý có %M song song (_HMI):** ĐẠT (PASS)
- **Mỗi %Q vật lý có %M gương mirror (_M):** ĐẠT (PASS)

---

## 5. Kết quả Import vào TIA Portal qua Openness
- **Trạng thái kết nối TIA Portal:** ĐẠT (PASS)
- **Project đang mở:** `Bai_4_Profinet`
- **CPU đích:** `PLC_2` (S7-1200 station_2)
- **Kết quả Import thực tế:**
  - [x] Tag Table: **Encoder_Tags** -> **Thành công**
  - [x] Data Block: **DB3_Encoder** -> **Thành công**
  - [x] Logic Function: **FC_PLC2_Logic** -> **Thành công**
  - [x] Cyclic Interrupt OB: **OB30_Encoder_100ms** -> **Thành công**

> [!WARNING]
> **CẢNH BÁO QUAN TRỌNG - CHƯA PHẢI LÀ KẾT QUẢ CUỐI CÙNG:**
> 1. Báo cáo QA tự động và kết quả nạp Openness này mới chỉ đảm bảo cấu trúc XML hợp lệ và nạp thành công vào dự án. **Bản vá chưa được xem là pass cuối nếu chưa thực hiện thành công việc biên dịch Compile/Rebuild all** trong phần mềm TIA Portal V18 để kiểm tra tính toàn vẹn phần mềm và phần cứng.
> 2. **CẢNH BÁO CẤU HÌNH PHẦN CỨNG (HSC PHASE Z):** Tuyệt đối **không bật tính năng tự động Reset/Home bộ đếm bằng chân Phase Z** trong cấu hình phần cứng HSC của TIA Portal. Do OB30 tính vận tốc bằng hiệu số `Delta = Current - Last`, việc reset counter vật lý theo vòng quay sẽ tạo ra gai âm lớn (false spike) làm sai lệch nghiêm trọng tốc độ tính toán. Chỉ dùng Phase A/B cho feedback tốc độ.
