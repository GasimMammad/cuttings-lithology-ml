#!/bin/zsh
cd "$(dirname "$0")"
LOG=~/sinkite_ml_work/final_run.log
while ! grep -q "ALL DONE" "$LOG" 2>/dev/null; do
  if grep -qE "FAILED" "$LOG" 2>/dev/null; then echo "[stage1 failed, aborting]" >> "$LOG"; exit 1; fi
  sleep 20
done
echo "[$(date +%H:%M:%S)] stage 2: tier-1 balanced (part b)" >> "$LOG"
.venv/bin/python 10_tier1_balanced.py >> "$LOG" 2>&1 || { echo "TIER1B FAILED" >> "$LOG"; exit 1; }
echo "[$(date +%H:%M:%S)] regenerating report" >> "$LOG"
.venv/bin/python 09_report.py >> "$LOG" 2>&1 || { echo "REPORT2 FAILED" >> "$LOG"; exit 1; }
echo "[$(date +%H:%M:%S)] STAGE2 DONE" >> "$LOG"
