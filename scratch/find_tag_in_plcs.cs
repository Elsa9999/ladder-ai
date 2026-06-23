using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Tags;

class FindTagInPlcs
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            var processes = TiaPortal.GetProcesses();
            if (processes.Count == 0)
            {
                Console.WriteLine("No TIA Portal instances found.");
                return;
            }
            var tia = processes[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Connected to: " + proj.Name);

            string[] searchTags = {
                "CV3211_Nuoc_Bon3_M",
                "FQ3200_Bon1_Eff",
                "CV3201_Nuoc_Bon1_M",
                "LT3203_Bon1_Eff",
                "V3230_Nuoc_Bon1_M",
                "V3240_Nuoc_Bon3_M",
                "Pump3264_Chuyen_Nhanh1_M",
                "HMI_SP_PLC2_Nhiet_Do_Bon4"
            };

            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    SearchInDevice(item, dev.Name, searchTags);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void SearchInDevice(DeviceItem item, string deviceName, string[] searchTags)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware)
        {
            var plc = sc.Software as PlcSoftware;
            Console.WriteLine("Searching in PLC: " + plc.Name + " (" + deviceName + ")");
            foreach (var table in plc.TagTableGroup.TagTables)
            {
                foreach (var tag in table.Tags)
                {
                    foreach (var sTag in searchTags)
                    {
                        if (tag.Name.Equals(sTag, StringComparison.OrdinalIgnoreCase))
                        {
                            Console.WriteLine(string.Format("  [FOUND] Tag '{0}' in PLC '{1}', Table '{2}', Address '{3}'", 
                                tag.Name, plc.Name, table.Name, tag.LogicalAddress));
                        }
                    }
                }
            }
        }
        foreach (DeviceItem child in item.DeviceItems)
        {
            SearchInDevice(child, deviceName, searchTags);
        }
    }
}
