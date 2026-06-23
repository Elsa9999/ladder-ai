using System;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;

class FindAlarmInDll
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

            Console.WriteLine("Types in Siemens.Engineering.Hmi.Alarm namespace:");
            foreach (Type t in types)
            {
                if (t.Namespace != null && t.Namespace.Equals("Siemens.Engineering.Hmi.Alarm"))
                {
                    Console.WriteLine("  " + t.FullName);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi: " + ex.ToString());
        }
    }
}
