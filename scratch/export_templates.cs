using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExportTemplates
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI EXTRA EXPORTER");
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

                // 1. Export Screen Templates
                var tempFolder = hmi.ScreenTemplateFolder;
                if (tempFolder != null)
                {
                    Console.WriteLine("ScreenTemplates count: " + tempFolder.ScreenTemplates.Count);
                    foreach (var template in tempFolder.ScreenTemplates)
                    {
                        string filePath = Path.Combine(outFolder, "Template_" + template.Name + ".xml");
                        Console.WriteLine("  Exporting Template: " + template.Name + " -> " + Path.GetFileName(filePath));
                        if (File.Exists(filePath)) File.Delete(filePath);
                        try
                        {
                            template.Export(new FileInfo(filePath), ExportOptions.WithDefaults);
                            Console.WriteLine("    [OK]");
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("    [FAILED]: " + ex.Message);
                        }
                    }
                }
            }

            Console.WriteLine("\nExtra export completed. Output folder: " + outFolder);
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
