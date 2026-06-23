using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Globalization;

class ExportAllGraphics
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" EXPORT ALL PROJECT GRAPHICS");
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

            string exportDir = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\exported_graphics";
            if (Directory.Exists(exportDir))
            {
                Directory.Delete(exportDir, true);
            }
            Directory.CreateDirectory(exportDir);

            MultiLingualGraphicComposition graphics = proj.Graphics;
            Console.WriteLine("Số lượng ảnh: " + graphics.Count);

            foreach (MultiLingualGraphic g in graphics)
            {
                try
                {
                    // Clean name for file system
                    string cleanName = g.Name;
                    foreach (char c in Path.GetInvalidFileNameChars())
                    {
                        cleanName = cleanName.Replace(c, '_');
                    }

                    string xmlPath = Path.Combine(exportDir, cleanName + ".xml");
                    Console.WriteLine("Đang xuất graphic: " + g.Name);
                    g.Export(new FileInfo(xmlPath), ExportOptions.WithDefaults);
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  Lỗi khi xuất " + g.Name + ": " + ex.Message);
                }
            }

            Console.WriteLine("\n========================================");
            Console.WriteLine("Danh sách các file ảnh đã xuất:");
            foreach (var file in Directory.GetFiles(exportDir, "*.png", SearchOption.AllDirectories))
            {
                FileInfo fi = new FileInfo(file);
                Console.WriteLine(string.Format("  - File: {0} ({1:F2} MB)", Path.GetFileName(file), (double)fi.Length / 1024 / 1024));
            }
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }
}
