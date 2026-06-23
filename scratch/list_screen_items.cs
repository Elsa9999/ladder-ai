using System;
using System.Reflection;
using System.Collections.Generic;

class ListScreenItems
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            // Load Siemens.Engineering assembly dynamically
            Assembly engAssembly = Assembly.LoadFrom(@"D:\AI_Agent_PLC_LADDER_ONLY\Ladder\Siemens.Engineering.dll");
            Console.WriteLine("Siemens.Engineering loaded successfully.");

            Type[] allTypes = null;
            try
            {
                allTypes = engAssembly.GetTypes();
            }
            catch (ReflectionTypeLoadException ex)
            {
                List<Type> list = new List<Type>();
                foreach (var t in ex.Types)
                {
                    if (t != null) list.Add(t);
                }
                allTypes = list.ToArray();
            }

            Console.WriteLine("\nAll types containing Hmi.Screen in Siemens.Engineering:");
            foreach (var type in allTypes)
            {
                if (type.FullName != null && type.FullName.Contains("Hmi.Screen"))
                {
                    Console.WriteLine(string.Format("  - {0}", type.FullName));
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
