using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;
using Siemens.Engineering.Hmi.Tag;

class ReadbackStage2
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" STAGE 2 READBACK EXPORTER TOOL");
        Console.WriteLine("========================================");

        string tagsOut = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags_readback.xml";
        string screenOut = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_readback.xml";

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
                    Console.WriteLine("Attaching to process PID: " + processes[i].Id);
                    var candidateTia = processes[i].Attach();
                    if (candidateTia.Projects.Count > 0)
                    {
                        proj = candidateTia.Projects[0];
                        tia = candidateTia;
                        break;
                    }
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine("  Failed to attach to process " + processes[i].Id + ": " + attachEx.Message);
                }
            }

            if (proj == null)
            {
                Console.WriteLine("Error: No open projects found in any running TIA Portal process.");
                return;
            }
            Console.WriteLine("Attached to Project: " + proj.Name + " (" + proj.Path.FullName + ")");

            // Find HMI Target
            HmiTarget hmi = null;
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is HmiTarget)
                    {
                        hmi = sc.Software as HmiTarget;
                        break;
                    }
                }
                if (hmi != null) break;
            }

            if (hmi == null)
            {
                Console.WriteLine("Error: No HMI target found in project.");
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

            // Export HMI Screen Screen_1
            Screen targetScreen = null;
            foreach (Screen s in hmi.ScreenFolder.Screens)
            {
                if (s.Name.Equals("Screen_1", StringComparison.OrdinalIgnoreCase))
                {
                    targetScreen = s;
                    break;
                }
            }

            if (targetScreen != null)
            {
                FileInfo fileInfo = new FileInfo(screenOut);
                if (File.Exists(screenOut)) File.Delete(screenOut);
                targetScreen.Export(fileInfo, ExportOptions.WithDefaults);
                Console.WriteLine("Successfully exported Screen_1 to: " + screenOut);
            }
            else
            {
                Console.WriteLine("Error: Screen 'Screen_1' not found.");
            }

            Console.WriteLine("READBACK EXPORTS COMPLETED!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
        }
    }
}
