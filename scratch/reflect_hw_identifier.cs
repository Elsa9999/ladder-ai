using System;
using System.Reflection;
using Siemens.Engineering;
using Siemens.Engineering.HW;

class ReflectHwIdentifier
{
    static void Main()
    {
        try
        {
            var assembly = Assembly.GetAssembly(typeof(Project));
            Type hwIdType = assembly.GetType("Siemens.Engineering.HW.HwIdentifier");
            if (hwIdType == null)
            {
                Console.WriteLine("Type HwIdentifier not found!");
                return;
            }
            Console.WriteLine("Properties of " + hwIdType.FullName + ":");
            foreach (var prop in hwIdType.GetProperties(BindingFlags.Public | BindingFlags.Instance))
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
