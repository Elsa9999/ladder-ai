using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Tags;

class CheckPlcTagsDetailed
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" DETAILED PLC TAGS CHECK");
        Console.WriteLine("========================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Project: " + proj.Name);

            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    InspectPlcSoftware(item);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi: " + ex.ToString());
        }
    }

    static void InspectPlcSoftware(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware)
        {
            var plc = sc.Software as PlcSoftware;
            Console.WriteLine("\nPLC: " + plc.Name);
            var tagFolder = plc.TagTableGroup;
            if (tagFolder != null)
            {
                foreach (var table in tagFolder.TagTables)
                {
                    Console.WriteLine(string.Format("  - Table: {0}", table.Name));
                    foreach (var tag in table.Tags)
                    {
                        string name = tag.Name;
                        if (name.Contains("Contactor") || name.Contains("V3230") || name.Contains("Bon2") || name.Contains("FreqActual") || name.Contains("MB"))
                        {
                            Console.WriteLine(string.Format("    * Tag: {0} | Addr: {1} | Type: {2}", tag.Name, tag.LogicalAddress, tag.DataTypeName));
                        }
                    }
                }
            }
        }
        foreach (var child in item.DeviceItems)
        {
            InspectPlcSoftware(child);
        }
    }
}
