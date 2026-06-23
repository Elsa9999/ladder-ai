# PROMPT SỬA VÒNG 2 SAU REVIEW ĐỘC LẬP

Bạn đang tiếp tục sửa dự án PLC/LAD:

`D:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026`

Hãy đọc:

- `D:\AI_Agent_PLC_LADDER_ONLY\AGENTS.md`
- `D:\AI_Agent_PLC_LADDER_ONLY\prompts\Fix_Mixing_Nuoc_Tuong_Maggi_PLC_2026.md`
- Toàn bộ mã nguồn hiện tại và diff đang có.

Không làm HMI. Không hoàn tác thay đổi của người khác. Không commit. Không chỉ sửa simulator hoặc tài liệu.

## Kết quả review hiện tại

Bản sửa vòng 1 **chưa đạt**:

- `python harness\run_acceptance.py` đang FAIL ở QA.
- Test Python PASS nhưng mô phỏng nhiều logic không tồn tại trong Ladder XML.
- TIA từng compile PLC1/PLC2 với 0 errors, nhưng đó không phải bằng chứng cho source mới nhất; `Main` PLC1 còn có lúc không export được do inconsistent.

Bạn phải sửa trực tiếp generator/thư viện, sinh lại XML, import lại TIA và chứng minh bản mới nhất.

## P0. Sửa trùng instance MB_CLIENT

Hiện tại hai mạng Write và Read cùng gọi:

`MB_CLIENT_DB`

tại `prepare_tia_import_sets.py`.

Yêu cầu:

1. Tuyệt đối không gọi cùng một instance FB asynchronous nhiều lần trong một scan với bộ tham số khác nhau.
2. Chọn một trong hai giải pháp hợp lệ:
   - Một MB_CLIENT call duy nhất, dùng state machine chọn MODE/ADDR/LEN/PTR; hoặc
   - Hai call với hai instance DB global độc lập thực sự tồn tại trong TIA.
3. Nếu dùng hai instance, phải bảo đảm `MB_CLIENT_DB_1` là GlobalVariable, instance DB thật được tạo/import trong TIA, không phải LocalVariable trong OB.
4. Không phát REQ mới khi instance đang BUSY.
5. Write/Read chỉ chuyển bước sau DONE hoặc ERROR.
6. `Agent_QA_Validator.py` phải PASS, không được vô hiệu hóa rule multi-call để che lỗi.

Tiêu chí:

- Trong XML import mới, không có một instance DB xuất hiện ở hơn một MB_CLIENT call.
- TIA compile 0 errors.
- `Main` PLC1 export ngược thành công.

## P0. Đưa phân xử bồn chứa vào Ladder thật

Các tag owner đã được khai báo nhưng hiện chỉ được dùng trong `scratch/test_plc_logic.py`. `FC_Bon_Chua_Loc` vẫn:

- Bật bơm Nhánh 1 chỉ theo cờ hoàn thành.
- Bật lệnh bơm Nhánh 2 chỉ theo cờ hoàn thành.
- Cho hai nhánh cùng chạy nếu hoàn thành đồng thời.
- Kết thúc nhận dịch bằng `AI_BonChua_Nhan_Dich_Xong_HMI`.

Yêu cầu sửa trong `build_storage()` / `FC_Bon_Chua_Loc.xml`:

1. Chỉ cấp owner khi cụm bồn chứa hoàn toàn rảnh.
2. Nếu hai nhánh cùng hoàn thành, Nhánh 1 được ưu tiên.
3. Nhánh 2 phải tiếp tục chờ; không được xóa cờ hoàn thành khi chưa được cấp owner.
4. `AI_Pump3264_Chuyen_Nhanh1` chỉ chạy khi:
   - Step nhận dịch active.
   - Owner Nhánh 1 active.
   - Nhánh 1 hoàn thành.
   - Không Stop/E-Stop/lỗi.
5. `AI_Pump3265_Chuyen_Nhanh2_Cmd` chỉ chạy khi:
   - Step nhận dịch active.
   - Owner Nhánh 2 active.
   - Nhánh 2 hoàn thành.
   - Không Stop/E-Stop/lỗi.
6. Kết thúc nhận dịch tự động:
   - Nhánh 1: mức Bồn 2 xuống ngưỡng cạn hợp lệ.
   - Nhánh 2: PLC1 nhận `Done_Discharge2` từ PLC2.
