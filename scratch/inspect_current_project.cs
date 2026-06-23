using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;
using Siemens.Engineering.Hmi.Tag;
using Siemens.Engineering.SW;

class InspectCurrentProject
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" INSPECT ACTIVE TIA PORTAL PROJECT");
        Console.WriteLine("========================================");

        try
        {
            var processes = TiaPortal.GetProcesses();
            if (processes.Count == 0)
            {
                Console.WriteLine("Lỗi: Không tìm thấy TIA Portal nào.");
                return;
            }

            TiaPortalProcess selectedProcess = null;
            foreach (var proc in processes)
            {
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

            if (selectedProcess == null)
            {
                Console.WriteLine("Lỗi: Không kết nối được TIA Portal có dự án.");
                return;
            }

            TiaPortal tia = selectedProcess.Attach();
            Project proj = tia.Projects[0];
            Console.WriteLine("Dự án: " + proj.Name + " (" + proj.Path.FullName + ")");

            // Find and inspect PLC Software
            Console.WriteLine("\n--- THIẾT BỊ TRONG DỰ ÁN ---");
            foreach (Device dev in proj.Devices)
            {
                Console.WriteLine("Device: " + dev.Name + " (Type: " + dev.TypeIdentifier + ")");
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    InspectDeviceItem(item, "  ");
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Lỗi hệ thống: " + ex.ToString());
        }
    }

    static void InspectDeviceItem(DeviceItem item, string indent)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null)
        {
            Console.WriteLine(indent + "SoftwareContainer: " + item.Name + " | Software Type: " + sc.Software.GetType().Name);
            if (sc.Software is HmiTarget)
            {
                var hmi = sc.Software as HmiTarget;
                Console.WriteLine(indent + "  HMI Target Name: " + hmi.Name);
                Console.WriteLine(indent + "  MÀN HÌNH:");
                foreach (Screen s in hmi.ScreenFolder.Screens)
                {
                    Console.WriteLine(indent + "    - Screen: " + s.Name);
                }
                Console.WriteLine(indent + "  BẢNG HMI TAGS:");
                foreach (TagTable tt in hmi.TagFolder.TagTables)
                {
                    Console.WriteLine(indent + "    - Table: " + tt.Name + " (Tags count: " + tt.Tags.Count + ")");
                }
            }
            else if (sc.Software is PlcSoftware)
            {
                var plc = sc.Software as PlcSoftware;
                Console.WriteLine(indent + "  PLC Name: " + plc.Name);
                Console.WriteLine(indent + "  PLC BLOCKS:");
                foreach (var block in plc.BlockGroup.Blocks)
                {
                    Console.WriteLine(indent + "    - Block: " + block.Name + " (Type: " + block.GetType().Name + ")");
                }
                Console.WriteLine(indent + "  BẢNG PLC TAGS:");
                foreach (var table in plc.TagTableGroup.TagTables)
                {
                    Console.WriteLine(indent + "    - Table: " + table.Name + " (Tags count: " + table.Tags.Count + ")");
                }
            }
        }
        foreach (DeviceItem child in item.DeviceItems)
        {
            InspectDeviceItem(child, indent + "  ");
        }
    }
}
