@echo off
title SIH26146 - 10,000+ Record Benchmark Evaluator
echo ============================================================
echo   SIH26146: Independent Benchmark Evaluation
echo   Scoring Pipeline Against Hidden Ground Truth
echo   Execution Mode: STRICT AIR-GAPPED OFFLINE
echo ============================================================
echo.
echo [*] Executing blind pipeline run on benchmark_data.json...
echo [*] Comparing results against hidden ground_truth.json...
echo.
python main.py evaluate-benchmark --data data/benchmark_10k/benchmark_data.json --ground-truth data/benchmark_10k/ground_truth.json --manifest data/benchmark_10k/benchmark_manifest.json --report data/benchmark_10k/benchmark_evaluation_report.md
echo.
echo ============================================================
echo Benchmark evaluation complete!
echo Report saved to: data\benchmark_10k\benchmark_evaluation_report.md
echo ============================================================
pause
