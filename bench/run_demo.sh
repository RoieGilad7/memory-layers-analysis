#!/usr/bin/env bash
# Step-1 benchmark suite, in order. Results in bench/results/*.json.
#
#   ./bench/run_demo.sh                 # everything
#   ./bench/run_demo.sh probe speed     # only those phases
#   STEPS=50 LEARN_STEPS=100 ./bench/run_demo.sh      # quick smoke run
#
# PYTORCH_ENABLE_MPS_FALLBACK is deliberately left UNSET: an op with no Metal
# kernel then raises instead of silently running on the CPU, so a clean run is
# evidence that nothing fell back.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
BENCH="$ROOT/bench/benchmark.py"
CFG="$ROOT/memlayers/configs"
RES="$ROOT/bench/results"
mkdir -p "$RES"
cd "$ROOT" || exit 1

unset PYTORCH_ENABLE_MPS_FALLBACK

STEPS="${STEPS:-300}"
WARMUP="${WARMUP:-30}"
LEARN_STEPS="${LEARN_STEPS:-1000}"

ALL_CONFIGS=(t1_dense t1_pkm t1_peer t1_pkm_frozen t2_dense t2_pkm t2_pkm_262k t2_peer)
MEMORY_CONFIGS=(t1_pkm t1_peer t1_pkm_frozen t2_pkm t2_pkm_262k t2_peer)
LEARN_CONFIGS=(t1_pkm t1_peer)

PHASES=("$@")
if [[ ${#PHASES[@]} -eq 0 ]]; then
  PHASES=(env probe speed readlog learn summarize)
fi

want() {
  local p
  for p in "${PHASES[@]}"; do
    if [[ "$p" == "$1" ]]; then return 0; fi
  done
  return 1
}

micro_of() {
  local f="$RES/$1__probe.json"
  if [[ -f "$f" ]]; then
    "$PY" -c "import json; print(json.load(open('$f')).get('largest_micro_batch') or 8)"
  else
    echo 8
  fi
}

banner() { echo; echo "=================== $* ==================="; }

if want env; then
  banner "ENVIRONMENT"
  "$PY" "$BENCH" summarize >/dev/null 2>&1 || true
  "$PY" -c "
import sys; sys.path.insert(0, '$ROOT')
import json
from bench.benchmark import env_info
json.dump(env_info(), open('$RES/env.json', 'w'), indent=2)
print(json.dumps(env_info(), indent=2))"
fi

if want probe; then
  banner "PHASE 1  micro-batch probe (4, 8, 16, 32)"
  for c in "${ALL_CONFIGS[@]}"; do
    echo "--- $c"
    "$PY" "$BENCH" probe --config "$CFG/$c.yaml" 2>&1 | tail -3
  done
fi

if want speed; then
  banner "PHASE 2  $STEPS steps on fake data (a), first $WARMUP discarded"
  for c in "${ALL_CONFIGS[@]}"; do
    m=$(micro_of "$c")
    echo "--- $c  (micro-batch $m)"
    "$PY" "$BENCH" speed --config "$CFG/$c.yaml" --steps "$STEPS" \
          --warmup "$WARMUP" --micro "$m" 2>&1 | tail -3
  done
fi

if want readlog; then
  banner "PHASE 3  same, with read logging on"
  for c in "${MEMORY_CONFIGS[@]}"; do
    m=$(micro_of "$c")
    echo "--- $c  (micro-batch $m, read logging)"
    "$PY" "$BENCH" speed --config "$CFG/$c.yaml" --steps "$STEPS" \
          --warmup "$WARMUP" --micro "$m" --read-logging 2>&1 | tail -3
  done
fi

if want learn; then
  banner "PHASE 4  $LEARN_STEPS steps on fake data (b), learning check"
  for c in "${LEARN_CONFIGS[@]}"; do
    m=$(micro_of "$c")
    echo "--- $c  (micro-batch $m)"
    "$PY" "$BENCH" learn --config "$CFG/$c.yaml" --steps "$LEARN_STEPS" \
          --micro "$m" 2>&1 | tail -4
  done
fi

if want summarize; then
  banner "PHASE 5  summary"
  "$PY" "$BENCH" summarize
fi

echo
echo "done. results in bench/results/"
