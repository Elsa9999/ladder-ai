using System;
using System.Reflection;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class ExploreHmiScreens
{
    static void Main()
    {
        Console.WriteLine("=== REFLECTING ON ScreenSystemFolder ===");
        ReflectType(typeof(ScreenSystemFolder));
        
        Console.WriteLine("=== REFLECTING ON ScreenFolder ===");
        // We don't have direct access to ScreenFolder type by compiling if it's in another namespace, 
        // but we can try to load it by name or through the Assembly.
        // Let's reflect on HmiTarget.ScreenFolder properties.
        try
        {
            Type folderType = typeof(ScreenSystemFolder);
            Console.WriteLine("Base Type: " + folderType.BaseType.FullName);
            ReflectType(folderType.BaseType);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error reflecting base type: " + ex.Message);
        }

        Console.WriteLine("=== REFLECTING ON Screen ===");
        try
        {
            // Try to find the Screen type. It's likely in Siemens.Engineering.Hmi.Screen.Screen.
            // Let's check using assembly-qualified name if we can, or typeof(Screen) if it resolves.
            // Wait, does Siemens.Engineering.Hmi.Screen.Screen compile? Let's try:
            Type screenType = typeof(Screen);
            ReflectType(screenType);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error reflecting Screen: " + ex.Message);
        }
    }

    static void ReflectType(Type t)
    {
        if (t == null) return;
        Console.WriteLine("Type: " + t.FullName);
        Console.WriteLine("Properties:");
        foreach (var prop in t.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            Console.WriteLine(string.Format("  {0} : {1}", prop.Name, prop.PropertyType.FullName));
        }
        Console.WriteLine("Methods:");
        foreach (var m in t.GetMethods(BindingFlags.Public | BindingFlags.Instance))
        {
            if (m.DeclaringType == t)
            {
                Console.WriteLine(string.Format("  {0} (returns {1})", m.Name, m.ReturnType.FullName));
            }
        }
    }
}
