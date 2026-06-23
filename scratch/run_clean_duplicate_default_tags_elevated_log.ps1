$exePath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\clean_duplicate_default_tags.exe"
$outputPath = "D:\AI_Agent_PLC_LADDER_ONLY\scratch\clean_duplicate_default_tags_log.txt"
Write-Host "Running clean tool with redirect..."
Start-Process cmd -ArgumentList "/c `"$exePath`" > `"$outputPath`"" -Verb RunAs -Wait
Write-Host "Done."
