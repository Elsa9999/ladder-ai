using System;
using System.Reflection;
using Siemens.Engineering;

class ExploreGraphics
{
    static void Main()
    {
        Console.WriteLine("=== REFLECTING ON MultiLingualGraphicComposition ===");
        // We load the assembly and find the type
        Assembly asm = Assembly.GetAssembly(typeof(Project));
        Type graphicsCompType = asm.GetType("Siemens.Engineering.Hmi.Globalization.MultiLingualGraphicComposition");
        if (graphicsCompType == null)
        {
            Console.WriteLine("Type Siemens.Engineering.Hmi.Globalization.MultiLingualGraphicComposition not found!");
            return;
        }

        foreach (var m in graphicsCompType.GetMethods(BindingFlags.Public | BindingFlags.Instance))
        {
            if (m.DeclaringType == graphicsCompType || m.Name == "Import" || m.Name == "Create" || m.Name == "Add")
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
