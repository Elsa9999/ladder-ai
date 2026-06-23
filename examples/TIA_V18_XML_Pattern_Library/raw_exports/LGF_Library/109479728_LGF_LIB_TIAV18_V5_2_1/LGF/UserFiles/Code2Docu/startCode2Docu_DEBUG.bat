@echo off
cls
setlocal enabledelayedexpansion

SET directory=%~dp0
Set file=
Set extension=
Set tiaInstallPath=
Set c2dInstallPath=

echo Actual path is: %directory%

REM Loop through files matching the patterns
for %%f in ("%directory%..\..\*.ap*" "%directory%..\..\*.amc*") do (
    REM Extract the extension

    Set "file=%%f"
    Set "extension=%%~xf"

    REM remove dot
    set "ext=!extension:~1!"
	
    REM Extract the number from the extension
	REM Itterate trough chars
    set "number="
    for /l %%i in (0,1,255) do (
        set "char=!ext:~%%i,1!"
        if "!char!"=="" goto done
        for %%d in (0 1 2 3 4 5 6 7 8 9) do (
            if "!char!"=="%%d" set "number=!number!!char!"
        )
    )
    echo Extension Version: !number!
    echo Extension: !ext!
)
:done

echo Projectfile: %file%
echo Project extension: %extension%
echo Project Version: %number%
echo.

echo Get TIA Installation Path

set key=HKEY_LOCAL_MACHINE\SOFTWARE\Siemens\Automation\_InstalledSW\TIAP%number%\STEP7
FOR /F "usebackq skip=2 tokens=1-2*" %%A IN (`REG QUERY !key! /v Path 2^>nul`) DO (
	set ValueValue=%%C
	if defined ValueValue (
		echo Found TIA Portal V%number%
		echo Select the original AddIn !AddInName! folder : !ValueValue!AddIns\!AddInName!
		echo.
        set tiaInstallPath=!ValueValue!
        set c2dInstallPath=!ValueValue!AddIns\Code2Docu\Code2DocuConsole.exe
    	rem count found tia versions
		set /a count += 1
	)
	set ValueValue=
)

echo TIA Install: path: %tiaInstallPath%
echo C2D Install: path: %c2dInstallPath%
echo Projectfile: path: %file%

rem just if C2D exist
if not exist "%c2dInstallPath%" (
    echo Code2Docu not found!
	pause
    exit /b
)
REM Can't be a directory
if exist "%c2dInstallPath%\" (
    echo Error: path found is directory, not an executable: %c2dInstallPath%
	pause
    exit /b 1
)

echo Start Code2Docu......
echo.

call "%c2dInstallPath%" "%file%" true

rem Hard coded path to call Code2Docu_DEBUG
rem "C:\Program Files\Siemens\Automation\Portal V17\AddIns\Code2Docu\Code2DocuConsole.exe"  "C:\Users\GeierB\Documents\Automation\Sessions\109479728_LGF_V17_LS_GeierB\LS\109479728_LGF_V17.amc17" true
