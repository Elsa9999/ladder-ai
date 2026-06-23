$exePath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\delete_tcon_blocks.exe"
Write-Host "Requesting Administrator privileges to run delete_tcon_blocks..."
Start-Process $exePath -Verb RunAs -Wait
Write-Host "Elevated execution completed."
