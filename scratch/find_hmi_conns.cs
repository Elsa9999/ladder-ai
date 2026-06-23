using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;

class FindHmiConns
{
    static void Main(string[] args)
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No TIA Portal processes found.");
                return;
            }
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Connected to Project: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }
            foreach (var group in proj.DeviceGroups)
            {
                ScanGroup(group, hmiTargets);
            }

            Console.WriteLine("Found " + hmiTargets.Count + " HMI targets:");
            foreach (var hmi in hmiTargets)
            {
                Console.WriteLine("HMI: " + hmi.Name);
                Console.WriteLine("Connections Count: " + hmi.Connections.Count);
                foreach (var conn in hmi.Connections)
                {
                    Console.WriteLine("  Connection Name: " + conn.Name);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.Message);
        }
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null)
        {
            HmiTarget ht = sc.Software as HmiTarget;
            if (ht != null) targets.Add(ht);
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, targets);
        }
    }

    static void ScanGroup(DeviceUserGroup g, List<HmiTarget> targets)
    {
        foreach (var dev in g.Devices)
        {
            foreach (var item in dev.DeviceItems)
            {
                FindHmiTargets(item, targets);
            }
        }
        foreach (var sub in g.Groups)
        {
            ScanGroup(sub, targets);
        }
    }
}
