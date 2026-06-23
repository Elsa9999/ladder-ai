using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Compiler;

class CompileProjectPid
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" COMPILE PLC & HMI WITH PID");
        Console.WriteLine("=================================================");

        int targetPid = -1;
        if (args.Length > 0)
        {
            int.TryParse(args[0], out targetPid);
        }

        try
        {
            var processes = TiaPortal.GetProcesses();
            if (processes.Count == 0)
            {
                Console.WriteLine("Error: Không tìm thấy TIA Portal nào.");
                return;
            }

            TiaPortalProcess selectedProcess = null;
            if (targetPid != -1)
            {
                foreach (var proc in processes)
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
                // Find the main process among processes
                foreach (var proc in processes)
                {
                    // main process has Id in the Window title or we just attach
                    try
                    {
                        var t = proc.Attach();
                        if (t.Projects.Count > 0)
                        {
                            selectedProcess = proc;
                            break;
                        }
                    }
                    catch {}
                }
            }

            if (selectedProcess == null)
            {
                Console.WriteLine("Lỗi: Không tìm thấy hoặc không thể kết nối tới TIA Portal.");
                return;
            }

            Console.WriteLine("Đang kết nối tới PID: " + selectedProcess.Id + "...");
            TiaPortal tia = selectedProcess.Attach();
            Project proj = tia.Projects[0];
            Console.WriteLine("Dự án đang mở: " + proj.Name + " (" + proj.Path.FullName + ")");

            // 1. Compile PLC
            Console.WriteLine("\n--- 1. BIÊN DỊCH PLC (PLC_1) ---");
            DeviceItem plcCpuItem = null;
            PlcSoftware plcSoftware = FindPlcSoftware(proj, "PLC_1", out plcCpuItem);
            if (plcSoftware != null)
            {
                ICompilable compilable = null;
                if (plcCpuItem != null) compilable = plcCpuItem.GetService<ICompilable>();
                if (compilable == null) compilable = plcSoftware.GetService<ICompilable>();

                if (compilable != null)
                {
                    Console.WriteLine("Đang biên dịch PLC_1...");
                    CompilerResult res = compilable.Compile();
                    Console.WriteLine("Kết quả biên dịch: " + res.State);
                    Console.WriteLine(string.Format("Lỗi: {0}, Cảnh báo: {1}", res.ErrorCount, res.WarningCount));
                    if (res.Messages != null) PrintMessages(res.Messages, "  ");
                }
                else
                {
                    Console.WriteLine("Không lấy được dịch vụ ICompilable cho PLC_1.");
                }
            }
            else
            {
                Console.WriteLine("Không tìm thấy PLC_1.");
            }

            // 2. Compile HMI
            Console.WriteLine("\n--- 2. BIÊN DỊCH HMI (HMI_RT_1) ---");
            HmiTarget hmiTarget = FindHmiTarget(proj, "HMI_RT_1");
            if (hmiTarget != null)
            {
                ICompilable compilable = hmiTarget.GetService<ICompilable>();
                if (compilable != null)
                {
                    Console.WriteLine("Đang biên dịch HMI_RT_1...");
                    CompilerResult res = compilable.Compile();
                    Console.WriteLine("Kết quả biên dịch: " + res.State);
                    Console.WriteLine(string.Format("Lỗi: {0}, Cảnh báo: {1}", res.ErrorCount, res.WarningCount));
                    if (res.Messages != null) PrintMessages(res.Messages, "  ");
                }
                else
                {
                    Console.WriteLine("Không lấy được dịch vụ ICompilable cho HMI_RT_1.");
                }
            }
            else
            {
                Console.WriteLine("Không tìm thấy HMI_RT_1.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi biên dịch hệ thống: " + ex.ToString());
        }
    }

    static PlcSoftware FindPlcSoftware(Project project, string plcName, out DeviceItem cpuItem)
    {
        cpuItem = null;
        foreach (Device device in project.Devices)
        {
            foreach (DeviceItem item in device.DeviceItems)
            {
                PlcSoftware plc = FindPlcSoftwareRecursive(item, plcName, out cpuItem);
                if (plc != null) return plc;
            }
        }
        return null;
    }

    static PlcSoftware FindPlcSoftwareRecursive(DeviceItem item, string plcName, out DeviceItem cpuItem)
    {
        cpuItem = null;
        SoftwareContainer container = item.GetService<SoftwareContainer>();
        if (container != null && container.Software is PlcSoftware)
        {
            PlcSoftware plc = (PlcSoftware)container.Software;
            if (plc.Name.IndexOf(plcName, StringComparison.OrdinalIgnoreCase) >= 0)
            {
                cpuItem = item;
                return plc;
            }
        }
        foreach (DeviceItem child in item.DeviceItems)
        {
            PlcSoftware plc = FindPlcSoftwareRecursive(child, plcName, out cpuItem);
            if (plc != null) return plc;
        }
        return null;
    }

    static HmiTarget FindHmiTarget(Project project, string hmiName)
    {
        foreach (Device device in project.Devices)
        {
            foreach (DeviceItem item in device.DeviceItems)
            {
                HmiTarget hmi = FindHmiTargetRecursive(item, hmiName);
                if (hmi != null) return hmi;
            }
        }
        return null;
    }

    static HmiTarget FindHmiTargetRecursive(DeviceItem item, string hmiName)
    {
        SoftwareContainer container = item.GetService<SoftwareContainer>();
        if (container != null && container.Software is HmiTarget)
        {
            HmiTarget hmi = (HmiTarget)container.Software;
            if (hmi.Name.IndexOf(hmiName, StringComparison.OrdinalIgnoreCase) >= 0)
            {
                return hmi;
            }
        }
        foreach (DeviceItem child in item.DeviceItems)
        {
            HmiTarget hmi = FindHmiTargetRecursive(child, hmiName);
            if (hmi != null) return hmi;
        }
        return null;
    }

    static void PrintMessages(System.Collections.IEnumerable messages, string indent)
    {
        foreach (dynamic msg in messages)
        {
            try
            {
                string state = msg.State.ToString();
                string desc = msg.Description != null ? msg.Description.ToString() : "";
                string errorCode = "";
                try { errorCode = msg.ErrorCode.ToString(); } catch {}
                
                // Show errors and warnings
                if (state.Equals("Error", StringComparison.OrdinalIgnoreCase) || 
                    state.Equals("Warning", StringComparison.OrdinalIgnoreCase))
                {
                    Console.WriteLine(string.Format("{0}{1}: {2} (Code: {3})", 
                        indent, state, desc, errorCode));
                }
                
                if (msg.Messages != null)
                {
                    PrintMessages(msg.Messages, indent + "  ");
                }
            }
            catch {}
        }
    }
}
