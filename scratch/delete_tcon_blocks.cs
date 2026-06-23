using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;

class DeleteTconBlocks
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
                if (proc.Id == 10500) continue;
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

            Console.WriteLine("Attached to Project: " + proj.Name);

            // Find PLC_1
            PlcSoftware plc1Software = null;
            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null && software.Name.Equals("PLC_1", StringComparison.OrdinalIgnoreCase))
                    {
                        plc1Software = software;
                        break;
                    }
                }
                if (plc1Software != null) break;
            }

            if (plc1Software == null)
            {
                Console.WriteLine("PLC_1 Software Container not found!");
                return;
            }

            Console.WriteLine("Found PLC_1 Software container. Recursively searching for TCON blocks to delete...");

            string[] blocksToDelete = new string[] { "DB_MB_TCP_Client_Conn_DB", "DB_MB_TCP_Server_Conn_DB" };

            foreach (var blockName in blocksToDelete)
            {
                DeleteBlockRecursive(plc1Software.BlockGroup, blockName);
            }

            Console.WriteLine("Saving project...");
            proj.Save();
            Console.WriteLine("Project saved successfully!");
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
            Console.WriteLine(string.Format("Found block '{0}' in group '{1}'. Deleting...", blockName, group.Name));
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
