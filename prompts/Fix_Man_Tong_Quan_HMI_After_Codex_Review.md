# Fix Man Tong Quan HMI After Codex Review

Bạn là implementation agent chịu trách nhiệm sửa màn hình HMI `Man Tong Quan` trong project:

- Repository: `D:\AI_Agent_PLC_LADDER_ONLY`
- TIA project: `C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18`
- HMI target: `HMI_RT_1`
- Screen source: `scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml`
- Patch script: `scratch\patch_man_tong_quan.py`

Không được chỉ cập nhật báo cáo. Hãy sửa implementation, chạy validation, import vào TIA, compile, rồi re-export readback để chứng minh kết quả.

## Phạm vi bắt buộc

Chỉ sửa hoặc tạo các file liên quan trực tiếp tới HMI `Man Tong Quan`:

- `scratch\patch_man_tong_quan.py`
- `scratch\hmi_export_actual\Hmi.Screen.Man Tong Quan.xml`
- HMI tag table mới dành cho màn hình này
- Script validator HMI chuyên biệt nếu cần
- Báo cáo mapping, task và walkthrough HMI
- Thư mục readback HMI sau import

Không sửa PLC logic, generator, LAD library, importer chung hoặc các file unrelated đang dirty. Không chạy formatter hay rewrite hàng loạt toàn repo.

## P0 - Tạo và xác minh HMI tags

Readback trực tiếp từ TIA cho thấy `HMI_RT_1` hiện chỉ có 3 HMI tags và 0/66 tên tag mà màn hình mới tham chiếu tồn tại.

1. Export và kiểm tra HMI connections hiện có trước khi tạo tag. Không đoán connection.
2. Tạo/import HMI tag table chứa chính xác 66 tag được màn hình sử dụng:
   - 41 tag cho GraphicIOField.
   - 25 tag cho giá trị analog/IOField.
3. Mỗi HMI tag phải có:
   - Tên đúng tuyệt đối với tên được tham chiếu trong screen XML.
   - Data type đúng với PLC tag.
   - PLC address đúng.
   - HMI connection đúng PLC sở hữu tag hoặc đúng cơ chế mirror đã có.
4. Nếu HMI chỉ kết nối PLC1, phải chứng minh các giá trị PLC2 đã được mirror sang PLC1 và dùng address mirror tương ứng. Không tạo tag treo.
5. Sau import, export lại toàn bộ HMI tag tables và kiểm tra tự động rằng `missing == 0` cho 66 screen references.

## P1 - Sửa nhãn cảm biến bị đảo

Theo đề thi, mã đúng là:

- Bồn 3: `LT3213`, `TT3214`.
- Bồn 4: `LT3218`, `TT3219`.

Sửa đồng bộ object name, label và mapping:

- `AI_IO_LT3213` -> `LT3213_Bon3_Eff`, label `LT 32.13`.
- `AI_IO_TT3214` -> `TT3214_Bon3_Eff`, label `TT 32.14`.
- `AI_IO_LT3218` -> `LT3218_Bon4_Eff`, label `LT 32.18`.
- `AI_IO_TT3219` -> `TT3219_Bon4_Eff`, label `TT 32.19`.

Không được giữ các tên sai `AI_IO_LT3214`, `AI_IO_TT3213`, `AI_IO_LT3219`, `AI_IO_TT3218`.

## P1 - Sửa bố cục và phần tử trùng

Màn hình có kích thước `1440x900`.

1. Tái sử dụng hai IOField gốc thay vì đặt phần tử mới đè lên chúng:
   - `I/O field_1` tại `(113,69)` dùng cho FT/FQ3200.
   - `I/O field_2` tại `(300,127)` dùng cho LT3203.
2. Tổng mục tiêu là 25 giá trị analog hiển thị:
   - Tái sử dụng 2 IOField gốc.
   - Chỉ tạo thêm 23 IOField.
   - Tổng số `Hmi.Screen.IOField` sau patch phải là 25, không phải 27.
3. Sửa toàn bộ overlap AI-vs-AI. Các lỗi đã biết:
   - `PI3308` và `FT3309` đang chồng nhau.
   - Unit `bar` của PI3308 đang đè FT3309.
   - Các label/field khu vực bốn bồn và van cấp có nhiều chồng lấn.
