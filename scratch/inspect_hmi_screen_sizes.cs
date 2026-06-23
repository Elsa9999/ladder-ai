using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class InspectHmiScreenSizes
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" INSPECT HMI SCREEN SIZES");
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

            // Reflect HmiTarget or try to find device/screen resolution
            Console.WriteLine("\nScreens currently in project:");
            foreach (Screen s in hmi.ScreenFolder.Screens)
            {
                Console.WriteLine(string.Format("  - Screen: '{0}'", s.Name));
                try
                {
                    // Let's reflect properties of Screen to see if width/height exist (even if not shown in standard properties)
                    // Wait, Screen is an IEngineeringObject. Let's see if we can get Width/Height attributes
                    int width = (int)s.GetAttribute("Width");
                    int height = (int)s.GetAttribute("Height");
                    Console.WriteLine(string.Format("    Size: {0} x {1}", width, height));
                }
                catch (Exception ex)
                {
                    Console.WriteLine("    Error getting size: " + ex.Message);
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
