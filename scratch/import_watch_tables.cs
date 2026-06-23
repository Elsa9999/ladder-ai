using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW.WatchAndForceTables;

class ImportWatchTables
{
    static void Main()
    {
        Console.WriteLine("=================================================");
        Console.WriteLine(" TIA OPENNESS WATCH TABLE IMPORTER");
        Console.WriteLine("=================================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Error: No running TIA Portal instances found!");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to Project: " + proj.Name);

            // Search PLCs
            PlcSoftware plc1 = null;
            PlcSoftware plc2 = null;

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is PlcSoftware)
                    {
                        var software = (PlcSoftware)sc.Software;
                        if (software.Name.Equals("PLC_1", StringComparison.OrdinalIgnoreCase))
                        {
                            plc1 = software;
                        }
                        else if (software.Name.Equals("PLC_2", StringComparison.OrdinalIgnoreCase))
                        {
                            plc2 = software;
                        }
                    }
                }
            }

            if (plc1 == null)
            {
                Console.WriteLine("Warning: PLC_1 not found in project!");
            }
            if (plc2 == null)
            {
                Console.WriteLine("Warning: PLC_2 not found in project!");
            }

            string xmlDir = @"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\watch_tables\xml";
            if (!Directory.Exists(xmlDir))
            {
                Console.WriteLine("Error: XML directory does not exist: " + xmlDir);
                return;
            }

            string[] xmlFiles = Directory.GetFiles(xmlDir, "*.xml");
            if (xmlFiles.Length == 0)
            {
                Console.WriteLine("Error: No XML files found in " + xmlDir);
                return;
            }

            foreach (var xmlFile in xmlFiles)
            {
                string fileName = Path.GetFileNameWithoutExtension(xmlFile);
                PlcSoftware targetPlc = null;

                if (fileName.StartsWith("WT_PLC1_", StringComparison.OrdinalIgnoreCase))
                {
                    targetPlc = plc1;
                }
                else if (fileName.StartsWith("WT_PLC2_", StringComparison.OrdinalIgnoreCase))
                {
                    targetPlc = plc2;
                }

                if (targetPlc == null)
                {
                    Console.WriteLine("Skipping " + fileName + " (cannot determine target PLC)");
                    continue;
                }

                Console.WriteLine("\nImporting Watch Table '" + fileName + "' into PLC: " + targetPlc.Name);
                try
                {
                    var wts = targetPlc.WatchAndForceTableGroup.WatchTables;
                    var existing = wts.Find(fileName);
                    if (existing != null)
                    {
                        existing.Delete();
                        Console.WriteLine("  Deleted existing watch table.");
                    }

                    wts.Import(new FileInfo(xmlFile), ImportOptions.None);
                    Console.WriteLine("  Imported watch table successfully.");
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  Failed to import watch table: " + ex.Message);
                }
            }

            Console.WriteLine("\nWatch table import process completed.");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void GetDevicesRecursive(Project project, List<Device> allDevices)
    {
        AddDevices(project.Devices, allDevices);
        if (project.UngroupedDevicesGroup != null)
        {
            AddDevices(project.UngroupedDevicesGroup.Devices, allDevices);
        }
        AddUserGroupsRecursive(project.DeviceGroups, allDevices);
    }

    static void AddDevices(DeviceComposition devices, List<Device> allDevices)
    {
        foreach (var dev in devices)
        {
            allDevices.Add(dev);
        }
    }

    static void AddUserGroupsRecursive(DeviceUserGroupComposition groups, List<Device> allDevices)
    {
        foreach (var group in groups)
        {
            AddDevices(group.Devices, allDevices);
            AddUserGroupsRecursive(group.Groups, allDevices);
        }
    }
}
