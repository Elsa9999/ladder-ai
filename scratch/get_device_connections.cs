using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Connection;

class GetDeviceConnections
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
            Console.WriteLine("Connected to Project: " + proj.Name);

            // Let's search for connections in HMI target
            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            foreach (var hmi in hmiTargets)
            {
                Console.WriteLine("\nHMI Target: " + hmi.Name);
                Console.WriteLine("Connections in hmi.Connections:");
                foreach (var conn in hmi.Connections)
                {
                    Console.WriteLine(string.Format("  Name: '{0}', Type: {1}", conn.Name, conn.GetType().Name));
                }
                
                // Let's also check if we can query TagFolder.TagTables
                foreach (var table in hmi.TagFolder.TagTables)
                {
                    Console.WriteLine("  Tag Table: " + table.Name);
                    foreach (var tag in table.Tags)
                    {
                        string connName = tag.Connection != null ? tag.Connection.Name : "None";
                        string controllerTagName = tag.ControllerTag != null ? tag.ControllerTag.Name : "None";
                        Console.WriteLine(string.Format("    Tag: '{0}', Connection: '{1}', ControllerTag: '{2}'", 
                            tag.Name, connName, controllerTagName));
                    }
                }
            }
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
