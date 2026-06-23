using System;
using System.IO;
using Siemens.Engineering;

class ReopenOriginalProject
{
    static void Main()
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            var tia = procList[0].Attach();
            if (tia.Projects.Count > 0)
            {
                var proj = tia.Projects[0];
                if (proj.Name.Equals("cuocthi_tdh_backup", StringComparison.OrdinalIgnoreCase))
                {
                    Console.WriteLine("Closing backup project: " + proj.Name);
                    proj.Close();
                }
            }

            string originalPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";
            Console.WriteLine("Opening original project: " + originalPath);
            tia.Projects.Open(new FileInfo(originalPath));
            Console.WriteLine("Original project opened successfully!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
