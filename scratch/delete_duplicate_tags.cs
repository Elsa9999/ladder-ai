using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Tags;

class DeleteDuplicateTags
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" TIA OPENNESS DUPLICATE TAG TABLES DELETER");
        Console.WriteLine("=================================================");

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
                    Console.WriteLine(string.Format("Trying to attach to TIA PID: {0}...", proc.Id));
                    var candidateTia = proc.Attach();
                    if (candidateTia.Projects.Count > 0)
                    {
                        var candidateProj = candidateTia.Projects[0];
                        Console.WriteLine(string.Format("Found TIA PID {0} with project: {1}", proc.Id, candidateProj.Name));
                        if (candidateProj.Name.Equals("cuocthi_tdh", StringComparison.OrdinalIgnoreCase))
                        {
                            tia = candidateTia;
                            proj = candidateProj;
                            Console.WriteLine("Using project 'cuocthi_tdh'.");
                            break;
                        }
                        if (proj == null)
                        {
                            tia = candidateTia;
                            proj = candidateProj;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(string.Format("Failed to attach to PID {0}: {1}", proc.Id, ex.Message));
                }
            }

            if (proj == null)
            {
                Console.WriteLine("Could not find any TIA Portal instance with an open project.");
                return;
            }
            Console.WriteLine("Attached to Project: " + proj.Name);

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            List<PlcSoftware> softwares = new List<PlcSoftware>();
            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null && !softwares.Contains(software))
                    {
                        softwares.Add(software);
                    }
                }
            }

            foreach (var plcSoftware in softwares)
            {
                Console.WriteLine("\nChecking PLC: " + plcSoftware.Name);
                
                // We want to delete duplicate tag tables
                // In PLC_1: we only keep AI_Tags_PLC1 (or AI_Tags). Let's delete AI_Tags_PLC1 and AI_Tags_PLC2 if they are duplicates.
                // Wait! Let's delete "AI_Tags_PLC1", "AI_Tags_PLC2", and "AI_Tags" so we can do a clean re-import of only the target files.
                string[] tablesToDelete = new string[] { "AI_Tags", "AI_Tags_PLC1", "AI_Tags_PLC2" };
                
                foreach (var tableName in tablesToDelete)
                {
                    var table = plcSoftware.TagTableGroup.TagTables.Find(tableName);
                    if (table != null)
                    {
                        Console.WriteLine(string.Format("Found Tag Table '{0}' in PLC '{1}'. Deleting...", tableName, plcSoftware.Name));
                        try
                        {
                            table.Delete();
                            Console.WriteLine("Deleted successfully.");
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("Failed to delete: " + ex.Message);
                        }
                    }
                }
            }

            Console.WriteLine("\nTag table cleanup completed.");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void GetDevicesRecursive(Project project, List<Device> allDevices)
    {
        AddDevices(project.Devices, allDevices);
        if (project.UngroupedDevicesGroup != null)
        {
            AddDevices(project.UngroupedDevicesGroup.Devices, allDevices);
        }
        AddUserGroupsRecursive(project.DeviceGroups, allDevices);
    }

    static void AddDevices(DeviceComposition devices, List<Device> allDevices)
    {
        foreach (var dev in devices)
        {
            allDevices.Add(dev);
        }
    }

    static void AddUserGroupsRecursive(DeviceUserGroupComposition groups, List<Device> allDevices)
    {
        foreach (var group in groups)
        {
            AddDevices(group.Devices, allDevices);
            AddUserGroupsRecursive(group.Groups, allDevices);
        }
    }

    static PlcSoftware GetPlcSoftware(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware) return sc.Software as PlcSoftware;
        foreach (var child in item.DeviceItems)
        {
            var sw = GetPlcSoftware(child);
            if (sw != null) return sw;
        }
        return null;
    }
}
