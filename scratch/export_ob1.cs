using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;

class ExportOb1
{
    static void Main()
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];

            PlcSoftware plcSw = null;
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    if (plcSw == null) plcSw = GetPlcSoftware(item);
                }
            }
            foreach (var devGrp in proj.DeviceGroups)
            {
                ScanGroup(devGrp, ref plcSw);
            }

            if (plcSw == null)
            {
                Console.WriteLine("PlcSoftware not found.");
                return;
            }

            // Find by name "Main"
            PlcBlock ob1 = plcSw.BlockGroup.Blocks.Find("Main");
            if (ob1 == null)
            {
                // Try to find any block with Number = 1
                foreach (var block in plcSw.BlockGroup.Blocks)
                {
                    if (block.Number == 1)
                    {
                        ob1 = block;
                        break;
                    }
                }
            }

            if (ob1 != null)
            {
                string exportPath = @"d:\AI_Agent_PLC_LADDER_ONLY\scratch\OB1_Export.xml";
                ob1.Export(new FileInfo(exportPath), ExportOptions.WithDefaults);
                Console.WriteLine("Exported OB1 (" + ob1.Name + ") to: " + exportPath);
            }
            else
            {
                Console.WriteLine("Main [OB1] block not found in project.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static PlcSoftware GetPlcSoftware(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null)
        {
            PlcSoftware ps = sc.Software as PlcSoftware;
            if (ps != null) return ps;
        }
        foreach (var child in item.DeviceItems)
        {
            var r = GetPlcSoftware(child);
            if (r != null) return r;
        }
        return null;
    }

    static void ScanGroup(DeviceUserGroup g, ref PlcSoftware plcSw)
    {
        foreach (var dev in g.Devices)
            foreach (var item in dev.DeviceItems)
            {
                if (plcSw == null) plcSw = GetPlcSoftware(item);
            }
        foreach (var sub in g.Groups)
            ScanGroup(sub, ref plcSw);
    }
}
