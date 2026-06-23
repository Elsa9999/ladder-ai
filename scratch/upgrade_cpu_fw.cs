using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;

class UpgradeCpuFw
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to Project: " + proj.Name);

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    if (item.Name.Equals("PLC_1") || item.Name.Equals("PLC_2"))
                    {
                        UpgradeDeviceItem(item, "OrderNumber:6ES7 214-1AG40-0XB0/V4.5");
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void UpgradeDeviceItem(DeviceItem item, string targetTypeIdentifier)
    {
        Console.WriteLine(string.Format("Checking CPU '{0}' (Current: {1})", item.Name, item.TypeIdentifier));
        if (item.TypeIdentifier.Equals(targetTypeIdentifier))
        {
            Console.WriteLine("  Already at target version.");
            return;
        }

        try
        {
            Console.WriteLine("  Upgrading to " + targetTypeIdentifier + "...");
            item.ChangeType(targetTypeIdentifier);
            Console.WriteLine("    SUCCESS!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("    FAILED: " + ex.Message);
            string v42Target = targetTypeIdentifier.Replace("/V4.5", "/V4.2");
            Console.WriteLine("  Trying alternative V4.2 (" + v42Target + ")...");
            try
            {
                item.ChangeType(v42Target);
                Console.WriteLine("    SUCCESS!");
            }
            catch (Exception ex2)
            {
                Console.WriteLine("    FAILED: " + ex2.Message);
                string v46Target = targetTypeIdentifier.Replace("/V4.5", "/V4.6");
                Console.WriteLine("  Trying alternative V4.6 (" + v46Target + ")...");
                try
                {
                    item.ChangeType(v46Target);
                    Console.WriteLine("    SUCCESS!");
                }
                catch (Exception ex3)
                {
                    Console.WriteLine("    FAILED: " + ex3.Message);
                }
            }
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
