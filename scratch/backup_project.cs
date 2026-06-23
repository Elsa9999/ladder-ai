using System;
using System.IO;
using Siemens.Engineering;

class BackupProject
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

            TiaPortal tia = null;
            Project proj = null;
            foreach (var proc in procList)
            {
                try
                {
                    Console.WriteLine("Trying to attach to TIA PID: " + proc.Id);
                    var candidateTia = proc.Attach();
                    if (candidateTia.Projects.Count > 0)
                    {
                        var candidateProj = candidateTia.Projects[0];
                        if (candidateProj.Name.Equals("cuocthi_tdh", StringComparison.OrdinalIgnoreCase))
                        {
                            tia = candidateTia;
                            proj = candidateProj;
                            break;
                        }
                    }
                }
                catch {}
            }

            if (proj == null)
            {
                Console.WriteLine("Project cuocthi_tdh not found open in TIA Portal!");
                return;
            }

            string backupPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh_backup";
            Console.WriteLine("Backing up project to: " + backupPath);
            
            if (Directory.Exists(backupPath))
            {
                Console.WriteLine("Backup folder already exists. Deleting it first...");
                Directory.Delete(backupPath, true);
            }

            proj.SaveAs(new DirectoryInfo(backupPath));
            Console.WriteLine("Backup created successfully!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error during backup: " + ex.ToString());
        }
    }
}
