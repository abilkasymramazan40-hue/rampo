"""Benchmark naive/KMP/RK. Run from repo root: python tests/student/benchmark.py
Timing scope: only the algorithm function call (A.naive/A.kmp/A.rk) on an in-memory request,
measured with time.perf_counter_ns; no JSON parsing, no process start. One untimed warm-up call
per algorithm/case, then 3 timed runs. Same request objects are used for all three algorithms.
"""
import os, random, statistics, sys, time, platform
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Python", "source"))
import algorithms as A

def gen_random(n, m, seed):
    r = random.Random(seed)
    text = "".join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n))
    st = r.randrange(n - m + 1)
    return text, text[st:st + m]

def gen_repetitive(n, m, seed):
    return "a" * n, "a" * (m - 1) + "b"

print("python", platform.python_version(), platform.platform(), platform.machine())
print("case,n,m,seed/generator,algorithm,run1_ms,run2_ms,run3_ms,median_ms,positions")
for case, gen in (("random", gen_random), ("repetitive", gen_repetitive)):
    for n, m in ((500, 50), (1500, 150), (3000, 300)):
        seed = 2026
        text, pat = gen(n, m, seed)
        req = {"text": text, "pattern": pat}
        outs = {}
        for name in ("naive", "kmp", "rk"):
            f = getattr(A, name)
            f(req) 
            times = []
            for _ in range(3):
                t0 = time.perf_counter_ns(); out = f(req); times.append((time.perf_counter_ns() - t0) / 1e6)
            outs[name] = out["positions"]
            print(f"{case},{n},{m},{'seed '+str(seed) if case=='random' else 'a^n / a^(m-1)b'},{name},"
                  + ",".join(f"{x:.3f}" for x in times) + f",{statistics.median(times):.3f},{len(out['positions'])}")
        agree = outs["naive"] == outs["kmp"] == outs["rk"]
        print(f"# {case} n={n} m={m} outputs identical across naive/kmp/rk: {agree}")
