using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.TextGraphicList;

class AgentTIAHmiExporter
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI TEXT/GRAPHIC LIST EXPORTER");
        Console.WriteLine("========================================");

        string outFolder = AppDomain.CurrentDomain.BaseDirectory;
        if (args.Length > 0)
        {
            outFolder = args[0];
        }

        if (!Directory.Exists(outFolder))
        {
            try
            {
                Directory.CreateDirectory(outFolder);
            }
            catch (Exception ex)
            {
                Console.WriteLine(string.Format("Lỗi: Không thể tạo thư mục đầu ra '{0}'. {1}", outFolder, ex.Message));
                return;
            }
        }

        Console.WriteLine(string.Format("Thư mục đầu ra: {0}", outFolder));

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
                Console.WriteLine("Lỗi: Không tìm thấy thiết bị hoặc ứng dụng HMI (HmiTarget) nào trong dự án.");
                return;
            }

            foreach (var hmiTarget in hmiTargets)
            {
                Console.WriteLine(string.Format("\nĐang xử lý thiết bị HMI: {0}", hmiTarget.Name));

                // 1. XUẤT TEXT LISTS
                Console.WriteLine("  --- Đang xuất Text Lists ---");
                foreach (TextList textList in hmiTarget.TextLists)
                {
                    string safeName = MakeSafeFilename(textList.Name);
                    string outFile = Path.Combine(outFolder, string.Format("Hmi.TextList.{0}.xml", safeName));
                    Console.WriteLine(string.Format("  - Xuất Text List: '{0}' -> {1}", textList.Name, Path.GetFileName(outFile)));
                    try
                    {
                        if (File.Exists(outFile))
                        {
                            File.Delete(outFile);
                        }
                        textList.Export(new FileInfo(outFile), ExportOptions.WithDefaults);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("    LỖI: {0}", ex.Message));
                    }
                }

                // 2. XUẤT GRAPHIC LISTS
                Console.WriteLine("  --- Đang xuất Graphic Lists ---");
                foreach (GraphicList graphicList in hmiTarget.GraphicLists)
                {
                    string safeName = MakeSafeFilename(graphicList.Name);
                    string outFile = Path.Combine(outFolder, string.Format("Hmi.GraphicList.{0}.xml", safeName));
                    Console.WriteLine(string.Format("  - Xuất Graphic List: '{0}' -> {1}", graphicList.Name, Path.GetFileName(outFile)));
                    try
                    {
                        if (File.Exists(outFile))
                        {
                            File.Delete(outFile);
                        }
                        graphicList.Export(new FileInfo(outFile), ExportOptions.WithDefaults);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("    LỖI: {0}", ex.Message));
                    }
                }
            }

            Console.WriteLine("\n========================================");
            Console.WriteLine("HOÀN THÀNH XUẤT DỮ LIỆU HMI!");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine(string.Format("LỖI HỆ THỐNG NGHIÊM TRỌNG: {0}", ex.Message));
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
