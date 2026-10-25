#!/usr/bin/env bash
# Re-run every step-0 access check. Each check is independent and idempotent; results land
# in logs/<name>.json and tiny samples in data_samples/.
#
#   ./step0_access/run_all.sh            # all checks
#   ./step0_access/run_all.sh 05 06      # only checks whose filename starts with those ids
#
# Note: check_09_mole.py needs the SECOND venv (.venv-mole, transformers==4.38.2) because
# the MoLE modeling code is written against transformers 4.38 and breaks on 5.x.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
PY_MOLE="$ROOT/.venv-mole/bin/python"
cd "$ROOT/step0_access" || exit 1

[[ -x "$PY" ]] || { echo "missing venv: $PY"; exit 1; }

ALL=(check_01_env.py check_02_pile.py check_03_slimpajama.py check_04_pretrain_corpora.py
     check_05_pkm.py check_06_peer.py check_07_faiss.py check_08_peer_model.py
     check_09_mole.py check_10_sparse_memory.py check_11_stretch_models.py
     check_12_stretch_tensors.py check_13_mps_train.py)

if [[ $# -gt 0 ]]; then
  SEL=()
  for id in "$@"; do for f in "${ALL[@]}"; do [[ "$f" == check_"$id"_* ]] && SEL+=("$f"); done; done
else
  SEL=("${ALL[@]}")
fi

mkdir -p "$ROOT/logs"
echo "=== free disk before ==="; df -h "$HOME" | tail -1

# portable per-check watchdog -- macOS ships no `timeout`/`gtimeout` by default
TIMEOUT_SECS=${TIMEOUT_SECS:-900}
run_with_timeout() {  # run_with_timeout <logfile> <cmd...>
  local log="$1"; shift
  "$@" > "$log" 2>&1 &
  local pid=$! waited=0
  while kill -0 "$pid" 2>/dev/null; do
    if (( waited >= TIMEOUT_SECS )); then
      kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
      echo "TIMEOUT after ${TIMEOUT_SECS}s" >> "$log"; return 124
    fi
    sleep 2; waited=$((waited + 2))
  done
  wait "$pid"
}

declare -a FAILED=()
for f in "${SEL[@]}"; do
  interp="$PY"
  if [[ "$f" == check_09_mole.py ]]; then
    if [[ -x "$PY_MOLE" ]]; then interp="$PY_MOLE"
    else echo "--- SKIP $f (no .venv-mole; see reports/step0_access_report.md) ---"; continue; fi
  fi
  echo; echo "=== $f ==="
  if run_with_timeout "$ROOT/logs/${f%.py}.out" "$interp" -u "$f"; then
    echo "PASS (log: logs/${f%.py}.out)"
  else
    rc=$?
    echo "FAIL rc=$rc (log: logs/${f%.py}.out)"; tail -15 "$ROOT/logs/${f%.py}.out"
    FAILED+=("$f")
  fi
done

echo; echo "=== C5: biography generator ==="
"$PY" "$ROOT/tools/bio_generator.py" --n 1000 --seed 0 \
      --out "$ROOT/data_samples/bios_sample.jsonl" --count-tokens | tail -12

echo; echo "=== free disk after ==="; df -h "$HOME" | tail -1
echo; echo "=== data_samples ==="; ls -lh "$ROOT/data_samples"

if [[ ${#FAILED[@]} -gt 0 ]]; then echo; echo "FAILED: ${FAILED[*]}"; exit 1; fi
echo; echo "all selected checks passed"
