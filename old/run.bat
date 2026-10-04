@echo off
title SIH26146 - Bitcoin Transaction & Network Intelligence
:MENU
cls
echo ============================================================
echo   SIH26146: Bitcoin Transaction ^& Network Intelligence
echo   Sponsor: National Technical Research Organisation (NTRO)
echo   Execution Mode: STRICT OFFLINE
echo ============================================================
echo.
echo   [1] Launch Investigation Web Dashboard (Opens Browser)
echo   [2] Launch Terminal Forensic Console (Headless / SSH / No Browser)
echo   [3] Run Forensic Pipeline CLI Batch (Ingest, Correlate, ML, Rank)
echo   [4] Run Automated Test Suite (39 Pytest Verification Tests)
echo   [5] Regenerate Baseline Test Datasets (34 records)
echo   [6] Generate 10,000+ Record Benchmark Dataset (JSON, CSV, XML, Hidden Key)
echo   [7] Run 10k Blind Benchmark Evaluation & Scorecard
echo   [8] Run Model Ablation Benchmark Study
echo   [9] Exit
echo.
echo ============================================================
set /p choice="Enter option [1-9]: "

if "%choice%"=="1" (
    echo.
    echo [+] Starting local dashboard server...
    start "" http://127.0.0.1:8000
    python main.py serve
    goto MENU
)
if "%choice%"=="2" (
    echo.
    python main.py console
    goto MENU
)
if "%choice%"=="3" (
    echo.
    python main.py run
    echo.
    pause
    goto MENU
)
if "%choice%"=="4" (
    echo.
    python -m pytest -v
    echo.
    pause
    goto MENU
)
if "%choice%"=="5" (
    echo.
    python main.py generate-data
    echo.
    pause
    goto MENU
)
if "%choice%"=="6" (
    echo.
    python main.py generate-benchmark
    echo.
    pause
    goto MENU
)
if "%choice%"=="7" (
    echo.
    python main.py evaluate-benchmark
    echo.
    pause
    goto MENU
)
if "%choice%"=="8" (
    echo.
    python main.py evaluate --ablation
    echo.
    pause
    goto MENU
)
if "%choice%"=="9" (
    exit /b
)

echo.
echo Invalid option selected.
pause
goto MENU
