using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.SW.Tags;
using Siemens.Engineering.SW.Types;

class ExportAllOpen
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" EXPORT ALL OPEN PLCS - TIA OPENNESS TOOL");
        Console.WriteLine("=================================================");

        string outFolder = @"D:\AI_Agent_PLC_LADDER_ONLY\examples\TIA_V18_XML_Pattern_Library\raw_exports\PLSP_export";
        Directory.CreateDirectory(outFolder);

        try
        {
            var processes = TiaPortal.GetProcesses();
            Console.WriteLine("Running TIA Portal processes found: " + processes.Count);

            if (processes.Count == 0)
            {
                Console.WriteLine("Error: No running TIA Portal instances found.");
                return;
            }

            Project project = null;
            TiaPortal tia = null;

            for (int i = 0; i < processes.Count; i++)
            {
                try
                {
                    var candidateTia = processes[i].Attach();
                    Console.WriteLine(string.Format("Attached to TIA process #{0}, open projects count: {1}", i + 1, candidateTia.Projects.Count));

                    if (candidateTia.Projects.Count > 0)
                    {
                        project = candidateTia.Projects[0]; // Take the first open project
                        tia = candidateTia;
                        break;
                    }
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine(string.Format("  Attach failed for TIA process #{0}: {1}", i + 1, attachEx.Message));
                }
            }

            if (project == null)
            {
                Console.WriteLine("Error: No open projects found in any running TIA Portal process.");
                return;
            }

            Console.WriteLine("Target Project: " + project.Name + " (" + project.Path.FullName + ")");

            // Collect all PLC Softwares
            var plcSoftwares = new List<PlcSoftware>();
            foreach (Device device in project.Devices)
            {
                foreach (DeviceItem item in device.DeviceItems)
                {
                    CollectPlcSoftware(item, plcSoftwares);
                }
            }

            Console.WriteLine("Found PLCs count: " + plcSoftwares.Count);
            if (plcSoftwares.Count == 0)
            {
                Console.WriteLine("Error: No PLC software found in the project.");
                return;
            }

            foreach (var plc in plcSoftwares)
            {
                string plcFolder = Path.Combine(outFolder, Sanitize(plc.Name));
                Directory.CreateDirectory(plcFolder);
                ExportPLC(plc, plcFolder);
            }

            Console.WriteLine("\nExport completed successfully. Destination: " + outFolder);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: Export operation failed: " + ex);
        }
    }

    static void ExportPLC(PlcSoftware plc, string plcFolder)
    {
        Console.WriteLine("\n-------------------------------------------------");
        Console.WriteLine("Exporting PLC: " + plc.Name);
        Console.WriteLine("-------------------------------------------------");

        string blockFolder = Path.Combine(plcFolder, "Blocks");
        string tagFolder = Path.Combine(plcFolder, "Tags");
        string typeFolder = Path.Combine(plcFolder, "Types");

        Directory.CreateDirectory(blockFolder);
        Directory.CreateDirectory(tagFolder);
        Directory.CreateDirectory(typeFolder);

        // 1. Export PLC Data Types (UDTs)
        Console.WriteLine("--- Exporting PLC Data Types (UDTs) ---");
        foreach (PlcType type in plc.TypeGroup.Types)
        {
            string filePath = Path.Combine(typeFolder, Sanitize(type.Name) + ".xml");
            Console.WriteLine("  Export type: " + type.Name);
            SafeDelete(filePath);
            try
            {
                type.Export(new FileInfo(filePath), ExportOptions.WithDefaults);
                Console.WriteLine("    [OK]");
            }
            catch (Exception ex)
            {
                Console.WriteLine("    [FAILED]: " + ex.Message);
            }
        }

        // 2. Export PLC Tag Tables
        Console.WriteLine("\n--- Exporting Tag Tables ---");
        foreach (PlcTagTable table in plc.TagTableGroup.TagTables)
        {
            string filePath = Path.Combine(tagFolder, Sanitize(table.Name) + ".xml");
            Console.WriteLine("  Export tag table: " + table.Name);
            SafeDelete(filePath);
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

        // 3. Export PLC Blocks (OB/FB/FC/DB)
        Console.WriteLine("\n--- Exporting Blocks ---");
        foreach (PlcBlock block in plc.BlockGroup.Blocks)
        {
            string filePath = Path.Combine(blockFolder, Sanitize(block.Name) + ".xml");
            Console.WriteLine("  Export block: " + block.Name);
            SafeDelete(filePath);
            try
            {
                block.Export(new FileInfo(filePath), ExportOptions.WithDefaults);
                Console.WriteLine("    [OK]");
            }
            catch (Exception ex)
            {
                Console.WriteLine("    [FAILED]: " + ex.Message);
            }
        }
    }

    static void CollectPlcSoftware(DeviceItem item, List<PlcSoftware> result)
    {
        SoftwareContainer container = item.GetService<SoftwareContainer>();
        if (container != null && container.Software is PlcSoftware)
        {
            result.Add((PlcSoftware)container.Software);
        }

        foreach (DeviceItem child in item.DeviceItems)
        {
            CollectPlcSoftware(child, result);
        }
    }

    static string Sanitize(string name)
    {
        foreach (char c in Path.GetInvalidFileNameChars())
        {
            name = name.Replace(c, '_');
        }
        return name;
    }

    static void SafeDelete(string path)
    {
        if (File.Exists(path))
        {
            File.Delete(path);
        }
    }
}
