using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW.WatchAndForceTables;

class TestWatchTableEntryEditor
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
            var existing = wts.Find("WT_Test_Editor");
            if (existing != null) existing.Delete();

            var wt = wts.Create("WT_Test_Editor");
            wt.ShowInEditor();
            System.Threading.Thread.Sleep(1000);

            var entry = wt.Entries.Create();
            Console.WriteLine("Entry type: " + entry.GetType().FullName);

            Console.WriteLine("Attributes found on created entry:");
            foreach (var info in entry.GetAttributeInfos())
            {
                Console.WriteLine("  " + info.Name + " [AccessMode: " + info.AccessMode + "]");
            }

            wt.Delete();
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
