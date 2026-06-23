using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW.WatchAndForceTables;

class TestWatchTableEntry
{
    static void Main()
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            
            // Get PLC_1 software container
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

            if (plc1 == null)
            {
                Console.WriteLine("PLC_1 not found!");
                return;
            }

            var wts = plc1.WatchAndForceTableGroup.WatchTables;
            var existing = wts.Find("WT_Test");
            if (existing != null) existing.Delete();

            var wt = wts.Create("WT_Test");
            Console.WriteLine("Watch table created: " + wt.Name);
            
            var entry = wt.Entries.Create();
            Console.WriteLine("Entry type: " + entry.GetType().FullName);

            try
            {
                entry.SetAttribute("Name", "AI_MB_TCP_iStep");
                Console.WriteLine("Successfully set Name attribute using SetAttribute!");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to set Name attribute: " + ex.Message);
            }

            wt.Delete();
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
