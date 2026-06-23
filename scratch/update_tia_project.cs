using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.SW.Tags;
using Siemens.Engineering.Compiler;
using Siemens.Engineering.SW.TechnologicalObjects;

// â”€â”€â”€ Custom exception for recoverable fatal errors â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class FatalException : Exception
{
    public FatalException(string msg) : base(msg) { }
}

// ─── Compile statistics returned by CompilePlc ──────────────────────────────
class CompileStats
{
    public string PlcName;
    public int    ErrorCount;
    public int    WarningCount;
    public int    AmbiguousAddressCount;
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class UpdateTiaProject
{
    // â”€â”€ Paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    static readonly string OriginalPath       = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";
    static readonly string BackupPath         = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh_backup_manual";
    static readonly string ExportReadbackDir  = @"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export_manual";
    static readonly string ExportReadbackTmp  = @"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\post_import_export_manual_tmp";
    static readonly string Plc1ImportDir      = @"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\tia_import\PLC_1_Mixing_Import";
    static readonly string Plc2ImportDir      = @"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\tia_import\PLC_2_Mixing_Import";
    static readonly string WarningsReportPath = @"d:\AI_Agent_PLC_LADDER_ONLY\scratch\compile_warnings_report.txt";

    static StringBuilder CompileLog = new StringBuilder();

    // â”€â”€ Entry point â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        System.Threading.Thread.CurrentThread.CurrentCulture = new System.Globalization.CultureInfo("en-US");
        System.Threading.Thread.CurrentThread.CurrentUICulture = new System.Globalization.CultureInfo("en-US");
        try
        {
            Run();
        }
        catch (FatalException ex)
        {
            Console.WriteLine("\n[FATAL] " + ex.Message);
            Environment.ExitCode = 1;
        }
        catch (Exception ex)
        {
            Console.WriteLine("\n[FATAL ERROR]\n" + ex.ToString());
            Environment.ExitCode = 1;
        }
    }

