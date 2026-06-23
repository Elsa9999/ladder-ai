$exePath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\launch_cuocthi_tdh.exe"
Write-Host "Requesting Administrator privileges to run launch_cuocthi_tdh..."
Start-Process $exePath -Verb RunAs -Wait
Write-Host "Elevated execution completed."
