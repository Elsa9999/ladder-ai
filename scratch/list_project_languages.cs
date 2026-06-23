using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;

class ListProjectLanguages
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" LIST PROJECT LANGUAGES & HMI LANGUAGES");
        Console.WriteLine("========================================");

        try
        {
            Assembly engAssembly = Assembly.LoadFrom(@"D:\AI_Agent_PLC_LADDER_ONLY\Ladder\Siemens.Engineering.dll");
            Type tiaPortalType = engAssembly.GetType("Siemens.Engineering.TiaPortal");
            var getProcessesMethod = tiaPortalType.GetMethod("GetProcesses", BindingFlags.Public | BindingFlags.Static);
            dynamic processes = getProcessesMethod.Invoke(null, null);
            
            if (processes.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy TIA Portal.");
                return;
            }

            dynamic tia = processes[0].Attach();
            dynamic proj = tia.Projects[0];
            Console.WriteLine("Dự án: " + proj.Name);

            // 1. Project Languages
            Console.WriteLine("\n--- Project Active Languages ---");
            dynamic activeLanguages = proj.LanguageSettings.ActiveLanguages;
            foreach (dynamic lang in activeLanguages)
            {
                Console.WriteLine(string.Format("  - Culture: {0} (Display: {1})", lang.Culture.Name, lang.Culture.DisplayName));
            }

            // 2. HMI Target Languages
            List<dynamic> hmiTargets = new List<dynamic>();
            foreach (dynamic dev in proj.Devices)
            {
                foreach (dynamic item in dev.DeviceItems)
                {
                    FindHmiTargets(item, hmiTargets);
                }
            }

            foreach (var hmi in hmiTargets)
            {
                Console.WriteLine(string.Format("\n--- HMI Target: {0} ---", hmi.Name));
                // Reflect on HmiTarget properties to find languages if possible
                try
                {
                    dynamic activeLangs = hmi.LanguageSettings.ActiveLanguages;
                    Console.WriteLine("Active HMI Languages count: " + activeLangs.Count);
                    foreach (dynamic lang in activeLangs)
                    {
                        Console.WriteLine(string.Format("  - HMI Language: {0} (Culture: {1})", lang.Name, lang.Culture.Name));
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  Error getting HMI languages: " + ex.Message);
                }
            }
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }

    static void FindHmiTargets(dynamic item, List<dynamic> targets)
    {
        try
        {
            var sc = item.GetService<Siemens.Engineering.HW.Features.SoftwareContainer>();
            if (sc != null && sc.Software is Siemens.Engineering.Hmi.HmiTarget)
            {
                targets.Add(sc.Software);
            }
        }
        catch {}
        
        try
        {
            foreach (var child in item.DeviceItems)
            {
                FindHmiTargets(child, targets);
            }
        }
        catch {}
    }
}
