# Wrapper script to run AutoCAD cleanup with Administrator privileges
$scriptPath = "d:\AI_Agent_PLC_LADDER_ONLY\scratch\clean_autocad.ps1"

Write-Host "Requesting Administrator privileges to run AutoCAD remnants cleanup..."
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs -Wait
Write-Host "Elevated execution completed."
