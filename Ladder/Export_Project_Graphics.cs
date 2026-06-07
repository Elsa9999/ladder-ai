using System;
using System.IO;
using System.Linq;
using Siemens.Engineering;
using Siemens.Engineering.Hmi.Globalization;

class ExportProjectGraphics
{
    static void Main()
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL GRAPHICS EXPORTER");
        Console.WriteLine("========================================");

        string outFolder = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "test_graphics_export");
        if (!Directory.Exists(outFolder))
        {
            Directory.CreateDirectory(outFolder);
        }

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

            Console.WriteLine(string.Format("Tổng số graphic: {0}", proj.Graphics.Count));
            foreach (var graphic in proj.Graphics)
            {
                string safeName = MakeSafeFilename(graphic.Name);
                string outFile = Path.Combine(outFolder, string.Format("Graphic.{0}.xml", safeName));
                Console.WriteLine(string.Format("  - Xuất Graphic: '{0}' -> {1}", graphic.Name, Path.GetFileName(outFile)));
                try
                {
                    if (File.Exists(outFile))
                    {
                        File.Delete(outFile);
                    }
                    graphic.Export(new FileInfo(outFile), ExportOptions.WithDefaults);
                    Console.WriteLine("    SUCCESS!");
                }
                catch (Exception ex)
                {
                    Console.WriteLine(string.Format("    LỖI: {0}", ex.Message));
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
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
