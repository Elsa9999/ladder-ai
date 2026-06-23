using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class ImportHmiTags
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI TAG TABLE IMPORTER");
        Console.WriteLine("========================================");

        string xmlPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\AI_HMI_Tags.xml";

        if (!File.Exists(xmlPath))
        {
            Console.WriteLine("Error: XML file not found: " + xmlPath);
            return;
        }

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Error: No running TIA Portal instances found.");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Connected to Project: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Error: No HMI target found in project.");
                return;
            }

            var hmi = hmiTargets[0];
            Console.WriteLine("Target HMI: " + hmi.Name);

            // Import the Tag Table
            FileInfo fileInfo = new FileInfo(xmlPath);
            Console.WriteLine("Importing Tag Table from XML...");
            hmi.TagFolder.TagTables.Import(fileInfo, ImportOptions.Override);
            Console.WriteLine("Import completed successfully!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error during import: " + ex.ToString());
        }
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
        {
            targets.Add(sc.Software as HmiTarget);
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, targets);
        }
    }
}
