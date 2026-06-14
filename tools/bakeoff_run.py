#!/usr/bin/env python3
"""bakeoff_run.py — run the Low Power Edge Mars benchmark for one Ollama model.

Runs ON the Jetson (reads tegrastats locally, queries localhost Ollama). Reports
decision ACCURACY on the benchmark + tok/s-PER-WATT at the current power mode.

  bakeoff_run.py <model> <benchmark.json>

Emits one JSON line: {model, mode, accuracy, accuracy_pct, gen_tok_s, avg_W,
tok_per_W, J_per_tok, detail:[{id,got,want,ok}]}.
"""
import json, sys, re, subprocess, urllib.request, time, os, tempfile

API = "http://localhost:11434/api/chat"
SYSTEM = None  # optional system prompt (set via --system); None = no system message (cold)


def gen(model, prompt, num_predict, temperature=0):
    # /api/chat applies the instruct template; think=False forces a DIRECT answer.
    # Gemma-4 is a thinking model — without this it spends the whole token budget on
    # reasoning that Ollama strips, returning EMPTY content. Pinned regime for all 3.
    messages = ([{"role": "system", "content": SYSTEM}] if SYSTEM else []) + \
               [{"role": "user", "content": prompt}]
    body = json.dumps({"model": model, "messages": messages,
                       "stream": False, "think": False,
                       "options": {"num_predict": num_predict, "temperature": temperature}}).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=180).read())


def content_of(r):
    return ((r.get("message") or {}).get("content") or "")


def extract_letter(text):
    t = (text or "").strip().upper()
    if not t:
        return None
    m = re.search(r'\b(?:ANSWER|CHOICE|OPTION|SELECT)\b[^A-Z]{0,12}([ABCD])\b', t)
    if m:
        return m.group(1)
    m = re.match(r'^[\s\W]*([ABCD])\b', t)         # leading "B" / "B." / "B)"
    if m:
        return m.group(1)
    ms = re.findall(r'\b([ABCD])\b', t)            # fallback: last standalone letter
    return ms[-1] if ms else None


def power_mode():
    try:
        out = subprocess.check_output(["nvpmodel", "-q"], text=True, stderr=subprocess.DEVNULL)
        for l in out.splitlines():
            if "Power Mode" in l:
                return l.split(":")[-1].strip()
    except Exception:
        pass
    return "?"


def measure_tok_per_watt(model):
    gen(model, "warm up", 8)                       # load model, exclude cold-start
    teg = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False); teg.close()
    p = subprocess.Popen(["tegrastats", "--interval", "200"],
                         stdout=open(teg.name, 'w'), stderr=subprocess.DEVNULL)
    r = gen(model, "Explain how a transistor works, in one paragraph.", 256)
    p.terminate(); time.sleep(0.3)
    ec = r.get('eval_count', 0); ed = r.get('eval_duration', 1) or 1
    toks = ec / (ed / 1e9)
    vals = [int(m) for line in open(teg.name) for m in re.findall(r'VDD_IN (\d+)mW', line)]
    os.unlink(teg.name)
    w = (sum(vals) / len(vals) / 1000) if vals else 0.0
    return {"gen_tok_s": round(toks, 2), "avg_W": round(w, 2),
            "peak_W": round(max(vals) / 1000, 2) if vals else None,
            "tok_per_W": round(toks / w, 2) if w else None,
            "J_per_tok": round(w / toks, 3) if toks else None}


def run_accuracy(model, items):
    correct = 0; detail = []
    for it in items:
        r = gen(model, it["prompt"], 64)
        got = extract_letter(content_of(r))
        ok = (got == it["answer"])
        correct += int(ok)
        detail.append({"id": it["id"], "got": got, "want": it["answer"], "ok": ok})
    return correct, len(items), detail


def main():
    global SYSTEM
    model, bench = sys.argv[1], sys.argv[2]
    if "--system" in sys.argv:
        SYSTEM = sys.argv[sys.argv.index("--system") + 1]
    mode = power_mode()
    if "--measure-only" in sys.argv:   # power-mode sweep: tok/s-per-watt only (accuracy is mode-independent)
        print(json.dumps({"model": model, "mode": mode, **measure_tok_per_watt(model)}))
        return
    eff = {} if "--accuracy-only" in sys.argv else measure_tok_per_watt(model)
    items = json.load(open(bench))["items"]
    correct, total, detail = run_accuracy(model, items)
    out = {"model": model, "mode": mode, "system_prompt": bool(SYSTEM),
           "accuracy": f"{correct}/{total}", "accuracy_pct": round(100 * correct / total, 1)}
    out.update(eff)
    out["detail"] = detail
    print(json.dumps(out))


if __name__ == "__main__":
    main()
