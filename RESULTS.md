# Results — v1 (2026-06-14)

Three contenders × three power modes on an **NVIDIA Jetson Orin Nano Super (8 GB)**,
served by **Ollama**, in a pinned **direct-answer regime** (`think: false`,
temperature 0). Decision accuracy is on the 10-scenario `mars_decision_v1` benchmark
and is **mode-independent** at temperature 0 (deterministic). `tok/s-per-watt` =
generation tokens/sec ÷ average board power (`tegrastats` `VDD_IN`).

## Contenders

| Model | Size (4-bit) | Provenance |
|---|---|---|
| `gemma4:e2b-it-qat` | 4.3 GB | **Google DeepMind** |
| `llama3.2:3b` | 2.0 GB | Meta — **the model NVIDIA recommends** for this board |
| `nemotron-mini` (4B) | 2.7 GB | **NVIDIA's own** |

## Decision accuracy (mode-independent)

| Model | Accuracy |
|---|---|
| Llama-3.2-3B | **10 / 10 (100%)** |
| Gemma-4 E2B | **9 / 10 (90%)** |
| Nemotron-mini | 5 / 10 (50%) |

Reference baseline: arXiv:2603.28926 reports **~80%** by a **70B** model
(Llama-3.3-70B / DeepSeek-V3) via **cloud API** in a 2 s latency budget. Our small
models run **on an 8 GB board at ≤17 W**.

## Efficiency — the tok/s-per-watt curve

Each cell: **tok/s · avg watts · tok/s-per-watt**.

| Model | 15W mode | 25W mode | MAXN_SUPER |
|---|---|---|---|
| **Gemma-4 E2B** | 17.9 · 8.8 · **2.04** | 24.9 · 11.4 · **2.18** | 26.1 · 12.0 · **2.17** |
| Llama-3.2-3B | 13.6 · 10.6 · 1.28 | 19.5 · 15.1 · 1.30 | 20.9 · 16.3 · 1.28 |
| Nemotron-mini | 12.3 · 10.8 · 1.15 | 17.6 · 15.5 · 1.13 | 18.9 · 17.0 · 1.11 |

## Findings

1. **Gemma-4 E2B is the efficiency winner at every power mode** — ~2.1 tok/s-per-watt,
   ~60% more than Llama-3.2-3B and ~85% more than Nemotron-mini — *and* it draws the
   least power, at 90% accuracy. At the 15 W mode it makes 90%-accurate decisions at
   ~18 tok/s drawing **8.8 watts**.
2. **Llama-3.2-3B — NVIDIA's recommended model — wins accuracy (100%)** but costs ~40%
   more energy per token.
3. **Nemotron-mini — NVIDIA's own model — trails on both** (50%, and the per-item detail
   shows a strong A-bias on the harder C/D items; least efficient).
4. **tok/s-per-watt is ~constant per model across power modes** — efficiency is a model
   property, not a power-mode artifact. MAXN_SUPER barely beats 25 W (diminishing
   returns); **15 W is the low-power sweet spot** (lowest absolute draw at ~85% of peak
   speed).

## Honest caveats

- **Runtime**: Ollama (llama.cpp under the hood), *not* TensorRT-LLM/MLC. NVIDIA's own
  published Orin Nano tok/s are higher because of their optimized stack; the **per-watt
  comparison here is internally consistent** (identical stack + board for all three).
- **Regime**: direct-answer (`think: false`) for parity — Gemma-4 is a *thinking* model;
  its chain-of-thought mode is untested here and may score differently.
- **Benchmark**: replicates the *methodology* of arXiv:2603.28926, not its exact
  (unpublished) items. n = 10 scenarios in v1; ground truth peer-reviewed.
- **Determinism**: temperature 0, single run.

Reproduce: `tools/bakeoff_run.py <model> benchmark/mars_decision_v1.json` on the Jetson
(accuracy + tok/s-per-watt); add `--measure-only` for the power-mode sweep.
