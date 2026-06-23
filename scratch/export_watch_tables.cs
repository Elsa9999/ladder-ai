using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.WatchAndForceTables;

class ExportWatchTables
{
    static void Main()
    {
        Console.WriteLine("Start ExportWatchTables...");
        try
        {
            var procList = TiaPortal.GetProcesses();
            Console.WriteLine("Processes found: " + procList.Count);
            if (procList.Count == 0) return;
            
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to Project: " + proj.Name);
            
            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);
            Console.WriteLine("Devices count: " + allDevices.Count);

            foreach (var dev in allDevices)
            {
                Console.WriteLine("Device: " + dev.Name);
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null)
                    {
                        Console.WriteLine("  PLC Software: " + software.Name);
                        var wts = software.WatchAndForceTableGroup.WatchTables;
                        Console.WriteLine("    Watch tables count: " + wts.Count);
                        foreach (var wt in wts)
                        {
                            Console.WriteLine("      Watch table: " + wt.Name);
                            try
                            {
                                string outPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, wt.Name + ".xml");
                                wt.Export(new FileInfo(outPath), ExportOptions.WithDefaults);
                                Console.WriteLine("        Exported to: " + outPath);
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine("        Export failed: " + ex.Message);
                            }
                        }
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static PlcSoftware GetPlcSoftware(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware) return sc.Software as PlcSoftware;
        foreach (var child in item.DeviceItems)
        {
            var sw = GetPlcSoftware(child);
            if (sw != null) return sw;
        }
        return null;
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
