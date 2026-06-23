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
using Siemens.Engineering.SW.Types;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.TextGraphicList;
using Siemens.Engineering.Compiler;
using System.Xml;

class AgentTIAImporterGeneric
{
    static void Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        Console.WriteLine("=================================================");
        Console.WriteLine(" UPGRADED TIA PORTAL OPENNESS IMPORTER");
        Console.WriteLine("=================================================");

        string inFolder = AppDomain.CurrentDomain.BaseDirectory;
        string targetPlcName = "";
        bool runCompile = false;

        foreach (string arg in args)
        {
            if (arg.Equals("compile", StringComparison.OrdinalIgnoreCase))
            {
                runCompile = true;
            }
            else if (Directory.Exists(arg))
            {
                inFolder = Path.GetFullPath(arg);
            }
            else
            {
                targetPlcName = arg;
            }
        }

        Console.WriteLine(string.Format("Target Folder: {0}", inFolder));
        if (!string.IsNullOrEmpty(targetPlcName))
        {
            Console.WriteLine(string.Format("Explicit PLC Selection: {0}", targetPlcName));
        }

        // 1. NGĂN CHẶN SỬ DỤNG SCL LOGIC (LADDER-ONLY POLICY)
        string[] sclFiles = Directory.GetFiles(inFolder, "*.scl", SearchOption.AllDirectories);
        if (sclFiles.Length > 0)
        {
            Console.WriteLine("\n--- THẤT BẠI: PHÁT HIỆN LOGIC SCL ---");
            Console.WriteLine("Lỗi nghiêm trọng: Quy tắc của dự án chỉ cho phép sử dụng 100% Ladder XML.");
            Console.WriteLine("Phát hiện các file logic SCL sau:");
            foreach (string sclFile in sclFiles)
            {
                Console.WriteLine(string.Format("  - {0}", Path.GetFileName(sclFile)));
            }
            Console.WriteLine("Importer dừng hoạt động ngay lập tức để bảo vệ tính toàn vẹn của dự án TIA!");
            return;
        }

