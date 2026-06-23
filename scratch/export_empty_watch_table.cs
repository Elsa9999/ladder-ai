using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW.WatchAndForceTables;

class ExportEmptyWatchTable
{
    static void Main()
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            
            PlcSoftware plc1 = null;
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is PlcSoftware)
                    {
                        var software = (PlcSoftware)sc.Software;
                        if (software.Name == "PLC_1")
                        {
                            plc1 = software;
                            break;
                        }
                    }
                }
            }

            if (plc1 == null) return;

            var wts = plc1.WatchAndForceTableGroup.WatchTables;
            var wt = wts.Find("WT_Temp_Schema");
            if (wt != null) wt.Delete();

            wt = wts.Create("WT_Temp_Schema");
            
            string outPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\empty_wt.xml";
            wt.Export(new FileInfo(outPath), ExportOptions.WithDefaults);
            Console.WriteLine("Exported empty watch table to: " + outPath);
            
            wt.Delete();
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
