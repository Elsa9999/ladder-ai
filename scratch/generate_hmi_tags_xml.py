# -*- coding: utf-8 -*-

tag_defs = [
    # Analogs
    {"name": "1400_FT115_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Lưu lượng dòng liệu đo được tại FT115"},
    {"name": "1400_FT101_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Lưu lượng dòng liệu đo được tại FT101"},
    {"name": "1400_1_02_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Giá trị đo của cảm biến 1-02"},
    {"name": "1406_TX35_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Giá trị đo cảm biến nhiệt độ/áp suất TX35"},
    {"name": "1400_TT64_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Nhiệt độ đo được tại TT64"},
    {"name": "1400_TT32_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Nhiệt độ đo được tại TT32"},
    {"name": "1400_LGFE01_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Mức bồn hoặc lưu lượng đo tại LGFE01"},
    {"name": "1400_FS51_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Giá trị lưu lượng đo được tại FS51"},
    {"name": "1400_FY301_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Mức cân hoặc vị trí điều khiển bồn FY301"},
    {"name": "1400_TT101_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Nhiệt độ đo được tại TT101"},
    {"name": "1400_FTT02_PV", "type": "Real", "coding": "IEEE754Float", "len": 4, "comment": "Lưu lượng/nhiệt độ đo được tại FTT02"},
    # Digitals
    {"name": "1500S_Trang_Thai", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Trạng thái hoạt động dòng liệu 1500S (0: Không chảy, 1: Đang chảy)"},
    {"name": "1404T_Trang_Thai", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Trạng thái hoạt động dòng liệu 1404T"},
    {"name": "CR_2013_FO_104_Trang_Thai", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Trạng thái hoạt động dòng liệu CR-2013-FO-104"},
    {"name": "BFOC_SS_20_06_Trang_Thai", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Trạng thái hoạt động dòng liệu BFOC-SS-20-06"},
    {"name": "PC03010T01_Trang_Thai", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Trạng thái dòng liệu đầu ra PC03010T01"},
    {"name": "1401_Trang_Thai", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Trạng thái dòng liệu xả đáy 1401"},
    {"name": "1400_PT91_Chay", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo chạy bơm 1400PT91 (1: Chạy)"},
    {"name": "1400_KCK01_Chay", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo chạy cánh khuấy bồn 1400KCK01"},
    {"name": "1400_FT102_Mo", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo mở van nạp liệu 1400FT102"},
    {"name": "1400_TY33_Mo", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo mở van điều khiển cooling 1400TY33"},
    {"name": "160_FEC53_Mo", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo mở van kẹp 160 FEC53"},
    {"name": "1400_TXC32_Mo", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo mở van điều khiển 1400TXC32"},
    {"name": "1400_TC32_Mo", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo mở van điều khiển 1400TC32"},
    {"name": "1400_FIC01_Mo", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo mở van điều khiển 1400FIC01"},
    {"name": "1400_FS51_Mo", "type": "Bool", "coding": "Binary", "len": 1, "comment": "Tín hiệu báo mở van xả đáy 1400FS51"},
    # Statuses
    {"name": "1500S_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái dòng liệu 1500S (0: Dừng, 1: Chạy, 2: Lỗi)"},
    {"name": "1404T_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái dòng liệu 1404T"},
    {"name": "CR_2013_FO_104_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái dòng liệu CR-2013-FO-104"},
    {"name": "BFOC_SS_20_06_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái dòng liệu BFOC-SS-20-06"},
    {"name": "PC03010T01_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái dòng liệu PC03010T01"},
    {"name": "1401_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái dòng liệu xả đáy 1401"},
    {"name": "1400_PT91_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động bơm 1400PT91 (0: Dừng, 1: Chạy, 2: Lỗi)"},
    {"name": "1400_KCK01_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động cánh khuấy 1400KCK01"},
    {"name": "1400_FT102_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động van 1400FT102 (0: Đóng, 1: Mở, 2: Lỗi)"},
    {"name": "1400_TY33_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động van 1400TY33"},
    {"name": "160_FEC53_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động van 160 FEC53"},
    {"name": "1400_TXC32_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động van 1400TXC32"},
    {"name": "1400_TC32_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động van 1400TC32"},
    {"name": "1400_FIC01_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động van 1400FIC01"},
    {"name": "1400_FS51_Status", "type": "Int", "coding": "Binary", "len": 2, "comment": "Mã trạng thái hoạt động van 1400FS51"}
]

def generate_hmi_xml(path, connection_name=None):
    xml_lines = []
    xml_lines.append('<?xml version="1.0" encoding="utf-8"?>')
    xml_lines.append('<Document>')
    xml_lines.append('  <Engineering version="V18" />')
    xml_lines.append('  <DocumentInfo>')
    xml_lines.append('    <Created>2026-06-11T12:00:00Z</Created>')
    xml_lines.append('    <ExportSetting>WithDefaults</ExportSetting>')
    xml_lines.append('    <InstalledProducts>')
    xml_lines.append('      <Product>')
    xml_lines.append('        <DisplayName>Totally Integrated Automation Portal</DisplayName>')
    xml_lines.append('        <DisplayVersion>V18</DisplayVersion>')
    xml_lines.append('      </Product>')
    xml_lines.append('      <OptionPackage>')
    xml_lines.append('        <DisplayName>TIA Portal Openness</DisplayName>')
    xml_lines.append('        <DisplayVersion>V18</DisplayVersion>')
    xml_lines.append('      </OptionPackage>')
    xml_lines.append('    </InstalledProducts>')
    xml_lines.append('  </DocumentInfo>')
    xml_lines.append('  <Hmi.Tag.TagTable ID="0">')
    xml_lines.append('    <AttributeList>')
    xml_lines.append('      <Name>HMI_Tags</Name>')
    xml_lines.append('    </AttributeList>')
    xml_lines.append('    <ObjectList>')

    id_counter = 1
    for tag in tag_defs:
        tag_id = hex(id_counter)[2:].upper()
        id_counter += 1
        
        xml_lines.append(f'      <Hmi.Tag.Tag ID="{tag_id}" CompositionName="Tags">')
        xml_lines.append('        <AttributeList>')
        xml_lines.append('          <AcquisitionTriggerMode>Visible</AcquisitionTriggerMode>')
        xml_lines.append('          <AddressAccessMode>Symbolic</AddressAccessMode>')
        xml_lines.append(f'          <Coding>{tag["coding"]}</Coding>')
        xml_lines.append('          <ConfirmationType>None</ConfirmationType>')
        xml_lines.append('          <GmpRelevant>false</GmpRelevant>')
        xml_lines.append('          <JobNumber>0</JobNumber>')
        xml_lines.append(f'          <Length>{tag["len"]}</Length>')
        xml_lines.append('          <LinearScaling>false</LinearScaling>')
        xml_lines.append('          <LogicalAddress />')
        xml_lines.append('          <MandatoryCommenting>false</MandatoryCommenting>')
        xml_lines.append(f'          <Name>{tag["name"]}</Name>')
        xml_lines.append('          <Persistency>false</Persistency>')
        xml_lines.append('          <QualityCode>false</QualityCode>')
        xml_lines.append('          <ScalingHmiHigh>100</ScalingHmiHigh>')
        xml_lines.append('          <ScalingHmiLow>0</ScalingHmiLow>')
        xml_lines.append('          <ScalingPlcHigh>10</ScalingPlcHigh>')
        xml_lines.append('          <ScalingPlcLow>0</ScalingPlcLow>')
        xml_lines.append('          <StartValue />')
        xml_lines.append('          <SubstituteValue />')
        xml_lines.append('          <SubstituteValueUsage>None</SubstituteValueUsage>')
        xml_lines.append('          <Synchronization>false</Synchronization>')
        xml_lines.append('          <UpdateMode>ProjectWide</UpdateMode>')
        xml_lines.append('          <UseMultiplexing>false</UseMultiplexing>')
        xml_lines.append('        </AttributeList>')
        xml_lines.append('        <LinkList>')
        xml_lines.append('          <AcquisitionCycle TargetID="@OpenLink">')
        xml_lines.append('            <Name>1 s</Name>')
        xml_lines.append('          </AcquisitionCycle>')
        
        if connection_name:
            xml_lines.append('          <Connection TargetID="@OpenLink">')
            xml_lines.append(f'            <Name>{connection_name}</Name>')
            xml_lines.append('          </Connection>')
            xml_lines.append('          <ControllerTag TargetID="@OpenLink">')
            xml_lines.append(f'            <Name>{tag["name"]}</Name>')
            xml_lines.append('          </ControllerTag>')
            
        xml_lines.append('          <DataType TargetID="@OpenLink">')
        xml_lines.append(f'            <Name>{tag["type"]}</Name>')
        xml_lines.append('          </DataType>')
        xml_lines.append('          <HmiDataType TargetID="@OpenLink">')
        xml_lines.append(f'            <Name>{tag["type"]}</Name>')
        xml_lines.append('          </HmiDataType>')
        xml_lines.append('        </LinkList>')
        
        # Add comment
        xml_lines.append('        <ObjectList>')
        xml_lines.append(f'          <MultilingualText ID="{hex(id_counter + 1000)[2:].upper()}" CompositionName="Comment">')
        xml_lines.append('            <ObjectList>')
        xml_lines.append(f'              <MultilingualTextItem ID="{hex(id_counter + 2000)[2:].upper()}" CompositionName="Items">')
        xml_lines.append('                <AttributeList>')
        xml_lines.append('                  <Culture>en-US</Culture>')
        xml_lines.append(f'                  <Text>{tag["comment"]}</Text>')
        xml_lines.append('                </AttributeList>')
        xml_lines.append('              </MultilingualTextItem>')
        xml_lines.append('            </ObjectList>')
        xml_lines.append('          </MultilingualText>')
        xml_lines.append('        </ObjectList>')
        
        xml_lines.append('      </Hmi.Tag.Tag>')

    xml_lines.append('    </ObjectList>')
    xml_lines.append('  </Hmi.Tag.TagTable>')
    xml_lines.append('</Document>')

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))
    print(f"[SUCCESS] Generated: {path}")

if __name__ == "__main__":
    # Generate both versions
    generate_hmi_xml(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\AI_HMI_Tags_Internal.xml", None)
    generate_hmi_xml(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\AI_HMI_Tags_Connected.xml", "HMI_Connection_1")
    generate_hmi_xml(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\AI_HMI_Tags.xml", None)
