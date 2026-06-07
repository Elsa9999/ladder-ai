using System;
using System.Collections.Generic;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.SW.Tags;

class ExportProjectByPath
{
    static void Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: Export_Project_ByPath.exe <project.ap18> <output_folder>");
            return;
        }

        string projectPath = args[0];
        string outFolder = args[1];

        if (!File.Exists(projectPath))
        {
            Console.WriteLine("Project file not found: " + projectPath);
            return;
        }

        Directory.CreateDirectory(outFolder);

        try
        {
            Project project = null;
            TiaPortal tia = null;
            var processes = TiaPortal.GetProcesses();
            Console.WriteLine("Running TIA Portal processes: " + processes.Count);

            for (int i = 0; i < processes.Count; i++)
            {
                try
                {
                    var candidateTia = processes[i].Attach();
                    Console.WriteLine("Attached to TIA process #" + (i + 1) + ", open projects: " + candidateTia.Projects.Count);

                    foreach (Project candidateProject in candidateTia.Projects)
                    {
                        Console.WriteLine("  Project: " + candidateProject.Name + " | " + candidateProject.Path.FullName);
                        if (String.Equals(candidateProject.Path.FullName, projectPath, StringComparison.OrdinalIgnoreCase) ||
                            String.Equals(candidateProject.Name, Path.GetFileNameWithoutExtension(projectPath), StringComparison.OrdinalIgnoreCase))
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
                    Console.WriteLine("  Attach failed for TIA process #" + (i + 1) + ": " + attachEx.Message);
                }
            }

            if (project == null)
            {
                Console.WriteLine("Target project is not open in any running TIA Portal process.");
                Console.WriteLine("Open the project in TIA Portal, then run this exporter again.");
                return;
            }

            ExportProject(project, outFolder);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Export failed: " + ex);
        }
    }

    static void ExportProject(Project project, string outFolder)
    {
        Console.WriteLine("Selected project: " + project.Name);

        var plcSoftwares = new List<PlcSoftware>();
        foreach (Device device in project.Devices)
        {
            foreach (DeviceItem item in device.DeviceItems)
            {
                CollectPlcSoftware(item, plcSoftwares);
            }
        }

        Console.WriteLine("PLC software count: " + plcSoftwares.Count);
        int plcIndex = 1;
        foreach (PlcSoftware plc in plcSoftwares)
        {
            string plcFolder = Path.Combine(outFolder, plcIndex.ToString("00") + "_" + Sanitize(plc.Name));
            string blockFolder = Path.Combine(plcFolder, "Blocks");
            string tagFolder = Path.Combine(plcFolder, "Tags");
            Directory.CreateDirectory(blockFolder);
            Directory.CreateDirectory(tagFolder);

            Console.WriteLine();
            Console.WriteLine("PLC " + plcIndex + ": " + plc.Name);

            foreach (PlcBlock block in plc.BlockGroup.Blocks)
            {
                string filePath = Path.Combine(blockFolder, Sanitize(block.Name) + ".xml");
                Console.WriteLine("  Export block: " + block.Name);
                SafeDelete(filePath);
                try
                {
                    block.Export(new FileInfo(filePath), ExportOptions.WithDefaults);
                }
                catch (Exception ex)
                {
                    Console.WriteLine("    Failed: " + ex.Message);
                }
            }

            foreach (PlcTagTable table in plc.TagTableGroup.TagTables)
            {
                string filePath = Path.Combine(tagFolder, Sanitize(table.Name) + ".xml");
                Console.WriteLine("  Export tag table: " + table.Name);
                SafeDelete(filePath);
                try
                {
                    table.Export(new FileInfo(filePath), ExportOptions.WithDefaults);
                }
                catch (Exception ex)
                {
                    Console.WriteLine("    Failed: " + ex.Message);
                }
            }

            plcIndex++;
        }

        Console.WriteLine();
        Console.WriteLine("Export complete: " + outFolder);
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
