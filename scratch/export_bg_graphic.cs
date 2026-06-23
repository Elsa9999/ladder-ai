using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Globalization;

class ExportBgGraphic
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" EXPORT PROJECT GRAPHIC");
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

            MultiLingualGraphicComposition graphics = proj.Graphics;
            MultiLingualGraphic targetGraphic = null;
            foreach (MultiLingualGraphic g in graphics)
            {
                if (g.Name == "9e382997-af09-41cf-ab1c-3299fad62071")
                {
                    targetGraphic = g;
                    break;
                }
            }

            if (targetGraphic == null)
            {
                Console.WriteLine("Không tìm thấy graphic: 9e382997-af09-41cf-ab1c-3299fad62071");
                return;
            }

            Console.WriteLine("Đang xuất graphic " + targetGraphic.Name + "...");
            string exportPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\exported_bg_graphic.xml";
            if (File.Exists(exportPath))
            {
                File.Delete(exportPath);
            }

            targetGraphic.Export(new FileInfo(exportPath), ExportOptions.WithDefaults);
            Console.WriteLine("Đã xuất thành công sang: " + exportPath);

            // Let's check if there are associated folders/files
            string directory = Path.GetDirectoryName(exportPath);
            string baseName = Path.GetFileNameWithoutExtension(exportPath);
            Console.WriteLine("\nKiểm tra thư mục xuất:");
            foreach (var file in Directory.GetFiles(directory, baseName + "*"))
            {
                Console.WriteLine("  - File: " + Path.GetFileName(file) + " (Size: " + new FileInfo(file).Length + " bytes)");
            }
            string subDir = Path.Combine(directory, baseName + "_Files");
            if (Directory.Exists(subDir))
            {
                Console.WriteLine("  - Thư mục con: " + Path.GetFileName(subDir));
                foreach (var file in Directory.GetFiles(subDir, "*", SearchOption.AllDirectories))
                {
                    Console.WriteLine("    * File con: " + Path.GetFileName(file) + " (Size: " + new FileInfo(file).Length + " bytes)");
                }
            }
            else
            {
                Console.WriteLine("  - Không tìm thấy thư mục con hình ảnh!");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }
}
