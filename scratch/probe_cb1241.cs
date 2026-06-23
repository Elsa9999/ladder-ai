using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;

class ProbeCb1241
{
    static void Main()
    {
        Console.OutputEncoding = Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" CB 1241 DETAILED PROBER");
        Console.WriteLine("=================================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No TIA processes!");
                return;
            }

            var t = procList[0].Attach();
            var proj = t.Projects[0];
            Console.WriteLine("Attached to: " + proj.Name);

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            DeviceItem cbItem = null;
            foreach (var dev in allDevices)
            {
                cbItem = FindCbItemRecursive(dev.DeviceItems);
                if (cbItem != null) break;
            }

            if (cbItem == null)
            {
                Console.WriteLine("CB 1241 (RS485) device item not found!");
                return;
            }

            Console.WriteLine("\nFound CB 1241!");
            Console.WriteLine("Item Name: " + cbItem.Name);
            Console.WriteLine("Item TypeIdentifier: " + cbItem.TypeIdentifier);

            // Let's try to query common attributes
            string[] attrs = new string[] {
                "HardwareIdentifier", "HardwareId", "SlotNumber", "PositionNumber", "OrderNumber",
                "FirmwareVersion", "Author", "Comment", "Label", "Description"
            };

            foreach (var attr in attrs)
            {
                try
                {
                    var val = cbItem.GetAttribute(attr);
                    Console.WriteLine(string.Format("  Attribute '{0}' = '{1}'", attr, val));
                }
                catch {}
            }

            // Query HwIdentifierController
            var controller = cbItem.GetService<HwIdentifierController>();
            if (controller != null)
            {
                Console.WriteLine("\nHwIdentifierController found!");
                try
                {
                    foreach (var assoc in controller.RegisteredHwIdentifiers)
                    {
                        Console.WriteLine("  HwIdentifier Association Item: " + assoc.ToString());
                        // Try to get properties of assoc
                        foreach (var prop in assoc.GetType().GetProperties())
                        {
                            try
                            {
                                Console.WriteLine(string.Format("    Property: {0} = {1}", prop.Name, prop.GetValue(assoc, null)));
                            }
                            catch {}
                        }
                    }
                }
                catch (Exception assocEx)
                {
                    Console.WriteLine("  Error reading association: " + assocEx.Message);
                }
            }
            else
            {
                Console.WriteLine("\nHwIdentifierController not supported on this item.");
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
