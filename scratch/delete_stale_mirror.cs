using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;

class DeleteStaleMirror
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" TIA OPENNESS STALE BLOCK CLEANER");
        Console.WriteLine("=================================================");

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

            List<PlcSoftware> softwares = new List<PlcSoftware>();
            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null && !softwares.Contains(software))
                    {
                        softwares.Add(software);
                    }
                }
            }

            foreach (var plcSoftware in softwares)
            {
                Console.WriteLine("\nChecking PLC: " + plcSoftware.Name);
                DeleteBlockRecursive(plcSoftware.BlockGroup, "FC_HMI_Mirror");
            }

            Console.WriteLine("\nCleanup process completed.");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void DeleteBlockRecursive(PlcBlockGroup group, string blockName)
    {
        var block = group.Blocks.Find(blockName);
        if (block != null)
        {
            Console.WriteLine(string.Format("Found block '{0}' (ID: {1}) in group '{2}'. Deleting...", blockName, block.Number, group.Name));
            try
            {
                block.Delete();
                Console.WriteLine("Deleted successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to delete: " + ex.Message);
            }
        }

        foreach (var subGroup in group.Groups)
        {
            DeleteBlockRecursive(subGroup, blockName);
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
