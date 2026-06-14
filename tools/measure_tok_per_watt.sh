#!/usr/bin/env bash
# Low Power Edge bake-off — measure tok/s-PER-WATT for an Ollama model on a Jetson.
# Runs ON the jetson. Pinned regime (temp 0, fixed prompt + num_predict). Warms the
# model first so cold-load isn't in the measured window; samples tegrastats VDD_IN
# (total board input power) across the generation; reports one JSON line.
#
#   bakeoff_measure.sh <model> [num_predict]
#
# Pair with `sudo nvpmodel -m <id>` to sweep power modes. VDD_IN is the honest
# board-level watts (not just the GPU rail) — what "tok/s per watt you can power" means.
set -uo pipefail
M="${1:?usage: bakeoff_measure.sh <model> [num_predict]}"
NP="${2:-256}"
PROMPT="Explain how a transistor works, in one paragraph."
API="http://localhost:11434/api/generate"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

req() { printf '{"model":"%s","prompt":"%s","stream":false,"options":{"num_predict":%s,"temperature":0}}' "$1" "$2" "$3"; }

# warm: load the model so the 12s cold-load isn't counted in the power window
curl -s "$API" -d "$(req "$M" "warm up" 8)" >/dev/null

# measure: sample tegrastats while the pinned generation runs
tegrastats --interval 200 > "$WORK/teg.log" 2>&1 &
TPID=$!
curl -s "$API" -d "$(req "$M" "$PROMPT" "$NP")" > "$WORK/resp.json"
kill "$TPID" 2>/dev/null; wait "$TPID" 2>/dev/null || true

MODE="$(nvpmodel -q 2>/dev/null | awk -F': ' '/Power Mode/{print $2}')"
TEG="$WORK/teg.log" RESP="$WORK/resp.json" MODE="${MODE:-?}" MODEL="$M" python3 - <<'PY'
import json, os, re
d = json.load(open(os.environ['RESP']))
ec = d.get('eval_count', 0)
ed = d.get('eval_duration', 1) or 1            # nanoseconds
toks = ec / (ed / 1e9)
vals = [int(m) for line in open(os.environ['TEG'])
        for m in re.findall(r'VDD_IN (\d+)mW', line)]
w = (sum(vals) / len(vals) / 1000) if vals else 0.0
print(json.dumps({
    "model": os.environ['MODEL'],
    "mode": os.environ.get('MODE', '?'),
    "gen_tokens": ec,
    "gen_tok_s": round(toks, 2),
    "avg_W": round(w, 2),
    "peak_W": round(max(vals) / 1000, 2) if vals else None,
    "tok_per_W": round(toks / w, 2) if w else None,
    "J_per_tok": round(w / toks, 3) if toks else None,
    "teg_samples": len(vals),
}))
PY
