using System;
using System.IO;
using System.Collections.Generic;
using System.Reflection;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;

class ExportAlarmLogging
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" EXPORT HMI ALARM LOGGING");
        Console.WriteLine("========================================");

        string exportDir = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Alarms";
        Directory.CreateDirectory(exportDir);

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy TIA Portal!");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Dự án: " + proj.Name);

            List<HmiTarget> hmiTargets = new List<HmiTarget>();
            foreach (var dev in proj.Devices)
                foreach (var item in dev.DeviceItems)
                    FindHmiTargets(item, hmiTargets);

            if (hmiTargets.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy HMI!");
                return;
            }

            var hmi = hmiTargets[0];
            Console.WriteLine("HMI: " + hmi.Name);

            // Reflect AlarmClasses and DiscreteAlarms / AnalogAlarms
            Type hmiType = hmi.GetType();
            Console.WriteLine("\nHmiTarget Properties:");
            foreach (var prop in hmiType.GetProperties())
            {
                if (prop.Name.Contains("Alarm") || prop.Name.Contains("Log"))
                    Console.WriteLine("  " + prop.Name + " : " + prop.PropertyType.Name);
            }

            // Try to access DiscreteAlarms / AnalogAlarms via reflection
            var alarmClasses = hmiType.GetProperty("AlarmClasses");
            if (alarmClasses != null)
            {
                var val = alarmClasses.GetValue(hmi, null);
                Console.WriteLine("\nAlarmClasses = " + (val != null ? val.ToString() : "null"));
            }

            // Try export via HmiTarget ExImService
            try 
            {
                var exSvc = hmi.GetService<Siemens.Engineering.ExImService>();
                if (exSvc != null)
                {
                    Console.WriteLine("ExImService found! Attempting export...");
                    string outFile = Path.Combine(exportDir, "AlarmLogging_Export.xml");
                    exSvc.Export(new FileInfo(outFile), Siemens.Engineering.ExportOptions.None);
                    Console.WriteLine("Exported to: " + outFile);
                }
                else
                {
                    Console.WriteLine("ExImService not available on HmiTarget");
                }
            }
            catch (Exception ex2)
            {
                Console.WriteLine("Export via HmiTarget error: " + ex2.Message);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi: " + ex.ToString());
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
