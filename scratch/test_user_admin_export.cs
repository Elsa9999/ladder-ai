using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;

class TestUserAdminExport
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("==============================================");
        Console.WriteLine(" TIA HMI USER ADMINISTRATION EXPORTER");
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
            Console.WriteLine("HMI Target Name: " + hmi.Name);

            // Access UserAdministration service via reflection to check what namespaces/types are exported
            // We use reflection so that the compiler doesn't throw if the type is slightly different in V18.
            object userAdmin = null;
            MethodInfo getServiceMethod = hmi.GetType().GetMethod("GetService");
            
            // Search through types to find the UserAdministration class
            Type userAdminType = null;
            foreach (var assembly in AppDomain.CurrentDomain.GetAssemblies())
            {
                if (assembly.FullName.Contains("Siemens.Engineering"))
                {
                    foreach (var type in assembly.GetTypes())
                    {
                        if (type.Name == "UserAdministration")
                        {
                            userAdminType = type;
                            break;
                        }
                    }
                }
                if (userAdminType != null) break;
            }

            if (userAdminType == null)
            {
                Console.WriteLine("Error: Type 'UserAdministration' not found in loaded assemblies.");
                return;
            }

            Console.WriteLine("Found UserAdministration Type: " + userAdminType.FullName);
            
            var genericGetService = getServiceMethod.MakeGenericMethod(userAdminType);
            userAdmin = genericGetService.Invoke(hmi, null);

            if (userAdmin == null)
            {
                Console.WriteLine("Error: GetService<UserAdministration> returned null.");
                return;
            }

            Console.WriteLine("Successfully retrieved UserAdministration object!");

            // Let's invoke the Export method on the UserAdministration object
            MethodInfo exportMethod = userAdmin.GetType().GetMethod("Export", new Type[] { typeof(FileInfo), typeof(ExportOptions) });
            if (exportMethod == null)
            {
                Console.WriteLine("Error: Export method not found on UserAdministration.");
                return;
            }

            string xmlPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\UserAdministration.xml";
            if (File.Exists(xmlPath)) File.Delete(xmlPath);

            Console.WriteLine("Exporting UserAdministration to: " + xmlPath);
            exportMethod.Invoke(userAdmin, new object[] { new FileInfo(xmlPath), ExportOptions.WithDefaults });
            Console.WriteLine("EXPORT SUCCESSFUL!");
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
