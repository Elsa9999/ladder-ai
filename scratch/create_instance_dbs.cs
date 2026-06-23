using System;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;

class CreateInstanceDBs
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Attached to Project: " + proj.Name);

            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var plcSoftware = GetPlcSoftware(item);
                    if (plcSoftware != null)
                    {
                        Console.WriteLine("\nProcessing PLC: " + plcSoftware.Name);
                        var blocks = plcSoftware.BlockGroup.Blocks;

                        if (plcSoftware.Name.Contains("PLC_1"))
                        {
                            CreateDb(blocks, "MB_COMM_LOAD_DB", 50, "MB_COMM_LOAD");
                            CreateDb(blocks, "MB_MASTER_DB", 51, "MB_MASTER");
                            CreateDb(blocks, "MB_CLIENT_DB", 52, "MB_CLIENT");
                        }
                        else if (plcSoftware.Name.Contains("PLC_2"))
                        {
                            CreateDb(blocks, "MB_SERVER_DB", 53, "MB_SERVER");
                        }
                    }
                }
            }
            Console.WriteLine("\nFinished processing!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void CreateDb(PlcBlockComposition blocks, string name, int dbNumber, string instanceOf)
    {
        var existing = blocks.Find(name);
        if (existing != null)
        {
            Console.WriteLine(string.Format("  Instance DB '{0}' already exists. Deleting to recreate...", name));
            try
            {
                existing.Delete();
            }
            catch (Exception ex)
            {
                Console.WriteLine("    Failed to delete existing: " + ex.Message);
            }
        }

        Console.WriteLine(string.Format("  Creating Instance DB '{0}' (DB {1}) for block '{2}'...", name, dbNumber, instanceOf));
        try
        {
            blocks.CreateInstanceDB(name, false, dbNumber, instanceOf);
            Console.WriteLine("    SUCCESS!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("    FAILED: " + ex.Message);
        }
    }

    static PlcSoftware GetPlcSoftware(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware) return sc.Software as PlcSoftware;
        foreach (var child in item.DeviceItems)
        {
            var sw = GetPlcSoftware(child);
            if (sw != null) return sw;
        }
        return null;
    }
}
