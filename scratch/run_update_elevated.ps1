$exePath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\update_tia_project.exe"
$outputPath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\update_log.txt"
Write-Host "Running update tool and redirecting to $outputPath..."
Start-Process cmd -ArgumentList "/c `"$exePath`" > `"$outputPath`" 2>&1" -Verb RunAs -Wait
Write-Host "Done."
