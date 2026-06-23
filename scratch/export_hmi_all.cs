using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;
using Siemens.Engineering.Hmi.Tag;

class ExportHmiAll
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI SCREENS & TAGS EXPORTER");
        Console.WriteLine("========================================");

        string outFolder = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export";
        Directory.CreateDirectory(outFolder);

        string blockFolder = Path.Combine(outFolder, "Screens");
        string tagFolder = Path.Combine(outFolder, "Tags");
        Directory.CreateDirectory(blockFolder);
        Directory.CreateDirectory(tagFolder);

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
            Console.WriteLine("Connected to Project: " + proj.Name + " (" + proj.Path.FullName + ")");

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
                Console.WriteLine("Error: No HMI targets (WinCC RT / Comfort Panel) found in project.");
                return;
            }

            foreach (var hmi in hmiTargets)
            {
                Console.WriteLine("\nProcessing HMI: " + hmi.Name);

                // 1. Export Tag Tables
                Console.WriteLine("--- Exporting HMI Tag Tables ---");
                ExportTagTablesInFolder(hmi.TagFolder, tagFolder);

                // 2. Export Screens
                Console.WriteLine("--- Exporting HMI Screens ---");
                var rootScreenFolder = hmi.ScreenFolder;
                if (rootScreenFolder != null)
                {
                    ExportScreensInFolder(rootScreenFolder.Screens, blockFolder, "");
                    ExportNestedFolders(rootScreenFolder.Folders, blockFolder, "");
                }
            }

            Console.WriteLine("\nExport completed successfully. Output folder: " + outFolder);
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
        }
    }

    static void ExportTagTablesInFolder(TagFolder folder, string outFolder)
    {
        foreach (var table in folder.TagTables)
        {
            string filePath = Path.Combine(outFolder, MakeSafeFilename(table.Name) + ".xml");
            Console.WriteLine("  Exporting HMI Tag Table: " + table.Name + " -> " + Path.GetFileName(filePath));
            if (File.Exists(filePath)) File.Delete(filePath);
            try
            {
                table.Export(new FileInfo(filePath), ExportOptions.WithDefaults);
                Console.WriteLine("    [OK]");
            }
            catch (Exception ex)
            {
                Console.WriteLine("    [FAILED]: " + ex.Message);
            }
        }
        foreach (var sub in folder.Folders)
        {
            ExportTagTablesInFolder(sub, outFolder);
        }
    }

    static void ExportScreensInFolder(ScreenComposition screens, string outFolder, string currentPath)
    {
        foreach (Screen screen in screens)
        {
            string safeName = MakeSafeFilename(screen.Name);
            string displayPath = string.IsNullOrEmpty(currentPath) ? safeName : currentPath + "_" + safeName;
            string filePath = Path.Combine(outFolder, string.Format("Hmi.Screen.{0}.xml", displayPath));
            Console.WriteLine("  Exporting Screen: " + screen.Name + " -> " + Path.GetFileName(filePath));
            if (File.Exists(filePath)) File.Delete(filePath);
            try
            {
                screen.Export(new FileInfo(filePath), ExportOptions.WithDefaults);
                Console.WriteLine("    [OK]");
            }
            catch (Exception ex)
            {
                Console.WriteLine("    [FAILED]: " + ex.Message);
            }
        }
    }

    static void ExportNestedFolders(ScreenUserFolderComposition folders, string outFolder, string currentPath)
    {
        foreach (ScreenUserFolder folder in folders)
        {
            string folderSafe = MakeSafeFilename(folder.Name);
            string newPath = string.IsNullOrEmpty(currentPath) ? folderSafe : currentPath + "_" + folderSafe;
            ExportScreensInFolder(folder.Screens, outFolder, newPath);
            ExportNestedFolders(folder.Folders, outFolder, newPath);
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

    static string MakeSafeFilename(string name)
    {
        foreach (char c in Path.GetInvalidFileNameChars())
        {
            name = name.Replace(c, '_');
        }
        return name;
    }
}
