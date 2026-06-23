using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExploreHmiStructure
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" EXPLORE HMI STRUCTURE");
        Console.WriteLine("========================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy tiến trình TIA Portal nào.");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Dự án: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (Device dev in proj.Devices)
            {
                Console.WriteLine("Device: " + dev.Name);
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy HmiTarget nào.");
                return;
            }

            foreach (var hmi in hmiTargets)
            {
                Console.WriteLine("\n----------------------------------------");
                Console.WriteLine("HMI Target: " + hmi.Name);
                // Parent device info removed to prevent InvalidCastException
                
                // Inspect ScreenFolder
                var screenFolder = hmi.ScreenFolder;
                if (screenFolder != null)
                {
                    Console.WriteLine("Screens in Root Folder:");
                    foreach (var screen in screenFolder.Screens)
                    {
                        Console.WriteLine(string.Format("  - Screen: {0}", screen.Name));
                    }
                    foreach (var folder in screenFolder.Folders)
                    {
                        Console.WriteLine(string.Format("  - Folder: {0}", folder.Name));
                    }
                }

                // Inspect ScreenTemplateFolder
                var templateFolder = hmi.ScreenTemplateFolder;
                if (templateFolder != null)
                {
                    Console.WriteLine("Templates Folder Type: " + templateFolder.GetType().FullName);
                    // Reflect properties of templateFolder
                    foreach (var prop in templateFolder.GetType().GetProperties())
                    {
                        Console.WriteLine(string.Format("  TemplateFolder Property: {0} ({1})", prop.Name, prop.PropertyType.Name));
                    }
                }

                // Check other objects by reflecting on the HmiTarget
                Console.WriteLine("\nReflecting services and properties of HmiTarget:");
                foreach (var prop in typeof(HmiTarget).GetProperties())
                {
                    try
                    {
                        object val = prop.GetValue(hmi, null);
                        string valStr = val != null ? val.GetType().Name : "null";
                        Console.WriteLine(string.Format("  Property {0} ({1}) = {2}", prop.Name, prop.PropertyType.Name, valStr));
                        
                        // If it's a composition, show count
                        if (val != null)
                        {
                            var countProp = val.GetType().GetProperty("Count");
                            if (countProp != null)
                            {
                                int count = (int)countProp.GetValue(val, null);
                                Console.WriteLine(string.Format("    Count = {0}", count));
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("  Property {0} - Lỗi: {1}", prop.Name, ex.Message));
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
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
