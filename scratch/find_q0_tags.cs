using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Tags;

class FindQ0Tags
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" FIND Q0 TAGS IN PLC1");
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
                    InspectPlc(item);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi: " + ex.ToString());
        }
    }

    static void InspectPlc(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware)
        {
            var plc = sc.Software as PlcSoftware;
            if (plc.Name.Contains("PLC_1"))
            {
                Console.WriteLine("\nPLC: " + plc.Name);
                var tagFolder = plc.TagTableGroup;
                if (tagFolder != null)
                {
                    foreach (var table in tagFolder.TagTables)
                    {
                        foreach (var tag in table.Tags)
                        {
                            if (tag.LogicalAddress.StartsWith("%Q", StringComparison.OrdinalIgnoreCase) || 
                                tag.Name.Contains("Contactor") || 
                                tag.LogicalAddress == "%Q0.0")
                            {
                                Console.WriteLine(string.Format("    * Tag: {0} | Addr: {1} | Type: {2} | Table: {3}", 
                                    tag.Name, tag.LogicalAddress, tag.DataTypeName, table.Name));
                            }
                        }
                    }
                }
            }
        }
        foreach (var child in item.DeviceItems)
        {
            InspectPlc(child);
        }
    }
}
