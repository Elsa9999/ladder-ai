using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.Compiler;

class CompileSoftware
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" COMPILE SOFTWARE - TIA OPENNESS V18 TOOL");
        Console.WriteLine("=================================================");

        string plcName = "PLC_1";
        if (args.Length > 0)
        {
            plcName = args[0];
        }

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
                    if (candidateTia.Projects.Count > 0)
                    {
                        project = candidateTia.Projects[0];
                        tia = candidateTia;
                        break;
                    }
                }
                catch {}
            }

            if (project == null)
            {
                Console.WriteLine("Error: No open projects found in any running TIA Portal process.");
                return;
            }

            Console.WriteLine("Target Project: " + project.Name + " (" + project.Path.FullName + ")");

            // Find PLC software
            PlcSoftware targetPlc = null;
            foreach (Device device in project.Devices)
            {
                foreach (DeviceItem item in device.DeviceItems)
                {
                    targetPlc = GetPlcSoftware(item, plcName);
                    if (targetPlc != null) break;
                }
                if (targetPlc != null) break;
            }

            if (targetPlc == null)
            {
                Console.WriteLine("Error: PLC named '" + plcName + "' not found.");
                return;
            }

            Console.WriteLine("Found PLC Software: " + targetPlc.Name);

            // 1. Compile BlockGroup
            Console.WriteLine("\n--- Compiling Block Group ---");
            ICompilable compilableBG = targetPlc.BlockGroup.GetService<ICompilable>();
            if (compilableBG != null)
            {
                CompilerResult resBG = compilableBG.Compile();
                Console.WriteLine("Block Group Compile State: " + resBG.State);
                Console.WriteLine("Errors: " + resBG.ErrorCount + ", Warnings: " + resBG.WarningCount);
                PrintMessages(resBG.Messages, "  ");
            }
            else
            {
                Console.WriteLine("Block Group does not support ICompilable.");
            }

            // 2. Compile individual blocks
            Console.WriteLine("\n--- Compiling Individual Blocks ---");
            foreach (PlcBlock block in targetPlc.BlockGroup.Blocks)
            {
                Console.WriteLine("Block: " + block.Name);
                ICompilable compilableBlock = block.GetService<ICompilable>();
                if (compilableBlock != null)
                {
                    CompilerResult resBlock = compilableBlock.Compile();
                    Console.WriteLine("  Compile State: " + resBlock.State);
                    Console.WriteLine("  Errors: " + resBlock.ErrorCount + ", Warnings: " + resBlock.WarningCount);
                    PrintMessages(resBlock.Messages, "    ");
                }
                else
                {
                    Console.WriteLine("  Does not support ICompilable.");
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: Compile software failed: " + ex);
        }
    }

    static PlcSoftware GetPlcSoftware(DeviceItem item, string plcName)
    {
        SoftwareContainer container = item.GetService<SoftwareContainer>();
        if (container != null && container.Software is PlcSoftware)
        {
            PlcSoftware plc = (PlcSoftware)container.Software;
            if (plc.Name.IndexOf(plcName, StringComparison.OrdinalIgnoreCase) >= 0)
            {
                return plc;
            }
        }
        foreach (DeviceItem child in item.DeviceItems)
        {
            PlcSoftware plc = GetPlcSoftware(child, plcName);
            if (plc != null) return plc;
        }
        return null;
    }

    static void PrintMessages(System.Collections.IEnumerable messages, string indent)
    {
        if (messages == null) return;
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
