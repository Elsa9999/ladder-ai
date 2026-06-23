using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class VerifyConnectionsOnce
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        string xmlPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\probe_conn_temp.xml";
        string[] candidates = { "HMI_Connection_1", "HMI_Connection_2" };

        try
        {
            var processes = TiaPortal.GetProcesses();
            if (processes.Count == 0)
            {
                Console.WriteLine("No TIA instances found.");
                return;
            }
            var tia = processes[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to Project: " + proj.Name);

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
                Console.WriteLine("No HMI target found.");
                return;
            }

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
                    sw.WriteLine("          <Name>Test_Tag_" + conn + "</Name>");
                    sw.WriteLine("          <DataTypeName>Real</DataTypeName>");
                    sw.WriteLine("          <LogicalAddress />");
                    sw.WriteLine("        </AttributeList>");
                    sw.WriteLine("        <LinkList>");
                    sw.WriteLine("          <AcquisitionCycle TargetID=\"@OpenLink\"><Name>1 s</Name></AcquisitionCycle>");
                    sw.WriteLine("          <Connection TargetID=\"@OpenLink\"><Name>" + conn + "</Name></Connection>");
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
                    Console.WriteLine("  ==> SUCCESS! Connection '" + conn + "' is VALID.");
                    
                    // Clean up table
                    table = hmi.TagFolder.TagTables.Find("Test_Table");
                    if (table != null) table.Delete();
                }
                catch (Exception ex)
                {
                    string msg = ex.Message;
                    if (ex.InnerException != null) msg += " -> " + ex.InnerException.Message;
                    
                    Console.WriteLine("  ==> FAILED: " + msg);
                }
                finally
                {
                    if (File.Exists(xmlPath)) File.Delete(xmlPath);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
        }
    }
}
