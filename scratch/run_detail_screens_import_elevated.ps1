$scriptPath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\run_detail_screens_import.py"
Write-Host "Requesting Administrator privileges to run run_detail_screens_import.py..."
Start-Process python -ArgumentList $scriptPath -Verb RunAs -Wait
Write-Host "Elevated execution completed."
