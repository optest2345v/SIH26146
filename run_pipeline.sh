#!/usr/bin/env bash
# SIH26146 — Linux End-to-End Pipeline CLI Runner
# Team COGNOVAX (Team ID: 162623) | Sponsor: NTRO

set -e

DATA_PATH="${1:-data/synthetic/transactions_sample.csv}"

echo "============================================================"
echo "  SIH26146: Offline Transaction Intelligence Pipeline (Linux)"
echo "  Team: COGNOVAX (Team ID: 162623)"
echo "============================================================"
echo ""
echo "[+] Processing target dataset: $DATA_PATH"
echo ""

python3 main.py run --data "$DATA_PATH"
