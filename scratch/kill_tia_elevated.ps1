Write-Host "Killing all Siemens.Automation.Portal processes..."
Stop-Process -Name Siemens.Automation.Portal -Force -ErrorAction SilentlyContinue
Stop-Process -Name Siemens.Automation.ObjectFrame -Force -ErrorAction SilentlyContinue
Write-Host "Completed."
