using System;
using Siemens.Engineering;

class SaveProject
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
                Console.WriteLine("Saving project: " + proj.Name);
                proj.Save();
                Console.WriteLine("Project saved successfully!");
            }
            else
            {
                Console.WriteLine("No open project found to save.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
