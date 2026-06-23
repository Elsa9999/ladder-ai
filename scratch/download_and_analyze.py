import os
import subprocess
import shutil

download_dir = r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\downloaded_projects"
os.makedirs(download_dir, exist_ok=True)

repositories = [
    ("Automated-Production-Line-Simulation", "https://github.com/Hesham-Hesham/Automated-Production-Line-Simulation.git"),
    ("TIAPORTALV16_S71200_completeProject", "https://github.com/onedevauto/TIAPORTALV16_S71200_completeProject.git"),
    ("FactoryIO", "https://github.com/rheradio/FactoryIO.git"),
    ("tia_portal_assignments", "https://github.com/bintangchristo/tia_portal_assignments.git"),
    ("PLC-Smoker", "https://github.com/trumakers/PLC-Smoker.git")
]

print("--- CLONING REPOSITORIES ---")
for name, url in repositories:
    target_path = os.path.join(download_dir, name)
    if os.path.exists(target_path):
        print(f"Repository {name} already exists. Skipping clone.")
        continue
    
    print(f"Cloning {name} from {url}...")
    try:
        # Run git clone
        result = subprocess.run(["git", "clone", "--depth", "1", url, target_path], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"  [OK] Cloned {name}")
        else:
            print(f"  [FAILED] {name}: {result.stderr.strip()}")
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")

print("\n--- ANALYZING DOWNLOADED REPOSITORIES ---")
found_tia_projects = []
found_xml_files = []

for root_dir, dirs, files in os.walk(download_dir):
    # Skip .git folders
    if ".git" in root_dir:
        continue
        
    for filename in files:
        filepath = os.path.join(root_dir, filename)
        rel_path = os.path.relpath(filepath, download_dir)
        
        # Check for TIA project files
        if any(filename.endswith(ext) for ext in [".ap18", ".ap17", ".ap16", ".ap15_1", ".ap15", ".zap18", ".zap17", ".zap16", ".zap15_1", ".zap15"]):
            found_tia_projects.append(rel_path)
            
        # Check for XML files
        if filename.endswith(".xml"):
            # Exclude some standard files if needed, but collect for check
            found_xml_files.append(rel_path)

print(f"\nFound TIA Portal Project Files ({len(found_tia_projects)}):")
for p in found_tia_projects:
    print(f"  - {p}")

print(f"\nFound XML Files ({len(found_xml_files)}):")
for x in found_xml_files[:15]:  # Limit output
    print(f"  - {x}")
if len(found_xml_files) > 15:
    print(f"  ... and {len(found_xml_files) - 15} more XML files.")
    
# Save analysis results
analysis_results = {
    "tia_projects": found_tia_projects,
    "xml_files": found_xml_files
}
with open(os.path.join(download_dir, "analysis_results.json"), "w", encoding="utf-8") as f:
    json.dump(analysis_results, f, indent=2, ensure_ascii=False)
