using System;
using System.IO;
using Siemens.Engineering;

class LaunchTia
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" LAUNCHING TIA PORTAL");
        Console.WriteLine("========================================");

        try
        {
            string projectPath = @"C:\Users\lienb\Downloads\Liên Gia Bảo_V18\Liên Gia Bảo_V18.ap18";
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