        try
        {
            var procList = TiaPortal.GetProcesses();
            if (procList.Count == 0)
            {
                Console.WriteLine("Error: No running TIA Portal instances found!");
                return;
            }

            Console.WriteLine(string.Format("Running TIA Portal processes found: {0}", procList.Count));
            TiaPortal tia = null;
            Project proj = null;

            // Search for the process containing the target PLC name or project
            for (int i = 0; i < procList.Count; i++)
            {
                try
                {
                    var candidateTia = procList[i].Attach();
                    foreach (Project p in candidateTia.Projects)
                    {
                        Console.WriteLine(string.Format("  Process #{0} has open project: {1}", i + 1, p.Name));
                        if (proj == null)
                        {
                            tia = candidateTia;
                            proj = p;
                        }

                        if (!string.IsNullOrEmpty(targetPlcName))
                        {
                            List<Device> devs = new List<Device>();
                            GetDevicesRecursive(p, devs);
                            foreach (var d in devs)
                            {
                                if (d.Name.IndexOf(targetPlcName, StringComparison.OrdinalIgnoreCase) >= 0)
                                {
                                    tia = candidateTia;
                                    proj = p;
                                    Console.WriteLine(string.Format("    Matched TIA process #{0} containing PLC: {1}", i + 1, d.Name));
                                    break;
                                }
                            }
                        }
                    }
                }
                catch (Exception attachEx)
                {
                    Console.WriteLine(string.Format("  Attach failed for TIA process #{0}: {1}", i + 1, attachEx.Message));
                }
            }

            if (proj == null)
            {
                Console.WriteLine("Error: No open projects found in any running TIA Portal instance!");
                return;
            }
            Console.WriteLine(string.Format("Attached to Project: {0}", proj.Name));

            PlcSoftware plcSoftware = null;
            string plcSearchName = targetPlcName;
            if (string.IsNullOrEmpty(plcSearchName))
            {
                if (inFolder.Contains("01_PLC_1") || inFolder.Contains("PLC_1"))
                {
                    plcSearchName = "PLC_1";
                }
                else if (inFolder.Contains("02_PLC_2") || inFolder.Contains("PLC_2"))
                {
                    plcSearchName = "PLC_2";
                }
            }

            List<Device> allDevices = new List<Device>();
            GetDevicesRecursive(proj, allDevices);

            foreach (var dev in allDevices)
            {
                foreach (var item in dev.DeviceItems)
                {
                    var software = GetPlcSoftware(item);
                    if (software != null)
                    {
                        if (string.IsNullOrEmpty(plcSearchName))
                        {
                            plcSoftware = software;
                            break;
                        }
                        else if (software.Name.IndexOf(plcSearchName, StringComparison.OrdinalIgnoreCase) >= 0 ||
                                 dev.Name.IndexOf(plcSearchName, StringComparison.OrdinalIgnoreCase) >= 0 ||
                                 (plcSearchName == "PLC_1" && dev.Name.EndsWith("_1")) ||
                                 (plcSearchName == "PLC_2" && dev.Name.EndsWith("_2")))
                        {
                            plcSoftware = software;
                            break;
                        }
                    }
                }
                if (plcSoftware != null) break;
            }

            if (plcSoftware == null)
            {
                Console.WriteLine("Error: No PLC Software container found in the project.");
                return;
            }
            Console.WriteLine(string.Format("PLC Software Container: {0}", plcSoftware.Name));

            // Create PID Technological Object if needed
            try
            {
                var techGroup = plcSoftware.TechnologicalObjectGroup;
                if (techGroup != null)
                {
                    string targetToName = plcSoftware.Name.Contains("PLC_1") ? "PID_Compact_1" : (plcSoftware.Name.Contains("PLC_2") ? "PID_Compact_2" : null);
                    string oldToName = plcSoftware.Name.Contains("PLC_1") ? "AI_PID_Compact_1" : (plcSoftware.Name.Contains("PLC_2") ? "AI_PID_Compact_2" : null);
                    
                    if (oldToName != null)
                    {
                        foreach (var obj in techGroup.TechnologicalObjects.ToList())
                        {
                            if (obj.Name == oldToName)
                            {
                                Console.WriteLine(string.Format("Renaming legacy Technological Object: {0} to {1} ...", oldToName, targetToName));
                                try 
                                {
                                    obj.Name = targetToName;
                                    Console.WriteLine("  SUCCESS!");
                                } 
                                catch (Exception ex) 
                                {
                                    Console.WriteLine("  FAILED! " + ex.Message); 
                                }
                            }
                        }
                    }

                    if (targetToName != null)
                    {
                        bool exists = false;
                        foreach (var obj in techGroup.TechnologicalObjects)
                        {
                            if (obj.Name == targetToName)
                            {
                                exists = true;
                                break;
                            }
                        }

                        if (!exists)
                        {
                            Console.WriteLine(string.Format("Creating Technological Object: {0} ...", targetToName));
                            string[] versions = { "1.2", "2.3", "2.2", "2.1", "2.0", "1.1", "1.0" };
                            bool created = false;
                            foreach (var verStr in versions)
                            {
                                try
                                {
                                    techGroup.TechnologicalObjects.Create(targetToName, "PID_Compact", new Version(verStr));
                                    Console.WriteLine(string.Format("  SUCCESS! Created version {0}", verStr));
                                    created = true;
                                    break;
                                }
                                catch (Exception ex)
                                {
                                    Console.WriteLine(string.Format("    Error creating version {0}: {1}", verStr, ex.Message));
                                }
                            }
                            if (!created)
                            {
                                Console.WriteLine("  FAILED to create PID_Compact technology object.");
                            }
                        }
                        else
                        {
                            Console.WriteLine(string.Format("Technology Object '{0}' already exists.", targetToName));
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Warning: Failed to process Technology Objects: " + ex.Message);
            }

            // Classify files for stable import order
            string[] xmlFiles = Directory.GetFiles(inFolder, "*.xml", SearchOption.AllDirectories);
            var typeFiles = new List<string>();
            var tagFiles = new List<string>();
            var blockFiles = new List<string>();
            var hmiTextListFiles = new List<string>();
            var hmiGraphicListFiles = new List<string>();

            foreach (var file in xmlFiles)
            {
                string content = File.ReadAllText(file);
                if (content.Contains("<Hmi.TextGraphicList.TextList"))
                {
                    hmiTextListFiles.Add(file);
                }
                else if (content.Contains("<Hmi.TextGraphicList.GraphicList"))
                {
                    hmiGraphicListFiles.Add(file);
                }
                else if (content.Contains("<SW.Types.PlcStruct") || content.Contains("<SW.Types.PlcUserType"))
                {
                    typeFiles.Add(file);
                }
                else if (file.IndexOf("Tag", StringComparison.OrdinalIgnoreCase) >= 0 || content.Contains("SW.Tags.PlcTagTable"))
                {
                    tagFiles.Add(file);
                }
                else
                {
                    blockFiles.Add(file);
                }
            }

            // 1. IMPORT UDTs (Types)
            if (typeFiles.Count > 0)
            {
                Console.WriteLine("\n--- 1. IMPORTING UDTs (PLC DATA TYPES) ---");
                foreach (string typeFile in typeFiles)
                {
                    string typeName = Path.GetFileNameWithoutExtension(typeFile);
                    Console.WriteLine(string.Format("Importing UDT: {0} ...", typeName));
                    try
                    {
                        plcSoftware.TypeGroup.Types.Import(new FileInfo(typeFile), ImportOptions.Override);
                        Console.WriteLine("  SUCCESS!");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("  FAILED! {0}", ex.Message));
                    }
                }
            }

            // Pre-clean legacy tag tables starting with "AI_" or matching "PLC_Tags"
            try
            {
                Console.WriteLine("Pre-clean tag tables block started.");
                Console.WriteLine("Number of tag tables: " + plcSoftware.TagTableGroup.TagTables.Count);
                foreach (var tbl in plcSoftware.TagTableGroup.TagTables.ToList())
                {
                    Console.WriteLine(string.Format("Checking tag table: {0}", tbl.Name));
                    if (tbl.Name.StartsWith("AI_", StringComparison.OrdinalIgnoreCase) || 
                        tbl.Name.StartsWith("PLC_Tags", StringComparison.OrdinalIgnoreCase))
                    {
                        Console.WriteLine(string.Format("Deleting old tag table: {0} ...", tbl.Name));
                        tbl.Delete();
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Warning: Failed to clean old tag tables: " + ex.Message);
            }

            // Pre-clean legacy tags starting with "AI_" in all remaining tag tables (e.g. Default tag table)
            try
            {
                Console.WriteLine("Pre-clean individual tags block started.");
                foreach (var tbl in plcSoftware.TagTableGroup.TagTables)
                {
                    Console.WriteLine(string.Format("Checking tags in table: {0} (total tags: {1})", tbl.Name, tbl.Tags.Count));
                    var tagsToDelete = new List<PlcTag>();
                    foreach (var tag in tbl.Tags)
                    {
                        if (tag.Name.StartsWith("AI_", StringComparison.OrdinalIgnoreCase))
                        {
                            tagsToDelete.Add(tag);
                        }
                    }
                    if (tagsToDelete.Count > 0)
                    {
                        Console.WriteLine(string.Format("Deleting {0} old tags starting with 'AI_' in table: {1} ...", tagsToDelete.Count, tbl.Name));
                        foreach (var tag in tagsToDelete)
                        {
                            try { tag.Delete(); } catch {}
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Warning: Failed to clean old tags: " + ex.Message);
            }

            // 2. IMPORT TAG TABLES
            if (tagFiles.Count > 0)
            {
                Console.WriteLine("\n--- 2. IMPORTING PLC TAG TABLES ---");
                foreach (string tagFile in tagFiles)
                {
                    string tableName = Path.GetFileNameWithoutExtension(tagFile);
                    Console.WriteLine(string.Format("Importing Tag Table: {0} ...", tableName));
                    try
                    {
                        string fileToImport = FilterTagXml(tagFile);
                        plcSoftware.TagTableGroup.TagTables.Import(new FileInfo(fileToImport), ImportOptions.Override);
                        if (fileToImport != tagFile)
                        {
                            try { File.Delete(fileToImport); } catch {}
                        }
                        Console.WriteLine("  SUCCESS!");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("  FAILED! {0}", ex.Message));
                    }
                }
            }

            // Pre-clean legacy blocks starting with "AI_"
            try
            {
                foreach (var block in plcSoftware.BlockGroup.Blocks.ToList())
                {
                    if (block.Name.StartsWith("AI_", StringComparison.OrdinalIgnoreCase))
                    {
                        Console.WriteLine(string.Format("Deleting old block: {0} ...", block.Name));
                        block.Delete();
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Warning: Failed to clean old blocks: " + ex.Message);
            }

            // 3. IMPORT BLOCKS
            if (blockFiles.Count > 0)
            {
                Console.WriteLine("\n--- 3. IMPORTING BLOCK XMLs ---");
                foreach (string blockFile in blockFiles)
                {
                    string blockName = Path.GetFileNameWithoutExtension(blockFile);
                    Console.WriteLine(string.Format("Importing Block: {0} ...", blockName));
                    try
                    {
                        plcSoftware.BlockGroup.Blocks.Import(new FileInfo(blockFile), ImportOptions.Override);
                        Console.WriteLine("  SUCCESS!");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(string.Format("  FAILED! {0}", ex.Message));
                    }
                }
            }

            // 3.5. IMPORT HMI TEXT AND GRAPHIC LISTS
            if (hmiTextListFiles.Count > 0 || hmiGraphicListFiles.Count > 0)
            {
                Console.WriteLine("\n--- 3.5. IMPORTING HMI TEXT & GRAPHIC LISTS ---");
                List<HmiTarget> hmiTargets = new List<HmiTarget>();
                foreach (var dev in proj.Devices)
                {
                    foreach (var item in dev.DeviceItems)
                    {
                        FindHmiTargets(item, hmiTargets);
                    }
                }

                if (hmiTargets.Count == 0)
                {
                    Console.WriteLine("Warning: Found HMI list XMLs to import, but no HMI device (HmiTarget) was found in the project.");
                }
                else
                {
                    foreach (var hmiTarget in hmiTargets)
                    {
                        Console.WriteLine(string.Format("Target HMI Device: {0}", hmiTarget.Name));

                        // Import Text Lists
                        foreach (string textListFile in hmiTextListFiles)
                        {
                            string listName = Path.GetFileNameWithoutExtension(textListFile);
                            Console.WriteLine(string.Format("  Importing HMI Text List: {0} ...", listName));
                            try
                            {
                                hmiTarget.TextLists.Import(new FileInfo(textListFile), ImportOptions.Override);
                                Console.WriteLine("    SUCCESS!");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine(string.Format("    FAILED! {0}", ex.Message));
                            }
                        }

                        // Import Graphic Lists
                        foreach (string graphicListFile in hmiGraphicListFiles)
                        {
                            string listName = Path.GetFileNameWithoutExtension(graphicListFile);
                            Console.WriteLine(string.Format("  Importing HMI Graphic List: {0} ...", listName));
                            try
                            {
                                hmiTarget.GraphicLists.Import(new FileInfo(graphicListFile), ImportOptions.Override);
                                Console.WriteLine("    SUCCESS!");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine(string.Format("    FAILED! {0}", ex.Message));
                            }
                        }
                    }
                }
            }

            // 4. COMPILATION
            if (runCompile)
            {
                Console.WriteLine("\n--- 4. COMPILING PLC SOFTWARE ---");
                ICompilable compilable = plcSoftware.GetService<ICompilable>();
                if (compilable == null)
                {
                    Console.WriteLine("Error: PLC software container does not support compilation.");
                }
                else
                {
                    Console.WriteLine("Compiling project software, please wait...");
                    CompilerResult result = compilable.Compile();
                    Console.WriteLine(string.Format("Compilation finished with state: {0}", result.State));
                    Console.WriteLine(string.Format("Total messages: {0}", result.Messages.Count));

                    int errors = 0;
                    int warnings = 0;
                    PrintCompilerMessages(result.Messages, ref errors, ref warnings);
                    Console.WriteLine(string.Format("Compilation summary: {0} Errors, {1} Warnings", errors, warnings));
                }
            }

            Console.WriteLine("\n========================================");
            Console.WriteLine("FINISHED GENERIC IMPORT PROCESS!");
            Console.WriteLine("========================================");
        }
        catch (Exception ex)
        {
            Console.WriteLine(string.Format("CRITICAL ERROR: {0}", ex.Message));
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

    static void FindHmiTargets(DeviceItem item, List<HmiTarget> targets)
    {
        var sc = item.GetService<SoftwareContainer>();
        if (sc != null && sc.Software is HmiTarget)
        {
            targets.Add(sc.Software as HmiTarget);
        }
        foreach (var child in item.DeviceItems)
        {
            FindHmiTargets(child, targets);
        }
    }

    static string FilterTagXml(string filePath)
    {
        try
        {
            XmlDocument doc = new XmlDocument();
            doc.Load(filePath);
            
            // Find all <SW.Tags.PlcTag> nodes
            XmlNodeList tagNodes = doc.GetElementsByTagName("SW.Tags.PlcTag");
            List<XmlNode> nodesToRemove = new List<XmlNode>();
            
            foreach (XmlNode node in tagNodes)
            {
                XmlNode attrList = FindChildByName(node, "AttributeList");
                if (attrList != null)
                {
                    XmlNode nameNode = FindChildByName(attrList, "Name");
                    if (nameNode != null)
                    {
                        string tagName = nameNode.InnerText;
                        if (tagName == "FirstScan" || tagName == "Clock_1Hz")
                        {
                            nodesToRemove.Add(node);
                        }
                    }
                }
            }
            
            if (nodesToRemove.Count > 0)
            {
                Console.WriteLine(string.Format("  Filtering out {0} conflicting system tag(s) from XML: FirstScan, Clock_1Hz...", nodesToRemove.Count));
                foreach (XmlNode node in nodesToRemove)
                {
                    node.ParentNode.RemoveChild(node);
                }
                
                string tempPath = Path.Combine(Path.GetTempPath(), Path.GetFileName(filePath));
                doc.Save(tempPath);
                return tempPath;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Warning: Failed to filter tag XML: " + ex.Message);
        }
        return filePath;
    }

    static XmlNode FindChildByName(XmlNode parent, string name)
    {
        foreach (XmlNode child in parent.ChildNodes)
        {
            if (child.Name == name)
            {
                return child;
            }
        }
        return null;
    }

    static void PrintCompilerMessages(CompilerResultMessageComposition messages, ref int errors, ref int warnings, int indent = 1)
    {
        string spaces = new string(' ', indent * 2);
        foreach (CompilerResultMessage msg in messages)
        {
            string stateStr = msg.State.ToString();
            string pathInfo = string.IsNullOrEmpty(msg.Path) ? "" : string.Format(" ({0})", msg.Path);
            if (stateStr.Contains("Error"))
            {
                errors++;
                Console.WriteLine(string.Format("{0}[ERROR]{1} {2}", spaces, pathInfo, msg.Description));
            }
            else if (stateStr.Contains("Warning"))
            {
                warnings++;
                Console.WriteLine(string.Format("{0}[WARNING]{1} {2}", spaces, pathInfo, msg.Description));
            }
            else
            {
                Console.WriteLine(string.Format("{0}[INFO]{1} {2}", spaces, pathInfo, msg.Description));
            }
            
            if (msg.Messages != null && msg.Messages.Count > 0)
            {
                PrintCompilerMessages(msg.Messages, ref errors, ref warnings, indent + 1);
            }
        }
    }
}
