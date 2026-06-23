import os
import subprocess

print("Process Owner Scan:")
try:
    # Use WMIC or powershell via subprocess to avoid parsing issues
    cmd = ["powershell", "-Command", "Get-WmiObject Win32_Process -Filter \"name='Siemens.Automation.Portal.exe'\" | ForEach-Object { $owner = $_.GetOwner(); Write-Output \"PID: $($_.ProcessId) | Owner: $($owner.Domain)\\$($owner.User)\" }"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Stdout:")
    print(res.stdout)
    print("Stderr:")
    print(res.stderr)
except Exception as e:
    print("Error:", e)
