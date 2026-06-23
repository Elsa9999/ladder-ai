using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;

class DeleteSystemBlocks
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" TIA OPENNESS SYSTEM BLOCK DELETER");
        Console.WriteLine("=================================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to Project: " + proj.Name);

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null && software.Name.Contains("PLC_2"))
                    {
                        Console.WriteLine("\nProcessing PLC: " + software.Name);

                        // 1. Delete instance DB MB_SERVER_DB from standard blocks
                        var blocks = software.BlockGroup.Blocks;
                        var instDb = blocks.Find("MB_SERVER_DB");
                        if (instDb != null)
                        {
                            Console.WriteLine("  Found instance DB 'MB_SERVER_DB'. Deleting...");
                            try
                            {
                                instDb.Delete();
                                Console.WriteLine("    Deleted MB_SERVER_DB successfully.");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine("    Failed to delete MB_SERVER_DB: " + ex.Message);
                            }
                        }

                        // 2. Access SystemBlockGroups and find MB_SERVER
                        var sysGroupsProp = software.BlockGroup.GetType().GetProperty("SystemBlockGroups");
                        if (sysGroupsProp != null)
                        {
                            var sysGroups = sysGroupsProp.GetValue(software.BlockGroup, null);
                            DeleteSystemBlockRecursive(sysGroups, "MB_SERVER");
                        }
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static bool DeleteSystemBlockRecursive(object groupObj, string blockName)
    {
        if (groupObj == null) return false;

        // If it is a composition, iterate items
        if (groupObj.GetType().Name.Contains("Composition") || groupObj.GetType().Name.Contains("List"))
        {
            var countProp = groupObj.GetType().GetProperty("Count");
            int count = countProp != null ? (int)countProp.GetValue(groupObj, null) : 0;
            var itemProp = groupObj.GetType().GetProperty("Item");
            if (itemProp == null)
            {
                foreach (var p in groupObj.GetType().GetProperties())
                {
                    if (p.GetIndexParameters().Length > 0)
                    {
                        itemProp = p;
                        break;
                    }
                }
            }

            if (itemProp != null)
            {
                for (int i = 0; i < count; i++)
                {
                    try
                    {
                        var itemObj = itemProp.GetValue(groupObj, new object[] { i });
                        if (DeleteSystemBlockRecursive(itemObj, blockName))
                            return true;
                    }
                    catch {}
                }
            }
            return false;
        }

        // It is an individual group. Check its blocks
        var blocksProp = groupObj.GetType().GetProperty("Blocks");
        if (blocksProp != null)
        {
            var blocksCol = blocksProp.GetValue(groupObj, null);
            var findMethod = blocksCol.GetType().GetMethod("Find", new Type[] { typeof(string) });
            if (findMethod != null)
            {
                var block = findMethod.Invoke(blocksCol, new object[] { blockName });
                if (block != null)
                {
                    Console.WriteLine(string.Format("  Found system block '{0}'. Deleting...", blockName));
                    try
                    {
                        var deleteMethod = block.GetType().GetMethod("Delete");
                        if (deleteMethod != null)
                        {
                            deleteMethod.Invoke(block, null);
                            Console.WriteLine("    Deleted successfully!");
                            return true;
                        }
                        else
                        {
                            Console.WriteLine("    Could not find Delete method on block.");
                        }
                    }
                    catch (Exception ex)
                    {
                        string errMsg = ex.Message;
                        if (ex.InnerException != null) errMsg = ex.InnerException.Message;
                        Console.WriteLine("    Failed to delete system block: " + errMsg);
                    }
                }
            }
        }

        // Recurse sub-groups
        var groupsProp = groupObj.GetType().GetProperty("Groups");
        if (groupsProp != null)
        {
            var groupsCol = groupsProp.GetValue(groupObj, null);
            if (DeleteSystemBlockRecursive(groupsCol, blockName))
                return true;
        }

        return false;
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
