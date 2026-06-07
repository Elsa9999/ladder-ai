# HƯỚNG DẪN TÍCH HỢP SIEMENS S7-1200: TRUYỀN THÔNG MODBUS RTU & ĐIỀU KHIỂN PID BIẾN TẦN
## MÃ NGUỒN XML LADDER IMPORT TRỰC TIẾP VÀO TIA PORTAL

Tài liệu này lưu trữ mã nguồn XML chuẩn hóa để import trực tiếp vào TIA Portal (định dạng Openness XML) cho 2 giải pháp kỹ thuật cốt lõi đã kiểm thử thành công.

---

### 1. Lỗi truyền thông Modbus kẹt bước & Lỗi "SLF1" biến tần
* **Giải pháp:** Tách chân `DONE` của từng bước `Step0_Done` đến `Step3_Done` và gom bằng cổng OR song song để kích hoạt `MB_Done` tập trung. Việc này loại bỏ hiện tượng các khối `MB_MASTER` ghi đè logic lẫn nhau gây kẹt bước truyền thông.
* **Mã XML Network Ladder (LAD):** Lưu đoạn mã dưới đây thành file `.xml` để import trực tiếp vào khối Block trong TIA Portal.

```xml
<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V17" />
  <SW.Blocks.CompileUnit ID="0" CompositionName="CompileUnits">
    <AttributeList>
      <NetworkSource>
        <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4">
          <Parts>
            <Part Name="Contact" UId="21" />
            <Part Name="Contact" UId="22" />
            <Part Name="Contact" UId="23" />
            <Part Name="Contact" UId="24" />
            <Part Name="Coil" UId="25" />
          </Parts>
          <Wires>
            <Wire UId="26">
              <Powerrail />
              <NameCon UId="21" Name="in" />
              <NameCon UId="22" Name="in" />
              <NameCon UId="23" Name="in" />
              <NameCon UId="24" Name="in" />
            </Wire>
            <Wire UId="27">
              <NameCon UId="21" Name="out" />
              <NameCon UId="22" Name="out" />
              <NameCon UId="23" Name="out" />
              <NameCon UId="24" Name="out" />
              <NameCon UId="25" Name="in" />
            </Wire>
            <Wire UId="28">
              <IdentCon UId="31" />
              <NameCon UId="21" Name="operand" />
            </Wire>
            <Wire UId="29">
              <IdentCon UId="32" />
              <NameCon UId="22" Name="operand" />
            </Wire>
            <Wire UId="30">
              <IdentCon UId="33" />
              <NameCon UId="23" Name="operand" />
            </Wire>
            <Wire UId="31">
              <IdentCon UId="34" />
              <NameCon UId="24" Name="operand" />
            </Wire>
            <Wire UId="32">
              <IdentCon UId="35" />
              <NameCon UId="25" Name="operand" />
            </Wire>
          </Wires>
          <Access Scope="GlobalVariable" UId="31">
            <Symbol>
              <Component Name="Step0_Done" />
            </Symbol>
          </Access>
          <Access Scope="GlobalVariable" UId="32">
            <Symbol>
              <Component Name="Step1_Done" />
            </Symbol>
          </Access>
          <Access Scope="GlobalVariable" UId="33">
            <Symbol>
              <Component Name="Step2_Done" />
            </Symbol>
          </Access>
          <Access Scope="GlobalVariable" UId="34">
            <Symbol>
              <Component Name="Step3_Done" />
            </Symbol>
          </Access>
          <Access Scope="GlobalVariable" UId="35">
            <Symbol>
              <Component Name="MB_Done" />
            </Symbol>
          </Access>
        </FlgNet>
      </NetworkSource>
      <ProgrammingLanguage>LAD</ProgrammingLanguage>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="1" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="2" CompositionName="Items">
            <AttributeList>
              <Culture>vi-VN</Culture>
              <Text>OR logic tập trung DONE từ các bước Modbus để chuyển Step</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
      <MultilingualText ID="3" CompositionName="Title">
        <ObjectList>
          <MultilingualTextItem ID="4" CompositionName="Items">
            <AttributeList>
              <Culture>vi-VN</Culture>
              <Text>Gom xung DONE Modbus Master</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.CompileUnit>
</Document>
```

---

### 2. Công thức mô phỏng phản hồi tốc độ ảo "AD"
* **Giải pháp:** Sử dụng khối tính toán `CALCULATE` định dạng Real để mô phỏng quán tính và phản hồi tốc độ động cơ ảo từ giá trị ngõ ra PID.
* **Công thức áp dụng:** `AD_new = AD_old * 0.99 + PID_Output * 0.1`
* **Cấu hình khối:**
  * `IN1`: `AD` (Địa chỉ `%MD6`)
  * `IN3`: `PID_Output` (Địa chỉ `%MD18`)
  * `OUT`: `AD` (Địa chỉ `%MD6`)
  * Hệ số quán tính `0.99` và hệ số phản hồi PID `0.1` được tích hợp cứng trực tiếp trong biểu thức.
* **Mã XML Network Ladder (LAD) - Khối Calculate:** Lưu đoạn mã dưới đây thành file `.xml` để import trực tiếp.

```xml
<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V17" />
  <SW.Blocks.CompileUnit ID="0" CompositionName="CompileUnits">
    <AttributeList>
      <NetworkSource>
        <FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4">
          <Parts>
            <Part Name="Calculate" UId="21">
              <TemplateValue Name="Card" Type="Cardinality">4</TemplateValue>
              <TemplateValue Name="Formula" Type="String">IN1 * 0.99 + IN3 * 0.1</TemplateValue>
              <TemplateValue Name="DstType" Type="Type">Real</TemplateValue>
            </Part>
          </Parts>
          <Wires>
            <Wire UId="22">
              <Powerrail />
              <NameCon UId="21" Name="en" />
            </Wire>
            <Wire UId="23">
              <IdentCon UId="31" />
              <NameCon UId="21" Name="in1" />
            </Wire>
            <Wire UId="24">
              <IdentCon UId="32" />
              <NameCon UId="21" Name="in3" />
            </Wire>
            <Wire UId="25">
              <IdentCon UId="31" />
              <NameCon UId="21" Name="out" />
            </Wire>
          </Wires>
          <Access Scope="GlobalVariable" UId="31">
            <Symbol>
              <Component Name="AD" />
            </Symbol>
          </Access>
          <Access Scope="GlobalVariable" UId="32">
            <Symbol>
              <Component Name="PID_Output" />
            </Symbol>
          </Access>
        </FlgNet>
      </NetworkSource>
      <ProgrammingLanguage>LAD</ProgrammingLanguage>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="1" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="2" CompositionName="Items">
            <AttributeList>
              <Culture>vi-VN</Culture>
              <Text>Tính toán giá trị phản hồi ảo AD dựa trên ngõ ra PID và quán tính</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
      <MultilingualText ID="3" CompositionName="Title">
        <ObjectList>
          <MultilingualTextItem ID="4" CompositionName="Items">
            <AttributeList>
              <Culture>vi-VN</Culture>
              <Text>Mô phỏng tốc độ phản hồi AD</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.CompileUnit>
</Document>
```
