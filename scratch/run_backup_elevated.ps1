$exePath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\backup_project.exe"
Write-Host "Requesting Administrator privileges to run backup_project..."
Start-Process $exePath -Verb RunAs -Wait
Write-Host "Elevated execution completed."
