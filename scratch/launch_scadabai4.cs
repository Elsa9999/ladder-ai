using System;
using System.IO;
using Siemens.Engineering;

class LaunchScadabai4
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" LAUNCHING TIA PORTAL WITH SCADABAI4");
        Console.WriteLine("========================================");

        try
        {
            string projectPath = @"D:\tonghopscada\scadabai4_V18\scadabai4_V18.ap18";
            if (!File.Exists(projectPath))
            {
                Console.WriteLine("Lỗi: Không tìm thấy tệp dự án TIA tại: " + projectPath);
                return;
            }

            Console.WriteLine("Đang khởi chạy TIA Portal với giao diện người dùng (UI)...");
            TiaPortal tia = new TiaPortal(TiaPortalMode.WithUserInterface);
            Console.WriteLine("TIA Portal đã khởi chạy thành công.");

            Console.WriteLine("Đang mở dự án: " + projectPath);
            Project project = tia.Projects.Open(new FileInfo(projectPath));
            Console.WriteLine("Đã mở dự án thành công: " + project.Name);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống khi khởi chạy TIA: " + ex.ToString());
        }
    }
}
