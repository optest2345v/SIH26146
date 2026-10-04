@echo off
title SIH26146 - 10,000+ Record Benchmark Generator
echo ============================================================
echo   SIH26146: Generating 10,000+ Forensic Benchmark
echo   Execution Mode: STRICT AIR-GAPPED OFFLINE
echo ============================================================
echo.
echo [*] Generating 10,000+ synthetic records across CSV, JSON, and XML...
echo [*] Compiling separate hidden ground truth (ground_truth.json)...
echo [*] Compiling benchmark verification manifest (benchmark_manifest.json)...
echo.
python main.py generate-benchmark --records 10250 --seed 42 --out-dir data/benchmark_10k
echo.
echo ============================================================
echo Benchmark generation complete!
echo Files saved under: data\benchmark_10k\
echo ============================================================
pause
