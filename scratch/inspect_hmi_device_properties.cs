using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;

class InspectHmiDeviceProperties
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" INSPECT HMI DEVICE PROPERTIES");
        Console.WriteLine("========================================");

        try
        {
            var processes = TiaPortal.GetProcesses();
            if (processes.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy TIA Portal.");
                return;
            }

            TiaPortal tia = processes[0].Attach();
            Project proj = tia.Projects[0];
            Console.WriteLine("Dự án: " + proj.Name);

            foreach (Device dev in proj.Devices)
            {
                Console.WriteLine("\nDevice: " + dev.Name + " (Type: " + dev.TypeIdentifier + ")");
                PrintDeviceItemRecursive(dev, "  ");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }

    static void PrintDeviceItemRecursive(IEngineeringObject obj, string indent)
    {
        // Print attributes of this object
        try
        {
            foreach (var info in obj.GetAttributeInfos())
            {
                try
                {
                    object val = obj.GetAttribute(info.Name);
                    Console.WriteLine(string.Format("{0}- Attr: {1} = {2}", indent, info.Name, val ?? "null"));
                }
                catch {}
            }
        }
        catch {}

        // Check if it's a DeviceItem
        DeviceItem item = obj as DeviceItem;
        if (item != null)
        {
            foreach (DeviceItem child in item.DeviceItems)
            {
                Console.WriteLine(string.Format("{0}Child DeviceItem: '{1}' (Type: '{2}')", indent, child.Name, child.TypeIdentifier));
                PrintDeviceItemRecursive(child, indent + "  ");
            }
        }
        
        // Check if it's a Device
        Device dev = obj as Device;
        if (dev != null)
        {
            foreach (DeviceItem child in dev.DeviceItems)
            {
                Console.WriteLine(string.Format("{0}Child DeviceItem: '{1}' (Type: '{2}')", indent, child.Name, child.TypeIdentifier));
                PrintDeviceItemRecursive(child, indent + "  ");
            }
        }
    }
}
