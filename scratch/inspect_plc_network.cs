using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;

class InspectPlcNetwork
{
    static void Main()
    {
        Console.WriteLine("Attaching to TIA...");
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No processes!");
                return;
            }
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Project: " + proj.Name);

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);
            Console.WriteLine("Found " + allDevices.Count + " devices.");

            foreach (var dev in allDevices)
            {
                Console.WriteLine("Device: " + dev.Name);
                FindAndPrintIp(dev);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void FindAndPrintIp(Device dev)
    {
        // Recursively find Ethernet interface
        FindIpRecursive(dev.DeviceItems);
    }

    static void FindIpRecursive(DeviceItemComposition items)
    {
        foreach (var item in items)
        {
            var net = item.GetService<NetworkInterface>();
            if (net != null)
            {
                Console.WriteLine("  Interface: " + item.Name);
                foreach (var node in net.Nodes)
                {
                    Console.WriteLine("    Node Name: " + node.Name);
                    try
                    {
                        Console.WriteLine("      IP Address: " + node.GetAttribute("IpAddress"));
                        Console.WriteLine("      Subnet Mask: " + node.GetAttribute("SubnetMask"));
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("      Failed to get attributes: " + ex.Message);
                    }
                }
            }
            FindIpRecursive(item.DeviceItems);
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
