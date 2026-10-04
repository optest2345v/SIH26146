#!/usr/bin/env bash
# SIH26146 — Linux Dashboard Launcher
# Team COGNOVAX (Team ID: 162623) | Sponsor: NTRO
# Mode: STRICT AIR-GAPPED OFFLINE

set -e

echo "============================================================"
echo "  SIH26146: Bitcoin Transaction & Network Intelligence"
echo "  Team: COGNOVAX (Team ID: 162623) | Sponsor: NTRO"
echo "  Mode: STRICT AIR-GAPPED OFFLINE (Linux)"
echo "============================================================"
echo ""
echo "[+] Initializing local investigation service on http://127.0.0.1:8000 ..."
echo "[+] Waiting for dashboard server to become ready before opening browser..."
echo ""

# Asynchronous health check poller to launch browser only after server is ready
(
  while ! curl -s -f http://127.0.0.1:8000/api/health > /dev/null 2>&1; do
    sleep 0.25
  done
  echo "[+] Service is ready! Launching default browser..."
  if command -v xdg-open > /dev/null 2>&1; then
    xdg-open "http://127.0.0.1:8000" > /dev/null 2>&1 &
  elif command -v gnome-open > /dev/null 2>&1; then
    gnome-open "http://127.0.0.1:8000" > /dev/null 2>&1 &
  elif command -v sensible-browser > /dev/null 2>&1; then
    sensible-browser "http://127.0.0.1:8000" > /dev/null 2>&1 &
  fi
) &

python3 main.py serve --host 127.0.0.1 --port 8000
