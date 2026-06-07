using System;
using System.Collections.Generic;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.SW.Tags;
using Siemens.Engineering.SW.Types;

class ExportDeviceByName
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" EXPORT DEVICE BY NAME - TIA OPENNESS V18 TOOL");
        Console.WriteLine("=================================================");

        if (args.Length < 3)
        {
            Console.WriteLine("Usage: Export_Device_ByName.exe <project_name_or_path> <plc_name> <output_folder>");
            return;
        }

        string projectParam = args[0];
        string plcName = args[1];
        string outFolder = Path.GetFullPath(args[2]);

        Directory.CreateDirectory(outFolder);

        try
        {
            Project project = null;
            TiaPortal tia = null;
            var processes = TiaPortal.GetProcesses();
            Console.WriteLine("Running TIA Portal processes found: " + processes.Count);

            for (int i = 0; i < processes.Count; i++)
            {
                try
                {
                    var candidateTia = processes[i].Attach();
                    Console.WriteLine(string.Format("Attached to TIA process #{0}, open projects count: {1}", i + 1, candidateTia.Projects.Count));

                    foreach (Project candidateProject in candidateTia.Projects)
                    {
                        Console.WriteLine(string.Format("  Checking project: {0} | {1}", candidateProject.Name, candidateProject.Path.FullName));
                        if (string.Equals(candidateProject.Path.FullName, projectParam, StringComparison.OrdinalIgnoreCase) ||
                            string.Equals(candidateProject.Name, projectParam, StringComparison.OrdinalIgnoreCase) ||
                            string.Equals(candidateProject.Name, Path.GetFileNameWithoutExtension(projectParam), StringComparison.OrdinalIgnoreCase))
                        {
                            tia = candidateTia;
                            project = candidateProject;
                            break;
                        }
                    }

                    if (project != null)
                    {
                        break;
                    }
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine(string.Format("  Attach failed for TIA process #{0}: {1}", i + 1, attachEx.Message));
                }
            }

            // Fallback: If projectParam is not open, but only one project is open in total, use it
            if (project == null && processes.Count > 0)
            {
                try
                {
                    var candidateTia = processes[0].Attach();
                    if (candidateTia.Projects.Count == 1)
                    {
                        project = candidateTia.Projects[0];
                        tia = candidateTia;
                        Console.WriteLine(string.Format("Fallback: Project '{0}' matched as the only open project.", project.Name));
                    }
                }
                catch {}
            }

            if (project == null)
            {
                Console.WriteLine("Error: Target project '" + projectParam + "' is not open in any running TIA Portal process.");
                Console.WriteLine("Please open the project in TIA Portal and try again.");
                return;
            }

            ExportPLC(project, plcName, outFolder);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: Export operation failed: " + ex);
        }
    }

    static void ExportPLC(Project project, string plcName, string outFolder)
    {
        Console.WriteLine("Selected Project: " + project.Name);

        var plcSoftwares = new List<PlcSoftware>();
        foreach (Device device in project.Devices)
        {
            foreach (DeviceItem item in device.DeviceItems)
            {
                CollectPlcSoftware(item, plcSoftwares);
            }
        }

        PlcSoftware targetPlc = null;
        foreach (var plc in plcSoftwares)
        {
            if (string.Equals(plc.Name, plcName, StringComparison.OrdinalIgnoreCase) ||
                plc.Name.IndexOf(plcName, StringComparison.OrdinalIgnoreCase) >= 0)
            {
                targetPlc = plc;
                break;
            }
        }

        if (targetPlc == null)
        {
            Console.WriteLine(string.Format("Error: PLC named '{0}' not found in project. Available PLCs:", plcName));
            foreach (var plc in plcSoftwares)
            {
                Console.WriteLine("  - " + plc.Name);
            }
            return;
        }

        Console.WriteLine(string.Format("Found target PLC: {0}", targetPlc.Name));

        string blockFolder = Path.Combine(outFolder, "Blocks");
        string tagFolder = Path.Combine(outFolder, "Tags");
        string typeFolder = Path.Combine(outFolder, "Types");

        Directory.CreateDirectory(blockFolder);
        Directory.CreateDirectory(tagFolder);
        Directory.CreateDirectory(typeFolder);

        // 1. Export PLC Data Types (UDTs)
        Console.WriteLine("\n--- Exporting PLC Data Types (UDTs) ---");
        foreach (PlcType type in targetPlc.TypeGroup.Types)
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
        foreach (PlcTagTable table in targetPlc.TagTableGroup.TagTables)
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
        foreach (PlcBlock block in targetPlc.BlockGroup.Blocks)
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

        Console.WriteLine("\nExport process finished. Target: " + outFolder);
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
