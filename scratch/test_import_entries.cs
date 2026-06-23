using System;
using System.IO;
using Siemens.Engineering;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW.WatchAndForceTables;

class TestImportEntries
{
    static void Main()
    {
        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0) return;
            var tia = procList[0].Attach();
            var proj = tia.Projects[0];
            
            PlcSoftware plc1 = null;
            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is PlcSoftware)
                    {
                        var software = (PlcSoftware)sc.Software;
                        if (software.Name == "PLC_1")
                        {
                            plc1 = software;
                            break;
                        }
                    }
                }
            }

            if (plc1 == null) return;

            string xml = @"<?xml version=""1.0"" encoding=""utf-8""?>
<Document>
  <Engineering version=""V18"" />
  <DocumentInfo>
    <Created>2026-06-08T05:50:11Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.WatchAndForceTables.PlcWatchTable ID=""0"">
    <AttributeList>
      <Name>WT_Test_Import_Schema</Name>
    </AttributeList>
    <ObjectList>
      <SW.WatchAndForceTables.PlcWatchTableEntry ID=""1"" CompositionName=""Entries"">
        <AttributeList>
          <Name>AI_MB_TCP_iStep</Name>
        </AttributeList>
      </SW.WatchAndForceTables.PlcWatchTableEntry>
      <SW.WatchAndForceTables.PlcWatchTableEntry ID=""2"" CompositionName=""Entries"">
        <AttributeList>
          <Name>AI_MB_TCP_Write_Req</Name>
        </AttributeList>
      </SW.WatchAndForceTables.PlcWatchTableEntry>
    </ObjectList>
  </SW.WatchAndForceTables.PlcWatchTable>
</Document>";

            string tempPath = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\test_import_wt.xml";
            File.WriteAllText(tempPath, xml, System.Text.Encoding.UTF8);

            var wts = plc1.WatchAndForceTableGroup.WatchTables;
            var existing = wts.Find("WT_Test_Import_Schema");
            if (existing != null) existing.Delete();

            Console.WriteLine("Importing watch table...");
            wts.Import(new FileInfo(tempPath), ImportOptions.None);
            Console.WriteLine("Import succeeded!");

            var imported = wts.Find("WT_Test_Import_Schema");
            if (imported != null)
            {
                Console.WriteLine("Imported table entries count: " + imported.Entries.Count);
                foreach (var entry in imported.Entries)
                {
                    Console.WriteLine("  Entry Type: " + entry.GetType().Name);
                    // Print name or address via reflection if it is PlcWatchTableEntry
                    if (entry is PlcWatchTableEntry)
                    {
                        var wte = (PlcWatchTableEntry)entry;
                        Console.WriteLine("    Tag Name: " + wte.Name + ", Address: " + wte.Address);
                    }
                }
                imported.Delete();
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }
}
