using System;
using System.Reflection;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;

class ExploreHmiTarget
{
    static void Main()
    {
        Console.WriteLine("=== REFLECTING ON HmiTarget ===");
        try
        {
            Type hmiTargetType = typeof(HmiTarget);
            Console.WriteLine("Type Name: " + hmiTargetType.FullName);
            Console.WriteLine("\n--- PROPERTIES ---");
            foreach (var prop in hmiTargetType.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static))
            {
                Console.WriteLine(string.Format("{0} : {1}", prop.Name, prop.PropertyType.FullName));
            }

            Console.WriteLine("\n--- METHODS ---");
            foreach (var method in hmiTargetType.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static))
            {
                if (method.DeclaringType == hmiTargetType)
                {
                    Console.WriteLine(string.Format("{0} (returns {1})", method.Name, method.ReturnType.FullName));
                }
            }

            // Also inspect types in Siemens.Engineering.Hmi assembly
            Console.WriteLine("\n--- ALL TYPES IN Siemens.Engineering.Hmi ASSEMBLY ---");
            Assembly asm = Assembly.GetAssembly(typeof(HmiTarget));
            foreach (Type t in asm.GetTypes())
            {
                if (t.IsPublic)
                {
                    Console.WriteLine(t.FullName);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
