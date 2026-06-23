using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class TestPlc2Connection
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        string xmlPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\test_conn_temp.xml";
        try
        {
            var processes = TiaPortal.GetProcesses();
            if (processes.Count == 0)
            {
                Console.WriteLine("No TIA Portal instances found.");
                return;
            }
            var tia = processes[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Connected to: " + proj.Name);

            // Fetch HMI target
            HmiTarget hmi = null;
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is HmiTarget)
                    {
                        hmi = sc.Software as HmiTarget;
                        break;
                    }
                }
                if (hmi != null) break;
            }

            if (hmi == null)
            {
                Console.WriteLine("No HMI targets found.");
                return;
            }
            Console.WriteLine("Target HMI: " + hmi.Name);

            // We test HMI_Connection_2
            string connName = "HMI_Connection_2";
            Console.WriteLine("Testing Connection: " + connName);

            using (StreamWriter sw = new StreamWriter(xmlPath, false, System.Text.Encoding.UTF8))
            {
                sw.WriteLine("<?xml version=\"1.0\" encoding=\"utf-8\"?>");
                sw.WriteLine("<Document>");
                sw.WriteLine("  <Engineering version=\"V18\" />");
                sw.WriteLine("  <Hmi.Tag.TagTable ID=\"0\">");
                sw.WriteLine("    <AttributeList><Name>Test_Table</Name></AttributeList>");
                sw.WriteLine("    <ObjectList>");
                sw.WriteLine("      <Hmi.Tag.Tag ID=\"1\" CompositionName=\"Tags\">");
                sw.WriteLine("        <AttributeList>");
                sw.WriteLine("          <Name>Test_Tag_PLC2</Name>");
                sw.WriteLine("          <DataTypeName>Real</DataTypeName>");
                sw.WriteLine("          <LogicalAddress />");
                sw.WriteLine("        </AttributeList>");
                sw.WriteLine("        <LinkList>");
                sw.WriteLine("          <AcquisitionCycle TargetID=\"@OpenLink\"><Name>1 s</Name></AcquisitionCycle>");
                sw.WriteLine("          <Connection TargetID=\"@OpenLink\"><Name>" + connName + "</Name></Connection>");
                sw.WriteLine("          <ControllerTag TargetID=\"@OpenLink\"><Name>CV3211_Nuoc_Bon3_M</Name></ControllerTag>");
                sw.WriteLine("          <DataType TargetID=\"@OpenLink\"><Name>Real</Name></DataType>");
                sw.WriteLine("          <HmiDataType TargetID=\"@OpenLink\"><Name>Real</Name></HmiDataType>");
                sw.WriteLine("        </LinkList>");
                sw.WriteLine("      </Hmi.Tag.Tag>");
                sw.WriteLine("    </ObjectList>");
                sw.WriteLine("  </Hmi.Tag.TagTable>");
                sw.WriteLine("</Document>");
            }

            try
            {
                var table = hmi.TagFolder.TagTables.Find("Test_Table");
                if (table != null) table.Delete();
                
                hmi.TagFolder.TagTables.Import(new FileInfo(xmlPath), ImportOptions.Override);
                Console.WriteLine("SUCCESS: Connection '" + connName + "' works for PLC_2 tag 'CV3211_Nuoc_Bon3_M'!");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed: " + ex.Message);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
        }
        finally
        {
            if (File.Exists(xmlPath)) File.Delete(xmlPath);
        }
    }
}
