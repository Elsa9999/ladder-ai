# -*- coding: utf-8 -*-
"""
generate_plc_sim_xml_cip_mixing.py
============================================================
Tự động sinh các tệp XML cho PLC S7-1200 (PLC_1) của dự án scadabai3_V18:
  1. AI_PLC_Tags_CIP_Mixing.xml (Bảng biến PLC Tag Table)
  2. FC_SCADA_Simulation.xml (Khối logic LAD giả lập cảm biến)
  3. Timer_Sim_DB.xml (Instance DB cho Timer 50ms)
  4. OB1_Main.xml (Khối OB1 gọi khối giả lập FC_SCADA_Simulation)
============================================================
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Thêm thư mục chứa thư viện Ladder vào python path
sys.path.append(r"D:\AI_Agent_PLC_LADDER_ONLY\Ladder")
from Agent_LAD_Library import TIALadderBuilder

# Định nghĩa các tag trong PLC
tag_defs = [
    # Cảm biến tương tự (Analogs)
    {"name": "AI_LT3203_PV", "type": "Real", "comment": "Mức bồn trộn 1 LT3203 (0.0 đến 1000.0 L)"},
    {"name": "AI_TT3204_PV", "type": "Real", "comment": "Nhiệt độ bồn trộn 1 TT3204 (0.0 đến 100.0 °C)"},
    {"name": "AI_LT3209_PV", "type": "Real", "comment": "Mức bồn trộn 2 LT3209 (0.0 đến 1000.0 L)"},
    {"name": "AI_TT3208_PV", "type": "Real", "comment": "Nhiệt độ bồn trộn 2 TT3208 (0.0 đến 100.0 °C)"},
    {"name": "AI_LT3213_PV", "type": "Real", "comment": "Mức bồn trộn 3 LT3213 (0.0 đến 1000.0 L)"},
    {"name": "AI_TT3214_PV", "type": "Real", "comment": "Nhiệt độ bồn trộn 3 TT3214 (0.0 đến 100.0 °C)"},
    {"name": "AI_LT3218_PV", "type": "Real", "comment": "Mức bồn trộn 4 LT3218 (0.0 đến 1000.0 L)"},
    {"name": "AI_TT3219_PV", "type": "Real", "comment": "Nhiệt độ bồn trộn 4 TT3219 (0.0 đến 100.0 °C)"},
    # Biến số (Digitals)
    {"name": "AI_BON1_Chay", "type": "Bool", "comment": "Báo trạng thái bồn trộn 1 đang chạy"},
    {"name": "AI_BON2_Chay", "type": "Bool", "comment": "Báo trạng thái bồn trộn 2 đang chạy"},
    {"name": "AI_BON3_Chay", "type": "Bool", "comment": "Báo trạng thái bồn trộn 3 đang chạy"},
    {"name": "AI_BON4_Chay", "type": "Bool", "comment": "Báo trạng thái bồn trộn 4 đang chạy"},
    {"name": "AI_PUMP3264_Chay", "type": "Bool", "comment": "Trạng thái chạy của bơm PUMP3264"},
    {"name": "AI_PUMP3265_Chay", "type": "Bool", "comment": "Trạng thái chạy của bơm PUMP3265"},
    # Trạng thái đăng nhập
    {"name": "AI_Logged_In", "type": "Int", "comment": "Trạng thái đăng nhập trên HMI"},
]

# Sinh file XML PLC Tag Table
def generate_plc_tags_xml(file_path):
    print("Đang tạo bảng biến PLC Tag Table XML...")
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<Document>')
    lines.append('  <Engineering version="V18" />')
    lines.append('  <DocumentInfo>')
    lines.append('    <Created>2026-06-12T00:00:00Z</Created>')
    lines.append('    <ExportSetting>WithDefaults</ExportSetting>')
    lines.append('  </DocumentInfo>')
    lines.append('  <SW.Tags.PlcTagTable ID="0">')
    lines.append('    <AttributeList>')
    lines.append('      <Name>AI_PLC_Tags_CIP_Mixing</Name>')
    lines.append('    </AttributeList>')
    lines.append('    <ObjectList>')

    uid = 1
    
    # 1. Áp địa chỉ cho các biến Real (bắt đầu từ %MD200, mỗi biến cách nhau 4 bytes)
    real_addr = 200
    for tag in tag_defs:
        if tag["type"] == "Real":
            addr = f"%MD{real_addr}"
            real_addr += 4
            write_plc_tag(lines, uid, tag["name"], tag["type"], addr, tag["comment"])
            uid += 3

    # 2. Áp địa chỉ cho các biến Bool (bắt đầu từ %M232.0, mỗi biến tăng 1 bit)
    byte_addr = 232
    bit_addr = 0
    for tag in tag_defs:
        if tag["type"] == "Bool":
            addr = f"%M{byte_addr}.{bit_addr}"
            bit_addr += 1
            if bit_addr > 7:
                bit_addr = 0
                byte_addr += 1
            write_plc_tag(lines, uid, tag["name"], tag["type"], addr, tag["comment"])
            uid += 3

    # 3. Áp địa chỉ cho biến Int (bắt đầu từ %MW234, 2 bytes)
    int_addr = 234
    for tag in tag_defs:
        if tag["type"] == "Int":
            addr = f"%MW{int_addr}"
            int_addr += 2
            write_plc_tag(lines, uid, tag["name"], tag["type"], addr, tag["comment"])
            uid += 3

    # 4. Các biến phụ phục vụ bộ giả lập sóng tam giác
    # Sim_Counter (Real) -> %MD236
    write_plc_tag(lines, uid, "Sim_Counter", "Real", "%MD236", "Biến đếm trung gian cho sóng tam giác mô phỏng")
    uid += 3
    # Sim_Dir (Bool) -> %M240.0
    write_plc_tag(lines, uid, "Sim_Dir", "Bool", "%M240.0", "Bit hướng đếm mô phỏng (0: Tăng, 1: Giảm)")
    uid += 3
    # Sim_Val_Norm (Real) -> %MD242
    write_plc_tag(lines, uid, "Sim_Val_Norm", "Real", "%MD242", "Giá trị đếm đã chuẩn hóa về dải 0.0 - 1.0")
    uid += 3
    # Timer_Sim_Pulse_Output (Bool) -> %M240.1
    write_plc_tag(lines, uid, "Timer_Sim_Pulse_Output", "Bool", "%M240.1", "Xung kích hoạt đếm từ Timer")
    uid += 3

    lines.append('    </ObjectList>')
    lines.append('  </SW.Tags.PlcTagTable>')
    lines.append('</Document>')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] PLC tag table đã lưu tại: {file_path}")

def write_plc_tag(lines, uid, name, data_type, address, comment):
    lines.append(f'      <SW.Tags.PlcTag ID="{hex(uid)[2:].upper()}" CompositionName="Tags">')
    lines.append('        <AttributeList>')
    lines.append(f'          <DataTypeName>{data_type}</DataTypeName>')
    lines.append('          <ExternalAccessible>true</ExternalAccessible>')
    lines.append('          <ExternalVisible>true</ExternalVisible>')
    lines.append('          <ExternalWritable>true</ExternalWritable>')
    lines.append(f'          <LogicalAddress>{address}</LogicalAddress>')
    lines.append(f'          <Name>{name}</Name>')
    lines.append('        </AttributeList>')
    lines.append('        <ObjectList>')
    lines.append(f'          <MultilingualText ID="{hex(uid+1)[2:].upper()}" CompositionName="Comment">')
    lines.append('            <ObjectList>')
    lines.append(f'              <MultilingualTextItem ID="{hex(uid+2)[2:].upper()}" CompositionName="Items">')
    lines.append('                <AttributeList>')
    lines.append('                  <Culture>en-US</Culture>')
    lines.append(f'                  <Text>{comment}</Text>')
    lines.append('                </AttributeList>')
    lines.append('              </MultilingualTextItem>')
    lines.append('            </ObjectList>')
    lines.append('          </MultilingualText>')
    lines.append('        </ObjectList>')
    lines.append('      </SW.Tags.PlcTag>')


# Sinh khối logic giả lập bằng Ladder XML
def generate_simulation_fc_xml(file_path):
    print("Đang tạo khối FC_SCADA_Simulation XML...")
    builder = TIALadderBuilder(fb_name="FC_SCADA_Simulation", block_id="10", block_type="FC")

    # Network 1: Tạo xung
    builder.add_network(
        "Tạo xung kích hoạt chu kỳ mô phỏng (50ms)",
        [
            ("NC", "Timer_Sim_Pulse_Output"),
            ("TON", "Timer_Sim_DB", "T#50MS", "Timer_Sim_Pulse_Output")
        ]
    )

    # Network 2: Cộng đếm
    builder.add_network(
        "Cộng Sim_Counter khi hướng đếm là Tăng (Sim_Dir = 0)",
        [
            ("NO", "Timer_Sim_Pulse_Output"),
            ("NC", "Sim_Dir"),
            ("MATH_ADD_Real", "Sim_Counter", "1.0", "Sim_Counter")
        ]
    )

    # Network 3: Chuyển hướng giảm
    builder.add_network(
        "Chuyển sang hướng giảm khi Sim_Counter đạt cực đại >= 100.0",
        [
            ("CMP_GE_Real", "Sim_Counter", "100.0"),
            ("SetCoil", "Sim_Dir")
        ]
    )

    # Network 4: Trừ đếm
    builder.add_network(
        "Trừ Sim_Counter khi hướng đếm là Giảm (Sim_Dir = 1)",
        [
            ("NO", "Timer_Sim_Pulse_Output"),
            ("NO", "Sim_Dir"),
            ("MATH_SUB_Real", "Sim_Counter", "1.0", "Sim_Counter")
        ]
    )

    # Network 5: Chuyển hướng tăng
    builder.add_network(
        "Chuyển sang hướng tăng khi Sim_Counter đạt cực tiểu <= 0.0",
        [
            ("CMP_LE_Real", "Sim_Counter", "0.0"),
            ("ResetCoil", "Sim_Dir")
        ]
    )

    # Network 6: Chuẩn hóa đếm
    builder.add_network(
        "Chuẩn hóa Sim_Counter từ dải 0.0-100.0 về dải 0.0-1.0",
        [
            ("GENERIC", "Normalize", 
             {"min": "0.0", "value": "Sim_Counter", "max": "100.0"}, 
             {"out": "Sim_Val_Norm"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )

    # Network 7: Mô phỏng mức bồn (LT3203, LT3209, LT3213, LT3218) từ 100.0 đến 900.0 L
    level_tags = ["AI_LT3203_PV", "AI_LT3209_PV", "AI_LT3213_PV", "AI_LT3218_PV"]
    for t in level_tags:
        builder.add_network(
            f"Mô phỏng Mức bồn cho {t} (100.0 - 900.0 L)",
            [
                ("GENERIC", "Scale_X", 
                 {"min": "100.0", "value": "Sim_Val_Norm", "max": "900.0"}, 
                 {"out": t}, 
                 {"SrcType": "Real", "DestType": "Real"})
            ]
        )

    # Network 8: Mô phỏng nhiệt độ bồn 1 và bồn 3 (Ambient: 25.0 - 35.0 °C)
    ambient_temp_tags = ["AI_TT3204_PV", "AI_TT3214_PV"]
    for t in ambient_temp_tags:
        builder.add_network(
            f"Mô phỏng Nhiệt độ môi trường cho {t} (25.0 - 35.0 °C)",
            [
                ("GENERIC", "Scale_X", 
                 {"min": "25.0", "value": "Sim_Val_Norm", "max": "35.0"}, 
                 {"out": t}, 
                 {"SrcType": "Real", "DestType": "Real"})
            ]
        )

    # Network 9: Mô phỏng nhiệt độ bồn 2 (Gia nhiệt đạt 75°C: 68.0 - 78.0 °C)
    builder.add_network(
        "Mô phỏng Nhiệt độ gia nhiệt bồn 2 AI_TT3208_PV (68.0 - 78.0 °C)",
        [
            ("GENERIC", "Scale_X", 
             {"min": "68.0", "value": "Sim_Val_Norm", "max": "78.0"}, 
             {"out": "AI_TT3208_PV"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )

    # Network 10: Mô phỏng nhiệt độ bồn 4 (Gia nhiệt đạt 95°C: 88.0 - 98.0 °C)
    builder.add_network(
        "Mô phỏng Nhiệt độ gia nhiệt bồn 4 AI_TT3219_PV (88.0 - 98.0 °C)",
        [
            ("GENERIC", "Scale_X", 
             {"min": "88.0", "value": "Sim_Val_Norm", "max": "98.0"}, 
             {"out": "AI_TT3219_PV"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )

    # Network 11: Mô phỏng trạng thái hoạt động thiết bị
    digital_tags = [
        "AI_BON1_Chay", "AI_BON2_Chay", "AI_BON3_Chay", "AI_BON4_Chay",
        "AI_PUMP3264_Chay", "AI_PUMP3265_Chay"
    ]
    for d in digital_tags:
        builder.add_network(
            f"Mô phỏng Trạng thái chạy cho {d} (ON khi Counter > 50)",
            [
                ("CMP_GT_Real", "Sim_Counter", "50.0"),
                ("Coil", d)
            ]
        )

    # Network 12: Đăng nhập luôn là 1
    builder.add_network(
        "Cài đặt mặc định Đăng nhập AI_Logged_In = 1",
        [
            ("MOVE", "1", "AI_Logged_In")
        ]
    )

    xml_out = builder.generate_xml()
    
    # Tắt ENO cho các khối Scale_X và Normalize
    xml_out = xml_out.replace('<Part Name="Scale_X"', '<Part Name="Scale_X" DisabledENO="true"')
    xml_out = xml_out.replace('<Part Name="Normalize"', '<Part Name="Normalize" DisabledENO="true"')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(xml_out)
    print(f"[OK] Khối logic FC đã lưu tại: {file_path}")


# Sinh file Instance DB Timer_Sim_DB
def generate_timer_db_xml(file_path):
    print("Đang tạo file Timer_Sim_DB XML...")
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-12T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Blocks.InstanceDB ID="0">
    <AttributeList>
      <AutoNumber>true</AutoNumber>
      <InstanceOfName>IEC_TIMER</InstanceOfName>
      <Interface><Sections xmlns="http://www.siemens.com/automation/Openness/SW/Interface/v5">
  <Section Name="Static">
    <Member Name="PT" Datatype="Time" Remanence="NonRetain" Accessibility="Public"><AttributeList><BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute></AttributeList></Member>
    <Member Name="ET" Datatype="Time" Remanence="NonRetain" Accessibility="Public"><AttributeList><BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalWritable" SystemDefined="true">false</BooleanAttribute><BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute></AttributeList></Member>
    <Member Name="IN" Datatype="Bool" Remanence="NonRetain" Accessibility="Public"><AttributeList><BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalWritable" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute></AttributeList></Member>
    <Member Name="Q" Datatype="Bool" Remanence="NonRetain" Accessibility="Public"><AttributeList><BooleanAttribute Name="ExternalAccessible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalVisible" SystemDefined="true">true</BooleanAttribute><BooleanAttribute Name="ExternalWritable" SystemDefined="true">false</BooleanAttribute><BooleanAttribute Name="SetPoint" SystemDefined="true">false</BooleanAttribute></AttributeList></Member>
  </Section>
</Sections></Interface>
      <Name>Timer_Sim_DB</Name>
      <Namespace />
      <Number>10</Number>
      <OfSystemLibElement>IEC_TIMER</OfSystemLibElement>
      <OfSystemLibVersion>1.0</OfSystemLibVersion>
      <ProgrammingLanguage>DB</ProgrammingLanguage>
    </AttributeList>
    <ObjectList>
      <MultilingualText ID="1" CompositionName="Comment">
        <ObjectList>
          <MultilingualTextItem ID="2" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>DB chứa biến đếm thời gian cho khối mô phỏng</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
      <MultilingualText ID="3" CompositionName="Title">
        <ObjectList>
          <MultilingualTextItem ID="4" CompositionName="Items">
            <AttributeList>
              <Culture>en-US</Culture>
              <Text>Timer_Sim_DB</Text>
            </AttributeList>
          </MultilingualTextItem>
        </ObjectList>
      </MultilingualText>
    </ObjectList>
  </SW.Blocks.InstanceDB>
</Document>"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
    print(f"[OK] Timer_Sim_DB đã lưu tại: {file_path}")


# Sinh khối OB1 Main gọi FC_SCADA_Simulation
def generate_ob1_xml(file_path):
    print("Đang tạo file OB1_Main XML...")
    builder = TIALadderBuilder(fb_name="Main", block_id="1", block_type="OB")
    
    # Gọi khối FC_SCADA_Simulation
    builder.add_network(
        "Gọi khối mô phỏng cảm biến SCADA",
        [
            ("CALL_FC", "FC_SCADA_Simulation")
        ]
    )

    xml_out = builder.generate_xml()
    
    # Custom post-processing để đặt đúng loại block là OB và định dạng thuộc tính OB1
    xml_out = xml_out.replace('<SW.Blocks.FB', '<SW.Blocks.OB')
    xml_out = xml_out.replace('</SW.Blocks.FB>', '</SW.Blocks.OB>')
    
    # Thay thế thuộc tính của FB thành OB
    xml_out = xml_out.replace('<InstanceOfName />', '')
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(xml_out)
    print(f"[OK] Khối OB1 Main đã lưu tại: {file_path}")


if __name__ == "__main__":
    out_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\import_temp"
    os.makedirs(out_dir, exist_ok=True)
    
    generate_plc_tags_xml(os.path.join(out_dir, "AI_PLC_Tags_CIP_Mixing.xml"))
    generate_timer_db_xml(os.path.join(out_dir, "Timer_Sim_DB.xml"))
    generate_simulation_fc_xml(os.path.join(out_dir, "FC_SCADA_Simulation.xml"))
    generate_ob1_xml(os.path.join(out_dir, "Main.xml"))
    
    print("\n" + "="*50)
    print("HOÀN THÀNH sinh toàn bộ tệp XML cho PLC!")
    print("="*50)
