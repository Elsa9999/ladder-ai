using System;
using System.IO;
using Siemens.Engineering;

class LaunchCuocThiTdh
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" LAUNCHING TIA PORTAL & cuocthi_tdh PROJECT");
        Console.WriteLine("========================================");

        try
        {
            string projectPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";
            if (!File.Exists(projectPath))
            {
                Console.WriteLine("Error: Project file not found: " + projectPath);
                return;
            }

            Console.WriteLine("Launching TIA Portal V18 with User Interface...");
            TiaPortal tia = new TiaPortal(TiaPortalMode.WithUserInterface);
            Console.WriteLine("TIA Portal launched successfully.");

            Console.WriteLine("Opening project: " + projectPath);
            Project project = tia.Projects.Open(new FileInfo(projectPath));
            Console.WriteLine("Project opened successfully: " + project.Name);
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
        }
    }
}
