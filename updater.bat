@ECHO OFF
SETLOCAL EnableDelayedExpansion

echo.
echo.
echo Downloading Latest Update . . .
powershell (New-Object System.Net.WebClient).Downloadfile('https://github.com/LIL-JRG/cjrtoolkit/archive/refs/heads/main.zip', 'cjrtoolkit-latest.zip') 
if %errorlevel% neq 0 (
    echo Error: No se pudo descargar la actualización.
    exit /b 1
)

echo Extracting Files
powershell.exe Expand-Archive -Path cjrtoolkit-latest.zip -Force 
if %errorlevel% neq 0 (
    echo Error: No se pudieron extraer los archivos.
    exit /b 1
)

echo Replacing Files
xcopy /s "cjrtoolkit-latest/cjrtoolkit-main" "*" /Y
if %errorlevel% neq 0 (
    echo Error: No se pudieron reemplazar los archivos.
    exit /b 1
)

echo Cleaning Up Temp Files !
powershell Remove-Item -Path cjrtoolkit-latest.zip -Force
powershell Remove-Item -Path cjrtoolkit-latest -Force -Recurse
echo Successfully Updated ! You may Now Run The Program.

ENDLOCAL
PAUSE
EXIT /B
