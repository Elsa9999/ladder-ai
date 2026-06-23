using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;

class ExportHw
{
    static readonly string OriginalPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";

    static void Main()
    {
        Console.OutputEncoding = Encoding.UTF8;
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var t = procList[0].Attach();
            var proj = t.Projects[0];

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            Device plc1Device = null;
            DeviceItem cbItem = null;

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

            if (plc1Device != null)
            {
                Console.WriteLine("Exporting PLC1 Device to XML...");
                string devXml = @"d:\AI_Agent_PLC_LADDER_ONLY\scratch\plc1_device.xml";
                plc1Device.Export(new FileInfo(devXml), ExportOptions.WithDefaults);
                Console.WriteLine("PLC1 Device exported successfully.");
            }

            cbItem = FindCbItemRecursive(plc1Device.DeviceItems);
            if (cbItem != null)
            {
                Console.WriteLine("Exporting CB1241 DeviceItem to XML...");
                string cbXml = @"d:\AI_Agent_PLC_LADDER_ONLY\scratch\cb1241_item.xml";
                cbItem.Export(new FileInfo(cbXml), ExportOptions.WithDefaults);
                Console.WriteLine("CB1241 DeviceItem exported successfully.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static DeviceItem FindCbItemRecursive(DeviceItemComposition items)
    {
        if (items == null) return null;
        foreach (var item in items)
        {
            if (item == null) continue;
            string name = item.Name ?? "";
            string type = item.TypeIdentifier ?? "";
            if (name.Contains("1241") || type.Contains("1241"))
                return item;
            var sub = FindCbItemRecursive(item.DeviceItems);
            if (sub != null) return sub;
        }
        return null;
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
