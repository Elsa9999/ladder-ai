$exePath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\inspect_current_project.exe"
$outputPath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\inspect_log.txt"
Write-Host "Running inspect tool and redirecting to $outputPath..."
Start-Process cmd -ArgumentList "/c `"$exePath`" > `"$outputPath`"" -Verb RunAs -Wait
Write-Host "Done."
