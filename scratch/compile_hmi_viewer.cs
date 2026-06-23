using System;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Compiler;

class CompileHmiViewer
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        string targetHmiName = "HMI_RT_1";

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
                        tia = candidateTia;
                        proj = candidateProj;
                        break;
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

            HmiTarget hmi = null;
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    hmi = GetHmiTarget(item);
                    if (hmi != null && hmi.Name.Contains(targetHmiName))
                        break;
                    hmi = null;
                }
                if (hmi != null) break;
            }

            if (hmi == null)
            {
                Console.WriteLine("No HMI target named " + targetHmiName + " found.");
                return;
            }

            Console.WriteLine("Target HMI: " + hmi.Name);
            ICompilable compilable = hmi.GetService<ICompilable>();
            if (compilable == null)
            {
                Console.WriteLine("HMI does not support compilation.");
                return;
            }

            Console.WriteLine("Compiling HMI target, please wait...");
            CompilerResult result = compilable.Compile();
            Console.WriteLine("Compilation state: " + result.State);
            Console.WriteLine("Errors: " + result.ErrorCount + ", Warnings: " + result.WarningCount);
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
            Console.WriteLine(string.Format("{0}[{1}] {2}: {3}", indentStr, msg.State, msg.Path, msg.Description));
            if (msg.Messages != null && msg.Messages.Count > 0)
            {
                PrintMessages(msg.Messages, indent + 1);
            }
        }
    }

    static HmiTarget GetHmiTarget(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget) return sc.Software as HmiTarget;
        foreach (var child in item.DeviceItems)
        {
            var sw = GetHmiTarget(child);
            if (sw != null) return sw;
        }
        return null;
    }
}
