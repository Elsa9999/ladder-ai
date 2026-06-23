using System;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;

class ListButtonType
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

            Console.WriteLine("Button/ScreenItem types:");
            foreach (Type t in types)
            {
                if (t.Name.Contains("Button") || t.Name.Contains("ScreenItem"))
                {
                    Console.WriteLine(string.Format("  Name: {0}, FullName: {1}", t.Name, t.FullName));
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
