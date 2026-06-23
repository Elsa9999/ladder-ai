using System;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.SW;

class ReflectOpenness
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            var assembly = Assembly.GetAssembly(typeof(Project));
            Type tidType = assembly.GetType("Siemens.Engineering.SW.TechnologicalObjects.TechnologicalInstanceDB");
            if (tidType == null)
            {
                Console.WriteLine("Type Siemens.Engineering.SW.TechnologicalObjects.TechnologicalInstanceDB not found!");
                return;
            }
            Console.WriteLine("\nProperties of " + tidType.FullName + ":");
            foreach (var prop in tidType.GetProperties(BindingFlags.Public | BindingFlags.Instance))
            {
                Console.WriteLine("  Property: " + prop.PropertyType.Name + " " + prop.Name);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
