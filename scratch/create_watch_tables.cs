using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.SW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.SW.WatchAndForceTables;

class CreateWatchTables
{
    static void Main()
    {
        Console.WriteLine("=================================================");
        Console.WriteLine(" TIA OPENNESS WATCH TABLE CREATOR");
        Console.WriteLine("=================================================");

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

            // Tags for PLC_1
            var plc1Tags = new List<string>
            {
                "AI_MB_TCP_iStep",
                "AI_MB_TCP_Write_Req",
                "AI_MB_TCP_Read_Req",
                "AI_MB_TCP_Write_Done",
                "AI_MB_TCP_Write_Busy",
                "AI_MB_TCP_Write_Error",
                "AI_MB_TCP_Write_Status",
                "AI_MB_TCP_Read_Done",
                "AI_MB_TCP_Read_Busy",
                "AI_MB_TCP_Read_Error",
                "AI_MB_TCP_Read_Status",
                "\"DB_PLC1_Send_To_PLC2_DB\".CmdSeq",
                "\"DB_PLC1_Send_To_PLC2_DB\".Cmd_Start",
                "\"DB_PLC1_Send_To_PLC2_DB\".Cmd_Stop",
                "\"DB_PLC1_Send_To_PLC2_DB\".Cmd_Reset",
                "\"DB_PLC1_Send_To_PLC2_DB\".Cmd_EStop",
                "\"DB_PLC1_Send_To_PLC2_DB\".Cmd_Pump_Branch2_To_SubTanks",
                "\"DB_PLC1_Send_To_PLC2_DB\".Cmd_Load_Recipe",
                "\"DB_PLC1_Send_To_PLC2_DB\".Heartbeat",
                "\"DB_PLC1_Recv_From_PLC2_DB\".AckSeq",
                "\"DB_PLC1_Recv_From_PLC2_DB\".State",
                "\"DB_PLC1_Recv_From_PLC2_DB\".PID_Bon4_SP",
                "\"DB_PLC1_Recv_From_PLC2_DB\".PID_Bon4_PV",
                "\"DB_PLC1_Recv_From_PLC2_DB\".PID_Bon4_CV",
                "\"DB_PLC1_Recv_From_PLC2_DB\".Heartbeat",
                "AI_PID_Bon2_Enable",
                "AI_PID_Bon2_SP",
                "AI_TT3208_Bon2_Eff",
                "AI_PID_Bon2_CV",
                "AI_VFD_Bon2_Toc_Do_AO"
            };

            // Tags for PLC_2
            var plc2Tags = new List<string>
            {
                "AI_MB_TCP_Server_NDR",
                "AI_MB_TCP_Server_DR",
                "AI_MB_TCP_Server_Error",
                "AI_MB_TCP_Server_Status",
                "\"DB_Modbus_Holding_Register_DB\".CmdSeq",
                "\"DB_Modbus_Holding_Register_DB\".AckSeq",
                "\"DB_Modbus_Holding_Register_DB\".Cmd_Start",
                "\"DB_Modbus_Holding_Register_DB\".Cmd_Stop",
                "\"DB_Modbus_Holding_Register_DB\".Cmd_Reset",
                "\"DB_Modbus_Holding_Register_DB\".Cmd_EStop",
                "\"DB_Modbus_Holding_Register_DB\".Cmd_Pump_Branch2_To_SubTanks",
                "\"DB_Modbus_Holding_Register_DB\".Cmd_Load_Recipe",
                "\"DB_Modbus_Holding_Register_DB\".Heartbeat_Client",
                "\"DB_Modbus_Holding_Register_DB\".Heartbeat_Server",
                "AI_PLC2_Last_CmdSeq",
                "AI_PLC2_CmdSeq_New",
                "AI_PLC2_State",
                "AI_PID_Bon4_Enable",
                "AI_PID_Bon4_SP",
                "AI_TT3219_Bon4_Sim",
                "AI_TT3219_Bon4_Eff",
                "AI_PID_Bon4_CV",
                "\"DB_Modbus_Holding_Register_DB\".PID_Bon4_SP",
                "\"DB_Modbus_Holding_Register_DB\".PID_Bon4_PV",
                "\"DB_Modbus_Holding_Register_DB\".PID_Bon4_CV"
            };

            // Search PLCs
            PlcSoftware plc1 = null;
            PlcSoftware plc2 = null;

            List<Device> allDevices = new List<Device>();
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
                        {
                            plc1 = software;
                        }
                        else if (software.Name.Equals("PLC_2", StringComparison.OrdinalIgnoreCase))
                        {
                            plc2 = software;
                        }
                    }
                }
            }

            if (plc1 != null)
            {
                CreateAndImportWatchTable(plc1, "WT_PLC1_Modbus_PID_HMI_Test", plc1Tags);
            }
            else
            {
                Console.WriteLine("Error: PLC_1 not found!");
            }

            if (plc2 != null)
            {
                CreateAndImportWatchTable(plc2, "WT_PLC2_Modbus_PID_HMI_Test", plc2Tags);
            }
            else
            {
                Console.WriteLine("Error: PLC_2 not found!");
            }

            Console.WriteLine("\nWatch table creation completed successfully.");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error: " + ex.ToString());
        }
    }

    static void CreateAndImportWatchTable(PlcSoftware plc, string tableName, List<string> tags)
    {
        Console.WriteLine("\nCreating Watch Table '" + tableName + "' for PLC: " + plc.Name);
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
            foreach (var tag in tags)
            {
                // Escape HTML entities in tag names if needed (e.g. quotes)
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
                Console.WriteLine("  Deleted existing table.");
            }

            wts.Import(new FileInfo(tempPath), ImportOptions.None);
            Console.WriteLine("  Imported watch table successfully with " + tags.Count + " entries.");
            
            // Clean up temporary file
            try
            {
                File.Delete(tempPath);
            }
            catch {}
        }
        catch (Exception ex)
        {
            Console.WriteLine("  Failed to create watch table: " + ex.Message);
        }
    }

    static void GetDevicesRecursive(Project project, List<Device> allDevices)
    {
        AddDevices(project.Devices, allDevices);
        if (project.UngroupedDevicesGroup != null)
        {
            AddDevices(project.UngroupedDevicesGroup.Devices, allDevices);
        }
        AddUserGroupsRecursive(project.DeviceGroups, allDevices);
    }

    static void AddDevices(DeviceComposition devices, List<Device> allDevices)
    {
        foreach (var dev in devices)
        {
            allDevices.Add(dev);
        }
    }

    static void AddUserGroupsRecursive(DeviceUserGroupComposition groups, List<Device> allDevices)
    {
        foreach (var group in groups)
        {
            AddDevices(group.Devices, allDevices);
            AddUserGroupsRecursive(group.Groups, allDevices);
        }
    }
}
