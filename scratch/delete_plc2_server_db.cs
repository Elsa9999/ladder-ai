using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW.Blocks;

class DeletePlc2ServerDb
{
    static void Main()
    {
        Console.WriteLine("Attaching to TIA...");
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];

            PlcSoftware plc2 = null;
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is PlcSoftware)
                    {
                        var software = (PlcSoftware)sc.Software;
                        if (software.Name.Equals("PLC_2", StringComparison.OrdinalIgnoreCase))
                        {
                            plc2 = software;
                            break;
                        }
                    }
                }
            }

            if (plc2 == null)
            {
                Console.WriteLine("PLC_2 not found!");
                return;
            }

            var block = plc2.BlockGroup.Blocks.Find("MB_SERVER_DB");
            if (block != null)
            {
                Console.WriteLine("Found MB_SERVER_DB in PLC_2. Deleting...");
                block.Delete();
                Console.WriteLine("Deleted successfully.");
            }
            else
            {
                Console.WriteLine("MB_SERVER_DB not found in PLC_2.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
