using System;
using System.IO;
using Siemens.Engineering;

class OpenCuocThiTdh
{
    static void Main()
    {
        try
        {
            Console.WriteLine("Searching for running TIA Portal instances...");
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            Console.WriteLine(string.Format("Found {0} TIA processes.", procList.Count));
            for (int i = 0; i < procList.Count; i++)
            {
                try
                {
                    Console.WriteLine(string.Format("Attaching to TIA process #{0}...", i + 1));
                    var tia = procList[i].Attach();
                    Console.WriteLine("  Successfully attached!");

                    if (tia.Projects.Count > 0)
                    {
                        var proj = tia.Projects[0];
                        Console.WriteLine(string.Format("  Closing open project: '{0}' at '{1}'...", proj.Name, proj.Path.FullName));
                        proj.Close();
                        Console.WriteLine("  Project closed successfully.");
                    }

                    string originalPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";
                    Console.WriteLine(string.Format("  Opening project: '{0}'...", originalPath));
                    tia.Projects.Open(new FileInfo(originalPath));
                    Console.WriteLine("  Project opened successfully!");
                    Console.WriteLine("SUCCESS!");
                    return;
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine("  Operation failed on this process: " + attachEx.Message);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
