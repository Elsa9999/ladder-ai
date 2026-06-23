using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;

class GetNetworkDetails
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            int targetPid = 14620;
            string expectedPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";
            
            var processes = TiaPortal.GetProcesses();
            TiaPortalProcess selectedProcess = null;
            foreach (var p in processes)
            {
                if (p.Id == targetPid)
                {
                    selectedProcess = p;
                    break;
                }
            }

            if (selectedProcess == null)
            {
                Console.WriteLine("ERROR: PID " + targetPid + " not found!");
                return;
            }

            TiaPortal tia = selectedProcess.Attach();
            Project proj = tia.Projects[0];
            if (!proj.Path.FullName.Equals(expectedPath, StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("ERROR: Project path mismatch!");
                return;
            }

            Console.WriteLine("Connected to project: " + proj.Name);

            // Scan all devices
            foreach (Device dev in proj.Devices)
            {
                Console.WriteLine("\n========================================");
                Console.WriteLine("Device: " + dev.Name + " (Type: " + dev.TypeIdentifier + ")");
                Console.WriteLine("========================================");
                
                InspectDeviceItems(dev.DeviceItems, dev.Name);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void InspectDeviceItems(DeviceItemComposition items, string deviceName)
    {
        foreach (DeviceItem item in items)
        {
            // Check for NetworkInterface service
            var netInterface = item.GetService<NetworkInterface>();
            if (netInterface != null)
            {
                Console.WriteLine("  Network Interface Name: " + item.Name + " (TypeIdentifier: " + item.TypeIdentifier + ")");
                foreach (var node in netInterface.Nodes)
                {
                    Console.WriteLine("    Node: " + node.Name + " (Type: " + node.GetType().Name + ")");
                    try
                    {
                        foreach (var attr in node.GetAttributeInfos())
                        {
                            try
                            {
                                object val = node.GetAttribute(attr.Name);
                                Console.WriteLine(string.Format("      - Attr: {0} = {1}", attr.Name, val ?? "null"));
                            }
                            catch {}
                        }
                    }
                    catch {}

                    // Check ConnectedSubnet
                    try
                    {
                        var subnet = node.ConnectedSubnet;
                        if (subnet != null)
                        {
                            Console.WriteLine("      Connected Subnet: " + subnet.Name + " (Type: " + subnet.GetType().Name + ")");
                        }
                        else
                        {
                            Console.WriteLine("      Connected Subnet: None");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("      Connected Subnet check error: " + ex.Message);
                    }
                }
            }

            InspectDeviceItems(item.DeviceItems, deviceName);
        }
    }
}
