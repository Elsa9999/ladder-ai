using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;
using Siemens.Engineering.Hmi.Tag;

class ImportTagsAndScreen
{
    static void Main(string[] args)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(" CIP-MIXING: IMPORT TAGS + SCREEN WITH PID");
        Console.WriteLine("========================================");

        int targetPid = -1;
        if (args.Length > 0)
        {
            int.TryParse(args[0], out targetPid);
        }

        string tagsFile   = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\AI_HMI_Tags_CIP_Mixing.xml";
        string screensDir = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_export\Screens";

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("LOI: Khong tim thay TIA Portal dang chay!");
                return;
            }

            TiaPortalProcess selectedProcess = null;
            if (targetPid != -1)
            {
                foreach (var proc in procList)
                {
                    if (proc.Id == targetPid)
                    {
                        selectedProcess = proc;
                        break;
                    }
                }
            }
            else
            {
                selectedProcess = procList[0];
            }

            if (selectedProcess == null)
            {
                Console.WriteLine("LOI: Khong tim thay TIA Portal voi PID = " + targetPid);
                return;
            }

            Console.WriteLine("Dang ket noi TIA Portal (PID: " + selectedProcess.Id + ")...");
            var tia  = selectedProcess.Attach();
            var proj = tia.Projects[0];
            Console.WriteLine("Du an: " + proj.Name);

            // ── Tim HMI Target ──────────────────────────────
            HmiTarget hmiTarget = null;
            foreach (var dev in proj.Devices)
                foreach (var item in dev.DeviceItems)
                {
                    hmiTarget = FindHmi(item);
                    if (hmiTarget != null) break;
                }

            if (hmiTarget == null) { Console.WriteLine("LOI: Khong tim thay HMI Target!"); return; }
            Console.WriteLine("HMI Target: " + hmiTarget.Name);

            // ── BUOC 1: Import HMI Tags ──────────────────────
            Console.WriteLine("\n[B1] Import HMI Tags...");
            if (File.Exists(tagsFile))
            {
                try
                {
                    // Xoa tag table cu neu co
                    foreach (TagTable tt in hmiTarget.TagFolder.TagTables)
                    {
                        if (tt.Name.Equals("HMI_Tags", StringComparison.OrdinalIgnoreCase))
                        {
                            Console.WriteLine("  Xoa tag table cu 'HMI_Tags'...");
                            tt.Delete();
                            break;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  [WARN xoa cu]: " + ex.Message);
                }

                try
                {
                    hmiTarget.TagFolder.TagTables.Import(new FileInfo(tagsFile), ImportOptions.Override);
                    Console.WriteLine("  [Tags THANH CONG!]");
                }
                catch (Exception ex)
                {
                    Console.WriteLine("  [Tags THAT BAI]: " + ex.Message);
                }
            }
            else
            {
                Console.WriteLine("  [WARN] Khong tim thay file tags: " + tagsFile);
            }

            // ── BUOC 2: Import Screen_2 ──────────────────────
            Console.WriteLine("\n[B2] Import Screen_2...");
            var rootFolder = hmiTarget.ScreenFolder;
            if (rootFolder != null && Directory.Exists(screensDir))
            {
                foreach (var file in Directory.GetFiles(screensDir, "*.xml"))
                {
                    string screenName = Path.GetFileNameWithoutExtension(file);
                    if (screenName.StartsWith("Hmi.Screen."))
                        screenName = screenName.Substring("Hmi.Screen.".Length);

                    Console.WriteLine("  Xu ly: " + screenName);

                    // Xoa man hinh cu
                    foreach (Screen s in rootFolder.Screens)
                    {
                        if (s.Name.Equals(screenName, StringComparison.OrdinalIgnoreCase))
                        {
                            try { s.Delete(); Console.WriteLine("    [Xoa OK]"); }
                            catch (Exception ex) { Console.WriteLine("    [Xoa WARN]: " + ex.Message); }
                            break;
                        }
                    }

                    // Nap man hinh moi
                    try
                    {
                        rootFolder.Screens.Import(new FileInfo(file), ImportOptions.Override);
                        Console.WriteLine("    [Import THANH CONG!]");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine("    [Import THAT BAI]: " + ex.Message);
                    }
                }
            }

            // ── BUOC 3: Luu project ──────────────────────────
            Console.WriteLine("\n[B3] Luu project...");
            proj.Save();
            Console.WriteLine("  [Luu THANH CONG!]");

            Console.WriteLine("\n========================================");
            Console.WriteLine(" HOAN THANH! Tags + Screen da duoc nap.");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine("LOI HE THONG: " + ex.ToString());
        }
    }

    static HmiTarget FindHmi(DeviceItem item)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget) return sc.Software as HmiTarget;
        foreach (var child in item.DeviceItems)
        {
            var r = FindHmi(child);
            if (r != null) return r;
        }
        return null;
    }
}
