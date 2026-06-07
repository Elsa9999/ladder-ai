using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Tags;

class AgentTIATagLister
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
            Console.WriteLine("Project: " + proj.Name);

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
                Console.WriteLine("No PLC software found.");
                return;
            }

            Console.WriteLine("PLC: " + plcSoftware.Name);
            Console.WriteLine("\n--- PLC TAG TABLES & TAGS ---");
            foreach (var table in plcSoftware.TagTableGroup.TagTables)
            {
                Console.WriteLine(string.Format("Table: {0}", table.Name));
                foreach (var tag in table.Tags)
                {
                    Console.WriteLine(string.Format("  Tag: '{0}', Type: {1}, Address: {2}", tag.Name, tag.DataTypeName, tag.LogicalAddress));
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.Message);
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
