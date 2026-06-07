using System;
using System.Reflection;
using Siemens.Engineering;

class ExploreProject
{
    static void Main()
    {
        Console.WriteLine("=== REFLECTING ON Project ===");
        Type projType = typeof(Project);
        foreach (var prop in projType.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            Console.WriteLine(string.Format("{0} : {1}", prop.Name, prop.PropertyType.FullName));
        }
    }
}
