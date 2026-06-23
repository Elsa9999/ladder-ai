using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.Compiler;

class CheckCompileErrors
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" CHECK COMPILE ERRORS - TIA OPENNESS V18 TOOL");
        Console.WriteLine("=================================================");

        string projectParam = "Project1";
        string plcName = "PLC_1";

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
                        Console.WriteLine(string.Format("  Checking project: {0}", candidateProject.Name));
                        if (string.Equals(candidateProject.Name, projectParam, StringComparison.OrdinalIgnoreCase))
                        {
                            tia = candidateTia;
                            project = candidateProject;
                            break;
                        }
                    }

                    if (project != null) break;
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine(string.Format("  Attach failed for TIA process #{0}: {1}", i + 1, attachEx.Message));
                }
            }

            if (project == null)
            {
                Console.WriteLine("Error: Target project '" + projectParam + "' is not open.");
                return;
            }

            // Find DeviceItem containing target PlcSoftware
            DeviceItem cpuItem = null;
            PlcSoftware targetPlc = FindPlc(project, plcName, out cpuItem);

            if (targetPlc == null)
            {
                Console.WriteLine(string.Format("Error: PLC named '{0}' not found.", plcName));
                return;
            }

            Console.WriteLine(string.Format("Found PLC: {0}. CPU DeviceItem: {1}", targetPlc.Name, cpuItem != null ? cpuItem.Name : "null"));

            // Get ICompilable
            ICompilable compilable = null;
            if (cpuItem != null)
            {
                compilable = cpuItem.GetService<ICompilable>();
            }
            if (compilable == null)
            {
                compilable = targetPlc.GetService<ICompilable>();
            }

            if (compilable == null)
            {
                Console.WriteLine("Error: Could not obtain ICompilable service for the PLC.");
                return;
            }

            Console.WriteLine("Starting Compilation...");
            CompilerResult result = compilable.Compile();
            Console.WriteLine("\n--- Compile Result ---");
            Console.WriteLine("State: " + result.State);
            Console.WriteLine("Errors: " + result.ErrorCount);
            Console.WriteLine("Warnings: " + result.WarningCount);

            Console.WriteLine("\n--- Compile Messages ---");
            if (result.Messages != null)
            {
                PrintMessages(result.Messages, "");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: Compile check failed: " + ex);
        }
    }

    static PlcSoftware FindPlc(Project project, string plcName, out DeviceItem cpuItem)
    {
        cpuItem = null;
        foreach (Device device in project.Devices)
        {
            foreach (DeviceItem item in device.DeviceItems)
            {
                PlcSoftware plc = FindPlcSoftwareRecursive(item, plcName, out cpuItem);
                if (plc != null) return plc;
            }
        }
        return null;
    }

    static PlcSoftware FindPlcSoftwareRecursive(DeviceItem item, string plcName, out DeviceItem cpuItem)
    {
        cpuItem = null;
        SoftwareContainer container = item.GetService<SoftwareContainer>();
        if (container != null && container.Software is PlcSoftware)
        {
            PlcSoftware plc = (PlcSoftware)container.Software;
            if (string.Equals(plc.Name, plcName, StringComparison.OrdinalIgnoreCase) ||
                plc.Name.IndexOf(plcName, StringComparison.OrdinalIgnoreCase) >= 0)
            {
                cpuItem = item;
                return plc;
            }
        }

        foreach (DeviceItem child in item.DeviceItems)
        {
            PlcSoftware plc = FindPlcSoftwareRecursive(child, plcName, out cpuItem);
            if (plc != null) return plc;
        }

        return null;
    }

    static void PrintMessages(System.Collections.IEnumerable messages, string indent)
    {
        foreach (dynamic msg in messages)
        {
            try
            {
                string state = msg.State.ToString();
                string desc = msg.Description != null ? msg.Description.ToString() : "";
                string errorCode = "";
                try { errorCode = msg.ErrorCode.ToString(); } catch {}
                
                Console.WriteLine(string.Format("{0}{1}: {2} (Code: {3})", 
                    indent, state, desc, errorCode));
                
                if (msg.Messages != null)
                {
                    PrintMessages(msg.Messages, indent + "  ");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(indent + "Error reading message: " + ex.Message);
            }
        }
    }
}
