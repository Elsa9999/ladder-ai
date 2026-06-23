using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;

class ListProjectGraphics
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" LIST PROJECT GRAPHICS VIA OPENNESS");
        Console.WriteLine("========================================");

        try
        {
            // Load Siemens.Engineering assembly dynamically
            Assembly engAssembly = Assembly.LoadFrom(@"D:\AI_Agent_PLC_LADDER_ONLY\Ladder\Siemens.Engineering.dll");
            
            // Get types
            Type tiaPortalType = engAssembly.GetType("Siemens.Engineering.TiaPortal");
            
            // Get running processes
            var getProcessesMethod = tiaPortalType.GetMethod("GetProcesses", BindingFlags.Public | BindingFlags.Static);
            dynamic processes = getProcessesMethod.Invoke(null, null);
            
            if (processes.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy tiến trình TIA Portal nào đang chạy!");
                return;
            }

            dynamic tia = processes[0].Attach();
            dynamic proj = tia.Projects[0];
            Console.WriteLine("Đã kết nối với Dự án: " + proj.Name);

            // Get proj.Graphics
            dynamic graphics = proj.Graphics;
            Console.WriteLine("Số lượng ảnh trong Project Graphics: " + graphics.Count);
            
            foreach (dynamic graphic in graphics)
            {
                Console.WriteLine(string.Format("  - Graphic: {0} (ID: {1})", graphic.Name, graphic.Parent != null ? "Yes" : "No"));
            }
            
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }
}
