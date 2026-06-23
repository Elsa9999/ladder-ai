using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;

class FindAllHwIds
{
    static readonly string OriginalPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";

    static void Main()
    {
        Console.OutputEncoding = Encoding.UTF8;
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var t = procList[0].Attach();
            var proj = t.Projects[0];
            Console.WriteLine("Attached to: " + proj.Name);

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                Console.WriteLine("\nDevice: " + dev.Name);
                InspectItemsRecursive(dev.DeviceItems);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void InspectItemsRecursive(DeviceItemComposition items)
    {
        if (items == null) return;
        foreach (var item in items)
        {
            if (item == null) continue;
            
            // Try HwIdentifierController
            var controller = item.GetService<HwIdentifierController>();
            if (controller != null)
            {
                Console.WriteLine(string.Format("  Item '{0}' (Type: {1}) supports HwIdentifierController:", item.Name, item.TypeIdentifier));
                try
                {
                    foreach (var assoc in controller.RegisteredHwIdentifiers)
                    {
                        // Get Identifier property
                        var idProp = assoc.GetType().GetProperty("Identifier");
                        var parentProp = assoc.GetType().GetProperty("Parent");
                        
                        long idVal = -1;
                        string parentName = "unknown";
                        string parentType = "unknown";

                        if (idProp != null)
                        {
                            idVal = Convert.ToInt64(idProp.GetValue(assoc, null));
                        }
                        if (parentProp != null)
                        {
                            var parentObj = parentProp.GetValue(assoc, null);
                            if (parentObj != null)
                            {
                                parentType = parentObj.GetType().Name;
                                try
                                {
                                    var nameProp = parentObj.GetType().GetProperty("Name");
                                    if (nameProp != null)
                                    {
                                        parentName = nameProp.GetValue(parentObj, null).ToString();
                                    }
                                }
                                catch {}
                            }
                        }
                        Console.WriteLine(string.Format("    - HwID: {0} | Parent: {1} ({2})", idVal, parentName, parentType));
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("    Error reading association: " + ex.Message);
                }
            }

            InspectItemsRecursive(item.DeviceItems);
        }
    }

    static void GetDevicesRecursive(Project project, List<Device> allDevices)
    {
        foreach (var dev in project.Devices) allDevices.Add(dev);
        if (project.UngroupedDevicesGroup != null)
        {
            foreach (var dev in project.UngroupedDevicesGroup.Devices) allDevices.Add(dev);
        }
        CollectGroups(project.DeviceGroups, allDevices);
    }

    static void CollectGroups(DeviceUserGroupComposition groups, List<Device> allDevices)
    {
        foreach (var g in groups)
        {
            foreach (var d in g.Devices) allDevices.Add(d);
            CollectGroups(g.Groups, allDevices);
        }
    }
}
