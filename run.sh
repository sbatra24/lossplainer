#!/usr/bin/env bash
# Reproduce everything: tests, self-play training, baseline matches, and the
# committed reports in outputs/.  Takes about an hour on two cores.
set -euo pipefail
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1
export PYTHONHASHSEED=0

MINUTES="${TRAIN_MINUTES:-30}"
MATCH_GAMES="${MATCH_GAMES:-20}"

echo "== tests (move generator, search, network, explainer, UCI)"
python3 -m pytest -q tests

echo "== self-play TD-Leaf training for ${MINUTES} minutes"
python3 train.py --minutes "${MINUTES}" --depth 2 --workers 2 --seed 0

echo "== matches against the untrained baselines"
python3 match.py --opponent init --games "${MATCH_GAMES}" --depth 2 --seed 0
python3 match.py --opponent material --games "${MATCH_GAMES}" --depth 2 --seed 0 --append

echo "== reports"
python3 report.py bench
python3 report.py examples --depth 4
python3 report.py selfgame --depth 4 --seconds 8

echo "done; see outputs/"
