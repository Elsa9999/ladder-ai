$scriptPath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\kill_tia_elevated.ps1"
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs -Wait
