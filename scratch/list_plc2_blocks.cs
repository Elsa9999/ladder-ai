using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.HW.Features;

class ListPlc2Blocks
{
    static void Main()
    {
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

            Console.WriteLine("Blocks in PLC_2 main BlockGroup:");
            PrintBlocksInGroup(plc2.BlockGroup, "");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void PrintBlocksInGroup(PlcBlockGroup group, string indent)
    {
        Console.WriteLine(indent + "[Group] " + group.Name);
        foreach (var block in group.Blocks)
        {
            Console.WriteLine(indent + "  - " + block.Name + " (" + block.GetType().Name + ", ID: " + block.Number + ")");
        }
        foreach (var subGroup in group.Groups)
        {
            PrintBlocksInGroup(subGroup, indent + "  ");
        }
    }
}
