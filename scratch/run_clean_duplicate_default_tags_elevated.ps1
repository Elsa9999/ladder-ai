$exePath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\clean_duplicate_default_tags.exe"
Write-Host "Requesting Administrator privileges to run clean_duplicate_default_tags..."
Start-Process $exePath -Verb RunAs -Wait
Write-Host "Elevated execution completed."
