using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExportActiveLoginScreen
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" EXPORT ACTIVE LOGIN SCREEN");
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

            Screen loginScreen = null;
            foreach (Screen s in hmi.ScreenFolder.Screens)
            {
                if (s.Name.Equals("Login/out", StringComparison.OrdinalIgnoreCase) || s.Name.Contains("Login"))
                {
                    loginScreen = s;
                    break;
                }
            }

            if (loginScreen == null)
            {
                Console.WriteLine("Không tìm thấy màn hình Login/out!");
                return;
            }

            Console.WriteLine("Tìm thấy màn hình: " + loginScreen.Name);
            string exportPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\active_login_screen_export.xml";
            if (File.Exists(exportPath))
            {
                File.Delete(exportPath);
            }

            loginScreen.Export(new FileInfo(exportPath), ExportOptions.WithDefaults);
            Console.WriteLine("Đã xuất màn hình hoạt động sang: " + exportPath);
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
