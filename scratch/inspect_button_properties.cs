using System;
using System.Reflection;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;

class InspectButtonPropertiesDirect
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            Type screenItemType = typeof(ScreenItem);
            Console.WriteLine("ScreenItem class: " + screenItemType.FullName);

            Console.WriteLine("ScreenItem properties:");
            foreach (var prop in screenItemType.GetProperties(BindingFlags.Public | BindingFlags.Instance))
            {
                Console.WriteLine(string.Format("  Property: {0} ({1})", prop.Name, prop.PropertyType.FullName));
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}

