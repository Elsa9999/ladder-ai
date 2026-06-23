using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Connection;

class FindAllConnections
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

            // Print all subnets and their connections
            Console.WriteLine("\n--- SUBNETS ---");
            foreach (var subnet in proj.Subnets)
            {
                Console.WriteLine("Subnet: " + subnet.Name);
            }

            // Print all connections for each device and device item
            Console.WriteLine("\n--- DEVICE CONNECTIONS ---");
            foreach (Device dev in proj.Devices)
            {
                Console.WriteLine("Device: " + dev.Name);
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    InspectDeviceItem(item, "  ");
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void InspectDeviceItem(DeviceItem item, string indent)
    {
        // Try to get ConnectionContainer if it exists in the API
        try
        {
            var cc = item.GetService<ConnectionContainer>();
            if (cc != null)
            {
                Console.WriteLine(indent + "ConnectionContainer found on item: " + item.Name);
                foreach (var conn in cc.Connections)
                {
                    Console.WriteLine(indent + "  Connection: " + conn.Name + " | Type: " + conn.GetType().Name);
                }
            }
        }
        catch {}

        foreach (DeviceItem child in item.DeviceItems)
        {
            InspectDeviceItem(child, indent + "  ");
        }
    }
}
