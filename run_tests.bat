@echo off
title SIH26146 - Test Suite Runner
echo ============================================================
echo   SIH26146: Running Automated Test Suite (Pytest)
echo   Verifying Ingestion, Geo-IP, Correlation, Graph, ML, Alerts
echo ============================================================
echo.

python -m pytest -v

echo.
echo ============================================================
echo   Tests finished. Press any key to close this window.
echo ============================================================
pause >nul
