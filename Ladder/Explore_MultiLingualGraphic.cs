using System;
using System.Reflection;
using Siemens.Engineering;

class ExploreMultiLingualGraphic
{
    static void Main()
    {
        Console.WriteLine("=== REFLECTING ON MultiLingualGraphic ===");
        Assembly asm = Assembly.GetAssembly(typeof(Project));
        Type graphicType = asm.GetType("Siemens.Engineering.Hmi.Globalization.MultiLingualGraphic");
        if (graphicType == null)
        {
            Console.WriteLine("Type Siemens.Engineering.Hmi.Globalization.MultiLingualGraphic not found!");
            return;
        }

        Console.WriteLine("Properties:");
        foreach (var prop in graphicType.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            Console.WriteLine(string.Format("  {0} : {1}", prop.Name, prop.PropertyType.FullName));
        }

        Console.WriteLine("Methods:");
        foreach (var m in graphicType.GetMethods(BindingFlags.Public | BindingFlags.Instance))
        {
            if (m.DeclaringType == graphicType || m.Name == "Export" || m.Name == "Import")
            {
                Console.Write(string.Format("  {0} (returns {1}) -> ", m.Name, m.ReturnType.FullName));
                foreach (var p in m.GetParameters())
                {
                    Console.Write(string.Format("{0} {1}, ", p.ParameterType.FullName, p.Name));
                }
                Console.WriteLine();
            }
        }
    }
}
