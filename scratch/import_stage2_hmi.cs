using System;
using System.IO;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.HW;
using Siemens.Engineering.HW.Features;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;
using Siemens.Engineering.Hmi.Tag;
using Siemens.Engineering.Compiler;

class ImportStage2Hmi
{
    static void Main()
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("========================================");
        Console.WriteLine(" STAGE 2 HMI IMPORT AND BINDING TOOL");
        Console.WriteLine("========================================");

        string tagsXml = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen1_HMI_Tags.xml";
        string screenXml = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\Screen_1_patched.xml";
        string probeXml = @"D:\AI_Agent_PLC_LADDER_ONLY\scratch\probe_conn2_temp.xml";

        try
        {
            Project proj = null;
            TiaPortal tia = null;
            var processes = TiaPortal.GetProcesses();
            Console.WriteLine("Running TIA Portal processes found: " + processes.Count);

            for (int i = 0; i < processes.Count; i++)
            {
                try
                {
                    Console.WriteLine("Attaching to process PID: " + processes[i].Id);
                    var candidateTia = processes[i].Attach();
                    if (candidateTia.Projects.Count > 0)
                    {
                        proj = candidateTia.Projects[0];
                        tia = candidateTia;
                        break;
                    }
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine("  Failed to attach to process " + processes[i].Id + ": " + attachEx.Message);
                }
            }

            if (proj == null)
            {
                Console.WriteLine("Error: No open projects found in any running TIA Portal process.");
                return;
            }
            Console.WriteLine("Attached to Project: " + proj.Name + " (" + proj.Path.FullName + ")");

            // Find HMI Target
            HmiTarget hmi = null;
            foreach (Device dev in proj.Devices)
            {
                foreach (DeviceItem item in dev.DeviceItems)
                {
                    var sc = item.GetService<SoftwareContainer>();
                    if (sc != null && sc.Software is HmiTarget)
                    {
                        hmi = sc.Software as HmiTarget;
                        break;
                    }
                }
                if (hmi != null) break;
            }

            if (hmi == null)
            {
                Console.WriteLine("Error: No HMI target found in project.");
                return;
            }
            Console.WriteLine("Target HMI: " + hmi.Name);

            // STEP 1: Verify Connection_2 exists using the probe method
            Console.WriteLine("Verifying if HMI_Connection_2 exists in the project...");
            using (StreamWriter sw = new StreamWriter(probeXml, false, System.Text.Encoding.UTF8))
            {
                sw.WriteLine("<?xml version=\"1.0\" encoding=\"utf-8\"?>");
                sw.WriteLine("<Document>");
                sw.WriteLine("  <Engineering version=\"V18\" />");
                sw.WriteLine("  <Hmi.Tag.TagTable ID=\"0\">");
                sw.WriteLine("    <AttributeList><Name>Test_Table_Conn2</Name></AttributeList>");
                sw.WriteLine("    <ObjectList>");
                sw.WriteLine("      <Hmi.Tag.Tag ID=\"1\" CompositionName=\"Tags\">");
                sw.WriteLine("        <AttributeList>");
                sw.WriteLine("          <Name>Test_Tag_Conn2_Probe</Name>");
                sw.WriteLine("          <Coding>IEEE754Float</Coding>");
                sw.WriteLine("          <Length>4</Length>");
                sw.WriteLine("        </AttributeList>");
                sw.WriteLine("        <LinkList>");
                sw.WriteLine("          <AcquisitionCycle TargetID=\"@OpenLink\"><Name>1 s</Name></AcquisitionCycle>");
                sw.WriteLine("          <Connection TargetID=\"@OpenLink\"><Name>HMI_Connection_2</Name></Connection>");
                sw.WriteLine("          <DataType TargetID=\"@OpenLink\"><Name>Real</Name></DataType>");
                sw.WriteLine("          <HmiDataType TargetID=\"@OpenLink\"><Name>Real</Name></HmiDataType>");
                sw.WriteLine("        </LinkList>");
                sw.WriteLine("      </Hmi.Tag.Tag>");
                sw.WriteLine("    </ObjectList>");
                sw.WriteLine("  </Hmi.Tag.TagTable>");
                sw.WriteLine("</Document>");
            }

            bool conn2Exists = false;
            try
            {
                var table = hmi.TagFolder.TagTables.Find("Test_Table_Conn2");
                if (table != null) table.Delete();

                hmi.TagFolder.TagTables.Import(new FileInfo(probeXml), ImportOptions.Override);
                
                // If it succeeds, it exists! Clean up and proceed
                table = hmi.TagFolder.TagTables.Find("Test_Table_Conn2");
                if (table != null) table.Delete();
                conn2Exists = true;
                Console.WriteLine("  ==> SUCCESS: HMI_Connection_2 exists and is ready.");
            }
            catch (Exception ex)
            {
                string msg = ex.Message;
                if (ex.InnerException != null) msg += " -> " + ex.InnerException.Message;
                Console.WriteLine("  ==> PROBE FAILED: " + msg);
            }
            finally
            {
                if (File.Exists(probeXml)) File.Delete(probeXml);
            }

            if (!conn2Exists)
            {
                Console.WriteLine("\n[CRITICAL ERROR] HMI_Connection_2 is MISSING in TIA Portal.");
                Console.WriteLine("Please manually create 'HMI_Connection_2' under HMI_RT_1 > Connections first.");
                Console.WriteLine("Stopping execution before any screen import/binding is performed.");
                Environment.Exit(1);
            }

            // STEP 2: Import HMI Tag Table
            Console.WriteLine("\nImporting HMI Tag Table...");
            if (!File.Exists(tagsXml))
            {
                Console.WriteLine("Error: Tag XML not found at " + tagsXml);
                return;
            }
            var existingTable = hmi.TagFolder.TagTables.Find("Screen1_HMI_Tags");
            if (existingTable != null)
            {
                Console.WriteLine("  Deleting existing Screen1_HMI_Tags table...");
                existingTable.Delete();
            }
            hmi.TagFolder.TagTables.Import(new FileInfo(tagsXml), ImportOptions.Override);
            Console.WriteLine("  ==> Tag Table imported successfully.");

            // STEP 3: Import Patched Screen_1
            Console.WriteLine("\nImporting Patched Screen_1...");
            if (!File.Exists(screenXml))
            {
                Console.WriteLine("Error: Screen XML not found at " + screenXml);
                return;
            }
            
            Screen existingScreen = null;
            foreach (Screen s in hmi.ScreenFolder.Screens)
            {
                if (s.Name.Equals("Screen_1", StringComparison.OrdinalIgnoreCase))
                {
                    existingScreen = s;
                    break;
                }
            }

            if (existingScreen != null)
            {
                Console.WriteLine("  Deleting old Screen_1...");
                existingScreen.Delete();
            }

            hmi.ScreenFolder.Screens.Import(new FileInfo(screenXml), ImportOptions.Override);
            Console.WriteLine("  ==> Screen_1 imported successfully.");

            // STEP 4: Save Project
            Console.WriteLine("\nSaving project...");
            proj.Save();
            Console.WriteLine("  ==> Project saved successfully.");

            // STEP 5: Compile HMI Target
            Console.WriteLine("\nCompiling HMI Target software...");
            ICompilable compilable = hmi.GetService<ICompilable>();
            if (compilable != null)
            {
                CompilerResult result = compilable.Compile();
                Console.WriteLine("  Compile State: " + result.State);
                Console.WriteLine("  Errors: " + result.ErrorCount + ", Warnings: " + result.WarningCount);
                PrintMessages(result.Messages, "    ");
                
                if (result.ErrorCount > 0)
                {
                    Console.WriteLine("\n[ERROR] HMI Compile failed with " + result.ErrorCount + " errors.");
                    Environment.Exit(1);
                }
            }
            else
            {
                Console.WriteLine("  Warning: HmiTarget does not support ICompilable.");
            }

            Console.WriteLine("\n========================================");
            Console.WriteLine(" STAGE 2 IMPORT COMPLETED SUCCESSFULLY!");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine("System Error: " + ex.ToString());
            Environment.Exit(1);
        }
    }

    static void PrintMessages(System.Collections.IEnumerable messages, string indent)
    {
        if (messages == null) return;
        foreach (dynamic msg in messages)
        {
            try
            {
                string state = msg.State.ToString();
                string desc = msg.Description != null ? msg.Description.ToString() : "";
                Console.WriteLine(string.Format("{0}{1}: {2}", indent, state, desc));
                if (msg.Messages != null)
                {
                    PrintMessages(msg.Messages, indent + "  ");
                }
            }
            catch {}
        }
    }
}
