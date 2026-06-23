using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Globalization;

class ImportBgGraphic
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" IMPORT PROJECT GRAPHIC");
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

            string xmlPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\exported_bg_graphic.xml";
            if (!File.Exists(xmlPath))
            {
                Console.WriteLine("Lỗi: Không tìm thấy file XML: " + xmlPath);
                return;
            }

            Console.WriteLine("Đang nhập graphic từ file " + Path.GetFileName(xmlPath) + "...");
            // MultiLingualGraphicComposition.Import takes (FileInfo, ImportOptions)
            proj.Graphics.Import(new FileInfo(xmlPath), ImportOptions.Override);
            Console.WriteLine("Đã nhập graphic thành công!");

            // Save project
            proj.Save();
            Console.WriteLine("Đã lưu dự án!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }
}
