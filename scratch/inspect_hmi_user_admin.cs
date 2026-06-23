using System;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;

class InspectHmiUserAdmin
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("==============================================");
        Console.WriteLine(" INSPECT HMI USER ADMINISTRATION OPENNESS");
        Console.WriteLine("==============================================");

        try
        {
            var processes = TiaPortal.GetProcesses();
            if (processes.Count == 0)
            {
                Console.WriteLine("Error: No running TIA Portal instance found.");
                return;
            }

            var tia = processes[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Connected to project: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("No HMI Target found.");
                return;
            }

            var hmi = hmiTargets[0];
            Console.WriteLine("HMI Name: " + hmi.Name);

            // Reflection to inspect properties on HmiTarget
            Type hmiType = hmi.GetType();
            Console.WriteLine("HmiTarget Type: " + hmiType.FullName);

            foreach (var prop in hmiType.GetProperties())
            {
                if (prop.Name.Contains("User") || prop.Name.Contains("Security") || prop.Name.Contains("Admin"))
                {
                    Console.WriteLine(string.Format("Property: {0} ({1})", prop.Name, prop.PropertyType.FullName));
                    try
                    {
                        var val = prop.GetValue(hmi, null);
                        if (val != null)
                        {
                            Console.WriteLine("  Value Type: " + val.GetType().FullName);
                            foreach (var method in val.GetType().GetMethods(BindingFlags.Public | BindingFlags.Instance))
                            {
                                if (method.Name == "Export" || method.Name == "Import")
                                {
                                    Console.WriteLine(string.Format("    Method: {0}", method.ToString()));
                                }
                            }
                        }
                        else
                        {
                            Console.WriteLine("  Value: null");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("  Error getting value: " + ex.Message);
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
