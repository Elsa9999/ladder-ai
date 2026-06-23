using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using System.Linq;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;

class InspectPlcSystemBlocks
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" TIA OPENNESS SYSTEM BLOCK INSPECTOR");
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
                    if (software != null)
                    {
                        Console.WriteLine("\n-------------------------------------------------");
                        Console.WriteLine("PLC Name: " + software.Name);
                        Console.WriteLine("-------------------------------------------------");

                        var blockGroup = software.BlockGroup;

                        // Try to access system block group
                        var sysGroupPropBG = blockGroup.GetType().GetProperty("SystemBlockGroups");
                        if (sysGroupPropBG != null)
                        {
                            Console.WriteLine("\nFound SystemBlockGroups property on BlockGroup!");
                            var val = sysGroupPropBG.GetValue(blockGroup, null);
                            DumpBlockGroupRecursive(val, "  ");
                        }
                        else
                        {
                            Console.WriteLine("\nNo SystemBlockGroups property found on BlockGroup.");
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

    static void DumpBlockGroupRecursive(object groupObj, string indent)
    {
        if (groupObj == null) return;
        
        // Check if it is a composition
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
                        DumpBlockGroupRecursive(itemObj, indent);
                    }
                    catch {}
                }
            }
            return;
        }

        // Use reflection to get name
        var nameProp = groupObj.GetType().GetProperty("Name");
        string groupName = nameProp != null ? (string)nameProp.GetValue(groupObj, null) : "Unknown";
        Console.WriteLine(string.Format("{0}BlockGroup: '{1}' ({2})", indent, groupName, groupObj.GetType().Name));

        // Get Blocks
        var blocksProp = groupObj.GetType().GetProperty("Blocks");
        if (blocksProp != null)
        {
            var blocksCol = blocksProp.GetValue(groupObj, null);
            var countProp = blocksCol.GetType().GetProperty("Count");
            int count = countProp != null ? (int)countProp.GetValue(blocksCol, null) : 0;
            
            var itemProp = blocksCol.GetType().GetProperty("Item");
            if (itemProp == null)
            {
                foreach (var p in blocksCol.GetType().GetProperties())
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
                        var block = itemProp.GetValue(blocksCol, new object[] { i });
                        var nameP = block.GetType().GetProperty("Name");
                        var bName = nameP != null ? nameP.GetValue(block, null) : "Unknown";
                        
                        var numP = block.GetType().GetProperty("Number");
                        var bNum = numP != null ? numP.GetValue(block, null) : -1;
                        
                        Console.WriteLine(string.Format("{0}  - Block: '{1}', Number: {2} (Type: {3})", indent, bName, bNum, block.GetType().Name));
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("{0}  - [Error reading block {1}: {2}]", indent, i, ex.Message));
                    }
                }
            }
        }

        // Recurse Groups
        var groupsProp = groupObj.GetType().GetProperty("Groups");
        if (groupsProp != null)
        {
            var groupsCol = groupsProp.GetValue(groupObj, null);
            DumpBlockGroupRecursive(groupsCol, indent + "  ");
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
