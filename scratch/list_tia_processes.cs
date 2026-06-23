using System;
using System.IO;
using System.Reflection;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;

class ListTiaProcesses
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        string dumpPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\network_details_output.txt";
        
        try
        {
            int targetPid = 14620;
            var processes = TiaPortal.GetProcesses();
            TiaPortalProcess selectedProcess = null;
            foreach (var p in processes)
            {
                if (p.Id == targetPid) { selectedProcess = p; break; }
            }

            if (selectedProcess == null)
            {
                Console.WriteLine("ERROR: PID " + targetPid + " not found!");
                return;
            }

            TiaPortal tia = selectedProcess.Attach();
            Project proj = tia.Projects[0];

            using (StreamWriter sw = new StreamWriter(dumpPath, false, System.Text.Encoding.UTF8))
            {
                sw.WriteLine("=== REFLECTING ON HW TYPES ===");
                
                // Reflect NetworkInterface
                sw.WriteLine("\n--- Siemens.Engineering.HW.Features.NetworkInterface ---");
                Type niType = typeof(NetworkInterface);
                foreach (var prop in niType.GetProperties())
                {
                    sw.WriteLine(string.Format("  Prop: {0} | Type: {1}", prop.Name, prop.PropertyType.FullName));
                }
                
                // Reflect Node
                sw.WriteLine("\n--- Siemens.Engineering.HW.Features.Node ---");
                Type nodeType = typeof(Node);
                foreach (var prop in nodeType.GetProperties())
                {
                    sw.WriteLine(string.Format("  Prop: {0} | Type: {1}", prop.Name, prop.PropertyType.FullName));
                }

                // Reflect Subnet
                sw.WriteLine("\n--- Siemens.Engineering.HW.Subnet ---");
                Type subnetType = typeof(Subnet);
                foreach (var prop in subnetType.GetProperties())
                {
                    sw.WriteLine(string.Format("  Prop: {0} | Type: {1}", prop.Name, prop.PropertyType.FullName));
                }
            }
            Console.WriteLine("SUCCESS: Written HW reflection to " + dumpPath);
        }
        catch (Exception ex)
        {
            Console.WriteLine("EXCEPTION: " + ex.ToString());
        }
    }
}
