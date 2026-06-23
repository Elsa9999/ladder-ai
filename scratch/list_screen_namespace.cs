using System;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;

class ListScreenNamespace
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            Assembly hmiAssembly = Assembly.GetAssembly(typeof(HmiTarget));
            Type[] types = null;
            try
            {
                types = hmiAssembly.GetTypes();
            }
            catch (ReflectionTypeLoadException ex)
            {
                List<Type> list = new List<Type>();
                foreach (var t in ex.Types)
                {
                    if (t != null) list.Add(t);
                }
                types = list.ToArray();
            }

            Console.WriteLine("Types in Siemens.Engineering.Hmi.Screen namespace:");
            foreach (Type t in types)
            {
                if (t.Namespace != null && t.Namespace.Contains("Siemens.Engineering.Hmi.Screen"))
                {
                    Console.WriteLine("  " + t.FullName);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
