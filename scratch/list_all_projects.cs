using System;
using Siemens.Engineering;

class ListAllProjects
{
    static void Main()
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            Console.WriteLine("Found " + procList.Count + " processes.");
            for (int i = 0; i < procList.Count; i++)
            {
                try
                {
                    var tia = procList[i].Attach();
                    Console.WriteLine("Process " + i + " has " + tia.Projects.Count + " open projects:");
                    foreach (Project p in tia.Projects)
                    {
                        Console.WriteLine("  Project: " + p.Name + " at " + p.Path.FullName);
                        foreach (var dev in p.Devices)
                        {
                            Console.WriteLine("    Device: " + dev.Name);
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  Failed to attach to process " + i + ": " + ex.Message);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
