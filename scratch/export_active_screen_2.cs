using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExportActiveScreen2
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" EXPORT ACTIVE SCREEN_2 WITH PID");
        Console.WriteLine("========================================");

        int targetPid = -1;
        if (args.Length > 0)
        {
            if (int.TryParse(args[0], out targetPid))
            {
                Console.WriteLine("Target PID: " + targetPid);
            }
        }

        try
        {
            var processes = TiaPortal.GetProcesses();
            if (processes.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy TIA Portal.");
                return;
            }

            TiaPortalProcess selectedProcess = null;
            if (targetPid != -1)
            {
                foreach (var proc in processes)
                {
                    if (proc.Id == targetPid)
                    {
                        selectedProcess = proc;
                        break;
                    }
                }
                if (selectedProcess == null)
                {
                    Console.WriteLine("Lỗi: Không tìm thấy tiến trình TIA Portal với PID = " + targetPid);
                    return;
                }
            }
            else
            {
                // Default fallback: find the one that has an open project, or just the first one
                Console.WriteLine("Không chỉ định PID. Sử dụng tiến trình đầu tiên.");
                selectedProcess = processes[0];
            }

            Console.WriteLine("Đang kết nối tới TIA Portal (PID: " + selectedProcess.Id + ")...");
            TiaPortal tia = selectedProcess.Attach();
            Console.WriteLine("Đã kết nối thành công.");

            if (tia.Projects.Count == 0)
            {
                Console.WriteLine("Lỗi: Không có dự án nào đang mở trong tiến trình này.");
                return;
            }

            Project proj = tia.Projects[0];
            Console.WriteLine("Dự án: " + proj.Name + " (" + proj.Path + ")");

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

            Console.WriteLine("Tìm thấy màn hình: " + screen2.Name);
            string exportPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\active_screen_2_export.xml";
            if (File.Exists(exportPath))
            {
                File.Delete(exportPath);
            }

            screen2.Export(new FileInfo(exportPath), ExportOptions.WithDefaults);
            Console.WriteLine("Đã xuất màn hình Screen_2 hoạt động sang: " + exportPath);
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
