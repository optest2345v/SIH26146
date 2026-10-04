#!/usr/bin/env bash
# SIH26146 — Unified Interactive Operations Launcher (Linux)
# Team COGNOVAX (Team ID: 162623) | Sponsoring Agency: NTRO

clear || true

echo "============================================================"
echo "  SIH26146: Bitcoin Transaction & Network Intelligence"
echo "  INVESTIGATIVE UNIT: TEAM COGNOVAX (Team ID: 162623)"
echo "  SPONSORING AGENCY : NTRO"
echo "  EXECUTION MODE    : 100% AIR-GAPPED OFFLINE (LINUX)"
echo "============================================================"
echo ""
echo "Select operation:"
echo "  1) Launch Investigation Dashboard (Web UI on :8000)"
echo "  2) Run Pipeline CLI on Synthetic Sample Dataset"
echo "  3) Run Complete Automated Verification Suite (39 Tests)"
echo "  4) Generate 10,000+ Record Forensic Benchmark Dataset"
echo "  5) Evaluate Detection Model against Blind Ground Truth"
echo "  6) Run Model Ablation Benchmark Study"
echo "  7) Exit"
echo ""
read -p "Enter choice [1-7]: " choice

case "$choice" in
  1)
    ./start_dashboard.sh
    ;;
  2)
    python3 main.py run
    ;;
  3)
    ./run_tests.sh
    ;;
  4)
    python3 main.py generate-benchmark
    ;;
  5)
    python3 main.py evaluate-benchmark
    ;;
  6)
    python3 main.py evaluate --ablation
    ;;
  7)
    echo "Exiting."
    clear
    exit 0
    ;;
  *)
    echo "Invalid selection. Exiting."
    exit 1
    ;;
esac
