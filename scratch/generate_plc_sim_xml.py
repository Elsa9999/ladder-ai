# -*- coding: utf-8 -*-
import sys
import os

# Add Ladder folder to python path to import Agent_LAD_Library
sys.path.append(r"D:\AI_Agent_PLC_LADDER_ONLY\Ladder")
from Agent_LAD_Library import TIALadderBuilder

# Define HMI/PLC tags definitions
tag_defs = [
    # Analogs
    {"name": "1400_FT115_PV", "type": "Real", "comment": "Lưu lượng dòng liệu đo được tại FT115"},
    {"name": "1400_FT101_PV", "type": "Real", "comment": "Lưu lượng dòng liệu đo được tại FT101"},
    {"name": "1400_1_02_PV", "type": "Real", "comment": "Giá trị đo của cảm biến 1-02"},
    {"name": "1406_TX35_PV", "type": "Real", "comment": "Giá trị đo cảm biến nhiệt độ/áp suất TX35"},
    {"name": "1400_TT64_PV", "type": "Real", "comment": "Nhiệt độ đo được tại TT64"},
    {"name": "1400_TT32_PV", "type": "Real", "comment": "Nhiệt độ đo được tại TT32"},
    {"name": "1400_LGFE01_PV", "type": "Real", "comment": "Mức bồn hoặc lưu lượng đo tại LGFE01"},
    {"name": "1400_FS51_PV", "type": "Real", "comment": "Giá trị lưu lượng đo được tại FS51"},
    {"name": "1400_FY301_PV", "type": "Real", "comment": "Mức cân hoặc vị trí điều khiển bồn FY301"},
    {"name": "1400_TT101_PV", "type": "Real", "comment": "Nhiệt độ đo được tại TT101"},
    {"name": "1400_FTT02_PV", "type": "Real", "comment": "Lưu lượng/nhiệt độ đo được tại FTT02"},
    # Digitals
    {"name": "1500S_Trang_Thai", "type": "Bool", "comment": "Trạng thái hoạt động dòng liệu 1500S (0: Không chảy, 1: Đang chảy)"},
    {"name": "1404T_Trang_Thai", "type": "Bool", "comment": "Trạng thái hoạt động dòng liệu 1404T"},
    {"name": "CR_2013_FO_104_Trang_Thai", "type": "Bool", "comment": "Trạng thái hoạt động dòng liệu CR-2013-FO-104"},
    {"name": "BFOC_SS_20_06_Trang_Thai", "type": "Bool", "comment": "Trạng thái hoạt động dòng liệu BFOC-SS-20-06"},
    {"name": "PC03010T01_Trang_Thai", "type": "Bool", "comment": "Trạng thái dòng liệu đầu ra PC03010T01"},
    {"name": "1401_Trang_Thai", "type": "Bool", "comment": "Trạng thái dòng liệu xả đáy 1401"},
    {"name": "1400_PT91_Chay", "type": "Bool", "comment": "Tín hiệu báo chạy bơm 1400PT91 (1: Chạy)"},
    {"name": "1400_KCK01_Chay", "type": "Bool", "comment": "Tín hiệu báo chạy cánh khuấy bồn 1400KCK01"},
    {"name": "1400_FT102_Mo", "type": "Bool", "comment": "Tín hiệu báo mở van nạp liệu 1400FT102"},
    {"name": "1400_TY33_Mo", "type": "Bool", "comment": "Tín hiệu báo mở van điều khiển cooling 1400TY33"},
    {"name": "160_FEC53_Mo", "type": "Bool", "comment": "Tín hiệu báo mở van kẹp 160 FEC53"},
    {"name": "1400_TXC32_Mo", "type": "Bool", "comment": "Tín hiệu báo mở van điều khiển 1400TXC32"},
    {"name": "1400_TC32_Mo", "type": "Bool", "comment": "Tín hiệu báo mở van điều khiển 1400TC32"},
    {"name": "1400_FIC01_Mo", "type": "Bool", "comment": "Tín hiệu báo mở van điều khiển 1400FIC01"},
    {"name": "1400_FS51_Mo", "type": "Bool", "comment": "Tín hiệu báo mở van xả đáy 1400FS51"},
    # Statuses
    {"name": "1500S_Status", "type": "Int", "comment": "Mã trạng thái dòng liệu 1500S (0: Dừng, 1: Chạy, 2: Lỗi)"},
    {"name": "1404T_Status", "type": "Int", "comment": "Mã trạng thái dòng liệu 1404T"},
    {"name": "CR_2013_FO_104_Status", "type": "Int", "comment": "Mã trạng thái dòng liệu CR-2013-FO-104"},
    {"name": "BFOC_SS_20_06_Status", "type": "Int", "comment": "Mã trạng thái dòng liệu BFOC-SS-20-06"},
    {"name": "PC03010T01_Status", "type": "Int", "comment": "Mã trạng thái dòng liệu PC03010T01"},
    {"name": "1401_Status", "type": "Int", "comment": "Mã trạng thái dòng liệu xả đáy 1401"},
    {"name": "1400_PT91_Status", "type": "Int", "comment": "Mã trạng thái hoạt động bơm 1400PT91 (0: Dừng, 1: Chạy, 2: Lỗi)"},
    {"name": "1400_KCK01_Status", "type": "Int", "comment": "Mã trạng thái hoạt động cánh khuấy 1400KCK01"},
    {"name": "1400_FT102_Status", "type": "Int", "comment": "Mã trạng thái hoạt động van 1400FT102 (0: Đóng, 1: Mở, 2: Lỗi)"},
    {"name": "1400_TY33_Status", "type": "Int", "comment": "Mã trạng thái hoạt động van 1400TY33"},
    {"name": "160_FEC53_Status", "type": "Int", "comment": "Mã trạng thái hoạt động van 160 FEC53"},
    {"name": "1400_TXC32_Status", "type": "Int", "comment": "Mã trạng thái hoạt động van 1400TXC32"},
    {"name": "1400_TC32_Status", "type": "Int", "comment": "Mã trạng thái hoạt động van 1400TC32"},
    {"name": "1400_FIC01_Status", "type": "Int", "comment": "Mã trạng thái hoạt động van 1400FIC01"},
    {"name": "1400_FS51_Status", "type": "Int", "comment": "Mã trạng thái hoạt động van 1400FS51"}
]

