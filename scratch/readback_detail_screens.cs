using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;
using Siemens.Engineering.Hmi.Tag;

class ReadbackDetailScreens
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" STAGE 2 DETAIL SCREENS READBACK EXPORTER (SMART ATTACH)");
        Console.WriteLine("========================================");

        string tagsOut = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags_readback.xml";
        var screensToExport = new Dictionary<string, string>()
        {
            { "bon tron 1", @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_1_readback.xml" },
            { "bon tron 2", @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_2_readback.xml" },
            { "bon tron 3", @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_3_readback.xml" },
            { "bon tron 4", @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\bon_tron_4_readback.xml" }
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
                return;
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
                return;
            }
            Console.WriteLine("Target HMI: " + hmi.Name);

            // Export HMI Tag Table Screen1_HMI_Tags
            var table = hmi.TagFolder.TagTables.Find("Screen1_HMI_Tags");
            if (table != null)
            {
                FileInfo fileInfo = new FileInfo(tagsOut);
                if (File.Exists(tagsOut)) File.Delete(tagsOut);
                table.Export(fileInfo, ExportOptions.WithDefaults);
                Console.WriteLine("Successfully exported HMI Tag Table to: " + tagsOut);
            }
            else
            {
                Console.WriteLine("Error: HMI Tag Table 'Screen1_HMI_Tags' not found.");
            }

            // Export HMI Screens
            foreach (var screenEntry in screensToExport)
            {
                string screenName = screenEntry.Key;
                string outputPath = screenEntry.Value;
                
                Screen targetScreen = null;
                foreach (Screen s in hmi.ScreenFolder.Screens)
                {
                    if (s.Name.Equals(screenName, StringComparison.OrdinalIgnoreCase))
                    {
                        targetScreen = s;
                        break;
                    }
                }

                if (targetScreen != null)
                {
                    FileInfo fileInfo = new FileInfo(outputPath);
                    if (File.Exists(outputPath)) File.Delete(outputPath);
                    targetScreen.Export(fileInfo, ExportOptions.WithDefaults);
                    Console.WriteLine("Successfully exported Screen '" + screenName + "' to: " + outputPath);
                }
                else
                {
                    Console.WriteLine("Error: Screen '" + screenName + "' not found.");
                }
            }

            Console.WriteLine("========================================");
            Console.WriteLine(" READBACK EXPORTS COMPLETED SUCCESSFULLY!");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
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
}
