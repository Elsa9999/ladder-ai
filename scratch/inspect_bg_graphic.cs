using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using System.Globalization;

class InspectBgGraphic
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" INSPECT BACKGROUND GRAPHIC");
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

            dynamic graphics = proj.Graphics;
            dynamic targetGraphic = null;
            foreach (dynamic g in graphics)
            {
                if (g.Name == "9e382997-af09-41cf-ab1c-3299fad62071")
                {
                    targetGraphic = g;
                    break;
                }
            }

            if (targetGraphic == null)
            {
                Console.WriteLine("Không tìm thấy graphic: 9e382997-af09-41cf-ab1c-3299fad62071");
                return;
            }

            Console.WriteLine("Đã tìm thấy graphic: " + targetGraphic.Name);
            Console.WriteLine("Type: " + targetGraphic.GetType().FullName);

            // Reflect properties
            foreach (var prop in targetGraphic.GetType().GetProperties())
            {
                try
                {
                    object val = prop.GetValue(targetGraphic, null);
                    Console.WriteLine(string.Format("  Property: {0} ({1}) = {2}", prop.Name, prop.PropertyType.Name, val ?? "null"));
                }
                catch (Exception ex)
                {
                    Console.WriteLine(string.Format("  Property: {0} - Lỗi: {1}", prop.Name, ex.Message));
                }
            }

            // Let's check if there are nested objects or compositions
            try
            {
                // Typically ProjectGraphic has a property for the actual files/images per language
                // Let's reflect methods
                Console.WriteLine("\nReflecting methods of graphic object:");
                foreach (var method in targetGraphic.GetType().GetMethods(BindingFlags.Public | BindingFlags.Instance))
                {
                    if (method.DeclaringType == targetGraphic.GetType())
                    {
                        Console.WriteLine(string.Format("  Method: {0}", method.Name));
                    }
                }
            }
            catch {}
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }
}
