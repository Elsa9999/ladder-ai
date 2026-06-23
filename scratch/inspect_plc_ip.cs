using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;

class InspectPlcIp
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
                Console.WriteLine("\nDevice Name: " + dev.Name);
                InspectDeviceItemsRecursive(dev.DeviceItems);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void InspectDeviceItemsRecursive(DeviceItemComposition items)
    {
        foreach (var item in items)
        {
            // If the item represents a network interface
            if (item.Name.Contains("PROFINET") || item.Name.Contains("Ethernet") || item.Name.Contains("Interface"))
            {
                Console.WriteLine("  DeviceItem Name: " + item.Name + " (Type: " + item.GetType().Name + ")");
                try
                {
                    foreach (var attr in item.GetAttributeInfos())
                    {
                        if (attr.Name.Contains("Address") || attr.Name.Contains("IP") || attr.Name.Contains("Subnet"))
                        {
                            try
                            {
                                object val = item.GetAttribute(attr.Name);
                                Console.WriteLine("    Attribute: " + attr.Name + " = " + val);
                            }
                            catch {}
                        }
                    }
                }
                catch {}
            }
            InspectDeviceItemsRecursive(item.DeviceItems);
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
