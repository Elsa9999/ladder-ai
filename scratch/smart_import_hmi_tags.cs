using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;
using Siemens.Engineering.Hmi.Communication;

class SmartImportHmiTags
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL SMART HMI TAG IMPORTER");
        Console.WriteLine("========================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Error: No running TIA Portal instances found.");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Connected to Project: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Error: No HMI target found in project.");
                return;
            }

            var hmi = hmiTargets[0];
            Console.WriteLine("Target HMI: " + hmi.Name);

            // Force connection name to HMI_Connection_1 as configured in TIA Portal
            string connectionName = "HMI_Connection_1";
            Console.WriteLine("Force HMI Connection: " + connectionName);

            // Generate HMI Tag Table XML dynamically
            string xmlPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\AI_HMI_Tags.xml";
            GenerateXml(xmlPath, connectionName);

            // Import the Tag Table
            FileInfo fileInfo = new FileInfo(xmlPath);
            Console.WriteLine("Importing HMI Tag Table into WinCC...");
            hmi.TagFolder.TagTables.Import(fileInfo, ImportOptions.Override);
            Console.WriteLine("Import completed successfully!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void GenerateXml(string xmlPath, string connectionName)
    {
        var tagDefs = new List<TagDef>
        {
            // Analogs
            new TagDef("1400_FT115_PV", "Real", "IEEE754Float", 4, "Lưu lượng dòng liệu đo được tại FT115"),
            new TagDef("1400_FT101_PV", "Real", "IEEE754Float", 4, "Lưu lượng dòng liệu đo được tại FT101"),
            new TagDef("1400_1_02_PV", "Real", "IEEE754Float", 4, "Giá trị đo của cảm biến 1-02"),
            new TagDef("1406_TX35_PV", "Real", "IEEE754Float", 4, "Giá trị đo cảm biến nhiệt độ/áp suất TX35"),
            new TagDef("1400_TT64_PV", "Real", "IEEE754Float", 4, "Nhiệt độ đo được tại TT64"),
            new TagDef("1400_TT32_PV", "Real", "IEEE754Float", 4, "Nhiệt độ đo được tại TT32"),
            new TagDef("1400_LGFE01_PV", "Real", "IEEE754Float", 4, "Mức bồn hoặc lưu lượng đo tại LGFE01"),
            new TagDef("1400_FS51_PV", "Real", "IEEE754Float", 4, "Giá trị lưu lượng đo được tại FS51"),
            new TagDef("1400_FY301_PV", "Real", "IEEE754Float", 4, "Mức cân hoặc vị trí điều khiển bồn FY301"),
            new TagDef("1400_TT101_PV", "Real", "IEEE754Float", 4, "Nhiệt độ đo được tại TT101"),
            new TagDef("1400_FTT02_PV", "Real", "IEEE754Float", 4, "Lưu lượng/nhiệt độ đo được tại FTT02"),
            // Digitals
            new TagDef("1500S_Trang_Thai", "Bool", "Binary", 1, "Trạng thái hoạt động dòng liệu 1500S (0: Không chảy, 1: Đang chảy)"),
            new TagDef("1404T_Trang_Thai", "Bool", "Binary", 1, "Trạng thái hoạt động dòng liệu 1404T"),
            new TagDef("CR_2013_FO_104_Trang_Thai", "Bool", "Binary", 1, "Trạng thái hoạt động dòng liệu CR-2013-FO-104"),
            new TagDef("BFOC_SS_20_06_Trang_Thai", "Bool", "Binary", 1, "Trạng thái hoạt động dòng liệu BFOC-SS-20-06"),
            new TagDef("PC03010T01_Trang_Thai", "Bool", "Binary", 1, "Trạng thái dòng liệu đầu ra PC03010T01"),
            new TagDef("1401_Trang_Thai", "Bool", "Binary", 1, "Trạng thái dòng liệu xả đáy 1401"),
            new TagDef("1400_PT91_Chay", "Bool", "Binary", 1, "Tín hiệu báo chạy bơm 1400PT91 (1: Chạy)"),
            new TagDef("1400_KCK01_Chay", "Bool", "Binary", 1, "Tín hiệu báo chạy cánh khuấy bồn 1400KCK01"),
            new TagDef("1400_FT102_Mo", "Bool", "Binary", 1, "Tín hiệu báo mở van nạp liệu 1400FT102"),
            new TagDef("1400_TY33_Mo", "Bool", "Binary", 1, "Tín hiệu báo mở van điều khiển cooling 1400TY33"),
            new TagDef("160_FEC53_Mo", "Bool", "Binary", 1, "Tín hiệu báo mở van kẹp 160 FEC53"),
            new TagDef("1400_TXC32_Mo", "Bool", "Binary", 1, "Tín hiệu báo mở van điều khiển 1400TXC32"),
            new TagDef("1400_TC32_Mo", "Bool", "Binary", 1, "Tín hiệu báo mở van điều khiển 1400TC32"),
            new TagDef("1400_FIC01_Mo", "Bool", "Binary", 1, "Tín hiệu báo mở van điều khiển 1400FIC01"),
            new TagDef("1400_FS51_Mo", "Bool", "Binary", 1, "Tín hiệu báo mở van xả đáy 1400FS51"),
            // Statuses
            new TagDef("1500S_Status", "Int", "Binary", 2, "Mã trạng thái dòng liệu 1500S (0: Dừng, 1: Chạy, 2: Lỗi)"),
            new TagDef("1404T_Status", "Int", "Binary", 2, "Mã trạng thái dòng liệu 1404T"),
            new TagDef("CR_2013_FO_104_Status", "Int", "Binary", 2, "Mã trạng thái dòng liệu CR-2013-FO-104"),
            new TagDef("BFOC_SS_20_06_Status", "Int", "Binary", 2, "Mã trạng thái dòng liệu BFOC-SS-20-06"),
            new TagDef("PC03010T01_Status", "Int", "Binary", 2, "Mã trạng thái dòng liệu PC03010T01"),
            new TagDef("1401_Status", "Int", "Binary", 2, "Mã trạng thái dòng liệu xả đáy 1401"),
            new TagDef("1400_PT91_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động bơm 1400PT91 (0: Dừng, 1: Chạy, 2: Lỗi)"),
            new TagDef("1400_KCK01_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động cánh khuấy 1400KCK01"),
            new TagDef("1400_FT102_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động van 1400FT102 (0: Đóng, 1: Mở, 2: Lỗi)"),
            new TagDef("1400_TY33_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động van 1400TY33"),
            new TagDef("160_FEC53_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động van 160 FEC53"),
            new TagDef("1400_TXC32_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động van 1400TXC32"),
            new TagDef("1400_TC32_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động van 1400TC32"),
            new TagDef("1400_FIC01_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động van 1400FIC01"),
            new TagDef("1400_FS51_Status", "Int", "Binary", 2, "Mã trạng thái hoạt động van 1400FS51")
        };

        using (StreamWriter sw = new StreamWriter(xmlPath, false, System.Text.Encoding.UTF8))
        {
            sw.WriteLine("<?xml version=\"1.0\" encoding=\"utf-8\"?>");
            sw.WriteLine("<Document>");
            sw.WriteLine("  <Engineering version=\"V18\" />");
            sw.WriteLine("  <DocumentInfo>");
            sw.WriteLine("    <Created>2026-06-11T12:00:00Z</Created>");
            sw.WriteLine("    <ExportSetting>WithDefaults</ExportSetting>");
            sw.WriteLine("    <InstalledProducts>");
            sw.WriteLine("      <Product>");
            sw.WriteLine("        <DisplayName>Totally Integrated Automation Portal</DisplayName>");
            sw.WriteLine("        <DisplayVersion>V18</DisplayVersion>");
            sw.WriteLine("      </Product>");
            sw.WriteLine("      <OptionPackage>");
            sw.WriteLine("        <DisplayName>TIA Portal Openness</DisplayName>");
            sw.WriteLine("        <DisplayVersion>V18</DisplayVersion>");
            sw.WriteLine("      </OptionPackage>");
            sw.WriteLine("    </InstalledProducts>");
            sw.WriteLine("  </DocumentInfo>");
            sw.WriteLine("  <Hmi.Tag.TagTable ID=\"0\">");
            sw.WriteLine("    <AttributeList>");
            sw.WriteLine("      <Name>HMI_Tags</Name>");
            sw.WriteLine("    </AttributeList>");
            sw.WriteLine("    <ObjectList>");

            int idCounter = 1;
            foreach (var tag in tagDefs)
            {
                string tagId = idCounter.ToString("X");
                idCounter++;

                sw.WriteLine("      <Hmi.Tag.Tag ID=\"" + tagId + "\" CompositionName=\"Tags\">");
                sw.WriteLine("        <AttributeList>");
                sw.WriteLine("          <AcquisitionTriggerMode>Visible</AcquisitionTriggerMode>");
                sw.WriteLine("          <AddressAccessMode>Symbolic</AddressAccessMode>");
                sw.WriteLine("          <Coding>" + tag.Coding + "</Coding>");
                sw.WriteLine("          <ConfirmationType>None</ConfirmationType>");
                sw.WriteLine("          <GmpRelevant>false</GmpRelevant>");
                sw.WriteLine("          <JobNumber>0</JobNumber>");
                sw.WriteLine("          <Length>" + tag.Length + "</Length>");
                sw.WriteLine("          <LinearScaling>false</LinearScaling>");
                sw.WriteLine("          <LogicalAddress />");
                sw.WriteLine("          <MandatoryCommenting>false</MandatoryCommenting>");
                sw.WriteLine("          <Name>" + tag.Name + "</Name>");
                sw.WriteLine("          <Persistency>false</Persistency>");
                sw.WriteLine("          <QualityCode>false</QualityCode>");
                sw.WriteLine("          <ScalingHmiHigh>100</ScalingHmiHigh>");
                sw.WriteLine("          <ScalingHmiLow>0</ScalingHmiLow>");
                sw.WriteLine("          <ScalingPlcHigh>10</ScalingPlcHigh>");
                sw.WriteLine("          <ScalingPlcLow>0</ScalingPlcLow>");
                sw.WriteLine("          <StartValue />");
                sw.WriteLine("          <SubstituteValue />");
                sw.WriteLine("          <SubstituteValueUsage>None</SubstituteValueUsage>");
                sw.WriteLine("          <Synchronization>false</Synchronization>");
                sw.WriteLine("          <UpdateMode>ProjectWide</UpdateMode>");
                sw.WriteLine("          <UseMultiplexing>false</UseMultiplexing>");
                sw.WriteLine("        </AttributeList>");
                sw.WriteLine("        <LinkList>");
                sw.WriteLine("          <AcquisitionCycle TargetID=\"@OpenLink\">");
                sw.WriteLine("            <Name>1 s</Name>");
                sw.WriteLine("          </AcquisitionCycle>");
                
                if (connectionName != null)
                {
                    sw.WriteLine("          <Connection TargetID=\"@OpenLink\">");
                    sw.WriteLine("            <Name>" + connectionName + "</Name>");
                    sw.WriteLine("          </Connection>");
                    sw.WriteLine("          <ControllerTag TargetID=\"@OpenLink\">");
                    sw.WriteLine("            <Name>" + tag.Name + "</Name>");
                    sw.WriteLine("          </ControllerTag>");
                }

                sw.WriteLine("          <DataType TargetID=\"@OpenLink\">");
                sw.WriteLine("            <Name>" + tag.Type + "</Name>");
                sw.WriteLine("          </DataType>");
                sw.WriteLine("          <HmiDataType TargetID=\"@OpenLink\">");
                sw.WriteLine("            <Name>" + tag.Type + "</Name>");
                sw.WriteLine("          </HmiDataType>");
                sw.WriteLine("        </LinkList>");
                
                // Add comment
                sw.WriteLine("        <ObjectList>");
                sw.WriteLine("          <MultilingualText ID=\"" + (idCounter + 1000).ToString("X") + "\" CompositionName=\"Comment\">");
                sw.WriteLine("            <ObjectList>");
                sw.WriteLine("              <MultilingualTextItem ID=\"" + (idCounter + 2000).ToString("X") + "\" CompositionName=\"Items\">");
                sw.WriteLine("                <AttributeList>");
                sw.WriteLine("                  <Culture>en-US</Culture>");
                sw.WriteLine("                  <Text>" + tag.Comment + "</Text>");
                sw.WriteLine("                </AttributeList>");
                sw.WriteLine("              </MultilingualTextItem>");
                sw.WriteLine("            </ObjectList>");
                sw.WriteLine("          </MultilingualText>");
                sw.WriteLine("        </ObjectList>");

                sw.WriteLine("      </Hmi.Tag.Tag>");
            }

            sw.WriteLine("    </ObjectList>");
            sw.WriteLine("  </Hmi.Tag.TagTable>");
            sw.WriteLine("</Document>");
        }
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
        {
            targets.Add(sc.Software as HmiTarget);
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, targets);
        }
    }
}

class TagDef
{
    public string Name { get; set; }
    public string Type { get; set; }
    public string Coding { get; set; }
    public int Length { get; set; }
    public string Comment { get; set; }

    public TagDef(string name, string type, string coding, int length, string comment)
    {
        Name = name;
        Type = type;
        Coding = coding;
        Length = length;
        Comment = comment;
    }
}
