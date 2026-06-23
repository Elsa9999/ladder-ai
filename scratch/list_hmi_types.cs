using System;
using System.Reflection;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;

class ListSecurityTypes
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        
        Assembly assembly = Assembly.GetAssembly(typeof(Project));
        Type[] types = null;
        try
        {
            types = assembly.GetTypes();
        }
        catch (ReflectionTypeLoadException ex)
        {
            List<Type> list = new List<Type>();
            foreach (var t in ex.Types)
            {
                if (t != null) list.Add(t);
            }
            types = list.ToArray();
        }

        Console.WriteLine("Security/Umac Namespaces:");
        foreach (Type t in types)
        {
            try
            {
                string ns = t.Namespace;
                if (ns != null && (ns.Contains("Umac") || ns.Contains("Security") || ns.Contains("Hmi")))
                {
                    if (t.Name.Contains("User") || t.Name.Contains("Security") || t.Name.Contains("Admin") || t.Name.Contains("Group"))
                    {
                        Console.WriteLine(string.Format("  Namespace: {0}, Name: {1}, FullName: {2}", ns, t.Name, t.FullName));
                    }
                }
            }
            catch {}
        }
    }
}
