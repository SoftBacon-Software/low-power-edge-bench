# Results — v2 (2026-06-14)

Three contenders on an **NVIDIA Jetson Orin Nano Super (8 GB)**, served by **Ollama**,
pinned **direct-answer regime** (`think: false`, temperature 0). Benchmark:
`autonomy_decision_v2` (20 scenarios mirroring the 9 publicly-stated analysis domains of
arXiv:2603.28926). Two metrics, reported as **separate standardized workloads**:

- **Decision accuracy** on the 20 benchmark items, in **two system-prompt conditions**:
  *cold* (no system prompt) and *primed* (one identical expert system prompt for all three).
- **Efficiency** — `tok/s-per-watt` — measured on a **standardized 256-token generation
  prompt** (not the benchmark items), board power from `tegrastats` `VDD_IN`, swept across
  power modes. (These are deliberately separate workloads; accuracy and efficiency are not
  measured on the same generation.)

## Contenders

| Model | Size (4-bit) | Provenance |
|---|---|---|
| `gemma4:e2b-it-qat` | 4.3 GB | **Google DeepMind** |
| `llama3.2:3b` | 2.0 GB | Meta — **the model NVIDIA recommends** for this board |
| `nemotron-mini` (4B / ~2.6B eff.) | 2.7 GB | **NVIDIA's own** |

## Decision accuracy (n = 20) — and it is prompt-sensitive

| Model | Cold (no system prompt) | Primed (expert system prompt) |
|---|---|---|
| Gemma-4 E2B | 90% (18/20) | **95% (19/20)** |
| Llama-3.2-3B | **100% (20/20)** | 90% (18/20) |
| Nemotron-mini | 45% (9/20) | 70% (14/20) |

**The system prompt flips the ranking.** Cold: Llama > Gemma. Primed: Gemma > Llama. The
expert prompt *helped* the weaker models (Nemotron +25 points, Gemma +5) but *hurt* the
strongest (Llama −10 — the framing changed two correct answers). So on accuracy,
**Gemma-4 E2B and Llama-3.2-3B are a statistical tie** (both ~90–100%; which leads depends
on the prompt — not separable at n = 20), while **Nemotron-mini clearly trails in both
conditions** (45–70%). Treat accuracy as *indicative*, not a precise ranking.

## Efficiency — the robust result

Standardized 256-token generation, swept across power modes. Each cell: **tok/s · avg W · tok/s-per-watt**.

| Model | 15W mode | 25W mode | MAXN_SUPER |
|---|---|---|---|
| **Gemma-4 E2B** | 17.9 · 8.8 · **2.04** | 24.9 · 11.4 · **2.18** | 26.1 · 12.0 · **2.17** |
| Llama-3.2-3B | 13.6 · 10.6 · 1.28 | 19.5 · 15.1 · 1.30 | 20.9 · 16.3 · 1.28 |
| Nemotron-mini | 12.3 · 10.8 · 1.15 | 17.6 · 15.5 · 1.13 | 18.9 · 17.0 · 1.11 |

**Gemma-4 E2B delivers 1.6–1.7× the tokens-per-watt of Llama-3.2-3B and ~1.8–1.9× that of
Nemotron-mini — at every power mode**, while drawing the least absolute power (8.8 W at the
15 W setting). Unlike accuracy, this is **prompt-independent and mode-independent** — it's a
property of the model, and it's the result that survives a hostile read.

## Findings

1. **Efficiency is the headline (robust): Gemma-4 E2B is ~1.6–1.9× more tokens-per-watt**
   than either NVIDIA-side model, across all three power modes, drawing the least power.
2. **Accuracy is a Gemma/Llama tie that the prompt decides** (both ~90–100%); Nemotron-mini
   trails (45–70%). Prompt-sensitivity is itself model-dependent — priming helped the weak
   models and hurt the strong one.
3. **tok/s-per-watt is ~constant across power modes**; MAXN barely beats 25 W; **15 W is the
   low-power sweet spot** (lowest draw at ~85% of peak speed).

## Baseline (reference only — NOT a head-to-head)

arXiv:2603.28926 reports its **best of three frontier models (Llama-3.3-70B) at ~80%** on its
own **unpublished, 10-item, multi-sampled** scenarios. This is **not directly comparable** to
our numbers (different items, different sampling, different domains, n = 20) — it's a
reference ceiling for the task family, not a head-to-head.

## Honest caveats

- **Runtime**: Ollama (llama.cpp), not TensorRT-LLM/MLC — NVIDIA's published Orin Nano tok/s
  are higher on their optimized stack; the per-watt comparison here is internally consistent
  (identical stack + board for all three).
- **Regime**: direct-answer (`think: false`); Gemma-4 is a thinking model whose CoT mode is
  not tested here. All three models had **empty default system prompts**, so both conditions
  are genuinely identical treatment.
- **Benchmark**: *mirrors the methodology and domain scope* of arXiv:2603.28926; it is not the
  paper's (unpublished) items. Ground truth peer-reviewed and adversarially audited; raw
  per-item outputs in `results/v2_runs.jsonl`.
- **Statistics**: n = 20, deterministic single run per condition. A single item is ±5 points;
  do not read a precise ranking into the Gemma/Llama accuracy gap.

Reproduce: `tools/bakeoff_run.py <model> benchmark/autonomy_decision_v2.json --accuracy-only`
(add `--system "<prompt>"` for the primed condition; `--measure-only` for the power sweep).
