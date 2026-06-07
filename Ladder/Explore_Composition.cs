using System;
using System.Reflection;
using Siemens.Engineering.Hmi.Screen;

class ExploreComposition
{
    static void Main()
    {
        Console.WriteLine("=== METHODS OF ScreenComposition ===");
        Type compType = typeof(ScreenComposition);
        foreach (var method in compType.GetMethods(BindingFlags.Public | BindingFlags.Instance))
        {
            if (method.DeclaringType == compType || method.Name == "Import" || method.Name == "Export")
            {
                Console.Write(string.Format("  {0} (returns {1}) -> ", method.Name, method.ReturnType.FullName));
                foreach (var p in method.GetParameters())
                {
                    Console.Write(string.Format("{0} {1}, ", p.ParameterType.FullName, p.Name));
                }
                Console.WriteLine();
            }
        }

        Console.WriteLine("\n=== METHODS OF Screen ===");
        Type screenType = typeof(Screen);
        foreach (var method in screenType.GetMethods(BindingFlags.Public | BindingFlags.Instance))
        {
            if (method.Name == "Export" || method.Name == "Import")
            {
                Console.Write(string.Format("  {0} (returns {1}) -> ", method.Name, method.ReturnType.FullName));
                foreach (var p in method.GetParameters())
                {
                    Console.Write(string.Format("{0} {1}, ", p.ParameterType.FullName, p.Name));
                }
                Console.WriteLine();
            }
        }
    }
}
