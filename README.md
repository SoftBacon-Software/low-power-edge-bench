# Low Power Edge Benchmark

An open benchmark for evaluating **small language models** on **autonomous-systems and
space-mission decisions** under hard physical constraint — built for the **low-power edge**
(e.g. an NVIDIA Jetson at 5–15 W).

It reports two things as **separate standardized workloads**: decision **accuracy** on
physics-grounded scenarios, and **tokens/sec per watt** on the actual board. The question:

> On a $250 8 GB board, which small model makes the **most decisions per watt** — and does it
> hold up against the model NVIDIA recommends, and NVIDIA's own?

## Why this exists

Every LLM leaderboard benchmarks big models on big GPUs. Almost nobody measures the
**lowest-power edge** on **decisions that matter where the cloud can't reach** (deep space,
off-grid, the field after a disaster). We found **no public benchmark** for it. The closest
work, [arXiv:2603.28926](https://arxiv.org/abs/2603.28926), scores LLMs on cross-domain
mission-autonomy decisions (its **best of three 70B-class models, Llama-3.3-70B, reaches
~80%** via cloud API) — but **does not release its test set**. This repo fills that gap with
an openly published, reproducible benchmark, plus the per-watt measurement the literature
hasn't reported.

It's also the sovereignty thesis made concrete: **owned intelligence at watts you can
actually power** off a solar panel or a battery.

## What's in the box

- **`benchmark/autonomy_decision_v2.json`** — **20 physics-grounded scenarios** mirroring the
  **nine publicly-stated analysis domains** of arXiv:2603.28926 (Walker constellation
  coverage; infrared Neyman-Pearson detection; EKF tracking; RF + acoustic link budgets; TDMA
  inter-satellite protocols; power-budget sizing; magnetic-signature formation; Arrhenius
  cryogenic reliability) across its mission settings (LEO surveillance, Mars nav, underwater
  swarms, deep-space relays, outer-planet probes). Each item: a multiple-choice prompt, the
  correct answer, and the physics rationale. (`benchmark/mars_decision_v1.json` is the
  retired v1.)
- **`tools/bakeoff_run.py`** — the runner: decision accuracy (with/without a system prompt)
  + tok/s-per-watt.
- **`tools/measure_tok_per_watt.sh`** — standalone efficiency rig (`tegrastats` `VDD_IN`).
- **`RESULTS.md`** + **`results/v2_runs.jsonl`** — the v2 results and raw per-item outputs.

## Methodology

- **Quality.** Show the model `prompt`, extract its single letter, score against `answer`.
  Run in two system-prompt conditions — *cold* (none) and *primed* (one identical expert
  prompt for all). Pinned regime (temp 0, `think:false`).
- **Efficiency.** `tok/s-per-watt` on a **standardized 256-token generation prompt** (a
  separate workload from the accuracy task), board power from Jetson `tegrastats`, swept
  across power modes. Grounded in the tools the edge community uses (llama.cpp-style tok/s +
  `tegrastats`); no formal MLPerf per-watt LLM metric exists.
- **Provenance.** Answer keys + methodology were **committed before any contender ran**
  (verifiable in git history) and **adversarially audited** by a separate model. Mirrors the
  paper's domain scope and evaluation structure — **not** its (unpublished) items.

## Results (v2)

On a Jetson Orin Nano Super (8 GB): **Gemma-4 E2B (DeepMind)** vs **Llama-3.2-3B (NVIDIA's
recommended)** vs **Nemotron-mini (NVIDIA's own)**.

> **Efficiency (robust): Gemma-4 E2B delivers ~1.6–1.9× the tokens-per-watt of either
> NVIDIA-side model, at every power mode, drawing the least power (8.8 W at 15 W).**
>
> **Accuracy (prompt-sensitive): Gemma-4 E2B and Llama-3.2-3B tie (~90–100%; the system
> prompt flips which leads); Nemotron-mini trails (45–70%).**

See **[RESULTS.md](RESULTS.md)**. The efficiency result is prompt- and mode-independent; the
accuracy gap between the top two is not — don't read a precise ranking into n = 20.

## License & citation

Code MIT (`LICENSE`); benchmark data CC-BY-4.0. Cite via `CITATION.cff`.

---

Built in public by the m5Max lab — small, owned, local models, measured honestly.
[mycelium.fyi](https://mycelium.fyi)
