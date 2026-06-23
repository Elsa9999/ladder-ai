using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Blocks;
using Siemens.Engineering.SW.Tags;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Tag;
using Siemens.Engineering.Compiler;

class ImportSimB3to7
{
    // ============================================================
    // PATHS - tất cả file cần import
    // ============================================================
    static readonly string FOLDER_PLC = @"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\PLC";
    static readonly string FOLDER_HMI = @"d:\AI_Agent_PLC_LADDER_ONLY\projects\scadabai_sim\HMI";

    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine("  IMPORT SIM B3→B7 INTO TIA PORTAL");
        Console.WriteLine("=================================================");

        bool doCompile = args.Any(a => a.Equals("compile", StringComparison.OrdinalIgnoreCase));

        try
        {
            // --- Kết nối TIA Portal ---
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("[ERROR] Không tìm thấy TIA Portal đang mở!");
                return;
            }

            Console.WriteLine("Tìm thấy " + procList.Count + " TIA Portal process...");
            var tia = procList[0].Attach();
            if (tia.Projects.Count == 0)
            {
                Console.WriteLine("[ERROR] Không có project nào đang mở!");
                return;
            }

            var proj = tia.Projects[0];
            Console.WriteLine("Project: " + proj.Name);

            // --- Tìm PLC Software ---
            PlcSoftware plcSw = null;
            List<HmiTarget> hmiTargets = new List<HmiTarget>();

