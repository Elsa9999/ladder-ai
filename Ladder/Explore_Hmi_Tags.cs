
using System;
using System.Reflection;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;

class ExploreHmiTags
{
    static void Main()
    {
        Console.WriteLine("=== REFLECTING ON HMI TAG CLASSES ===");
        try
        {
            InspectType(typeof(TagFolder));
            InspectType(typeof(TagTable));
            InspectType(typeof(Tag));
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void InspectType(Type type)
    {
        Console.WriteLine("\n---------------------------------");
        Console.WriteLine("Class: " + type.FullName);
        Console.WriteLine("---------------------------------");
        Console.WriteLine("Properties:");
        foreach (var prop in type.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            Console.WriteLine(string.Format("  {0} : {1}", prop.Name, prop.PropertyType.FullName));
        }
    }
}
