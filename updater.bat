@ECHO OFF
SETLOCAL EnableDelayedExpansion
SET $Echo=FOR %%I IN (1 2) DO IF %%I==2 (SETLOCAL EnableDelayedExpansion ^& FOR %%A IN (^^^!Text:""^^^^^=^^^^^"^^^!) DO ENDLOCAL ^& ENDLOCAL ^& ECHO %%~A) ELSE SETLOCAL DisableDelayedExpansion ^& SET Text=

SETLOCAL DisableDelayedExpansion

echo.
echo.
echo Downloading Latest Update . . .
powershell (New-Object System.Net.WebClient).Downloadfile('https://github.com/LIL-JRG/cjrtoolkit/archive/refs/heads/main.zip', 'cjrtoolkit-latest.zip') 
echo Extracting Files
powershell.exe Expand-Archive -Path cjrtoolkit-latest.zip -Force 
echo Replacing Files
xcopy /s "cjrtoolkit-latest/cjrtoolkit-main" "*" /Y
echo Cleaning Up Temp Files !
powershell Remove-Item -Path cjrtoolkit-latest.zip -Force
powershell Remove-Item -Path cjrtoolkit-latest -Force -Recurse
echo Successfully Updated ! You may Now Run The Program.

ENDLOCAL

PAUSE
ENDLOCAL & EXIT /B