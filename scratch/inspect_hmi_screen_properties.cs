using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class InspectHmiScreenProperties
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" INSPECT HMI SCREEN PROPERTIES");
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

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy HmiTarget nào.");
                return;
            }

            HmiTarget hmi = hmiTargets[0];
            Console.WriteLine("HMI Target: " + hmi.Name);

            Screen screen2 = null;
            foreach (Screen s in hmi.ScreenFolder.Screens)
            {
                if (s.Name.Equals("Screen_2", StringComparison.OrdinalIgnoreCase))
                {
                    screen2 = s;
                    break;
                }
            }

            if (screen2 == null)
            {
                Console.WriteLine("Không tìm thấy màn hình Screen_2!");
                return;
            }

            Console.WriteLine("\nĐã tìm thấy màn hình: " + screen2.Name);
            Console.WriteLine("Reflecting Screen interfaces and their properties:");
            foreach (var iface in screen2.GetType().GetInterfaces())
            {
                Console.WriteLine("  Interface: " + iface.FullName);
                foreach (var prop in iface.GetProperties())
                {
                    try
                    {
                        Console.WriteLine(string.Format("    Property: {0} ({1})", prop.Name, prop.PropertyType.Name));
                    }
                    catch {}
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
        {
            targets.Add(sc.Software as HmiTarget);
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, targets);
        }
    }
}
