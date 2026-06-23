using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExportScreenByName
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" OPENNESS SCREEN EXPORTER");
        Console.WriteLine("========================================");

        if (args.Length < 2)
        {
            Console.WriteLine("Usage: ExportScreenByName.exe <PID> <ScreenName> [OutputFile]");
            return;
        }

        int targetPid = int.Parse(args[0]);
        string screenName = args[1];
        string outputFile = args.Length > 2 ? args[2] : Path.Combine(@"D:\AI_Agent_PLC_LADDER_ONLY\scratch", screenName + "_export.xml");

        try
        {
            var processes = TiaPortal.GetProcesses();
            TiaPortalProcess selectedProcess = null;
            foreach (var proc in processes)
            {
                if (proc.Id == targetPid)
                {
                    selectedProcess = proc;
                    break;
                }
            }

            if (selectedProcess == null)
            {
                Console.WriteLine("Error: TIA Portal process with PID " + targetPid + " not found.");
                return;
            }

            Console.WriteLine("Attaching to TIA Portal (PID: " + selectedProcess.Id + ")...");
            TiaPortal tia = selectedProcess.Attach();
            Project proj = tia.Projects[0];
            Console.WriteLine("Project: " + proj.Name + " (" + proj.Path.FullName + ")");

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Error: No HmiTarget found in project.");
                return;
            }

            HmiTarget hmi = hmiTargets[0];
            Console.WriteLine("HMI Target: " + hmi.Name);

            Screen targetScreen = null;
            foreach (Screen s in hmi.ScreenFolder.Screens)
            {
                if (s.Name.Equals(screenName, StringComparison.OrdinalIgnoreCase))
                {
                    targetScreen = s;
                    break;
                }
            }

            if (targetScreen == null)
            {
                Console.WriteLine("Error: Screen '" + screenName + "' not found.");
                Console.WriteLine("Available screens:");
                foreach (Screen s in hmi.ScreenFolder.Screens)
                {
                    Console.WriteLine("  - " + s.Name);
                }
                return;
            }

            Console.WriteLine("Found screen: " + targetScreen.Name);
            if (File.Exists(outputFile))
            {
                File.Delete(outputFile);
            }

            targetScreen.Export(new FileInfo(outputFile), ExportOptions.WithDefaults);
            Console.WriteLine("Successfully exported screen to: " + outputFile);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Exception: " + ex.ToString());
        }
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
        {
            targets.Add(sc.Software as HmiTarget);
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, targets);
        }
    }
}
