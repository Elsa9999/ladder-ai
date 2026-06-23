using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;

class ListAllBlocks
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No TIA Portal instances found!");
                return;
            }
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to project: " + proj.Name);

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null)
                    {
                        Console.WriteLine("\n=========================================");
                        Console.WriteLine(" PLC: " + software.Name);
                        Console.WriteLine("=========================================");
                        PrintBlocksInGroup(software.BlockGroup, "");
                    }
                }
            }
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

    static void PrintBlocksInGroup(PlcBlockGroup group, string indent)
    {
        Console.WriteLine(indent + "[Group] " + group.Name);
        foreach (var block in group.Blocks)
        {
            Console.WriteLine(indent + "  - " + block.Name + " (" + block.GetType().Name + ", Number: " + block.Number + ")");
        }
        foreach (var subGroup in group.Groups)
        {
            PrintBlocksInGroup(subGroup, indent + "  ");
        }
    }
}
