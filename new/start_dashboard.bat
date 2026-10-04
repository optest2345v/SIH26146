@echo off
title SIH26146 - Bitcoin Telemetry Intelligence Dashboard
echo ============================================================
echo   SIH26146: Bitcoin Transaction ^& Network Intelligence
echo   Team: COGNOVAX (Team ID: 162623)
echo   Sponsor: National Technical Research Organisation (NTRO)
echo   Mode: STRICT AIR-GAPPED OFFLINE
echo ============================================================
echo.
echo [+] Initializing local investigation service on http://127.0.0.1:8000 ...
echo [+] Waiting for dashboard server to become ready before opening browser...
echo.

:: Start browser launcher in background that polls until server is ready
start /b "" powershell -NoProfile -Command "$ready = $false; while (-not $ready) { Start-Sleep -Milliseconds 250; try { $res = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue; if ($res.StatusCode -eq 200) { $ready = $true } } catch {} }; Start-Process 'http://127.0.0.1:8000'"

:: Start FastAPI local dashboard server
python main.py serve

pause
