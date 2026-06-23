using System;
using System.IO;
using Siemens.Engineering;

class Program
{
    static void Main()
    {
        string logPath = @"d:\AI_Agent_PLC_LADDER_ONLY\scratch\test_openness_simple_admin.log";
        try
        {
            File.WriteAllText(logPath, "Getting processes...\n");
            var list = TiaPortal.GetProcesses();
            File.AppendAllText(logPath, "Success! Found: " + list.Count + "\n");
            foreach (var p in list)
            {
                File.AppendAllText(logPath, string.Format("PID: {0}\n", p.Id));
            }
        }
        catch (Exception ex)
        {
            File.AppendAllText(logPath, "Error: " + ex.ToString() + "\n");
        }
    }
}
