using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class DeleteUnwantedScreens
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" DELETE UNWANTED HMI SCREENS");
        Console.WriteLine("========================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy tiến trình TIA Portal nào.");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Đã kết nối với dự án: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy thiết bị HMI nào.");
                return;
            }

            var hmi = hmiTargets[0];
            var screenFolder = hmi.ScreenFolder;
            if (screenFolder == null)
            {
                Console.WriteLine("Lỗi: Không tìm thấy thư mục Screens.");
                return;
            }

            string[] screensToDelete = { "Alarms", "Menu_Lựa_chọn", "Screen_1" };

            foreach (var screenName in screensToDelete)
            {
                var screen = screenFolder.Screens.Find(screenName);
                if (screen != null)
                {
                    Console.WriteLine(string.Format("Đang xóa màn hình: {0}...", screenName));
                    try
                    {
                        screen.Delete();
                        Console.WriteLine("  Thành công!");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("  Thất bại! Lỗi: {0}", ex.Message));
                    }
                }
                else
                {
                    Console.WriteLine(string.Format("Không tìm thấy màn hình '{0}' (đã được xóa hoặc không tồn tại).", screenName));
                }
            }

            Console.WriteLine("\nĐang lưu dự án...");
            proj.Save();
            Console.WriteLine("Đã lưu dự án thành công!");
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
