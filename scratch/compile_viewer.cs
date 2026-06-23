using System;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.Compiler;

class CompileViewer
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        string targetPlcName = args.Length > 0 ? args[0] : "PLC_1";

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            TiaPortal tia = null;
            Project proj = null;
            foreach (var proc in procList)
            {
                try
                {
                    Console.WriteLine(string.Format("Trying to attach to TIA PID: {0}...", proc.Id));
                    var candidateTia = proc.Attach();
                    if (candidateTia.Projects.Count > 0)
                    {
                        var candidateProj = candidateTia.Projects[0];
                        Console.WriteLine(string.Format("Found TIA PID {0} with project: {1}", proc.Id, candidateProj.Name));
                        if (candidateProj.Name.Equals("cuocthi_tdh", StringComparison.OrdinalIgnoreCase))
                        {
                            tia = candidateTia;
                            proj = candidateProj;
                            Console.WriteLine("Using project 'cuocthi_tdh'.");
                            break;
                        }
                        if (proj == null)
                        {
                            tia = candidateTia;
                            proj = candidateProj;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(string.Format("Failed to attach to PID {0}: {1}", proc.Id, ex.Message));
                }
            }

            if (proj == null)
            {
                Console.WriteLine("Could not find any TIA Portal instance with an open project.");
                return;
            }
            Console.WriteLine("Attached to Project: " + proj.Name);

            PlcSoftware plcSoftware = null;
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    plcSoftware = GetPlcSoftware(item);
                    if (plcSoftware != null && plcSoftware.Name.Contains(targetPlcName))
                        break;
                    plcSoftware = null;
                }
                if (plcSoftware != null) break;
            }

            if (plcSoftware == null)
            {
                // Fallback: get first PLC
                foreach (var dev in proj.Devices)
                {
                    foreach (var item in dev.DeviceItems)
                    {
                        plcSoftware = GetPlcSoftware(item);
                        if (plcSoftware != null) break;
                    }
                    if (plcSoftware != null) break;
                }
            }

            if (plcSoftware == null)
            {
                Console.WriteLine("No PLC software container found.");
                return;
            }

            Console.WriteLine("Target PLC: " + plcSoftware.Name);
            ICompilable compilable = plcSoftware.GetService<ICompilable>();
            if (compilable == null)
            {
                Console.WriteLine("PLC does not support compilation.");
                return;
            }

            Console.WriteLine("Compiling, please wait...");
            CompilerResult result = compilable.Compile();
            Console.WriteLine("Compilation state: " + result.State);
            Console.WriteLine("\n=== DETAILED ERROR/WARNING MESSAGES ===");
            PrintMessages(result.Messages, 0);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void PrintMessages(CompilerResultMessageComposition messages, int indent)
    {
        string indentStr = new string(' ', indent * 2);
        foreach (var msg in messages)
        {
            if (msg.State == CompilerResultState.Error || msg.State == CompilerResultState.Warning)
            {
                Console.WriteLine(string.Format("{0}[{1}] {2}: {3}", indentStr, msg.State, msg.Path, msg.Description));
            }
            if (msg.Messages != null && msg.Messages.Count > 0)
            {
                PrintMessages(msg.Messages, indent + 1);
            }
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