7. `Done_Discharge2` phải được map đầy đủ:
   - PLC2: `AI_PLC2_Xa_Bon4_Xong` → holding register.
   - PLC1 receive DB → `AI_PLC2_Xa_Bon4_Xong_Nhan`.
8. HMI flag chỉ được dùng như override mô phỏng tùy chọn, không phải điều kiện bắt buộc.
9. Chỉ xóa owner khi nhánh tương ứng đã xả xong và storage chuyển sang giải nhiệt.
10. Stop/E-Stop/lỗi phải xóa owner và dừng cả hai lệnh bơm.

Tiêu chí XML:

- `FC_Bon_Chua_Loc.xml` phải thật sự chứa `AI_BonChua_Owner_Nhanh1` và `AI_BonChua_Owner_Nhanh2`.
- Mạng bơm phải chứa owner và step nhận dịch.
- Mạng chuyển giải nhiệt phải chứa điều kiện hoàn thành tự động của đúng owner.

## P0. Sửa dry-run trong Ladder thật

Hiện tại Ladder vẫn chốt lỗi tức thời:

```text
Pump ON + Level <= 0.5 → Set Loi_Dry_Run
```

Trong khi simulator tự thêm debounce 2 giây. Đây là sai lệch nghiêm trọng.

Yêu cầu:

1. Dùng `AI_Timer_DryRun_Bon2` và `AI_Timer_DryRun_Bon4` thật trong Ladder.
2. Hoàn thành xả bình thường phải dừng bơm/đóng van trước khi có thể chốt dry-run.
3. Không báo dry-run khi mức vừa xuống ngưỡng cạn trong một chu trình xả hợp lệ.
4. Dry-run chỉ báo khi:
   - Bơm vẫn bị yêu cầu chạy bất thường sau trạng thái cạn; hoặc
   - Bơm chạy khi bồn đã cạn mà không nằm trong chuyển tiếp hoàn thành hợp lệ.
5. Dùng debounce hợp lý, ví dụ `T#2S`.
6. Sắp xếp network/order hoặc thêm cờ completion sao cho scan PLC không latch lỗi trước mạng dừng bình thường.
7. Stop/E-Stop/lỗi phải reset IN của timer và dừng bơm.

Tiêu chí XML:

- `FC_PLC1_Mixing.xml` chứa TON instance `AI_Timer_DryRun_Bon2`.
- `FC_PLC2_Mixing.xml` chứa TON instance `AI_Timer_DryRun_Bon4`.
- Không còn mạng immediate `Pump + Level low → SetCoil DryRun`.

## P0. Sửa PID Bồn 4 trong thanh trùng

Hiện tại mạng:

`Reset CV hơi Bồn 4 khi không chạy PID`

vẫn kiểm tra:

`NC AI_PLC2_Step_Bon4_PID_Mo_Phong`

Step này đã reset khi chuyển sang State 31, nên CV vẫn bị ghi về 0 trong thanh trùng.

Yêu cầu:

1. Cleanup CV Bồn 4 phải kiểm tra `NC AI_PID_Bon4_Enable`.
2. Trong State 31, PID Enable phải giữ TRUE đến khi hết timer thanh trùng.
3. Không network nào trong FC ghi `AI_CV3216_Hoi_Bon4 = 0.0` khi PID Enable còn TRUE, trừ Stop/E-Stop/lỗi.
4. Kiểm tra Bồn 2 theo cùng nguyên tắc.

Tiêu chí XML:

- Network cleanup CV Bồn 4 chứa `AI_PID_Bon4_Enable`, không chứa Step PID.
- Test XML xác nhận điều này trực tiếp.

## P1. Tổng hợp lỗi PLC2

Hiện `AI_PID_Bon4_Error` được tạo và reset nhưng không được đưa vào `AI_PLC2_Loi_Tong`.

Yêu cầu:

- Thêm `AI_PID_Bon4_Error` vào tổng lỗi PLC2.
- Lỗi MB_SERVER/heartbeat tiếp tục đi qua lỗi truyền thông.
- Kiểm tra `AI_VFD_Bon2_MBCL_Error` và `AI_VFD_Bon2_MB_Error`; lỗi khởi tạo/truyền thông VFD cần đi vào lỗi phù hợp của PLC1.
- Không reset lỗi liên tục khi nguyên nhân vẫn tồn tại.

## P1. Sửa đại lượng dosing/totalizer

