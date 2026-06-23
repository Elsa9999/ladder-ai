using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class ExportHmiTags
{
    static void Main(string[] args)
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Connected to Project: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0) return;
            var hmi = hmiTargets[0];
            Console.WriteLine("HMI Target: " + hmi.Name);

            // Export HMI tag table
            string tableName = args.Length > 0 ? args[0] : "Screen1_HMI_Tags";
            string outPath = args.Length > 1 ? args[1] : @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\HMI_Tags_Exported.xml";
            
            var table = hmi.TagFolder.TagTables.Find(tableName);
            if (table != null)
            {
                FileInfo fileInfo = new FileInfo(outPath);
                if (File.Exists(outPath)) File.Delete(outPath);
                table.Export(fileInfo, ExportOptions.WithDefaults);
                Console.WriteLine("Exported HMI tags table '" + tableName + "' to: " + outPath);
            }
            else
            {
                Console.WriteLine("Tag table '" + tableName + "' not found.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
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
