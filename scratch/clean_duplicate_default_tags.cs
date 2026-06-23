using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class CleanDuplicateDefaultTags
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" CLEAN DUPLICATE DEFAULT HMI TAGS TOOL (SMART ATTACH)");
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

            // Find HMI Target
            HmiTarget hmi = null;
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, ref hmi);
                }
                if (hmi != null) break;
            }

            if (hmi == null)
            {
                Console.WriteLine("Error: No HMI target found in project 'cuocthi_tdh'.");
                return;
            }
            Console.WriteLine("HMI Target: " + hmi.Name);

            var tagFolder = hmi.TagFolder;
            if (tagFolder != null)
            {
                var defaultTable = tagFolder.TagTables.Find("Default tag table");
                if (defaultTable != null)
                {
                    string[] tagsToDelete = { "HMI_SP_PLC2_Nuoc_Bon3", "HMI_SP_PLC2_Nhiet_Do_Bon4" };
                    foreach (var tagName in tagsToDelete)
                    {
                        var tag = defaultTable.Tags.Find(tagName);
                        if (tag != null)
                        {
                            Console.WriteLine("Deleting duplicate tag '" + tagName + "' from Default tag table...");
                            tag.Delete();
                            Console.WriteLine("  Deleted successfully.");
                        }
                        else
                        {
                            Console.WriteLine("Tag '" + tagName + "' not found in Default tag table (already clean).");
                        }
                    }
                }
                else
                {
                    Console.WriteLine("Default tag table not found.");
                }
            }

            Console.WriteLine("Saving project...");
            proj.Save();
            Console.WriteLine("Project saved successfully.");
            Console.WriteLine("SUCCESS!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
        }
    }

    static void FindHmiTargets(DeviceItem item, ref HmiTarget target)
    {
        if (target != null) return;
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
        {
            target = sc.Software as HmiTarget;
            return;
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, ref target);
        }
    }
}
