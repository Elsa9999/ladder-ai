# Optimized Scan script to find AutoCAD / AutoCAD Electrical residual files/folders on C and D drives
$results = [System.Collections.Generic.List[PSCustomObject]]::new()

# Known folders on C drive
$knownAutodeskPaths = @(
    "C:\Program Files\Autodesk",
    "C:\Program Files (x86)\Autodesk",
    "C:\ProgramData\Autodesk",
    "C:\Users\Public\Documents\Autodesk",
    "C:\Autodesk"
)

# AppData for each user
$users = Get-ChildItem "C:\Users" -Directory -ErrorAction SilentlyContinue
foreach ($user in $users) {
    $username = $user.Name
    if ($username -eq "All Users" -or $username -eq "Default" -or $username -eq "Default User") {
        continue
    }
    $knownAutodeskPaths += "C:\Users\$username\AppData\Local\Autodesk"
    $knownAutodeskPaths += "C:\Users\$username\AppData\Roaming\Autodesk"
    $knownAutodeskPaths += "C:\Users\$username\Documents\Autodesk"
}

Write-Host "Checking targeted Autodesk paths on C:..."

foreach ($path in $knownAutodeskPaths) {
    if (Test-Path $path) {
        # Calculate size of the directory
        $size = 0
        try {
            $files = Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue
            foreach ($f in $files) { $size += $f.Length }
        } catch {}
        
        $results.Add([PSCustomObject]@{
            Path = $path
            Type = "Directory"
            SizeMB = [Math]::Round($size / 1MB, 2)
            Description = "Autodesk/AutoCAD remnant directory (C:)"
        })
    }
}

# Scan D drive - search only up to 2 levels deep to avoid scanning the entire D: drive recursively
Write-Host "Scanning D: drive up to level 2 for Autodesk/AutoCAD..."
$dPatterns = @(
    "D:\*Autodesk*",
    "D:\*AutoCAD*",
    "D:\*\*Autodesk*",
    "D:\*\*AutoCAD*"
)

foreach ($pattern in $dPatterns) {
    try {
        $items = Get-Item $pattern -ErrorAction SilentlyContinue
        foreach ($item in $items) {
            $size = 0
            if ($item.PSIsContainer) {
                try {
                    $files = Get-ChildItem -Path $item.FullName -Recurse -File -ErrorAction SilentlyContinue
                    foreach ($f in $files) { $size += $f.Length }
                } catch {}
                $type = "Directory"
            } else {
                $size = $item.Length
                $type = "File"
            }
            
            $results.Add([PSCustomObject]@{
                Path = $item.FullName
                Type = $type
                SizeMB = [Math]::Round($size / 1MB, 2)
                Description = "Autodesk/AutoCAD remnant found on D:"
            })
        }
    } catch {}
}

# Unique results by path
$uniqueResults = $results | Group-Object Path | ForEach-Object { $_.Group[0] }

# Export to JSON
$outputPath = Join-Path $PSScriptRoot "scan_results.json"
$uniqueResults | ConvertTo-Json -Depth 4 | Out-File -FilePath $outputPath -Encoding utf8
Write-Host "Scan completed. Results written to: $outputPath"
Write-Host "Found $($uniqueResults.Count) potential remnant locations."
