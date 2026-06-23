using System;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;

class ReflectHwTypes
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            var assembly = Assembly.GetAssembly(typeof(Project));
            Console.WriteLine("Assembly: " + assembly.FullName);

            Type[] allTypes = null;
            try
            {
                allTypes = assembly.GetTypes();
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

            foreach (var type in allTypes)
            {
                if (type.FullName.StartsWith("Siemens.Engineering.HW") && type.IsPublic)
                {
                    Console.WriteLine("Type: " + type.FullName);
                    if (type.IsInterface)
                        Console.WriteLine("  (Interface)");
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
