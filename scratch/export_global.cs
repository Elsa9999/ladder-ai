using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExportGlobal
{
    static void Main()
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI GLOBAL ELEMENTS EXPORTER");
        Console.WriteLine("========================================");

        string outFolder = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export_extra";
        Directory.CreateDirectory(outFolder);

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Error: No running TIA Portal instances found.");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Connected to Project: " + proj.Name);

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
                Console.WriteLine("Error: No HMI targets found.");
                return;
            }

            foreach (var hmi in hmiTargets)
            {
                Console.WriteLine("\nProcessing HMI: " + hmi.Name);
                var globalElements = hmi.ScreenGlobalElements;
                if (globalElements != null)
                {
                    string filePath = Path.Combine(outFolder, "GlobalElements_" + hmi.Name + ".xml");
                    Console.WriteLine("  Exporting GlobalElements -> " + Path.GetFileName(filePath));
                    if (File.Exists(filePath)) File.Delete(filePath);
                    try
                    {
                        globalElements.Export(new FileInfo(filePath), ExportOptions.WithDefaults);
                        Console.WriteLine("    [OK]");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("    [FAILED]: " + ex.Message);
                    }
                }
                else
                {
                    Console.WriteLine("  GlobalElements is null.");
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
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
