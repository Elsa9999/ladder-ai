import subprocess

print("Scanning for Siemens/Openness services:")
try:
    cmd = ["powershell", "-Command", "Get-Service | Where-Object { $_.DisplayName -like '*openness*' -or $_.Name -like '*openness*' -or $_.DisplayName -like '*siemens*' } | ForEach-Object { Write-Output \"Name: $($_.Name) | Status: $($_.Status) | Display: $($_.DisplayName)\" }"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Stdout:")
    print(res.stdout)
    print("Stderr:")
    print(res.stderr)
except Exception as e:
    print("Error:", e)
