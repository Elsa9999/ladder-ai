using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class TestConnectionImport
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

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is HmiTarget)
                        hmiTargets.Add(sc.Software as HmiTarget);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("No HMI targets found.");
                return;
            }

            var hmi = hmiTargets[0];
            Console.WriteLine("Target HMI: " + hmi.Name);

            // Let's test different connections by generating XML and importing
            string[] testConnections = { "HMI_Connection_1", "HMI_Connection_2", "PLC_Connection_1", "PLC_Connection_2", "HMI_Connection_PLC2" };
            
            foreach (var conn in testConnections)
            {
                Console.WriteLine("\n----------------------------------------");
                Console.WriteLine("Testing Connection: " + conn);
                
                // Write a single-tag HMI Tag table XML
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
                    sw.WriteLine("          <Connection TargetID=\"@OpenLink\"><Name>" + conn + "</Name></Connection>");
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
                    Console.WriteLine("SUCCESS: Connection '" + conn + "' works for PLC_2 tag 'CV3211_Nuoc_Bon3_M'!");
                    break;
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Failed for connection '" + conn + "': " + ex.Message);
                }
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
