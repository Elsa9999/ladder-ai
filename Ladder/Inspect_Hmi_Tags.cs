
using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class InspectHmiTags
{
    static void Main(string[] args)
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No TIA Portal instances found!");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to Project: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("No HMI targets found.");
                return;
            }

            foreach (var hmi in hmiTargets)
            {
                Console.WriteLine("\nHMI Target: " + hmi.Name);
                Console.WriteLine("--- HMI TAG TABLES & TAGS ---");
                ListTags(hmi.TagFolder);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void ListTags(TagFolder folder)
    {
        foreach (var table in folder.TagTables)
        {
            Console.WriteLine("Table: " + table.Name);
            foreach (var tag in table.Tags)
            {
                Console.WriteLine("  Tag: " + tag.Name);
            }
        }
        foreach (var subFolder in folder.Folders)
        {
            Console.WriteLine("Folder: " + subFolder.Name);
            ListTags(subFolder);
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
