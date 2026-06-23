$exePath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\list_hmi_tags_in_tia.exe"
$outputPath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\hmi_tags_in_project.txt"
Write-Host "Listing HMI tags into $outputPath via cmd..."
Start-Process cmd -ArgumentList "/c `"$exePath`" > `"$outputPath`"" -Verb RunAs -Wait
Write-Host "Done."