Hiện AI chỉ thêm FQ3205/FQ3210 như input `%ID` mới và còn MOVE `0.0` vào tag input. Đây không phải totalizer đúng nghĩa.

Yêu cầu:

1. Không ghi MOVE vào input vật lý `%I/%ID`.
2. Xác định rõ:
   - Nếu FQ là tín hiệu tổng lượng thật: chỉ đọc, không reset trực tiếp.
   - Nếu chỉ có FT lưu lượng tức thời: tạo biến tổng lượng nội bộ `%M/DB` và tích phân theo chu kỳ xác định.
3. Dùng mô hình nhất quán cho Bồn 1–4.
4. Biến tích lũy nội bộ được reset khi bắt đầu bước dosing, không reset liên tục trong mọi scan ngoài dosing.
5. So sánh setpoint L với tổng lượng L, không so với flow rate.
6. Không tự ý cấp thêm địa chỉ input phần cứng nếu đề/I/O map không có cảm biến đó.

## P1. Làm test bám Ladder, không bịa logic

`scratch/test_plc_logic.py` hiện tự cài owner và timer dry-run nên PASS dù XML không có.

Yêu cầu:

1. Simulator chỉ được mô phỏng đúng logic thật trong generator.
2. Thêm một verifier mới, ví dụ:

`scratch/verify_mixing_runtime_fixes.py`

Verifier phải parse XML vừa sinh và FAIL nếu:

- Hai MB_CLIENT dùng chung instance.
- `FC_Bon_Chua_Loc` không tham chiếu owner.
- Mạng bơm thiếu owner hoặc thiếu step nhận dịch.
- `Done_Discharge2` không được map hai chiều.
- FC PLC1/PLC2 không có TON dry-run.
- Cleanup CV Bồn 4 dùng Step PID thay vì PID Enable.
- PID Bồn 4 không nằm trong tổng lỗi PLC2.
- Có MOVE ghi vào tag input vật lý FQ/FT.

3. Thêm verifier này vào `harness/run_acceptance.py`.
4. Không đọc `post_import_export` cũ để tuyên bố bản mới đạt.
5. `verify_post_import_export.py` phải nhận đường dẫn export mới hoặc kiểm tra timestamp để từ chối bản export cũ.

## P2. Giữ phạm vi gọn

- Không thêm hoặc sửa HMI.
- Không thêm class HMI mới vào `Agent_LAD_Library.py` trong nhiệm vụ PLC này.
- Không refactor lan rộng những phần không liên quan.
- Xóa trailing whitespace do thay đổi mới gây ra.
- Tiêu đề Network mới phải là tiếng Việt có dấu.
- Tag/DB mới phải ASCII và bắt đầu bằng `AI_`.

## Quy trình bắt buộc sau khi sửa

Chạy theo đúng thứ tự:

```powershell
python projects\Mixing_Nuoc_Tuong_Maggi_2026\generate_mixing_project.py
python projects\Mixing_Nuoc_Tuong_Maggi_2026\prepare_tia_import_sets.py
python scratch\verify_mixing_runtime_fixes.py
python scratch\validate_tia_imports.py
python scratch\verify_clean.py
python scratch\test_plc_logic.py
python harness\run_acceptance.py
git diff --check
```

Tất cả phải PASS.

## Xác nhận TIA Portal bắt buộc

TIA Portal hiện có thể đang mở project:

`cuocthi_tdh`

Thực hiện an toàn:

1. Export/backup trước khi import.
2. Import tag/DB/block mới nhất cho cả PLC1 và PLC2.
3. Compile cả hai PLC:
   - PLC1: 0 errors.
   - PLC2: 0 errors.
4. Export ngược cả hai PLC vào thư mục mới có timestamp, không ghi đè export cũ.
5. Chạy verifier trên export mới.
6. Xác nhận `Main.xml` của PLC1 export thành công; nếu block inconsistent hoặc export fail thì nhiệm vụ chưa đạt.

Không được dùng kết quả compile/export ngày 08/06/2026 để chứng minh source ngày 13/06/2026.

## Báo cáo hoàn thành

Khi xong, báo:

1. File đã sửa.
2. Cách sửa từng mục P0/P1.
3. Kết quả từng command.
4. Kết quả compile TIA và số warning.
5. Đường dẫn export TIA mới cùng timestamp.
6. Các rủi ro còn lại.
7. `git diff --stat`.

Sau khi báo cáo, dừng sửa file để reviewer kiểm tra trên một snapshot ổn định.
