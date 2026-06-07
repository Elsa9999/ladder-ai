using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ImportTestScreen
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI SCREEN IMPORTER TEST");
        Console.WriteLine("========================================");

        string screenFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "test_hmi_screens_export", "Hmi.Screen.Test_Import_Screen.xml");
        if (args.Length > 0)
        {
            screenFilePath = args[0];
        }

        if (!File.Exists(screenFilePath))
        {
            Console.WriteLine(string.Format("Lỗi: Không tìm thấy tệp XML màn hình '{0}'", screenFilePath));
            return;
        }

        Console.WriteLine(string.Format("Tệp màn hình import: {0}", screenFilePath));

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy tiến trình TIA Portal nào đang chạy!");
                return;
            }

            Console.WriteLine("Đang kết nối tới TIA Portal...");
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine(string.Format("Đã kết nối với Dự án: {0}", proj.Name));

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
                Console.WriteLine("Lỗi: Không tìm thấy thiết bị HMI (HmiTarget) nào.");
                return;
            }

            foreach (var hmiTarget in hmiTargets)
            {
                Console.WriteLine(string.Format("\nĐang xử lý thiết bị HMI: {0}", hmiTarget.Name));
                
                var rootFolder = hmiTarget.ScreenFolder;
                if (rootFolder != null)
                {
                    Console.WriteLine("Đang import màn hình vào root ScreenFolder...");
                    try
                    {
                        var importedScreens = rootFolder.Screens.Import(new FileInfo(screenFilePath), ImportOptions.Override);
                        if (importedScreens != null && importedScreens.Count > 0)
                        {
                            Console.WriteLine(string.Format("THÀNH CÔNG! Đã import màn hình: '{0}'", importedScreens[0].Name));
                        }
                        else
                        {
                            Console.WriteLine("THÀNH CÔNG! (Openness không trả về đối tượng màn hình nhưng quá trình import hoàn tất)");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("THẤT BẠI! Lỗi: {0}", ex.Message));
                    }
                }
                else
                {
                    Console.WriteLine("Lỗi: root ScreenFolder của HMI target bằng null.");
                }
            }

            Console.WriteLine("\n========================================");
            Console.WriteLine("HOÀN THÀNH THỬ NGHIỆM IMPORT!");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine(string.Format("LỖI HỆ THỐNG: {0}", ex.ToString()));
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
