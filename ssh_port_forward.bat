@echo off
setlocal enabledelayedexpansion

echo SSH Port Forwarding Tool
echo ========================
echo This script will set up SSH port forwarding for IPFS services
echo - Port 5001: IPFS API
echo - Port 8080: IPFS Gateway
echo.

REM Check if plink is installed
where plink >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: plink.exe not found. Please install PuTTY tools.
    echo You can download PuTTY from: https://www.putty.org/
    echo.
    echo After installation, make sure plink.exe is in your PATH or copy it to the same directory as this script.
    pause
    exit /b 1
)

echo Starting port forwarding...
echo.

REM Create a temporary batch file for the first port forwarding
set "temp_batch1=%TEMP%\ssh_forward_5001_%RANDOM%.bat"
echo @echo off > "!temp_batch1!"
echo echo Forwarding localhost:5001 to 172.22.232.42:5001 >> "!temp_batch1!"
echo echo Password: dev01@gzhu >> "!temp_batch1!"
echo echo. >> "!temp_batch1!"
echo plink -ssh -L 5001:localhost:5001 -pw dev01@gzhu dev01@172.22.232.42 >> "!temp_batch1!"
echo exit >> "!temp_batch1!"

REM Create a temporary batch file for the second port forwarding
set "temp_batch2=%TEMP%\ssh_forward_8080_%RANDOM%.bat"
echo @echo off > "!temp_batch2!"
echo echo Forwarding localhost:8080 to 172.22.232.42:8080 >> "!temp_batch2!"
echo echo Password: dev01@gzhu >> "!temp_batch2!"
echo echo. >> "!temp_batch2!"
echo plink -ssh -L 8080:127.0.0.1:8080 -pw dev01@gzhu dev01@172.22.232.42 >> "!temp_batch2!"
echo exit >> "!temp_batch2!"

REM Start port forwarding processes
start "IPFS API Port Forward (5001)" cmd /c "!temp_batch1!"
set "pid1=!ERRORLEVEL!"
start "IPFS Gateway Port Forward (8080)" cmd /c "!temp_batch2!"
set "pid2=!ERRORLEVEL!"

echo Port forwarding started in separate windows.
echo.
echo You can now access:
echo - IPFS API at http://localhost:5001/webui
echo - IPFS Gateway at http://localhost:8080/ipfs/[hash]
echo.
echo This console window controls the port forwarding sessions.
echo When you close this window, the port forwarding will stop.
echo.
echo Press Ctrl+C to stop port forwarding and exit...
echo.

REM Keep the main console open and wait for user to close it
timeout /t 86400 > nul

REM When the script exits, the started processes will be terminated automatically
REM because they are child processes of this cmd window
endlocal
