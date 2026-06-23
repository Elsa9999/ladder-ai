@echo off
cls
setlocal enabledelayedexpansion

echo Create ZIP folder with the necessary debug information for Code2Docu
echo.

REM Set working directory
cd /d %~dp0
echo Starting path: %cd%
cd ..\..
echo Reworked path: %cd%
echo.

:: Define the list of folders to include (whitelist)
set log="Logs\*_C2D.log"
set includeList=("AddIn\Code2Docu" "UserFiles\Code2Docu" "log")

if not exist "log" (
    mkdir "log"
)
for %%i in ("Logs\*_C2D.log") do (
    xcopy %%i "log" /H /C /I /Y /Q
)

set includeParams=
for %%i in ("*.amc*") do (
    set includeParams=!includeParams! "%%i"
)
for %%i in ("*.ap*") do (
    set includeParams=!includeParams! "%%i"
)

:: Create the inclusion parameters for tar
for %%j in %includeList% do (
    set includeParams=!includeParams! %%j
)

echo Include params: %includeParams%

:: Define the list of files/directories to exclude
set excludeList=("siemens" "thumbs.db" ".mudb" "AdditionalFiles" "Logs" "IM" "System" "tmp" "VCI" "XRef" "UserFiles/Code2Docu/Code2DocuDebuggingInfos.zip" "UserFiles/Code2Docu/highlightJS" "UserFiles/Code2Docu/KaTeX")

:: Create the exclusion parameters for tar
set excludeParams=
for %%i in %excludeList% do (
    set excludeParams=!excludeParams! --exclude=%%i
)
echo.

set /p withImages="Would you include images into the debug container (Y/N): "

:: Überprüfen der Auswahl
if /i "%withImages%"=="J" (
    echo Include images in container
) else if /i "%withImages%"=="Y" (
    echo Include images in container
) else (
    echo DO NOT Include images in container!
    set excludeParams=!excludeParams! --exclude="UserFiles/Code2Docu/images"
)
echo.

echo Exclude params: %excludeParams%
echo.

echo Delete ZIP with needed information for debugging
del /F /Q  Code2DocuDebuggingInfos.zip
echo.

rem pause
rem echo.

echo Create ZIP with needed information for debugging
rem tar.exe --exclude-from=zipExclude.txt -c -a -v -f Code2DocuDebuging.zip %sourceDir%
rem tar.exe -c -a -v -f Code2DocuDebuging.zip !sourceDir!
tar.exe %excludeParams% -c -a -v -f UserFiles\Code2Docu\Code2DocuDebuggingInfos.zip %includeParams%
echo.

if exist "log" (
    rmdir /S /Q "log"
)

echo creating the necessary debug information for Code2Docu finished.....
pause
