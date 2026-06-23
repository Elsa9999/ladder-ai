using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExportScadaBai3
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" EXPORT SCADA_BAI3 SCREEN");
        Console.WriteLine("========================================");

        int targetPid = 26292;
        if (args.Length > 0)
        {
            int.TryParse(args[0], out targetPid);
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
                Console.WriteLine("Lỗi: Không tìm thấy TIA Portal với PID = " + targetPid);
                return;
            }

            Console.WriteLine("Đang kết nối tới TIA Portal (PID: " + selectedProcess.Id + ")...");
            TiaPortal tia = selectedProcess.Attach();
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

            Screen targetScreen = null;
            foreach (Screen s in hmi.ScreenFolder.Screens)
            {
                if (s.Name.Equals("scadabai3", StringComparison.OrdinalIgnoreCase))
                {
                    targetScreen = s;
                    break;
                }
            }

            if (targetScreen == null)
            {
                Console.WriteLine("Không tìm thấy màn hình scadabai3!");
                return;
            }

            Console.WriteLine("Tìm thấy màn hình: " + targetScreen.Name);
            string exportPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\scadabai3_export.xml";
            if (File.Exists(exportPath))
            {
                File.Delete(exportPath);
            }

            targetScreen.Export(new FileInfo(exportPath), ExportOptions.WithDefaults);
            Console.WriteLine("Đã xuất màn hình scadabai3 sang: " + exportPath);
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
