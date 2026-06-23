using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class ProbeConnections
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        string xmlPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\probe_conn_temp.xml";
        
        string[] candidates = {
            "HMI_Connection_1",
            "HMI_Connection_2",
            "HMI_Connection_3",
            "PLC_Connection_1",
            "PLC_Connection_2",
            "HMI_Connection_PLC1",
            "HMI_Connection_PLC_1",
            "HMI_Connection_PLC2",
            "HMI_Connection_PLC_2",
            "S7_Connection_1",
            "S7_Connection_2",
            "HMI_RT_1_Connection_1",
            "HMI_RT_1_Connection_2"
        };

        foreach (var conn in candidates)
        {
            Console.WriteLine("Probing connection: " + conn);
            
            // Generate XML with target tag
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
                // We attach freshly for each run to avoid disposed object errors
                var processes = TiaPortal.GetProcesses();
                if (processes.Count == 0)
                {
                    Console.WriteLine("  No TIA instances found.");
                    continue;
                }
                var tia = processes[0].Attach();
                var proj = tia.Projects[0];

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
                    Console.WriteLine("  No HMI target found.");
                    continue;
                }

                var table = hmi.TagFolder.TagTables.Find("Test_Table");
                if (table != null) table.Delete();

                hmi.TagFolder.TagTables.Import(new FileInfo(xmlPath), ImportOptions.Override);
                Console.WriteLine("  ==> SUCCESS! Connection '" + conn + "' connects to PLC_2 and 'CV3211_Nuoc_Bon3_M' imported successfully!");
                break;
            }
            catch (Exception ex)
            {
                string msg = ex.Message;
                if (ex.InnerException != null) msg += " -> " + ex.InnerException.Message;
                
                if (msg.Contains("was not found"))
                {
                    if (msg.Contains("tag was not found") || msg.Contains("Connection") && msg.Contains("not found"))
                    {
                        Console.WriteLine("  ==> INVALID CONNECTION: " + conn);
                    }
                    else
                    {
                        Console.WriteLine("  ==> VALID CONNECTION: " + conn + " (but controller tag not found on the target PLC)");
                    }
                }
                else
                {
                    Console.WriteLine("  ==> Error: " + msg);
                }
            }
            finally
            {
                if (File.Exists(xmlPath)) File.Delete(xmlPath);
            }
        }
    }
}
