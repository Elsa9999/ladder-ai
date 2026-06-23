# PowerShell Script to safely clean AutoCAD/Autodesk remnants (Elevated Version)

$logPath = "d:\AI_Agent_PLC_LADDER_ONLY\scratch\cleanup_log.txt"
Start-Transcript -Path $logPath -Force -ErrorAction SilentlyContinue

$targets = @(
    "C:\Program Files\Autodesk",
    "C:\Program Files (x86)\Autodesk",
    "C:\ProgramData\Autodesk",
    "C:\Users\Public\Documents\Autodesk",
    "C:\Autodesk",
    "C:\Users\lienb\AppData\Local\Autodesk",
    "C:\Users\lienb\AppData\Roaming\Autodesk",
    "D:\Autodesk",
    "D:\AutoCAD_Electrical_2024_English_Win_64bit"
)

# Dynamically find the path to "học autocad" to avoid UTF-8 script encoding issues in PowerShell console
$hocAutoCadPath = (Get-Item "D:\h*c autocad" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName)
if (-not $hocAutoCadPath) {
    # fallback
    $hocAutoCadPath = "D:\học autocad"
}

$safeFolders = @(
    $hocAutoCadPath,
    "D:\Optimization_Tools\AutoCAD"
)

Write-Host "--- BẮT ĐẦU QUÁ TRÌNH DỌN DẸP AUTOCAD REMNANTS (ADMIN) ---"

# 1. Stop any running Autodesk processes / services to avoid file locks
Write-Host "Stopping AutoCAD / Autodesk services and processes..."
$processes = Get-Process | Where-Object { $_.Name -like "*autodesk*" -or $_.Name -like "*acad*" -or $_.Name -like "*adsk*" }
foreach ($p in $processes) {
    try {
        Write-Host "Stopping process: $($p.Name) ($($p.Id))"
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Warning "Could not stop process $($p.Name): $_"
    }
}

$services = Get-Service | Where-Object { $_.Name -like "*autodesk*" -or $_.Name -like "*adsk*" -or $_.DisplayName -like "*autodesk*" }
foreach ($s in $services) {
    if ($s.Status -eq 'Running') {
        try {
            Write-Host "Stopping service: $($s.Name) ($($s.DisplayName))"
            Stop-Service -Name $s.Name -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Warning "Could not stop service $($s.Name): $_"
        }
    }
}

# 2. Delete targets
$totalSpaceSaved = 0
$deletedCount = 0
$errorCount = 0

foreach ($target in $targets) {
    if (Test-Path $target) {
        Write-Host "Processing: $target"
        
        # Calculate size before deletion
        $size = 0
        try {
            $files = Get-ChildItem -Path $target -Recurse -File -ErrorAction SilentlyContinue
            if ($files -ne $null) {
                foreach ($f in $files) { 
                    $size += $f.Length 
                }
            }
        } catch {}
        
        try {
            # Perform deletion
            Remove-Item -Path $target -Recurse -Force -ErrorAction Stop
            $sizeMB = [Math]::Round($size / 1MB, 2)
            Write-Host "Successfully deleted: $target (Saved $sizeMB MB)"
            $totalSpaceSaved += $size
            $deletedCount++
        } catch {
            Write-Warning "Failed to delete: $target. Error: $_"
            $errorCount++
            try {
                Remove-Item -Path "$target\*" -Recurse -Force -ErrorAction SilentlyContinue
            } catch {}
        }
    } else {
        Write-Host "Target not found (already clean): $target"
    }
}

# 3. Verification of safe folders
Write-Host ""
Write-Host "Checking safety of protected folders:"
foreach ($safe in $safeFolders) {
    if (Test-Path $safe) {
        Write-Host "[SAFE] Thu muc van ton tai va an toan: $safe"
    } else {
        Write-Warning "[ALERT] Thu muc bao ve khong tim thay: $safe"
    }
}

# 4. Summary
$totalSpaceSavedMB = [Math]::Round($totalSpaceSaved / 1MB, 2)
$totalSpaceSavedGB = [Math]::Round($totalSpaceSaved / 1GB, 2)

Write-Host ""
Write-Host "--- TONG KET QUA TRINH DON DEP ---"
Write-Host "Da xoa thanh cong: $deletedCount thu muc."
if ($errorCount -gt 0) {
    Write-Host "So thu muc gap loi: $errorCount (Co the mot so file dang bi he thong khoa)."
}
Write-Host "Dung luong dia da giai phong: $totalSpaceSavedMB MB (~ $totalSpaceSavedGB GB)"
Write-Host "----------------------------------"

Stop-Transcript -ErrorAction SilentlyContinue