# Generate PLC Tag Table XML
def generate_plc_tags_xml(file_path):
    print("Generating PLC Tag Table XML...")
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<Document>')
    lines.append('  <Engineering version="V18" />')
    lines.append('  <DocumentInfo>')
    lines.append('    <Created>2026-06-11T12:00:00Z</Created>')
    lines.append('    <ExportSetting>WithDefaults</ExportSetting>')
    lines.append('  </DocumentInfo>')
    lines.append('  <SW.Tags.PlcTagTable ID="0">')
    lines.append('    <AttributeList>')
    lines.append('      <Name>PLC_Simulation_Tags</Name>')
    lines.append('    </AttributeList>')
    lines.append('    <ObjectList>')

    uid = 1
    
    # 1. Map Real variables (starting at %MD100, step 4 bytes)
    real_addr = 100
    for tag in tag_defs:
        if tag["type"] == "Real":
            addr = f"%MD{real_addr}"
            real_addr += 4
            write_plc_tag(lines, uid, tag["name"], tag["type"], addr, tag["comment"])
            uid += 3

    # 2. Map Bool variables (starting at %M200.0, step 1 bit)
    byte_addr = 200
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

    # 3. Map Int variables (starting at %MW300, step 2 bytes)
    int_addr = 300
    for tag in tag_defs:
        if tag["type"] == "Int":
            addr = f"%MW{int_addr}"
            int_addr += 2
            write_plc_tag(lines, uid, tag["name"], tag["type"], addr, tag["comment"])
            uid += 3

    # 4. Map Simulator helper tags
    # Sim_Counter (Real) -> %MD400
    write_plc_tag(lines, uid, "Sim_Counter", "Real", "%MD400", "Biến đếm trung gian cho sóng tam giác mô phỏng")
    uid += 3
    # Sim_Dir (Bool) -> %M404.0
    write_plc_tag(lines, uid, "Sim_Dir", "Bool", "%M404.0", "Bit hướng đếm mô phỏng (0: Tăng, 1: Giảm)")
    uid += 3
    # Sim_Val_Norm (Real) -> %MD408
    write_plc_tag(lines, uid, "Sim_Val_Norm", "Real", "%MD408", "Giá trị đếm đã chuẩn hóa về dải 0.0 - 1.0")
    uid += 3
    # Timer_Sim_Pulse_Output (Bool) -> %M404.1
    write_plc_tag(lines, uid, "Timer_Sim_Pulse_Output", "Bool", "%M404.1", "Xung kích hoạt đếm từ Timer")
    uid += 3

    lines.append('    </ObjectList>')
    lines.append('  </SW.Tags.PlcTagTable>')
    lines.append('</Document>')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[SUCCESS] PLC tag table generated at: {file_path}")

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


