
using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;

class InspectPlcBlocks
{
    static void Main(string[] args)
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No TIA Portal instances found!");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to Project: " + proj.Name);

            PlcSoftware plcSoftware = null;
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    plcSoftware = GetPlcSoftware(item);
                    if (plcSoftware != null) break;
                }
                if (plcSoftware != null) break;
            }

            if (plcSoftware == null)
            {
                Console.WriteLine("No PLC software container found.");
                return;
            }

            Console.WriteLine("PLC Name: " + plcSoftware.Name);
            Console.WriteLine("\n--- PLC BLOCKS ---");
            ListBlocks(plcSoftware.BlockGroup);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void ListBlocks(PlcBlockGroup group)
    {
        foreach (var block in group.Blocks)
        {
            Console.WriteLine(string.Format("  Block: '{0}', Number: {1}, Language: {2}", block.Name, block.Number, block.ProgrammingLanguage));
        }
        foreach (var subGroup in group.Groups)
        {
            Console.WriteLine(string.Format("Group: {0}", subGroup.Name));
            ListBlocks(subGroup);
        }
    }

    static PlcSoftware GetPlcSoftware(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware) return sc.Software as PlcSoftware;
        foreach (var child in item.DeviceItems)
        {
            var sw = GetPlcSoftware(child);
            if (sw != null) return sw;
        }
        return null;
    }
}
