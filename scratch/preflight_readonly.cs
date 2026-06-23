using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Tags;

class PreflightReadonly
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        string dumpPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\preflight_tia_dump.txt";
        
        try
        {
            int targetPid = 14620;
            string expectedPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";
            
            var processes = TiaPortal.GetProcesses();
            TiaPortalProcess selectedProcess = null;
            foreach (var p in processes)
            {
                if (p.Id == targetPid)
                {
                    selectedProcess = p;
                    break;
                }
            }

            if (selectedProcess == null)
            {
                Console.WriteLine("ERROR: PID " + targetPid + " not found!");
                Environment.Exit(1);
            }

            TiaPortal tia = selectedProcess.Attach();
            if (tia.Projects.Count == 0)
            {
                Console.WriteLine("ERROR: No project open in TIA Portal PID " + targetPid);
                Environment.Exit(1);
            }

            Project proj = tia.Projects[0];
            if (!proj.Path.FullName.Equals(expectedPath, StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine(string.Format("ERROR: Attached project path '{0}' does not match expected '{1}'", 
                    proj.Path.FullName, expectedPath));
                Environment.Exit(1);
            }

            using (StreamWriter sw = new StreamWriter(dumpPath, false, System.Text.Encoding.UTF8))
            {
                sw.WriteLine("=== PROJECT DETAILS ===");
                sw.WriteLine("ProjectName: " + proj.Name);
                sw.WriteLine("ProjectPath: " + proj.Path.FullName);
                sw.WriteLine("TIA Portal PID: " + targetPid);
                sw.WriteLine();

                // List devices
                foreach (Device dev in proj.Devices)
                {
                    sw.WriteLine("Device: " + dev.Name + " | Type: " + dev.TypeIdentifier);
                    foreach (DeviceItem item in dev.DeviceItems)
                    {
                        DumpDeviceItem(item, sw, "  ");
                    }
                    sw.WriteLine();
                }
            }
            Console.WriteLine("SUCCESS: Project dump completed at " + dumpPath);
        }
        catch (Exception ex)
        {
            Console.WriteLine("EXCEPTION: " + ex.ToString());
            Environment.Exit(1);
        }
    }

    static void DumpDeviceItem(DeviceItem item, StreamWriter sw, string indent)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null)
        {
            sw.WriteLine(indent + "Software: " + item.Name + " | Type: " + sc.Software.GetType().Name);
            
            if (sc.Software is PlcSoftware)
            {
                var plc = sc.Software as PlcSoftware;
                sw.WriteLine(indent + "  [PLC Tags]");
                foreach (var table in plc.TagTableGroup.TagTables)
                {
                    sw.WriteLine(indent + "    Table: " + table.Name);
                    foreach (var tag in table.Tags)
                    {
                        sw.WriteLine(string.Format("{0}      Tag: {1} | DataType: {2} | Address: {3}", 
                            indent, tag.Name, tag.DataTypeName, tag.LogicalAddress));
                    }
                }
            }
            else if (sc.Software is HmiTarget)
            {
                var hmi = sc.Software as HmiTarget;
                sw.WriteLine(indent + "  [HMI Connections]");
                foreach (var conn in hmi.Connections)
                {
                    sw.WriteLine(indent + "    Connection: " + conn.Name + " | Type: " + conn.GetType().Name);
                }
                
                sw.WriteLine(indent + "  [HMI Tag Tables]");
                foreach (var table in hmi.TagFolder.TagTables)
                {
                    sw.WriteLine(indent + "    Table: " + table.Name);
                    foreach (var tag in table.Tags)
                    {
                        // Get attributes generically without typed casts
                        string connName = "None";
                        string ctrlTagName = "None";
                        
                        try {
                            // Some versions retrieve connection name as string/object attribute
                            var connAttr = tag.GetAttribute("Connection");
                            if (connAttr != null) connName = connAttr.ToString();
                        } catch {}

                        try {
                            var ctrlAttr = tag.GetAttribute("ControllerTag");
                            if (ctrlAttr != null) ctrlTagName = ctrlAttr.ToString();
                        } catch {}

                        sw.WriteLine(string.Format("{0}      Tag: {1} | Connection: {2} | ControllerTag: {3}", 
                            indent, tag.Name, connName, ctrlTagName));
                    }
                }
            }
        }

        foreach (DeviceItem child in item.DeviceItems)
        {
            DumpDeviceItem(child, sw, indent + "  ");
        }
    }
}
