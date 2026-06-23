using System;
using System.Reflection;
using Siemens.Engineering.Hmi.Tag;

class ReflectTagProperties
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            Type tagType = typeof(Tag);
            Console.WriteLine("Type Name: " + tagType.FullName);
            Console.WriteLine("\n--- PROPERTIES ---");
            foreach (var prop in tagType.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static))
            {
                Console.WriteLine(string.Format("  Prop: {0} | Type: {1} | CanRead: {2} | CanWrite: {3}", 
                    prop.Name, prop.PropertyType.FullName, prop.CanRead, prop.CanWrite));
            }

            Console.WriteLine("\n--- METHODS ---");
            foreach (var method in tagType.GetMethods(BindingFlags.Public | BindingFlags.Instance))
            {
                if (method.DeclaringType == tagType)
                {
                    Console.WriteLine(string.Format("  Method: {0} | ReturnType: {1}", 
                        method.Name, method.ReturnType.FullName));
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
