using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ImportScreenOnly
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI SCREEN ONLY IMPORTER");
        Console.WriteLine("========================================");

        string screensDir = @"d:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens";

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
            Console.WriteLine("Đã kết nối với Dự án: " + proj.Name);

            // --- Tìm HMI Target ---
            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }
            foreach (var devGrp in proj.DeviceGroups)
            {
                ScanGroup(devGrp, hmiTargets);
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy thiết bị HMI (HmiTarget) nào.");
                return;
            }

            var hmiTarget = hmiTargets[0];
            Console.WriteLine("HMI Target: " + hmiTarget.Name);
            
            var rootFolder = hmiTarget.ScreenFolder;
            if (rootFolder != null)
            {
                if (Directory.Exists(screensDir))
                {
                    var files = Directory.GetFiles(screensDir, "Hmi.Screen.*.xml");
                    Console.WriteLine("Tìm thấy " + files.Length + " file màn hình cần nạp.");
                    foreach (var file in files)
                    {
                        string fileName = Path.GetFileNameWithoutExtension(file);
                        string screenName = fileName;
                        if (screenName.StartsWith("Hmi.Screen."))
                        {
                            screenName = screenName.Substring("Hmi.Screen.".Length);
                        }

                        Console.WriteLine("Đang xử lý màn hình HMI: '" + screenName + "'...");

                        // Tìm và xóa màn hình cũ để tránh lỗi trùng số màn hình (Screen Number conflict)
                        Screen existingScreen = null;
                        foreach (Screen s in rootFolder.Screens)
                        {
                            if (s.Name.Equals(screenName, StringComparison.OrdinalIgnoreCase))
                            {
                                existingScreen = s;
                                break;
                            }
                        }

                        if (existingScreen != null)
                        {
                            Console.WriteLine("  Xóa màn hình cũ '" + screenName + "'...");
                            try
                            {
                                existingScreen.Delete();
                                Console.WriteLine("    [Xóa OK]");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine("    [Xóa THẤT BẠI]: " + ex.Message);
                            }
                        }

                        // Thực hiện nạp
                        Console.WriteLine("  Nạp màn hình từ tệp " + Path.GetFileName(file) + "...");
                        try
                        {
                            rootFolder.Screens.Import(new FileInfo(file), ImportOptions.Override);
                            Console.WriteLine("    [Nạp THÀNH CÔNG!]");
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("    [Nạp THẤT BẠI!]: " + ex.Message);
                        }
                    }
                }
                else
                {
                    Console.WriteLine("Lỗi: Không tìm thấy thư mục Screens '" + screensDir + "'");
                }
            }

            Console.WriteLine("\n========================================");
            Console.WriteLine("HOÀN THÀNH QUÁ TRÌNH NẠP MÀN HÌNH HMI!");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine("LỖI HỆ THỐNG: " + ex.ToString());
        }
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null)
        {
            HmiTarget ht = sc.Software as HmiTarget;
            if (ht != null) targets.Add(ht);
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, targets);
        }
    }

    static void ScanGroup(DeviceUserGroup g, List<HmiTarget> targets)
    {
        foreach (var dev in g.Devices)
        {
            foreach (var item in dev.DeviceItems)
            {
                FindHmiTargets(item, targets);
            }
        }
        foreach (var sub in g.Groups)
        {
            ScanGroup(sub, targets);
        }
    }
}
