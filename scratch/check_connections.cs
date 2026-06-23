using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class CheckConnections
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

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("No HMI targets found.");
                return;
            }

            var hmi = hmiTargets[0];
            Console.WriteLine("\nVerifying HMI Tags under: " + hmi.Name);
            
            var table = hmi.TagFolder.TagTables.Find("HMI_Tags");
            if (table == null)
            {
                Console.WriteLine("Tag table 'HMI_Tags' not found!");
                return;
            }

            Console.WriteLine(string.Format("Table Name: {0} (Total Tags: {1})", table.Name, table.Tags.Count));
            int boundCount = 0;
            int internalCount = 0;

            foreach (var tag in table.Tags)
            {
                string connName = "<Internal tag>";
                string plcTagLink = "<Undefined>";

                if (tag.Connection != null)
                {
                    connName = tag.Connection.Name;
                    boundCount++;
                }
                else
                {
                    internalCount++;
                }

                if (tag.ControllerTag != null)
                {
                    plcTagLink = tag.ControllerTag.Name;
                }

                Console.WriteLine(string.Format("  Tag: '{0}', Connection: '{1}', Linked PLC Tag: '{2}'", 
                    tag.Name, connName, plcTagLink));
            }

            Console.WriteLine("\n--- SUMMARY ---");
            Console.WriteLine(string.Format("Bound Tags: {0}, Internal Tags: {1}", boundCount, internalCount));
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
        {
            targets.Add(sc.Software as HmiTarget);
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, targets);
        }
    }
}
