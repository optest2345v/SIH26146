@echo off
title SIH26146 - Bitcoin Transaction & Network Intelligence
:MENU
cls
echo ============================================================
echo   SIH26146: Bitcoin Transaction ^& Network Intelligence
echo   Team: COGNOVAX (Team ID: 162623)
echo   Sponsor: National Technical Research Organisation (NTRO)
echo   Execution Mode: STRICT AIR-GAPPED OFFLINE
echo ============================================================
echo.
echo   [1] Launch Investigation Web Dashboard (Opens Browser)
echo   [2] Run Forensic Pipeline CLI (Ingest, Correlate, ML, Rank)
echo   [3] Run Automated Test Suite (39 Pytest Verification Tests)
echo   [4] Regenerate Baseline Test Datasets (34 records)
echo   [5] Generate 10,000+ Record Benchmark Dataset (JSON, CSV, XML, Hidden Key)
echo   [6] Run 10k Blind Benchmark Evaluation ^& Scorecard
echo   [7] Run Model Ablation Benchmark Study
echo   [8] Exit
echo.
echo ============================================================
set /p choice="Enter option [1-8]: "

if "%choice%"=="1" (
    call start_dashboard.bat
    goto MENU
)
if "%choice%"=="2" (
    echo.
    python main.py run
    echo.
    pause
    goto MENU
)
if "%choice%"=="3" (
    call run_tests.bat
    goto MENU
)
if "%choice%"=="4" (
    echo.
    python main.py generate-data
    echo.
    pause
    goto MENU
)
if "%choice%"=="5" (
    echo.
    python main.py generate-benchmark
    echo.
    pause
    goto MENU
)
if "%choice%"=="6" (
    echo.
    python main.py evaluate-benchmark
    echo.
    pause
    goto MENU
)
if "%choice%"=="7" (
    echo.
    python main.py evaluate --ablation
    echo.
    pause
    goto MENU
)
if "%choice%"=="8" (
    exit /b
)

echo.
echo Invalid option selected.
pause
goto MENU
