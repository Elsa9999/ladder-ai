using System;
using System.Reflection;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.WatchAndForceTables;

class InspectPlcSoftware
{
    static void Main()
    {
        InspectMethods(typeof(PlcWatchTable));
        InspectMethods(typeof(PlcWatchAndForceTableSystemGroup));
        InspectMethods(typeof(PlcWatchTableComposition));
    }

    static void InspectMethods(Type t)
    {
        Console.WriteLine("\nMethods of " + t.Name + ":");
        foreach (var m in t.GetMethods())
        {
            if (m.IsPublic && !m.IsSpecialName)
            {
                var paras = m.GetParameters();
                string pStr = "";
                foreach (var p in paras) pStr += p.ParameterType.Name + " " + p.Name + ", ";
                Console.WriteLine("  " + m.ReturnType.Name + " " + m.Name + "(" + pStr.TrimEnd(' ', ',') + ")");
            }
        }
    }
}
