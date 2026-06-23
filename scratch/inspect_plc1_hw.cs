using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;

class InspectPlc1Hw
{
    static readonly string OriginalPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";

    static void Main()
    {
        Console.OutputEncoding = Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" PLC_1 HARDWARE INVENTORY PROBER");
        Console.WriteLine("=================================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            TiaPortal tia = null;
            Project proj = null;
            for (int i = 0; i < procList.Count; i++)
            {
                try
                {
                    var t = procList[i].Attach();
                    if (t.Projects.Count > 0)
                    {
                        var p = t.Projects[0];
                        string actualPath = Path.GetFullPath(p.Path.FullName);
                        string expectedPath = Path.GetFullPath(OriginalPath);
                        if (string.Equals(actualPath, expectedPath, StringComparison.OrdinalIgnoreCase))
                        {
                            tia = t;
                            proj = p;
                            break;
                        }
                    }
                }
                catch {}
            }

            if (proj == null)
            {
                Console.WriteLine("ERROR: cuocthi_tdh project not found open in any TIA instance!");
                return;
            }

            Console.WriteLine("Attached to Project: " + proj.Name);

            // Find PLC1 Device
            Device plc1Device = null;
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
                            plc1Device = dev;
                            break;
                        }
                    }
                }
                if (plc1Device != null) break;
            }

            if (plc1Device == null)
            {
                Console.WriteLine("ERROR: PLC_1 device not found!");
                return;
            }

            Console.WriteLine("\n[INVENTORY] Device Name: " + plc1Device.Name + " (Type: " + plc1Device.TypeIdentifier + ")");
            Console.WriteLine("Listing all Device Items recursively:");
            PrintDeviceItemsRecursive(plc1Device.DeviceItems, "  ");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void PrintDeviceItemsRecursive(DeviceItemComposition items, string indent)
    {
        foreach (var item in items)
        {
            string typeId = item.TypeIdentifier;
            string orderNum = GetAttributeSafe(item, "OrderNumber");
            string slot = GetAttributeSafe(item, "PositionNumber"); 
            string hwId = GetAttributeSafe(item, "HardwareIdentifier");

            Console.WriteLine(string.Format("{0}- Name: {1}", indent, item.Name));
            Console.WriteLine(string.Format("{0}  Type: {1}", indent, typeId));
            if (!string.IsNullOrEmpty(orderNum))
                Console.WriteLine(string.Format("{0}  Order Number: {1}", indent, orderNum));
            if (!string.IsNullOrEmpty(slot))
                Console.WriteLine(string.Format("{0}  Slot/Position: {1}", indent, slot));
            if (!string.IsNullOrEmpty(hwId))
                Console.WriteLine(string.Format("{0}  Hardware ID: {1}", indent, hwId));

            PrintDeviceItemsRecursive(item.DeviceItems, indent + "  ");
        }
    }

    static string GetAttributeSafe(DeviceItem item, string attributeName)
    {
        try
        {
            var val = item.GetAttribute(attributeName);
            return val != null ? val.ToString() : "";
        }
        catch
        {
            return "";
        }
    }

    static void GetDevicesRecursive(Project project, List<Device> allDevices)
    {
        foreach (var dev in project.Devices) allDevices.Add(dev);
        if (project.UngroupedDevicesGroup != null)
        {
            foreach (var dev in project.UngroupedDevicesGroup.Devices) allDevices.Add(dev);
        }
        CollectGroups(project.DeviceGroups, allDevices);
    }

    static void CollectGroups(DeviceUserGroupComposition groups, List<Device> allDevices)
    {
        foreach (var g in groups)
        {
            foreach (var d in g.Devices) allDevices.Add(d);
            CollectGroups(g.Groups, allDevices);
        }
    }
}
