using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;

class DeleteDirtyBlocks
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" TIA OPENNESS DIRTY BLOCKS DELETER FOR PLC_1");
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

            PlcSoftware plc1Software = null;
            PlcSoftware plc2Software = null;
            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null)
                    {
                        if (software.Name.Equals("PLC_1", StringComparison.OrdinalIgnoreCase))
                            plc1Software = software;
                        else if (software.Name.Equals("PLC_2", StringComparison.OrdinalIgnoreCase))
                            plc2Software = software;
                    }
                }
            }

            if (plc1Software != null)
            {
                Console.WriteLine("Cleaning up dirty blocks from PLC_1...");
                string[] blocksToDelete1 = new string[] {
                    "FC_PLC2_Mixing",
                    "FC_HMI_Mirror_PLC2",
                    "FC_Init_Default_Recipe_PLC2",
                    "OB31_PID_PLC2_Bon4",
                    "AI_Timers_PLC2",
                    "OB1_Main"
                };
                foreach (var blockName in blocksToDelete1)
                {
                    DeleteBlockRecursive(plc1Software.BlockGroup, blockName);
                }
            }
            else
            {
                Console.WriteLine("PLC_1 software container not found.");
            }

            if (plc2Software != null)
            {
                Console.WriteLine("\nCleaning up dirty blocks from PLC_2...");
                string[] blocksToDelete2 = new string[] {
                    "FC_PLC1_Mixing",
                    "FC_HMI_Mirror_PLC1",
                    "FC_Init_Default_Recipe_PLC1",
                    "OB30_PID_PLC1_Bon2",
                    "AI_Timers_PLC1",
                    "FC_Bon_Chua_Loc",
                    "OB1_Main"
                };
                foreach (var blockName in blocksToDelete2)
                {
                    DeleteBlockRecursive(plc2Software.BlockGroup, blockName);
                }
            }
            else
            {
                Console.WriteLine("PLC_2 software container not found.");
            }

            Console.WriteLine("\nDirty blocks cleanup completed.");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void DeleteBlockRecursive(PlcBlockGroup group, string blockName)
    {
        var block = group.Blocks.Find(blockName);
        if (block != null)
        {
            Console.WriteLine(string.Format("Found dirty block '{0}' in group '{1}'. Deleting...", blockName, group.Name));
            try
            {
                block.Delete();
                Console.WriteLine("Deleted successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to delete: " + ex.Message);
            }
        }

        foreach (var subGroup in group.Groups)
        {
            DeleteBlockRecursive(subGroup, blockName);
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