    // â”€â”€ Main logic (throws FatalException on any unrecoverable error) â”€â”€â”€â”€â”€
    static void Run()
    {
        Banner("TIA PORTAL AUTOMATIC UPDATE & COMPILE TOOL (v3)");

        // â”€â”€ 1. Attach â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 1: ATTACHING TO TIA PORTAL");
        var procList = TiaPortal.GetProcesses();
        if (procList.Count == 0)
            throw new FatalException("No running TIA Portal instances found!");
        Console.WriteLine(string.Format("Found {0} TIA Portal instance(s). Finding target project instance...", procList.Count));

        TiaPortalProcess targetProcess = null;
        TiaPortal tia = null;
        foreach (var p in procList)
        {
            try
            {
                var tempTia = p.Attach();
                if (tempTia.Projects.Count > 0 && tempTia.Projects[0].Path.FullName.ToLower().Contains("cuocthi_tdh"))
                {
                    targetProcess = p;
                    tia = tempTia;
                    break;
                }
            }
            catch {}
        }
        if (tia == null)
        {
            Console.WriteLine("Warning: Expected project 'cuocthi_tdh' not found in active instances. Fallback to first process.");
            targetProcess = procList[0];
            tia = targetProcess.Attach();
        }

        if (tia.Projects.Count == 0)
            throw new FatalException("No open projects in TIA Portal!");

        var proj = tia.Projects[0];
        Console.WriteLine(string.Format("Attached to: {0}  Path: {1}", proj.Name, proj.Path.FullName));

        // â”€â”€ 2. Verify project path BEFORE backup â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 2: VERIFYING PROJECT PATH");
        VerifyProjectPath(proj);

        // â”€â”€ 3. Backup â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 3: PROJECT BACKUP");
        Console.WriteLine("Saving current state...");
        proj.Save();
        if (Directory.Exists(BackupPath))
        {
            Console.WriteLine("Removing old backup directory...");
            Directory.Delete(BackupPath, true);
        }
        Console.WriteLine(string.Format("Saving backup to: {0}", BackupPath));
        proj.SaveAs(new DirectoryInfo(BackupPath));
        Console.WriteLine("[OK] Backup saved. Active project is now the backup copy.");

        // â”€â”€ 4. Reopen original â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 4: REOPENING ORIGINAL PROJECT");
        proj.Close();
        Console.WriteLine(string.Format("Opening: {0}", OriginalPath));
        proj = tia.Projects.Open(new FileInfo(OriginalPath));
        Console.WriteLine("[OK] Original project opened.");

        // â”€â”€ 5. Re-verify path after reopen â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 5: RE-VERIFYING REOPENED PROJECT PATH");
        VerifyProjectPath(proj);

        // â”€â”€ 6. Discover PLCs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 6: SCANNING DEVICES");
        List<PlcSoftware> softwares = DiscoverAllPlcSoftwares(proj);
        Console.WriteLine(string.Format("Found {0} PLC Software instance(s):", softwares.Count));
        foreach (var s in softwares)
            Console.WriteLine(string.Format("  Â· {0}", s.Name));

        PlcSoftware plc1 = FindPLC1(softwares);
        PlcSoftware plc2 = FindPLC2(softwares);
        if (plc1 == null) throw new FatalException("Cannot identify PLC1 in project!");
        if (plc2 == null) throw new FatalException("Cannot identify PLC2 in project!");
        Console.WriteLine(string.Format("[IDENTIFIED] PLC1 = {0}   PLC2 = {1}", plc1.Name, plc2.Name));

        // â”€â”€ 7. Pre-import inventory â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 7: PRE-IMPORT BLOCK INVENTORY");
        PrintBlockInventory(plc1, "PLC1");
        PrintBlockInventory(plc2, "PLC2");

        // ── 8. Import PLC1 ───────────────────────────────────────────────
        Section("STEP 8: IMPORTING PLC1 TAGS AND BLOCKS");
        ImportTagTable(plc1, Path.Combine(Plc1ImportDir, "PLC_Tags.xml"), "PLC1");
        DeleteStaleBlock(plc1, "FC_Manual_Control_PLC1", 60);
        ImportBlocks(plc1, Plc1ImportDir, new string[]
        {
            "MB_CLIENT_Write_DB.xml",
            "MB_CLIENT_Read_DB.xml",
            "DB_MB_TCP_Client_Conn_DB.xml",
            "DB_PLC1_MB_Word_Buffer_DB.xml",
            "DB_PLC1_MB_Buffer_DB.xml",
            "DB_PLC1_Recv_From_PLC2_DB.xml",
            "DB_PLC1_Send_To_PLC2_DB.xml",
            "FC_Bon_Chua_Loc.xml",
            "FC_HMI_Animation_PLC1.xml",
            "FC_HMI_Mirror_PLC1.xml",
            "FC_Init_Default_Recipe_PLC1.xml",
            "FC_Manual_Control_PLC1.xml",
            "FC_PLC1_Mixing.xml",
            "FC_VFD_Bon2_Hybrid.xml",
            "Main.xml",
            "Timers_PLC1.xml",
            "OB30_PID_PLC1_Bon2.xml"
        }, "PLC1");
        RenameTechnologicalObjectIfExists(plc1, "AI_PID_Compact_1", "PID_Compact_1", "PLC1");

        // ── 9. Import PLC2 ───────────────────────────────────────────────
        Section("STEP 9: IMPORTING PLC2 TAGS AND BLOCKS");
        DeleteTagTableIfExists(plc2, "AI_Tags", "PLC2");
        ImportTagTable(plc2, Path.Combine(Plc2ImportDir, "PLC_Tags.xml"), "PLC2");
        DeleteStaleBlock(plc2, "FC_Manual_Control_PLC2", 60);
        ImportBlocks(plc2, Plc2ImportDir, new string[]
        {
            "DB_MB_TCP_Server_Conn_DB.xml",
            "DB_PLC2_MB_Holding_Word_DB.xml",
            "DB_MB_TCP_Server_Conn_DB.xml",
            "DB_PLC2_MB_Holding_Word_DB.xml",
            "DB_Modbus_Holding_Register_DB.xml",
            "FC_HMI_Animation_PLC2.xml",
            "FC_HMI_Mirror_PLC2.xml",
            "FC_Init_Default_Recipe_PLC2.xml",
            "FC_Manual_Control_PLC2.xml",
            "FC_PLC2_Mixing.xml",
            "Main.xml",
            "Timers_PLC2.xml",
            "OB31_PID_PLC2_Bon4.xml"
        }, "PLC2");
        RenameTechnologicalObjectIfExists(plc2, "AI_PID_Compact_2", "PID_Compact_2", "PLC2");

        // â”€â”€ 10. Post-import inventory â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 10: POST-IMPORT BLOCK INVENTORY");
        PrintBlockInventory(plc1, "PLC1");
        PrintBlockInventory(plc2, "PLC2");

        // â”€â”€ 11. Compile both PLCs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 11: COMPILING PLC SOFTWARE (REBUILD ALL)");
        CompileStats stats1 = CompilePlc(plc1, proj, "PLC1");
        CompileStats stats2 = CompilePlc(plc2, proj, "PLC2");

        // â”€â”€ 12. Always write compile report â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        File.WriteAllText(WarningsReportPath, CompileLog.ToString(), new System.Text.UTF8Encoding(false));
        Console.WriteLine(string.Format("[OK] Compile report written to: {0}", WarningsReportPath));

        // â”€â”€ 13. Gate on compile errors â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if (stats1.ErrorCount > 0 || stats2.ErrorCount > 0)
        {
            // Close project WITHOUT saving – discards all import changes.
            // The project file on disk is preserved in its last-saved state.
            Console.WriteLine("\n[SAFE CLOSE] Closing project WITHOUT saving (discarding failed-compile import changes)...");
            try
            {
                proj.Close();
                Console.WriteLine("[OK] Project closed without saving. Disk state unchanged.");
            }
            catch (Exception closeEx)
            {
                Console.WriteLine("[WARN] Could not close project cleanly: " + closeEx.Message);
            }

            throw new FatalException(string.Format(
                "Compile failed! PLC1 errors: {0}, PLC2 errors: {1}.\n" +
                "Project NOT saved. Import changes discarded. Readback NOT exported.\n" +
                "See compile report: {2}",
                stats1.ErrorCount, stats2.ErrorCount, WarningsReportPath));
        }

        // â”€â”€ 14. Save project â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 12: SAVING UPDATED PROJECT");
        proj.Save();
        Console.WriteLine("[OK] Project saved.");

        // â”€â”€ 15. Atomic readback export â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Section("STEP 13: EXPORTING READBACK XML (ATOMIC)");
        ExportReadback(proj, plc1, plc2, stats1, stats2);

        Banner("TIA PORTAL UPDATE COMPLETED SUCCESSFULLY!");
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // Path verification
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static void VerifyProjectPath(Project proj)
    {
        string actual   = Path.GetFullPath(proj.Path.FullName);
        string expected = Path.GetFullPath(OriginalPath);
        Console.WriteLine(string.Format("  Expected : {0}", expected));
        Console.WriteLine(string.Format("  Actual   : {0}", actual));
        if (!string.Equals(actual, expected, StringComparison.OrdinalIgnoreCase))
            throw new FatalException(string.Format(
                "Project path MISMATCH!\n  Expected: {0}\n  Actual  : {1}\n" +
                "Aborting to prevent editing the wrong project.",
                expected, actual));
        Console.WriteLine("[OK] Project path verified.");
    }

    // â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• 
    // Device and PLC discovery
    // â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• 
    static List<PlcSoftware> DiscoverAllPlcSoftwares(Project proj)
    {
        var result     = new List<PlcSoftware>();
        var allDevices = new List<Device>();
        CollectDevices(proj, allDevices);
        foreach (var dev in allDevices)
            foreach (var item in dev.DeviceItems)
                CollectPlcSoftware(item, result);
        return result;
    }

    static void CollectDevices(Project proj, List<Device> all)
    {
        foreach (var d in proj.Devices) all.Add(d);
        if (proj.UngroupedDevicesGroup != null)
            foreach (var d in proj.UngroupedDevicesGroup.Devices) all.Add(d);
        CollectGroups(proj.DeviceGroups, all);
    }

    static void CollectGroups(DeviceUserGroupComposition groups, List<Device> all)
    {
        foreach (var g in groups)
        {
            foreach (var d in g.Devices) all.Add(d);
            CollectGroups(g.Groups, all);
        }
    }

    static void CollectPlcSoftware(DeviceItem item, List<PlcSoftware> result)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is PlcSoftware)
        {
            var plc = (PlcSoftware)sc.Software;
            if (!result.Contains(plc)) result.Add(plc);
        }
        foreach (var child in item.DeviceItems)
            CollectPlcSoftware(child, result);
    }

    static PlcSoftware FindPLC1(List<PlcSoftware> softwares)
    {
        foreach (var plc in softwares)
            foreach (var table in plc.TagTableGroup.TagTables)
                foreach (PlcTag tag in table.Tags)
                    if (tag.Name == "Pump3264_Chuyen_Nhanh1" || tag.Name == "MB_TCP_STATUS")
                        return plc;
        return softwares.FirstOrDefault(p => p.Name.Contains("PLC_1") || p.Name.Contains("PLC1"));
    }

    static PlcSoftware FindPLC2(List<PlcSoftware> softwares)
    {
        foreach (var plc in softwares)
            foreach (var table in plc.TagTableGroup.TagTables)
                foreach (PlcTag tag in table.Tags)
                    if (tag.Name == "Pump3265_Chuyen_Nhanh2" || tag.Name == "MB_TCP_Server_Status")
                        return plc;
        return softwares.FirstOrDefault(p => p.Name.Contains("PLC_2") || p.Name.Contains("PLC2"));
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // Block inventory (diagnostic print only)
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static void PrintBlockInventory(PlcSoftware plc, string label)
    {
        Console.WriteLine(string.Format("\n  [{0}] Block Inventory:", label));
        var lines = new List<string>();
        foreach (PlcBlock blk in plc.BlockGroup.Blocks)
        {
            string typeName = blk.GetType().Name;
            string number   = "";
            try { number = GetBlockNumber(blk).ToString(); } catch {}
            lines.Add(string.Format("    {0,-30} #{1,-5}  {2}", typeName, number, blk.Name));
        }
        lines.Sort();
        foreach (var l in lines) Console.WriteLine(l);
        Console.WriteLine(string.Format("  [{0}] Total: {1} block(s).", label, lines.Count));
    }

    static int GetBlockNumber(PlcBlock blk)
    {
        if (blk is OB)        return ((OB)blk).Number;
        if (blk is FC)        return ((FC)blk).Number;
        if (blk is FB)        return ((FB)blk).Number;
        if (blk is GlobalDB)  return ((GlobalDB)blk).Number;
        if (blk is InstanceDB)return ((InstanceDB)blk).Number;
        return -1;
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // Stale block deletion (only when Number == expectedOldNumber)
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static void DeleteStaleBlock(PlcSoftware plc, string blockName, int expectedOldNumber)
    {
        var blk = plc.BlockGroup.Blocks.Find(blockName);
        if (blk == null)
        {
            Console.WriteLine(string.Format("  [SKIP] {0} not found â€“ nothing to delete.", blockName));
            return;
        }
        int actual = -1;
        try { actual = GetBlockNumber(blk); } catch {}
        if (actual == expectedOldNumber)
        {
            Console.WriteLine(string.Format("  [DELETE] Removing stale {0} (#{1}) before importing FC62...", blockName, actual));
            blk.Delete();
            Console.WriteLine(string.Format("  [OK] Deleted {0} #{1}.", blockName, actual));
        }
        else
        {
            Console.WriteLine(string.Format(
                "  [SKIP] {0} found as #{1} (not old #{2}) – Override import will handle it.",
                blockName, actual, expectedOldNumber));
        }
    }

    // ─── Delete tag table by name if it exists ──────────────────────────────────
    static void DeleteTagTableIfExists(PlcSoftware plc, string tableName, string label)
    {
        var table = plc.TagTableGroup.TagTables.Find(tableName);
        if (table != null)
        {
            Console.WriteLine(string.Format("  [DELETE] Removing tag table '{0}' from {1}...", tableName, label));
            table.Delete();
            Console.WriteLine(string.Format("  [OK] Deleted tag table '{0}' from {1}.", tableName, label));
        }
    }

    // ─── Rename technological object if it exists ──────────────────────────────
    static void RenameTechnologicalObjectIfExists(PlcSoftware plc, string oldName, string newName, string label)
    {
        var techGroup = plc.TechnologicalObjectGroup;
        if (techGroup != null)
        {
            foreach (TechnologicalInstanceDB obj in techGroup.TechnologicalObjects)
            {
                if (obj.Name == oldName)
                {
                    Console.WriteLine(string.Format("  [RENAME] Found Technological Object '{0}' in {1}. Renaming to '{2}'...", oldName, label, newName));
                    obj.Name = newName;
                    Console.WriteLine(string.Format("  [OK] Renamed to '{0}'.", newName));
                    break;
                }
            }
        }
    }

    // ─── Count "ambiguous address" warnings in compile messages recursively ───
    static int CountAmbiguousAddressWarnings(System.Collections.IEnumerable messages)
    {
        int count = 0;
        foreach (dynamic msg in messages)
        {
            try
            {
                string desc = msg.Description != null ? msg.Description.ToString() : "";
                if (desc.IndexOf("ambiguous address", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    count++;
                }
                if (msg.Messages != null)
                {
                    count += CountAmbiguousAddressWarnings(msg.Messages);
                }
            }
            catch {}
        }
        return count;
    }

    // ─── Get duplicate address count and table name list ──────────────────────
    static int GetDuplicateAddressCount(PlcSoftware plc, out List<string> tableNames)
    {
        tableNames = new List<string>();
        var addressCounts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
        foreach (PlcTagTable table in plc.TagTableGroup.TagTables)
        {
            tableNames.Add(table.Name);
            foreach (PlcTag tag in table.Tags)
            {
                string addr = tag.LogicalAddress;
                if (!string.IsNullOrEmpty(addr))
                {
                    if (addressCounts.ContainsKey(addr))
                        addressCounts[addr]++;
                    else
                        addressCounts[addr] = 1;
                }
            }
        }
        int dupCount = 0;
        foreach (var kvp in addressCounts)
        {
            if (kvp.Value > 1)
            {
                dupCount++;
            }
        }
        return dupCount;
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• 
    // Tag table import (fatal if file missing or table not importable)
    // â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• 
    // â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• 
    static void ImportTagTable(PlcSoftware plc, string xmlPath, string label)
    {
        if (!File.Exists(xmlPath))
            throw new FatalException(string.Format("{0} tag table file not found: {1}", label, xmlPath));

        Console.WriteLine(string.Format("  Deleting existing {0} tag table (if present)...", label));
        var existing = plc.TagTableGroup.TagTables.Find("PLC_Tags");
        if (existing != null)
        {
            existing.Delete();
            Console.WriteLine("  Existing table deleted.");
        }

        Console.WriteLine(string.Format("  Filtering system tags from {0} tag table...", label));
        string filtered = FilterSystemTags(xmlPath);

        Console.WriteLine(string.Format("  Importing {0} tag table...", label));
        plc.TagTableGroup.TagTables.Import(new FileInfo(filtered), ImportOptions.None);
        Console.WriteLine(string.Format("  [OK] {0} tag table imported.", label));
        try { File.Delete(filtered); } catch {}
    }

    // â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• 
    // Block import (fatal if any file missing)
    // â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• 
    static void ImportBlocks(PlcSoftware plc, string importDir, string[] blockFiles, string label)
    {
        // Pre-check all files exist before importing any
        foreach (var name in blockFiles)
        {
            string path = Path.Combine(importDir, name);
            if (!File.Exists(path))
                throw new FatalException(string.Format(
                    "{0} import file not found: {1}", label, path));
        }

        foreach (var name in blockFiles)
        {
            string path = Path.Combine(importDir, name);
            Console.WriteLine(string.Format("  Importing {0} into {1}...", name, label));
            plc.BlockGroup.Blocks.Import(new FileInfo(path), ImportOptions.Override);
            Console.WriteLine(string.Format("  [OK] {0} imported.", name));
        }
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // Compile â€“ returns CompileStats; NEVER throws on compile errors
    // (caller decides what to do based on ErrorCount)
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static CompileStats CompilePlc(PlcSoftware plc, Project proj, string label)
    {
        var stats = new CompileStats { PlcName = plc.Name };
        Console.WriteLine(string.Format("\n  Compiling {0}...", label));

        ICompilable compilable = GetCompilable(plc, proj);
        if (compilable == null)
            throw new FatalException(string.Format("Cannot get ICompilable for {0}.", label));

        CompilerResult res = compilable.Compile();
        stats.ErrorCount   = res.ErrorCount;
        stats.WarningCount = res.WarningCount;
        stats.AmbiguousAddressCount = CountAmbiguousAddressWarnings(res.Messages);

        string summary = string.Format(
            "  {0} â†’ Status: {1}  |  Errors: {2}  |  Warnings: {3}",
            label, res.State, res.ErrorCount, res.WarningCount);
        Console.WriteLine(summary);
        CompileLog.AppendLine(summary);

        // Log ALL messages (errors + warnings)
        if (res.ErrorCount > 0 || res.WarningCount > 0)
        {
            string hdr = string.Format("\n  [{0} Compile Messages]", label);
            Console.WriteLine(hdr);
            CompileLog.AppendLine(hdr);
            CollectMessages(res.Messages, "    ");
        }

        if (res.ErrorCount == 0)
            Console.WriteLine(string.Format("  [OK] {0} compiled with 0 errors.", label));
        else
            Console.WriteLine(string.Format("  [COMPILE FAIL] {0} has {1} error(s).", label, res.ErrorCount));

        return stats;
    }

    static void CollectMessages(System.Collections.IEnumerable messages, string indent)
    {
        foreach (dynamic msg in messages)
        {
            try
            {
                string state = msg.State  != null ? msg.State.ToString()  : "?";
                string desc  = msg.Description != null ? msg.Description.ToString() : "";
                string code  = "";
                try { code = msg.ErrorCode != null ? msg.ErrorCode.ToString() : ""; } catch {}
                string path  = "";
                try { path = msg.Path != null ? msg.Path.ToString() : ""; } catch {}

                string line = string.Format("{0}[{1}] {2}{3}{4}",
                    indent, state.ToUpper(), desc,
                    string.IsNullOrEmpty(code) ? "" : " (Code: " + code + ")",
                    string.IsNullOrEmpty(path) ? "" : " [Path: " + path + "]");

                Console.WriteLine(line);
                CompileLog.AppendLine(line);
                try { if (msg.Messages != null) CollectMessages(msg.Messages, indent + "  "); } catch {}
            }
            catch (Exception ex)
            {
                Console.WriteLine(indent + "Error reading message: " + ex.Message);
            }
        }
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // Atomic readback export
    //   1. Export everything to ExportReadbackTmp
    //   2. Verify all required files present (fatal if any missing)
    //   3. Write readback_manifest.json to tmp
    //   4. Delete old ExportReadbackDir
    //   5. Move ExportReadbackTmp â†’ ExportReadbackDir
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static void ExportReadback(Project proj, PlcSoftware plc1, PlcSoftware plc2,
                               CompileStats stats1, CompileStats stats2)
    {
        // Clear tmp
        if (Directory.Exists(ExportReadbackTmp))
            Directory.Delete(ExportReadbackTmp, true);
        string p1Blocks = Path.Combine(ExportReadbackTmp, "PLC_1", "Blocks");
        string p2Blocks = Path.Combine(ExportReadbackTmp, "PLC_2", "Blocks");
        Directory.CreateDirectory(p1Blocks);
        Directory.CreateDirectory(p2Blocks);

        var exportedFiles = new List<string>();

        // â”€â”€ PLC1 tags â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Console.WriteLine("\n  [PLC1] Exporting...");
        ExportTagTableRequired(plc1, "PLC_Tags",
            Path.Combine(ExportReadbackTmp, "PLC_1", "PLC_Tags.xml"), "PLC1", exportedFiles);

        // â”€â”€ PLC1 blocks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        string[] plc1Names = new string[]
        {
            "MB_CLIENT_Write_DB",
            "MB_CLIENT_Read_DB",
            "DB_MB_TCP_Client_Conn_DB",
            "DB_PLC1_MB_Word_Buffer_DB",
            "DB_PLC1_MB_Buffer_DB",
            "DB_PLC1_Recv_From_PLC2_DB",
            "DB_PLC1_Send_To_PLC2_DB",
            "FC_Bon_Chua_Loc",
            "FC_HMI_Animation_PLC1",
            "FC_HMI_Mirror_PLC1",
            "FC_Init_Default_Recipe_PLC1",
            "FC_Manual_Control_PLC1",
            "FC_PLC1_Mixing",
            "FC_VFD_Bon2_Hybrid",
            "Main",
            "Timers_PLC1",
            "OB30_PID_PLC1_Bon2"     // NOT re-imported; exported for verification only
        };
        foreach (var name in plc1Names)
            ExportBlockRequired(plc1, name, Path.Combine(p1Blocks, name + ".xml"), "PLC1", exportedFiles);

        // â”€â”€ PLC2 tags â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        Console.WriteLine("\n  [PLC2] Exporting...");
        ExportTagTableRequired(plc2, "PLC_Tags",
            Path.Combine(ExportReadbackTmp, "PLC_2", "PLC_Tags.xml"), "PLC2", exportedFiles);

        // â”€â”€ PLC2 blocks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        string[] plc2Names = new string[]
        {
            "DB_MB_TCP_Server_Conn_DB",
            "DB_PLC2_MB_Holding_Word_DB",
            "DB_Modbus_Holding_Register_DB",
            "FC_HMI_Animation_PLC2",
            "FC_HMI_Mirror_PLC2",
            "FC_Init_Default_Recipe_PLC2",
            "FC_Manual_Control_PLC2",
            "FC_PLC2_Mixing",
            "Main",
            "Timers_PLC2",
            "OB31_PID_PLC2_Bon4"     // NOT re-imported; exported for verification only
        };
        foreach (var name in plc2Names)
            ExportBlockRequired(plc2, name, Path.Combine(p2Blocks, name + ".xml"), "PLC2", exportedFiles);

        // â”€â”€ Verify required files â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        // ── Verify required files ──────────────────────────────────────────────────────────────
        VerifyRequiredExports(p1Blocks, p2Blocks);

        // ── Write manifest ─────────────────────────────────────────────────────────────────────
        WriteManifest(ExportReadbackTmp, plc1, plc2, stats1, stats2, exportedFiles);

        // ── Atomic rename tmp → final with retry loop to handle Windows/TIA Openness filesystem locks
        if (Directory.Exists(ExportReadbackDir))
        {
            for (int i = 0; i < 10; i++)
            {
                try
                {
                    Directory.Delete(ExportReadbackDir, true);
                    break;
                }
                catch
                {
                    System.Threading.Thread.Sleep(500);
                }
            }
        }

        for (int i = 0; i < 15; i++)
        {
            try
            {
                Directory.Move(ExportReadbackTmp, ExportReadbackDir);
                break;
            }
            catch (Exception moveEx)
            {
                if (i == 14) throw moveEx;
                System.Threading.Thread.Sleep(1000);
            }
        }
        Console.WriteLine(string.Format("\n  [OK] Readback atomically committed to: {0}", ExportReadbackDir));

        // ── Final inventory ────────────────────────────────────────────────────────────────────
        Console.WriteLine("\n  [FINAL INVENTORY]");
        PrintBlockInventory(plc1, "PLC1");
        PrintBlockInventory(plc2, "PLC2");
    }

    static void ExportTagTableRequired(PlcSoftware plc, string tableName, string destPath,
                                       string label, List<string> exported)
    {
        var table = plc.TagTableGroup.TagTables.Find(tableName);
        if (table == null)
            throw new FatalException(string.Format(
                "{0} tag table '{1}' not found in TIA â€“ cannot export.", label, tableName));
        table.Export(new FileInfo(destPath), ExportOptions.WithDefaults);
        string rel = destPath.Substring(ExportReadbackTmp.Length + 1).Replace("\\", "/");
        exported.Add(rel);
        Console.WriteLine(string.Format("  [EXPORT] {0} {1} â†’ {2}", label, tableName, Path.GetFileName(destPath)));
    }

    static void ExportBlockRequired(PlcSoftware plc, string blockName, string destPath,
                                    string label, List<string> exported)
    {
        var blk = plc.BlockGroup.Blocks.Find(blockName);
        if (blk == null)
            throw new FatalException(string.Format(
                "{0} block '{1}' not found in TIA â€“ cannot export.", label, blockName));
        blk.Export(new FileInfo(destPath), ExportOptions.WithDefaults);
        string rel = destPath.Substring(ExportReadbackTmp.Length + 1).Replace("\\", "/");
        exported.Add(rel);
        Console.WriteLine(string.Format("  [EXPORT] {0} {1} â†’ {2}", label, blockName, Path.GetFileName(destPath)));
    }

    static void VerifyRequiredExports(string p1Blocks, string p2Blocks)
    {
        string[] plc1Required = new string[]
        {
            "OB30_PID_PLC1_Bon2.xml", "FC_PLC1_Mixing.xml",
            "FC_HMI_Animation_PLC1.xml", "FC_HMI_Mirror_PLC1.xml",
            "FC_Manual_Control_PLC1.xml", "FC_Bon_Chua_Loc.xml",
            "FC_Init_Default_Recipe_PLC1.xml", "Timers_PLC1.xml",
            "Main.xml", "DB_MB_TCP_Client_Conn_DB.xml",
            "DB_PLC1_MB_Word_Buffer_DB.xml",
            "DB_PLC1_MB_Buffer_DB.xml",
            "DB_PLC1_Recv_From_PLC2_DB.xml", "DB_PLC1_Send_To_PLC2_DB.xml",
            "FC_VFD_Bon2_Hybrid.xml", "MB_CLIENT_Write_DB.xml",
            "MB_CLIENT_Read_DB.xml"
        };
        string[] plc2Required = new string[]
        {
            "OB31_PID_PLC2_Bon4.xml", "FC_PLC2_Mixing.xml",
            "FC_HMI_Animation_PLC2.xml", "FC_HMI_Mirror_PLC2.xml",
            "FC_Manual_Control_PLC2.xml", "FC_Init_Default_Recipe_PLC2.xml",
            "Timers_PLC2.xml", "Main.xml", "DB_Modbus_Holding_Register_DB.xml"
        };

        var missing = new List<string>();
        foreach (var f in plc1Required)
            if (!File.Exists(Path.Combine(p1Blocks, f))) missing.Add("PLC_1/Blocks/" + f);
        foreach (var f in plc2Required)
            if (!File.Exists(Path.Combine(p2Blocks, f))) missing.Add("PLC_2/Blocks/" + f);

        if (missing.Count > 0)
            throw new FatalException(
                "Export verification failed â€“ missing files:\n  " +
                string.Join("\n  ", missing.ToArray()));

        Console.WriteLine("  [OK] All required export files present.");
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // Manifest JSON (manual construction â€“ no JSON library needed)
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static void WriteManifest(string dir, PlcSoftware plc1, PlcSoftware plc2,
                              CompileStats s1, CompileStats s2, List<string> files)
    {
        List<string> plc1Tables;
        int plc1Dups = GetDuplicateAddressCount(plc1, out plc1Tables);
        List<string> plc2Tables;
        int plc2Dups = GetDuplicateAddressCount(plc2, out plc2Tables);

        var sb = new StringBuilder();
        sb.AppendLine("{");
        sb.AppendLine(string.Format("  \"timestamp\": \"{0}\",",
            DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")));
        sb.AppendLine(string.Format("  \"project_path\": \"{0}\",",
            OriginalPath.Replace("\\", "\\\\")));
        
        sb.AppendLine(string.Format("  \"plc1_name\": \"{0}\",", s1.PlcName));
        sb.AppendLine(string.Format("  \"plc1_errors\": {0},",   s1.ErrorCount));
        sb.AppendLine(string.Format("  \"plc1_warnings\": {0},", s1.WarningCount));
        sb.AppendLine(string.Format("  \"plc1_ambiguous_address_warnings\": {0},", s1.AmbiguousAddressCount));
        sb.AppendLine(string.Format("  \"plc1_duplicate_addresses\": {0},", plc1Dups));
        
        sb.Append("  \"plc1_tag_tables\": [");
        for (int i = 0; i < plc1Tables.Count; i++)
        {
            sb.Append(string.Format("\"{0}\"", plc1Tables[i]));
            if (i < plc1Tables.Count - 1) sb.Append(", ");
        }
        sb.AppendLine("],");

        sb.AppendLine(string.Format("  \"plc2_name\": \"{0}\",", s2.PlcName));
        sb.AppendLine(string.Format("  \"plc2_errors\": {0},",   s2.ErrorCount));
        sb.AppendLine(string.Format("  \"plc2_warnings\": {0},", s2.WarningCount));
        sb.AppendLine(string.Format("  \"plc2_ambiguous_address_warnings\": {0},", s2.AmbiguousAddressCount));
        sb.AppendLine(string.Format("  \"plc2_duplicate_addresses\": {0},", plc2Dups));

        sb.Append("  \"plc2_tag_tables\": [");
        for (int i = 0; i < plc2Tables.Count; i++)
        {
            sb.Append(string.Format("\"{0}\"", plc2Tables[i]));
            if (i < plc2Tables.Count - 1) sb.Append(", ");
        }
        sb.AppendLine("],");

        sb.AppendLine("  \"exported_files\": [");
        for (int i = 0; i < files.Count; i++)
        {
            string comma = (i < files.Count - 1) ? "," : "";
            sb.AppendLine(string.Format("    \"{0}\"{1}", files[i], comma));
        }
        sb.AppendLine("  ]");
        sb.Append("}");

        string manifestPath = Path.Combine(dir, "readback_manifest.json");
        File.WriteAllText(manifestPath, sb.ToString(), new System.Text.UTF8Encoding(false));
        Console.WriteLine("  [OK] Manifest written: " + manifestPath);
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // ICompilable resolution (DeviceItem â†’ PlcSoftware fallback)
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static ICompilable GetCompilable(PlcSoftware plc, Project proj)
    {
        DeviceItem cpu = FindCpuDeviceItem(proj, plc);
        if (cpu != null)
        {
            var c = cpu.GetService<ICompilable>();
            if (c != null) return c;
        }
        return plc.GetService<ICompilable>();
    }

    static DeviceItem FindCpuDeviceItem(Project project, PlcSoftware plc)
    {
        var allDevices = new List<Device>();
        CollectDevices(project, allDevices);
        foreach (var dev in allDevices)
            foreach (var item in dev.DeviceItems)
            {
                var r = FindCpuRecursive(item, plc);
                if (r != null) return r;
            }
        return null;
    }

    static DeviceItem FindCpuRecursive(DeviceItem item, PlcSoftware plc)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software == plc) return item;
        foreach (var child in item.DeviceItems)
        {
            var r = FindCpuRecursive(child, plc);
            if (r != null) return r;
        }
        return null;
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // Strip Clock_1Hz / FirstScan system tags before import
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static string FilterSystemTags(string xmlPath)
    {
        var doc = new System.Xml.XmlDocument();
        doc.Load(xmlPath);
        var toRemove = new List<System.Xml.XmlNode>();
        foreach (System.Xml.XmlNode n in doc.SelectNodes("//*[local-name()='SW.Tags.PlcTag']"))
        {
            var nameNode = n.SelectSingleNode(".//*[local-name()='Name']");
            if (nameNode != null &&
                (nameNode.InnerText == "Clock_1Hz" || nameNode.InnerText == "FirstScan"))
                toRemove.Add(n);
        }
        foreach (var n in toRemove) n.ParentNode.RemoveChild(n);
        string tmp = xmlPath + ".filtered_temp";
        doc.Save(tmp);
        return tmp;
    }

    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    // Console helpers
    // â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    static void Section(string title)
    {
        Console.WriteLine("\n--- " + title + " ---");
    }

    static void Banner(string title)
    {
        Console.WriteLine("\n=================================================");
        Console.WriteLine(" " + title);
        Console.WriteLine("=================================================");
    }
}

