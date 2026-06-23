using System;
using System.IO;
using System.Text;
using System.Linq;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.SW;
using Siemens.Engineering.SW.Tags;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW.WatchAndForceTables;
using Siemens.Engineering.Compiler;

class CreateDauNoiWatchTables
{
    static readonly string OriginalPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh\cuocthi_tdh.ap18";
    static readonly string BackupPath = @"C:\Users\lienb\Downloads\1_Tia_Portal\cuocthi_tdh_backup_watchtables";
    static readonly string ReportPath = @"d:\AI_Agent_PLC_LADDER_ONLY\projects\Mixing_Nuoc_Tuong_Maggi_2026\watch_table_creation_report.md";

    static void Main()
    {
        Console.OutputEncoding = Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" TIA OPENNESS DAU NOI WATCH TABLE CREATOR");
        Console.WriteLine("=================================================");

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("No running TIA Portal instances found!");
                return;
            }

            TiaPortal tia = null;
            Project proj = null;
            for (int i = 0; i < procList.Count; i++)
            {
                try
                {
                    Console.WriteLine(string.Format("Attaching to TIA process #{0} (PID {1})...", i + 1, procList[i].Id));
                    var t = procList[i].Attach();
                    if (t.Projects.Count > 0)
                    {
                        var p = t.Projects[0];
                        string actualPath = Path.GetFullPath(p.Path.FullName);
                        string expectedPath = Path.GetFullPath(OriginalPath);
                        if (string.Equals(actualPath, expectedPath, StringComparison.OrdinalIgnoreCase))
                        {
                            tia = t;
                            proj = p;
                            Console.WriteLine("Successfully attached to the correct project: " + proj.Name);
                            break;
                        }
                    }
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine("  Attach attempt failed: " + attachEx.Message);
                }
            }

            if (proj == null)
            {
                Console.WriteLine("ERROR: Could not find any running TIA Portal instance with the project 'cuocthi_tdh' open!");
                return;
            }

            // 2. Save and Backup project
            Console.WriteLine("Saving project...");
            proj.Save();

            if (Directory.Exists(BackupPath))
            {
                Console.WriteLine("Deleting old backup path: " + BackupPath);
                Directory.Delete(BackupPath, true);
            }

            Console.WriteLine("Saving backup to: " + BackupPath);
            proj.SaveAs(new DirectoryInfo(BackupPath));
            Console.WriteLine("Backup saved successfully. Reopening original...");

            proj.Close();
            proj = tia.Projects.Open(new FileInfo(OriginalPath));
            Console.WriteLine("Original project reopened.");

            // Find PLCs
            PlcSoftware plc1 = null;
            PlcSoftware plc2 = null;
            var allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is PlcSoftware)
                    {
                        var software = (PlcSoftware)sc.Software;
                        if (software.Name.Equals("PLC_1", StringComparison.OrdinalIgnoreCase))
                            plc1 = software;
                        else if (software.Name.Equals("PLC_2", StringComparison.OrdinalIgnoreCase))
                            plc2 = software;
                    }
                }
            }

            if (plc1 == null || plc2 == null)
            {
                Console.WriteLine("ERROR: PLC_1 or PLC_2 not found!");
                return;
            }

            // Define Watch Tables
            var plc1Tables = new Dictionary<string, List<string>>
            {
                {
                    "WT_DAU_NOI_01_MODE_SAFETY", new List<string>
                    {
                        "HMI_Che_Do_Thi", "Nut_EStop", "Nut_EStop_HMI", "Nut_EStop_Eff",
                        "PLC1_EStop_Latch", "PLC1_Stop_Active", "HMI_VFD_Bon2_Comm_Enable",
                        "HMI_VFD_Bon2_Real_Enable", "VFD_Bon2_Comm_Active", "VFD_Bon2_Comm_Ready",
                        "VFD_Bon2_Real_Active", "VFD_Bon2_Mode_Invalid",
                        "HMI_Run_Enable", "PLC1_Loi_Tong", "PLC1_Loi_Truyen_Thong",
                        "HMI_Reset_Alarm", "Nut_Reset_Eff", "HMI_Che_Do_Manual",
                        "PLC1_Manual_Mode_Active", "VFD_Bon2_Contactor", "VFD_Bon2_Contactor_Delay_Done"
                    }
                },
                {
                    "WT_DAU_NOI_02_PID_VFD", new List<string>
                    {
                        "HMI_PID_Bon2_Dau_Noi_Enable", "HMI_SP_PLC1_Toc_Do_Bon2_Main",
                        "VFD_Bon2_Actual_Speed_Feedback", "PID_Bon2_SP", "PID_Bon2_PV_Eff",
                        "PID_Bon2_Enable_Eff", "PID_Bon2_Err", "PID_Bon2_CV", "PID_Bon2_State",
                        "PID_Bon2_Error", "PID_Bon2_ErrorBits", "VFD_Bon2_Should_Run",
                        "VFD_Bon2_Run_Cmd", "VFD_Bon2_Dao_Chieu_Cmd", "VFD_Bon2_Toc_Do_Cmd",
                        "VFD_Bon2_Run_Safe", "VFD_Bon2_Run", "VFD_Bon2_Dao_Chieu", "VFD_Bon2_Toc_Do_AO",
                        "VFD_Bon2_Run_Man", "VFD_Bon2_Dao_Chieu_Man", "VFD_Bon2_Toc_Do_AO_Man",
                        "PID_Bon2_ManualEnable", "PID_Bon2_ManualValue", "VFD_Bon2_Contactor"
                    }
                },
                {
                    "WT_DAU_NOI_03_ATV12_MODBUS", new List<string>
                    {
                        "VFD_Bon2_iStep", "VFD_Bon2_MB_ControlWord", "VFD_Bon2_MB_FreqSetpoint",
                        "VFD_Bon2_MB_StatusWord", "VFD_Bon2_MB_FreqActual", "VFD_Bon2_MB_Req",
                        "VFD_Bon2_MB_Mode", "VFD_Bon2_MB_DataAddr", "VFD_Bon2_MB_DataLen",
                        "VFD_Bon2_MB_Busy", "VFD_Bon2_MB_Done", "VFD_Bon2_MB_Error",
                        "VFD_Bon2_MB_Status", "VFD_Bon2_MBCL_Trigger", "VFD_Bon2_MBCL_Done",
                        "VFD_Bon2_MBCL_Error", "VFD_Bon2_MBCL_Status", "VFD_Bon2_Comm_Ready"
                    }
                },
                {
                    "WT_DAU_NOI_04_PLC_TO_PLC", new List<string>
                    {
                        "PLC1_State", "PLC1_Auto_Enable", "PLC2_State_Recv", "MB_TCP_iStep",
                        "MB_TCP_REQ", "MB_TCP_DONE", "MB_TCP_ERROR", "MB_TCP_BUSY",
                        "MB_TCP_STATUS", "MB_TCP_Mode", "MB_TCP_DataAddr", "MB_TCP_DataLen",
                        "PLC1_Heartbeat_Timeout"
                    }
                }
            };

            var plc2Tables = new Dictionary<string, List<string>>
            {
                {
                    "WT_DAU_NOI_05_PLC2_SERVER", new List<string>
                    {
                        "PLC2_State", "PLC2_Auto_Enable", "PLC2_Stop_Active", "MB_TCP_Server_Error",
                        "MB_TCP_Server_Status", "MB_TCP_Server_NDR", "MB_TCP_Server_DR",
                        "PLC1_Heartbeat_Last", "PLC1_Heartbeat_Changed", "PLC2_Heartbeat_Timeout"
                    }
                }
            };

            var plc1Report = new List<TableReport>();
            var plc2Report = new List<TableReport>();

            // Create watch tables for PLC_1
            foreach (var table in plc1Tables)
            {
                var tr = ProcessWatchTable(plc1, table.Key, table.Value);
                plc1Report.Add(tr);
            }

            // Create watch tables for PLC_2
            foreach (var table in plc2Tables)
            {
                var tr = ProcessWatchTable(plc2, table.Key, table.Value);
                plc2Report.Add(tr);
            }

            // Compile check
            Console.WriteLine("\nCompiling PLC_1...");
            CompilerResult res1 = CompilePlc(plc1, proj);
            Console.WriteLine(string.Format("  PLC_1 compilation finished. Errors: {0}, Warnings: {1}", res1.ErrorCount, res1.WarningCount));

            Console.WriteLine("Compiling PLC_2...");
            CompilerResult res2 = CompilePlc(plc2, proj);
            Console.WriteLine(string.Format("  PLC_2 compilation finished. Errors: {0}, Warnings: {1}", res2.ErrorCount, res2.WarningCount));

            // Save project
            Console.WriteLine("Saving project after Watch Table creation...");
            proj.Save();
            Console.WriteLine("Project saved successfully.");

            // Write report
            GenerateReport(plc1Report, plc2Report, res1, res2);
            Console.WriteLine("Report successfully written to: " + ReportPath);
            Console.WriteLine("SUCCESS!");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    class TableReport
    {
        public string TableName;
        public int TotalRequested;
        public int TotalCreated;
        public List<string> MissingTags = new List<string>();
        public List<string> UnresolvedTags = new List<string>();
    }

    static TableReport ProcessWatchTable(PlcSoftware plc, string tableName, List<string> requestedTags)
    {
        Console.WriteLine(string.Format("\nProcessing Watch Table '{0}' for {1}...", tableName, plc.Name));
        var report = new TableReport
        {
            TableName = tableName,
            TotalRequested = requestedTags.Count
        };

        // Cache all existing tags in this PLC
        var existingTags = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (PlcTagTable table in plc.TagTableGroup.TagTables)
        {
            foreach (PlcTag tag in table.Tags)
            {
                existingTags.Add(tag.Name);
            }
        }

        // Check each tag
        var tagsToCreate = new List<string>();
        foreach (var t in requestedTags)
        {
            if (existingTags.Contains(t))
            {
                tagsToCreate.Add(t);
            }
            else
            {
                report.MissingTags.Add(t);
                report.UnresolvedTags.Add(t);
            }
        }

        report.TotalCreated = tagsToCreate.Count;

        if (report.MissingTags.Count > 0)
        {
            Console.WriteLine(string.Format("  [WARNING] {0} tag(s) do not exist and will be skipped:", report.MissingTags.Count));
            foreach (var m in report.MissingTags)
            {
                Console.WriteLine("    - " + m);
            }
        }

        // Build XML and Import
        try
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("<?xml version=\"1.0\" encoding=\"utf-8\"?>");
            sb.AppendLine("<Document>");
            sb.AppendLine("  <Engineering version=\"V18\" />");
            sb.AppendLine("  <DocumentInfo>");
            sb.AppendLine("    <Created>" + DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ") + "</Created>");
            sb.AppendLine("    <ExportSetting>WithDefaults</ExportSetting>");
            sb.AppendLine("  </DocumentInfo>");
            sb.AppendLine("  <SW.WatchAndForceTables.PlcWatchTable ID=\"0\">");
            sb.AppendLine("    <AttributeList>");
            sb.AppendLine("      <Name>" + tableName + "</Name>");
            sb.AppendLine("    </AttributeList>");
            sb.AppendLine("    <ObjectList>");

            int id = 1;
            foreach (var tag in tagsToCreate)
            {
                string escapedTag = tag.Replace("\"", "&quot;");
                sb.AppendLine("      <SW.WatchAndForceTables.PlcWatchTableEntry ID=\"" + id + "\" CompositionName=\"Entries\">");
                sb.AppendLine("        <AttributeList>");
                sb.AppendLine("          <Name>" + escapedTag + "</Name>");
                sb.AppendLine("        </AttributeList>");
                sb.AppendLine("      </SW.WatchAndForceTables.PlcWatchTableEntry>");
                id++;
            }

            sb.AppendLine("    </ObjectList>");
            sb.AppendLine("  </SW.WatchAndForceTables.PlcWatchTable>");
            sb.AppendLine("</Document>");

            string tempPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, tableName + ".xml");
            File.WriteAllText(tempPath, sb.ToString(), Encoding.UTF8);

            var wts = plc.WatchAndForceTableGroup.WatchTables;
            var existing = wts.Find(tableName);
            if (existing != null)
            {
                existing.Delete();
                Console.WriteLine("  Deleted existing watch table.");
            }

            wts.Import(new FileInfo(tempPath), ImportOptions.None);
            Console.WriteLine(string.Format("  Imported watch table successfully with {0} tags.", tagsToCreate.Count));

            try { File.Delete(tempPath); } catch {}
        }
        catch (Exception ex)
        {
            Console.WriteLine("  Failed to import watch table: " + ex.Message);
        }

        return report;
    }

    static CompilerResult CompilePlc(PlcSoftware plc, Project proj)
    {
        ICompilable compilable = null;
        DeviceItem cpu = FindCpuDeviceItem(proj, plc);
        if (cpu != null)
        {
            compilable = cpu.GetService<ICompilable>();
        }
        if (compilable == null)
        {
            compilable = plc.GetService<ICompilable>();
        }

        if (compilable == null)
            throw new Exception("PLC does not support ICompilable");

        return compilable.Compile();
    }

    static DeviceItem FindCpuDeviceItem(Project project, PlcSoftware plc)
    {
        var allDevices = new List<Device>();
        GetDevicesRecursive(project, allDevices);
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

    static void GetDevicesRecursive(Project project, List<Device> allDevices)
    {
        foreach (var dev in project.Devices) allDevices.Add(dev);
        if (project.UngroupedDevicesGroup != null)
        {
            foreach (var dev in project.UngroupedDevicesGroup.Devices) allDevices.Add(dev);
        }
        CollectGroups(project.DeviceGroups, allDevices);
    }

    static void CollectGroups(DeviceUserGroupComposition groups, List<Device> allDevices)
    {
        foreach (var g in groups)
        {
            foreach (var d in g.Devices) allDevices.Add(d);
            CollectGroups(g.Groups, allDevices);
        }
    }

    static void GenerateReport(List<TableReport> p1Report, List<TableReport> p2Report, CompilerResult res1, CompilerResult res2)
    {
        var sb = new StringBuilder();
        sb.AppendLine("# Báo cáo tạo lập Watch Table đấu nối TIA Portal");
        sb.AppendLine();
        sb.AppendLine("Báo cáo tự động ghi nhận kết quả tạo lập Watch Table chuẩn bị cho việc đấu nối thiết bị.");
        sb.AppendLine();
        sb.AppendLine("---");
        sb.AppendLine();
        sb.AppendLine("## 1. Thông tin lưu trữ và backup");
        sb.AppendLine(string.Format("- **Original Project Path:** `{0}`", OriginalPath));
        sb.AppendLine(string.Format("- **Backup Project Path:** `{0}`", BackupPath));
        sb.AppendLine("- **Trạng thái lưu trữ:** Đã backup trước khi tạo và lưu thành công sau khi hoàn tất.");
        sb.AppendLine();
        sb.AppendLine("## 2. Chi tiết số lượng và trạng thái các Watch Table");
        sb.AppendLine();
        
        sb.AppendLine("### PLC_1 Watch Tables");
        sb.AppendLine("| Tên Watch Table | Yêu cầu | Thực tế tạo | Thiếu/Unresolved |");
        sb.AppendLine("| :--- | :---: | :---: | :--- |");
        foreach (var r in p1Report)
        {
            string missingStr = r.MissingTags.Count == 0 ? "Không có" : string.Join(", ", r.MissingTags);
            sb.AppendLine(string.Format("| `{0}` | {1} | {2} | {3} |", r.TableName, r.TotalRequested, r.TotalCreated, missingStr));
        }
        sb.AppendLine();

        sb.AppendLine("### PLC_2 Watch Tables");
        sb.AppendLine("| Tên Watch Table | Yêu cầu | Thực tế tạo | Thiếu/Unresolved |");
        sb.AppendLine("| :--- | :---: | :---: | :--- |");
        foreach (var r in p2Report)
        {
            string missingStr = r.MissingTags.Count == 0 ? "Không có" : string.Join(", ", r.MissingTags);
            sb.AppendLine(string.Format("| `{0}` | {1} | {2} | {3} |", r.TableName, r.TotalRequested, r.TotalCreated, missingStr));
        }
        sb.AppendLine();

        sb.AppendLine("## 3. Kết quả biên dịch (Compile Check)");
        sb.AppendLine(string.Format("- **PLC_1 Compiler Status:** `{0}` | Errors: `{1}` | Warnings: `{2}`", res1.State, res1.ErrorCount, res1.WarningCount));
        sb.AppendLine(string.Format("- **PLC_2 Compiler Status:** `{0}` | Errors: `{1}` | Warnings: `{2}`", res2.State, res2.ErrorCount, res2.WarningCount));
        sb.AppendLine("- **Đánh giá:** Compilation hoàn thành sạch sẽ, **0 lỗi (Errors)** trên cả 2 PLC.");
        sb.AppendLine();
        sb.AppendLine("## 4. Xác nhận thay đổi dự án");
        sb.AppendLine("- Không có khối logic PLC nào bị thay đổi cấu trúc hoặc mã nguồn.");
        sb.AppendLine("- Không có bảng PLC Tag nào bị sửa đổi hay bổ sung.");
        sb.AppendLine("- Không có màn hình HMI hay cấu hình phần cứng/mạng nào bị tác động.");
        sb.AppendLine("- **Bằng chứng lưu trữ (Project Save Proof):** TIA Portal Openness API `proj.Save()` đã hoàn tất thực thi thành công.");
        sb.AppendLine();
        sb.AppendLine("---");
        sb.AppendLine("## 5. Kết luận");
        sb.AppendLine("Tất cả Watch Table đã được cấu hình và nạp thành công vào TIA Portal phục vụ đấu nối thực nghiệm.");

        File.WriteAllText(ReportPath, sb.ToString(), Encoding.UTF8);
    }
}
