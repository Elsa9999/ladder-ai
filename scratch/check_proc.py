import subprocess

try:
    cmd = "Get-CimInstance Win32_Process | Where-Object {$_.Name -like '*Portal*' -or $_.Name -like '*Siemens*' -or $_.Name -like '*Engineering*'} | Select-Object Name, CommandLine"
    output = subprocess.check_output(["powershell", "-Command", cmd], text=True, errors='ignore')
    print("Siemens/Portal Processes:")
    print(output)
except Exception as ex:
    print(f"Error: {ex}")
