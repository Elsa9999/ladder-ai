using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class ListHmiTagsInTia
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" LIST HMI TAGS IN TIA (SMART ATTACH)");
        Console.WriteLine("========================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            Console.WriteLine("Running TIA Portal processes: " + procList.Count);

            TiaPortal tia = null;
            Project proj = null;
            for (int i = 0; i < procList.Count; i++)
            {
                try
                {
                    Console.WriteLine("Checking process PID: " + procList[i].Id);
                    var candidateTia = procList[i].Attach();
                    if (candidateTia.Projects.Count > 0)
                    {
                        var candidateProj = candidateTia.Projects[0];
                        Console.WriteLine("  Found project open: '" + candidateProj.Name + "'");
                        if (candidateProj.Name.Equals("cuocthi_tdh", StringComparison.OrdinalIgnoreCase))
                        {
                            proj = candidateProj;
                            tia = candidateTia;
                            break;
                        }
                    }
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine("  Failed to attach or read: " + attachEx.Message);
                }
            }

            if (proj == null)
            {
                Console.WriteLine("Error: Project 'cuocthi_tdh' not found open in any running TIA Portal instance.");
                return;
            }
            Console.WriteLine("Connected to Project: " + proj.Name + " (" + proj.Path.FullName + ")");

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
                Console.WriteLine("No HMI Target found.");
                return;
            }

            var hmi = hmiTargets[0];
            Console.WriteLine("HMI Target: " + hmi.Name);

            var tagFolder = hmi.TagFolder;
            if (tagFolder != null)
            {
                Console.WriteLine("\n--- HMI TAG TABLES & TAGS ---");
                foreach (var table in tagFolder.TagTables)
                {
                    Console.WriteLine(string.Format("Table: {0}", table.Name));
                    foreach (var tag in table.Tags)
                    {
                        Console.WriteLine(string.Format("  Tag: {0}", tag.Name));
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
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
