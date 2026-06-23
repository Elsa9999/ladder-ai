using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Tags;

class ListPlcTagsInTia
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" LIST PLC TAGS IN TIA");
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
                Console.WriteLine("\nDevice: " + dev.Name);
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
            Console.WriteLine("  PLC Software Container: " + plc.Name);
            var tagFolder = plc.TagTableGroup;
            if (tagFolder != null)
            {
                Console.WriteLine("    Tag Tables:");
                foreach (var table in tagFolder.TagTables)
                {
                    Console.WriteLine(string.Format("      - Table: {0} (Tags: {1})", table.Name, table.Tags.Count));
                    foreach (var tag in table.Tags)
                    {
                        string lowerName = tag.Name.ToLower();
                        if (lowerName.Contains("cap_nuoc") || lowerName.Contains("nguyen_lieu") || lowerName.Contains("nhiet_do") || lowerName.Contains("start") || lowerName.Contains("tron"))
                        {
                            Console.WriteLine(string.Format("        * Found Match: {0} (Addr: {1}, Type: {2})", tag.Name, tag.LogicalAddress, tag.DataTypeName));
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
