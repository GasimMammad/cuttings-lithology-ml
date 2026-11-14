#!/bin/zsh
# Final iteration driver: wait for feature shards -> combine -> compare -> report.
cd "$(dirname "$0")"
LOG=~/sinkite_ml_work/final_run.log
: > "$LOG"

echo "[$(date +%H:%M:%S)] waiting for 9 feature shards..." >> "$LOG"
while [ "$(ls ~/sinkite_ml_work/feature_shards/shard_*.csv 2>/dev/null | wc -l | tr -d ' ')" != "9" ]; do
  sleep 20
done
echo "[$(date +%H:%M:%S)] shards complete; combining" >> "$LOG"
../.venv/bin/python 07_extract_features.py >> "$LOG" 2>&1 || { echo "COMBINE FAILED" >> "$LOG"; exit 1; }

echo "[$(date +%H:%M:%S)] running 08_compare_models.py" >> "$LOG"
../.venv/bin/python 08_compare_models.py >> "$LOG" 2>&1 || { echo "COMPARE FAILED" >> "$LOG"; exit 1; }

echo "[$(date +%H:%M:%S)] running 09_report.py" >> "$LOG"
../.venv/bin/python 09_report.py >> "$LOG" 2>&1 || { echo "REPORT FAILED" >> "$LOG"; exit 1; }

echo "[$(date +%H:%M:%S)] ALL DONE" >> "$LOG"