            foreach (var dev in proj.Devices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    if (plcSw == null)
                        plcSw = GetPlcSoftware(item);
                    FindHmiTargets(item, hmiTargets);
                }
            }
            foreach (var devGrp in proj.DeviceGroups)
                ScanGroup(devGrp, ref plcSw, hmiTargets);

            if (plcSw == null)
            {
                Console.WriteLine("[ERROR] Không tìm thấy PLC Software!");
                return;
            }
            Console.WriteLine("PLC Software: " + plcSw.Name);
            Console.WriteLine("HMI Targets: " + hmiTargets.Count);

            int totalOk = 0, totalFail = 0;

            // ============================================================
            // STEP 1: Import PLC Tag Table
            // ============================================================
            Console.WriteLine("\n--- [1/4] Import PLC Tags ---");
            string plcTagFile = Path.Combine(FOLDER_PLC, "PLC_Tags_B3to7.xml");
            if (File.Exists(plcTagFile))
            {
                Console.WriteLine("  File: PLC_Tags_B3to7.xml");
                try
                {
                    plcSw.TagTableGroup.TagTables.Import(new FileInfo(plcTagFile), ImportOptions.Override);
                    Console.WriteLine("  [OK] PLC_Tags_B3to7 imported!");
                    totalOk++;
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  [FAIL] " + ex.Message);
                    totalFail++;
                }
            }
            else
            {
                Console.WriteLine("  [SKIP] Không tìm thấy: " + plcTagFile);
            }

            // ============================================================
            // STEP 2: Import Timer Instance DB
            // ============================================================
            Console.WriteLine("\n--- [2/4] Import Timer_Sim_DB ---");
            string timerDbFile = Path.Combine(FOLDER_PLC, "Timer_Sim_DB.xml");
            if (File.Exists(timerDbFile))
            {
                Console.WriteLine("  File: Timer_Sim_DB.xml");
                try
                {
                    plcSw.BlockGroup.Blocks.Import(new FileInfo(timerDbFile), ImportOptions.Override);
                    Console.WriteLine("  [OK] Timer_Sim_DB imported!");
                    totalOk++;
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  [FAIL] " + ex.Message);
                    totalFail++;
                }
            }
            else
            {
                Console.WriteLine("  [SKIP] Không tìm thấy: " + timerDbFile);
            }

            // ============================================================
            // STEP 3: Import FC Simulation (236 networks LAD)
            // ============================================================
            Console.WriteLine("\n--- [3/4] Import FC_SCADA_Sim_B3to7 (LAD, 236 networks) ---");
            string fcFile = Path.Combine(FOLDER_PLC, "FC_SCADA_Sim_B3to7.xml");
            if (File.Exists(fcFile))
            {
                Console.WriteLine("  File: FC_SCADA_Sim_B3to7.xml (" + (new FileInfo(fcFile).Length / 1024) + " KB)");
                Console.WriteLine("  (Đang import 236 LAD networks, vui lòng chờ...)");
                try
                {
                    plcSw.BlockGroup.Blocks.Import(new FileInfo(fcFile), ImportOptions.Override);
                    Console.WriteLine("  [OK] FC_SCADA_Sim_B3to7 imported!");
                    totalOk++;
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  [FAIL] " + ex.Message);
                    totalFail++;
                }
            }
            else
            {
                Console.WriteLine("  [SKIP] Không tìm thấy: " + fcFile);
            }

            // ============================================================
            // STEP 4: Import HMI Tags
            // ============================================================
            Console.WriteLine("\n--- [4/4] Import HMI Tags (230 tags) ---");
            string hmiTagFile = Path.Combine(FOLDER_HMI, "HMI_Tags_B3to7_All.xml");

            if (!File.Exists(hmiTagFile))
            {
                Console.WriteLine("  [SKIP] Không tìm thấy: " + hmiTagFile);
            }
            else if (hmiTargets.Count == 0)
            {
                Console.WriteLine("  [SKIP] Không tìm thấy HMI device trong project!");
            }
            else
            {
                foreach (var hmiTarget in hmiTargets)
                {
                    Console.WriteLine("  HMI Target: " + hmiTarget.Name);
                    Console.WriteLine("  File: HMI_Tags_B3to7_All.xml");
                    try
                    {
                        hmiTarget.TagFolder.TagTables.Import(new FileInfo(hmiTagFile), ImportOptions.Override);
                        Console.WriteLine("  [OK] HMI_Tags_B3to7_All imported vào " + hmiTarget.Name + "!");
                        totalOk++;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("  [FAIL] " + ex.Message);
                        totalFail++;
                    }
                }
            }

            // ============================================================
            // OPTIONAL: Compile
            // ============================================================
            if (doCompile)
            {
                Console.WriteLine("\n--- [5/5] Compiling PLC ---");
                try
                {
                    var compilable = plcSw.GetService<ICompilable>();
                    if (compilable != null)
                    {
                        Console.WriteLine("  Compiling...");
                        var result = compilable.Compile();
                        int errors = 0, warnings = 0;
                        foreach (var msg in result.Messages)
                        {
                            string s = msg.State.ToString();
                            if (s.Contains("Error")) { errors++; Console.WriteLine("  [ERROR] " + msg.Description); }
                            else if (s.Contains("Warning")) { warnings++; }
                        }
                        Console.WriteLine("  Compile result: " + result.State + " | Errors: " + errors + " | Warnings: " + warnings);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  [FAIL] Compile: " + ex.Message);
                }
            }

            Console.WriteLine("\n=================================================");
            Console.WriteLine("  XONG! OK=" + totalOk + "  FAIL=" + totalFail);
            Console.WriteLine("=================================================");
            Console.WriteLine("\nBƯỚC TIẾP:");
            Console.WriteLine("  - Mở OB1 → thêm gọi FC_SCADA_Sim_B3to7");
            Console.WriteLine("  - Compile → Download → Runtime");
        }
        catch (Exception ex)
        {
            Console.WriteLine("\n[CRITICAL ERROR] " + ex.Message);
        }
    }

    static PlcSoftware GetPlcSoftware(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null)
        {
            PlcSoftware ps = sc.Software as PlcSoftware;
            if (ps != null) return ps;
        }
        foreach (var child in item.DeviceItems)
        {
            var r = GetPlcSoftware(child);
            if (r != null) return r;
        }
        return null;
    }

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null)
        {
            HmiTarget ht = sc.Software as HmiTarget;
            if (ht != null) targets.Add(ht);
        }
        foreach (var child in item.DeviceItems)
            FindHmiTargets(child, targets);
    }

    static void ScanGroup(DeviceUserGroup g, ref PlcSoftware plcSw, List<HmiTarget> hmiTargets)
    {
        foreach (var dev in g.Devices)
            foreach (var item in dev.DeviceItems)
            {
                if (plcSw == null) plcSw = GetPlcSoftware(item);
                FindHmiTargets(item, hmiTargets);
            }
        foreach (var sub in g.Groups)
            ScanGroup(sub, ref plcSw, hmiTargets);
    }
}
