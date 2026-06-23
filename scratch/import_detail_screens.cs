using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;
using Siemens.Engineering.Hmi.Tag;
using Siemens.Engineering.Compiler;

class ImportDetailScreens
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" STAGE 2 DETAIL SCREENS IMPORT TOOL (SMART ATTACH)");
        Console.WriteLine("========================================");

        string tagsXml = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml";
        
        var screenFiles = new Dictionary<string, string>()
        {
            { "bon tron 1", @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_patched.xml" },
            { "bon tron 2", @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_2_patched.xml" },
            { "bon tron 3", @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_3_patched.xml" },
            { "bon tron 4", @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_4_patched.xml" }
        };

        try
        {
            Project proj = null;
            TiaPortal tia = null;
            var processes = TiaPortal.GetProcesses();
            Console.WriteLine("Running TIA Portal processes found: " + processes.Count);

            for (int i = 0; i < processes.Count; i++)
            {
                try
                {
                    Console.WriteLine("Checking process PID: " + processes[i].Id);
                    var candidateTia = processes[i].Attach();
                    if (candidateTia.Projects.Count > 0)
                    {
                        var candidateProj = candidateTia.Projects[0];
                        Console.WriteLine("  Found project open: '" + candidateProj.Name + "'");
                        if (candidateProj.Name.Equals("cuocthi_tdh", StringComparison.OrdinalIgnoreCase))
                        {
                            proj = candidateProj;
                            tia = candidateTia;
                            break;
                        }
                    }
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine("  Failed to attach or read: " + attachEx.Message);
                }
            }

            if (proj == null)
            {
                Console.WriteLine("Error: Project 'cuocthi_tdh' not found open in any running TIA Portal instance.");
                Environment.Exit(1);
            }
            Console.WriteLine("Attached to Project: " + proj.Name + " (" + proj.Path.FullName + ")");

            // Find HMI Target
            HmiTarget hmi = null;
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, ref hmi);
                }
                if (hmi != null) break;
            }

            if (hmi == null)
            {
                Console.WriteLine("Error: No HMI target found in project 'cuocthi_tdh'.");
                Environment.Exit(1);
            }
            Console.WriteLine("Target HMI: " + hmi.Name);

            // STEP 1: Import updated HMI Tag Table
            Console.WriteLine("\nImporting HMI Tag Table...");
            if (!File.Exists(tagsXml))
            {
                Console.WriteLine("Error: Tag XML not found at " + tagsXml);
                Environment.Exit(1);
            }
            var existingTable = hmi.TagFolder.TagTables.Find("Screen1_HMI_Tags");
            if (existingTable != null)
            {
                Console.WriteLine("  Deleting old Screen1_HMI_Tags table...");
                existingTable.Delete();
            }
            hmi.TagFolder.TagTables.Import(new FileInfo(tagsXml), ImportOptions.Override);
            Console.WriteLine("  ==> Tag Table imported successfully.");

            // STEP 2: Delete and Import the 4 patched screens
            foreach (var screenEntry in screenFiles)
            {
                string screenName = screenEntry.Key;
                string screenXml = screenEntry.Value;
                
                Console.WriteLine("\nImporting Patched screen: " + screenName + "...");
                if (!File.Exists(screenXml))
                {
                    Console.WriteLine("Error: Screen XML not found at " + screenXml);
                    Environment.Exit(1);
                }
                
                Screen existingScreen = null;
                foreach (Screen s in hmi.ScreenFolder.Screens)
                {
                    if (s.Name.Equals(screenName, StringComparison.OrdinalIgnoreCase))
                    {
                        existingScreen = s;
                        break;
                    }
                }

                if (existingScreen != null)
                {
                    Console.WriteLine("  Deleting old screen " + screenName + "...");
                    existingScreen.Delete();
                }

                hmi.ScreenFolder.Screens.Import(new FileInfo(screenXml), ImportOptions.Override);
                Console.WriteLine("  ==> Screen " + screenName + " imported successfully.");
            }

            // STEP 3: Save Project
            Console.WriteLine("\nSaving project...");
            proj.Save();
            Console.WriteLine("  ==> Project saved successfully.");

            // STEP 4: Compile HMI Target
            Console.WriteLine("\nCompiling HMI Target software...");
            ICompilable compilable = hmi.GetService<ICompilable>();
            if (compilable != null)
            {
                CompilerResult result = compilable.Compile();
                Console.WriteLine("  Compile State: " + result.State);
                Console.WriteLine("  Errors: " + result.ErrorCount + ", Warnings: " + result.WarningCount);
                PrintMessages(result.Messages, "    ");
                
                using (StreamWriter sw = new StreamWriter(@"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_compile_log.txt", false, System.Text.Encoding.UTF8))
                {
                    sw.WriteLine("========================================");
                    sw.WriteLine(" HMI COMPILE LOG");
                    sw.WriteLine("========================================");
                    sw.WriteLine("Compile State: " + result.State);
                    sw.WriteLine("Errors: " + result.ErrorCount + ", Warnings: " + result.WarningCount);
                    WriteMessagesToFile(result.Messages, "    ", sw);
                }
                
                if (result.ErrorCount > 0)
                {
                    Console.WriteLine("\n[ERROR] HMI Compile failed with " + result.ErrorCount + " errors.");
                    Environment.Exit(1);
                }
            }
            else
            {
                Console.WriteLine("  Warning: HmiTarget does not support ICompilable.");
            }

            Console.WriteLine("\n========================================");
            Console.WriteLine(" STAGE 2 DETAIL SCREENS IMPORT COMPLETED SUCCESSFULLY!");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
            Environment.Exit(1);
        }
    }

    static void FindHmiTargets(DeviceItem item, ref HmiTarget target)
    {
        if (target != null) return;
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
        {
            target = sc.Software as HmiTarget;
            return;
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, ref target);
        }
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
                Console.WriteLine(string.Format("{0}{1}: {2}", indent, state, desc));
                if (msg.Messages != null)
                {
                    PrintMessages(msg.Messages, indent + "  ");
                }
            }
            catch {}
        }
    }
    
    static void WriteMessagesToFile(System.Collections.IEnumerable messages, string indent, StreamWriter sw)
    {
        if (messages == null) return;
        foreach (dynamic msg in messages)
        {
            try
            {
                string state = msg.State.ToString();
                string desc = msg.Description != null ? msg.Description.ToString() : "";
                sw.WriteLine(string.Format("{0}{1}: {2}", indent, state, desc));
                if (msg.Messages != null)
                {
                    WriteMessagesToFile(msg.Messages, indent + "  ", sw);
                }
            }
            catch {}
        }
    }
}
