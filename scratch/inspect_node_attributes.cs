using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;

class InspectNodeAttributes
{
    static void Main()
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            
            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                InspectRecursive(dev.DeviceItems);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void InspectRecursive(DeviceItemComposition items)
    {
        foreach (var item in items)
        {
            var net = item.GetService<NetworkInterface>();
            if (net != null)
            {
                foreach (var node in net.Nodes)
                {
                    Console.WriteLine("\nNode Name: " + node.Name);
                    foreach (var attr in node.GetAttributeInfos())
                    {
                        try
                        {
                            object val = node.GetAttribute(attr.Name);
                            Console.WriteLine("  Attribute: " + attr.Name + " = " + val);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("  Attribute: " + attr.Name + " (Error: " + ex.Message + ")");
                        }
                    }
                }
            }
            InspectRecursive(item.DeviceItems);
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
