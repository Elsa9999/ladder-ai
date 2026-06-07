using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExportHmiScreens
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI SCREENS EXPORTER");
        Console.WriteLine("========================================");

        string outFolder = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "test_hmi_screens_export");
        if (args.Length > 0)
        {
            outFolder = args[0];
        }

        if (!Directory.Exists(outFolder))
        {
            Directory.CreateDirectory(outFolder);
        }

        Console.WriteLine(string.Format("Output Folder: {0}", outFolder));

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
                
                // Root Screen Folder
                var rootFolder = hmiTarget.ScreenFolder;
                if (rootFolder != null)
                {
                    ExportScreensInFolder(rootFolder.Screens, outFolder, "");
                    ExportNestedFolders(rootFolder.Folders, outFolder, "");
                }
            }

            Console.WriteLine("\n========================================");
            Console.WriteLine("HOÀN THÀNH XUẤT CÁC MÀN HÌNH HMI!");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine(string.Format("LỖI HỆ THỐNG: {0}", ex.ToString()));
        }
    }

    static void ExportScreensInFolder(ScreenComposition screens, string outFolder, string currentPath)
    {
        foreach (Screen screen in screens)
        {
            string safeName = MakeSafeFilename(screen.Name);
            string displayPath = string.IsNullOrEmpty(currentPath) ? safeName : currentPath + "_" + safeName;
            string outFile = Path.Combine(outFolder, string.Format("Hmi.Screen.{0}.xml", displayPath));
            Console.WriteLine(string.Format("  - Xuất Màn hình: '{0}' -> {1}", screen.Name, Path.GetFileName(outFile)));
            try
            {
                if (File.Exists(outFile))
                {
                    File.Delete(outFile);
                }
                screen.Export(new FileInfo(outFile), ExportOptions.WithDefaults);
                Console.WriteLine("    SUCCESS!");
            }
            catch (Exception ex)
            {
                Console.WriteLine(string.Format("    LỖI: {0}", ex.Message));
            }
        }
    }

    static void ExportNestedFolders(ScreenUserFolderComposition folders, string outFolder, string currentPath)
    {
        foreach (ScreenUserFolder folder in folders)
        {
            string folderSafe = MakeSafeFilename(folder.Name);
            string newPath = string.IsNullOrEmpty(currentPath) ? folderSafe : currentPath + "_" + folderSafe;
            Console.WriteLine(string.Format("  Thư mục: '{0}'", folder.Name));
            ExportScreensInFolder(folder.Screens, outFolder, newPath);
            ExportNestedFolders(folder.Folders, outFolder, newPath);
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

    static string MakeSafeFilename(string name)
    {
        foreach (char c in Path.GetInvalidFileNameChars())
        {
            name = name.Replace(c, '_');
        }
        return name;
    }
}
