using System;
using System.IO;
using System.Collections.Generic;
using System.Reflection;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;

class ImportAlarmLogging
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" TIA PORTAL HMI ALARM LOGGING IMPORTER");
        Console.WriteLine("========================================");

        string alarmFile = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Alarms\Hmi.Alarm.AlarmLogging_1.xml";

        if (!File.Exists(alarmFile))
        {
            Console.WriteLine("Loi: Khong tim thay file XML alarm: " + alarmFile);
            return;
        }

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Loi: Khong tim thay TIA Portal dang chay!");
                return;
            }

            Console.WriteLine("Dang ket noi TIA Portal...");
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Du an: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (var dev in proj.Devices)
                foreach (var item in dev.DeviceItems)
                    FindHmiTargets(item, hmiTargets);

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Loi: Khong tim thay HMI!");
                return;
            }

            var hmi = hmiTargets[0];
            Console.WriteLine("HMI Target: " + hmi.Name);

            // Reflect to find AlarmLogging import method
            Type hmiType = hmi.GetType();
            Console.WriteLine("\nTim AlarmLogging properties:");
            foreach (var prop in hmiType.GetProperties())
            {
                if (prop.Name.ToLower().Contains("alarm"))
                    Console.WriteLine("  Property: " + prop.Name + " : " + prop.PropertyType.Name);
            }

            // Try to find import method on alarm compositions
            var alarmClasses = hmiType.GetProperty("AlarmClasses");
            Console.WriteLine("\nAlarmClasses available: " + (alarmClasses != null ? "YES" : "NO"));

            // Try AnalogAlarms
            var analogAlarmsProperty = hmiType.GetProperty("AnalogAlarms");
            Console.WriteLine("AnalogAlarms property: " + (analogAlarmsProperty != null ? "YES" : "NO"));

            // Get all methods on HmiTarget
            Console.WriteLine("\nMethods on HmiTarget containing 'Import':");
            foreach (var m in hmiType.GetMethods())
            {
                if (m.Name.ToLower().Contains("import") || m.Name.ToLower().Contains("alarm"))
                    Console.WriteLine("  Method: " + m.Name);
            }

            // Try to find alarm logging composition via property
            Console.WriteLine("\nAll HmiTarget properties:");
            foreach (var prop in hmiType.GetProperties())
                Console.WriteLine("  " + prop.Name + " : " + prop.PropertyType.Name);

        }
        catch (Exception ex)
        {
            Console.WriteLine("Loi he thong: " + ex.Message);
        }
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
            targets.Add(sc.Software as HmiTarget);
        foreach (var child in item.DeviceItems)
            FindHmiTargets(child, targets);
    }
}
