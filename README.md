# Low Power Edge — Mars Decision Benchmark

An open benchmark for evaluating **small language models** on **space-mission survival and
engineering decisions** under hard physical constraint — built for the **low-power edge**
(e.g. an NVIDIA Jetson at 5–15 W).

It reports **two numbers together**: decision **accuracy** on physics-grounded scenarios, and
**tokens/sec per watt** on the actual board. The question it asks:

> A 70B model scored ~80% on space-mission decisions via cloud API within a 2-second budget.
> **What does a 2B model score on a 10-watt board?**

## Why this exists

Every LLM leaderboard benchmarks big models on big GPUs. Almost nobody rigorously measures the
**lowest-power edge** — tiny models on a tiny board at minimal watts — on **decisions that
matter where the cloud cannot reach** (deep space, off-grid, the field after a disaster).

A literature + repository search (June 2026) turned up **no public benchmark** for LLM
space / onboard-autonomy decision-making. The closest work,
[arXiv:2603.28926](https://arxiv.org/abs/2603.28926) ("A Computational Framework for
Cross-Domain Mission Design and Onboard Cognitive Decision Support"), describes the evaluation
methodology and reports results, but **does not release its test set, dataset, or code**. This
repo fills that gap with an openly published, reproducible benchmark.

It's also a sovereignty argument made concrete: **owned intelligence at watts you can actually
power** off a solar panel or a battery.

## What's in the box

- **`benchmark/mars_decision_v1.json`** — 10 discrete, physics-grounded scenarios, *The
  Martian*–flavored, across the domains named in 2603.28926 (RF/acoustic **link budgets**,
  Walker **coverage geometry**, **EKF** state estimation) plus Mars-survival engineering
  (power budget, life support, propulsion, thermal, EVA consumables, pressure integrity,
  ISRU agriculture). Each item carries a multiple-choice prompt, the correct `answer`, and the
  physics `rationale` (the answer key, so you can check our work).
- **`tools/measure_tok_per_watt.sh`** — the on-device measurement rig: a pinned generation
  regime, tokens/sec from the runtime, and average board power from Jetson `tegrastats`
  (`VDD_IN`, the total board input rail).

## Methodology

- **Quality.** Show the model the `prompt`, extract its single-letter choice, score against
  `answer`. Accuracy = correct / 10. Pinned regime (temperature 0, fixed `num_predict`).
- **Efficiency.** `tok/s-per-watt = (generation tokens/sec) / (avg VDD_IN watts)` — grounded in
  the two tools the edge community actually uses: runtime-reported tokens/sec (the
  llama.cpp / ollama convention) and Jetson `tegrastats` board power. No formal MLPerf
  "per-watt LLM" metric exists; this is defined here from those conventions.
- **Baseline.** 2603.28926 reports **~80%** decision accuracy by a 70B model
  (Llama-3.3-70B / DeepSeek-V3) via cloud API within a **2-second** latency budget. We report
  small-model accuracy + tok/s-per-watt against that ceiling.
- **Pre-registration.** The tests, answer keys, and baseline target are published **before**
  any contender is run — so the eval cannot be tuned to flatter a result. Contender results
  land in this repo afterward, in a separate commit.

## Honest caveats

- These scenarios **replicate the methodology** of 2603.28926; they are **not** that paper's
  exact (unpublished) items. Ground truth is derived from first-principles physics and
  peer-reviewed by the authors — every answer ships with its rationale so you can verify it.
- "Small" is real: ~2–4B edge-quantized is the practical ceiling on a 7–8 GB board.
- Correct-answer letters are spread (A×3, B×3, C×2, D×2) to defeat position-gaming.

## Status

**v1 — results in.** Gemma-4 E2B (DeepMind) vs Llama-3.2-3B (NVIDIA's recommended pick) vs
Nemotron-mini (NVIDIA's own), swept across Jetson power modes. See **[RESULTS.md](RESULTS.md)**.

> Headline: at **15 W**, Gemma-4 E2B makes **90%-accurate** space-survival decisions at
> ~18 tok/s drawing **8.8 watts** — ~60% more tokens-per-watt than the model NVIDIA
> recommends, and ~80% more than NVIDIA's own model, on NVIDIA's own board.

## License & citation

Code under MIT (`LICENSE`); benchmark data under CC-BY-4.0 — attribution appreciated, it's how
people find this. If you use it, please cite via `CITATION.cff`.

---

Built in public by the m5Max lab — small, owned, local models, measured honestly.
[mycelium.fyi](https://mycelium.fyi)
