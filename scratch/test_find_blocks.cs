using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;

class TestFindBlocks
{
    static void Main()
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];

            Console.WriteLine("Project: " + proj.Name);
            PlcSoftware plc1 = null;
            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null && software.Name.Equals("PLC_1", StringComparison.OrdinalIgnoreCase))
                    {
                        plc1 = software;
                        break;
                    }
                }
                if (plc1 != null) break;
            }

            if (plc1 == null)
            {
                Console.WriteLine("PLC_1 not found!");
                return;
            }

            Console.WriteLine("PLC_1 found. Root Block count: " + plc1.BlockGroup.Blocks.Count);
            SearchBlocks(plc1.BlockGroup, "");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void SearchBlocks(PlcBlockGroup group, string path)
    {
        string currentPath = path + "/" + group.Name;
        foreach (var block in group.Blocks)
        {
            Console.WriteLine("Block: " + block.Name + " in " + currentPath);
        }
        foreach (var subGroup in group.Groups)
        {
            SearchBlocks(subGroup, currentPath);
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
}