4. Sửa toàn bộ out-of-bounds:
   - Unit `%` của `CV Filler` đang kết thúc tại X=1475.
   - Nhãn `Pump 33.62` đang kết thúc tại Y=915.
5. Mọi IOField, unit và label phải nằm hoàn toàn trong `0..1440 x 0..900`.
6. Unit label phải cách cạnh phải IOField đúng 8 px, nhưng phải điều chỉnh cả cụm sang trái nếu gần biên màn hình.
7. Không che valve/pump hoặc phần hiển thị quan trọng. Sau import phải chụp/export ảnh màn hình để kiểm tra trực quan.

## P1 - Mapping GraphicIOField

Giữ đủ 41 GraphicIOField và bind mỗi object chính xác một `ProcessValue` tag.

Validator phải fail nếu:

- Thiếu bất kỳ GraphicIOField nào trong mapping.
- Object name bị trùng.
- Một object có 0 hoặc nhiều hơn 1 ProcessValue binding.
- HMI tag được tham chiếu không tồn tại trong tag table readback.

## Idempotency và backup

1. Giữ bản backup XML gốc riêng biệt và không overwrite.
2. Patch script phải deterministic/idempotent.
3. Chạy patch hai lần liên tiếp; lần thứ hai không được tạo thêm object, thay đổi ID vô cớ hoặc tạo diff mới.
4. Không dùng `max_id + 5000` theo cách khiến ID tăng sau mỗi lần chạy. Dùng ID ổn định hoặc tái sử dụng phần tử hiện có.

## Validation bắt buộc

Tạo một validator HMI chuyên biệt và chạy các kiểm tra sau:

1. XML parse thành công.
2. Không trùng XML ID.
3. Không trùng ObjectName.
4. Đúng 41 GraphicIOField.
5. Đúng 25 IOField tổng cộng.
6. Đúng 81 TextField nếu vẫn giữ 31 device labels + 25 sensor labels + 25 unit labels.
7. Đúng 66 ProcessValue bindings duy nhất.
8. 66/66 referenced HMI tags tồn tại trong tag table re-export từ TIA.
9. Zero AI-vs-AI overlap.
10. Zero out-of-bounds trên màn hình 1440x900.
11. Bốn nhãn LT/TT bồn 3 và 4 khớp tuyệt đối với tag.
12. Patch chạy hai lần cho kết quả không đổi.

## Import và readback TIA

1. Backup project TIA trước khi import.
2. Import HMI tag table trước.
3. Import screen sau khi tags đã tồn tại.
4. Compile HMI target và yêu cầu 0 error.
5. Save project chỉ sau khi import và compile thành công.
6. Re-export:
   - `Man Tong Quan` screen.
   - Tất cả HMI tag tables liên quan.
   - Compile result/log.
7. Chạy validator trên chính file readback, không chỉ trên file chuẩn bị import.

## Báo cáo cuối

Tạo các file có tên rõ ràng, không ghi đè walkthrough PLC cũ:

- `projects\Mixing_Nuoc_Tuong_Maggi_2026\task_hmi_man_tong_quan.md`
- `projects\Mixing_Nuoc_Tuong_Maggi_2026\walkthrough_hmi_man_tong_quan.md`
- `scratch\man_tong_quan_mapping_report.md`

Báo cáo phải ghi đúng một số lượng thống nhất:

- 41 GraphicIOField.
- 25 analog values/IOFields tổng cộng.
- 66 bindings tổng cộng.
- Số HMI tags readback tồn tại: 66/66.
- Kết quả overlap, bounds, idempotency và HMI compile.

Không được tuyên bố “hoàn tất”, “0 lỗi”, “không chồng lấn” hoặc “QA OK” nếu chưa có output kiểm tra tương ứng.

Khi hoàn thành, chỉ báo cáo:

1. File đã thay đổi.
2. HMI connection/address mapping đã dùng.
3. Kết quả validator đầy đủ.
4. Kết quả import + compile HMI.
5. Đường dẫn readback screen/tag tables để Codex review vòng tiếp theo.