# Generate PLC Ladder Simulation FC XML
def generate_simulation_fc_xml(file_path):
    print("Generating FC_SCADA_Simulation XML using TIALadderBuilder...")
    builder = TIALadderBuilder(fb_name="FC_SCADA_Simulation", block_id="10", block_type="FC")

    # 1. Timer pulse network (repeating 50ms)
    builder.add_network(
        "Tạo xung kích hoạt chu kỳ mô phỏng (50ms)",
        [
            ("NC", "Timer_Sim_Pulse_Output"),
            ("TON", "Timer_Sim_DB", "T#50MS", "Timer_Sim_Pulse_Output")
        ]
    )

    # 2. Count up network (Sim_Counter = Sim_Counter + 1.0 when Sim_Dir = 0 and Timer_Sim_Pulse_Output = 1)
    builder.add_network(
        "Cộng Sim_Counter khi hướng đếm là Tăng (Sim_Dir = 0)",
        [
            ("NO", "Timer_Sim_Pulse_Output"),
            ("NC", "Sim_Dir"),
            ("MATH_ADD_Real", "Sim_Counter", "1.0", "Sim_Counter")
        ]
    )

    # 3. Direction toggle to DOWN (Sim_Dir = 1 when Sim_Counter >= 100.0) -> MUST use SetCoil to latch Sim_Dir
    builder.add_network(
        "Chuyển sang hướng giảm khi Sim_Counter đạt cực đại >= 100.0",
        [
            ("CMP_GE_Real", "Sim_Counter", "100.0"),
            ("SetCoil", "Sim_Dir")
        ]
    )

    # 4. Count down network (Sim_Counter = Sim_Counter - 1.0 when Sim_Dir = 1 and Timer_Sim_Pulse_Output = 1)
    builder.add_network(
        "Trừ Sim_Counter khi hướng đếm là Giảm (Sim_Dir = 1)",
        [
            ("NO", "Timer_Sim_Pulse_Output"),
            ("NO", "Sim_Dir"),
            ("MATH_SUB_Real", "Sim_Counter", "1.0", "Sim_Counter")
        ]
    )

    # 5. Direction toggle to UP (Sim_Dir = 0 when Sim_Counter <= 0.0) -> Uses ResetCoil to unlatch Sim_Dir
    builder.add_network(
        "Chuyển sang hướng tăng khi Sim_Counter đạt cực tiểu <= 0.0",
        [
            ("CMP_LE_Real", "Sim_Counter", "0.0"),
            ("ResetCoil", "Sim_Dir")
        ]
    )

    # 6. Normalize Sim_Counter (0.0 - 100.0) to Sim_Val_Norm (0.0 - 1.0)
    builder.add_network(
        "Chuẩn hóa Sim_Counter từ dải 0.0-100.0 về dải 0.0-1.0",
        [
            ("GENERIC", "Normalize", 
             {"min": "0.0", "value": "Sim_Counter", "max": "100.0"}, 
             {"out": "Sim_Val_Norm"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )

    # 7. Scale real outputs
    # Temperature 50 - 80
    temp_tags = ["1400_TT64_PV", "1400_TT32_PV", "1400_TT101_PV"]
    for t in temp_tags:
        builder.add_network(
            f"Tỷ lệ hóa Nhiệt độ cho {t} (50.0 - 80.0 °C)",
            [
                ("GENERIC", "Scale_X", 
                 {"min": "50.0", "value": "Sim_Val_Norm", "max": "80.0"}, 
                 {"out": t}, 
                 {"SrcType": "Real", "DestType": "Real"})
            ]
        )

    # Pressure 7 - 8
    builder.add_network(
        "Tỷ lệ hóa Áp suất cho 1406_TX35_PV (7.0 - 8.0 bar)",
        [
            ("GENERIC", "Scale_X", 
             {"min": "7.0", "value": "Sim_Val_Norm", "max": "8.0"}, 
             {"out": "1406_TX35_PV"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )

    # Flow 100 - 200
    flow_tags = ["1400_FT115_PV", "1400_FT101_PV", "1400_1_02_PV"]
    for t in flow_tags:
        builder.add_network(
            f"Tỷ lệ hóa Lưu lượng cho {t} (100.0 - 200.0)",
            [
                ("GENERIC", "Scale_X", 
                 {"min": "100.0", "value": "Sim_Val_Norm", "max": "200.0"}, 
                 {"out": t}, 
                 {"SrcType": "Real", "DestType": "Real"})
            ]
        )

    # Frequency 20 - 30
    builder.add_network(
        "Tỷ lệ hóa Tần số cho 1400_FS51_PV (20.0 - 30.0 Hz)",
        [
            ("GENERIC", "Scale_X", 
             {"min": "20.0", "value": "Sim_Val_Norm", "max": "30.0"}, 
             {"out": "1400_FS51_PV"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )

    # Additional analogs
    builder.add_network(
        "Tỷ lệ hóa Mức bồn LGFE01_PV (10.0 - 90.0)",
        [
            ("GENERIC", "Scale_X", 
             {"min": "10.0", "value": "Sim_Val_Norm", "max": "90.0"}, 
             {"out": "1400_LGFE01_PV"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )
    builder.add_network(
        "Tỷ lệ hóa Vị trí điều khiển bồn FY301_PV (0.0 - 100.0)",
        [
            ("GENERIC", "Scale_X", 
             {"min": "0.0", "value": "Sim_Val_Norm", "max": "100.0"}, 
             {"out": "1400_FY301_PV"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )
    builder.add_network(
        "Tỷ lệ hóa FTT02_PV (40.0 - 70.0)",
        [
            ("GENERIC", "Scale_X", 
             {"min": "40.0", "value": "Sim_Val_Norm", "max": "70.0"}, 
             {"out": "1400_FTT02_PV"}, 
             {"SrcType": "Real", "DestType": "Real"})
        ]
    )

    # 8. Digital tags
    phase_a_digitals = [
        "1500S_Trang_Thai", "1404T_Trang_Thai", "CR_2013_FO_104_Trang_Thai",
        "1400_PT91_Chay", "1400_KCK01_Chay", "1400_FT102_Mo", "1400_TY33_Mo", "160_FEC53_Mo"
    ]
    phase_b_digitals = [
        "BFOC_SS_20_06_Trang_Thai", "PC03010T01_Trang_Thai", "1401_Trang_Thai",
        "1400_TXC32_Mo", "1400_TC32_Mo", "1400_FIC01_Mo", "1400_FS51_Mo"
    ]

    for d in phase_a_digitals:
        builder.add_network(
            f"Điều khiển trạng thái số cho {d} (ON khi Counter > 50)",
            [
                ("CMP_GT_Real", "Sim_Counter", "50.0"),
                ("Coil", d)
            ]
        )

    for d in phase_b_digitals:
        builder.add_network(
            f"Điều khiển trạng thái số cho {d} (ON khi Counter <= 50)",
            [
                ("CMP_LE_Real", "Sim_Counter", "50.0"),
                ("Coil", d)
            ]
        )

    # 9. Status tags (Ints, 0: Off/Closed, 1: On/Open)
    # We map status tags to match their respective digital tags
    for d in phase_a_digitals:
        status_name = d.replace("_Trang_Thai", "_Status").replace("_Chay", "_Status").replace("_Mo", "_Status")
        builder.add_network(
            f"Cập nhật mã trạng thái cho {status_name} = 1 (Chạy/Mở)",
            [
                ("NO", d),
                ("MOVE", "1", status_name)
            ]
        )
        builder.add_network(
            f"Cập nhật mã trạng thái cho {status_name} = 0 (Dừng/Đóng)",
            [
                ("NC", d),
                ("MOVE", "0", status_name)
            ]
        )

    for d in phase_b_digitals:
        status_name = d.replace("_Trang_Thai", "_Status").replace("_Chay", "_Status").replace("_Mo", "_Status")
        builder.add_network(
            f"Cập nhật mã trạng thái cho {status_name} = 1 (Chạy/Mở)",
            [
                ("NO", d),
                ("MOVE", "1", status_name)
            ]
        )
        builder.add_network(
            f"Cập nhật mã trạng thái cho {status_name} = 0 (Dừng/Đóng)",
            [
                ("NC", d),
                ("MOVE", "0", status_name)
            ]
        )

    xml_out = builder.generate_xml()
    
    # Post-processing to disable ENO for Scale_X and Normalize blocks for cleaner visual rendering
    xml_out = xml_out.replace('<Part Name="Scale_X"', '<Part Name="Scale_X" DisabledENO="true"')
    xml_out = xml_out.replace('<Part Name="Normalize"', '<Part Name="Normalize" DisabledENO="true"')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(xml_out)
    print(f"[SUCCESS] PLC Logic FC generated at: {file_path}")


# Generate standalone Timer DB XML
def generate_timer_db_xml(file_path):
    print("Generating Timer_Sim_DB XML...")
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-06-11T12:00:00Z</Created>
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
              <Text>Instance DB for simulation timer</Text>
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
    print(f"[SUCCESS] Timer_Sim_DB XML generated at: {file_path}")


if __name__ == "__main__":
    out_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch"
    generate_plc_tags_xml(os.path.join(out_dir, "PLC_Simulation_Tags.xml"))
    generate_simulation_fc_xml(os.path.join(out_dir, "FC_SCADA_Simulation.xml"))
    generate_timer_db_xml(os.path.join(out_dir, "Timer_Sim_DB.xml"))
