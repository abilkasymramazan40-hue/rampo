"""Own tests: brute-force oracles written independently of the solution.
Run from repo root:  python tests/student/test_student.py
"""
import itertools, json, os, random, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Python", "source"))
import algorithms as A

fails = 0
def check(name, cond):
    global fails
    if not cond:
        fails += 1
        print("FAIL", name)

def is_subseq(s, t):
    it = iter(t)
    return all(c in it for c in s)

def lcs_oracle(a, b):
    best = 0
    for mask in range(1 << len(a)):
        s = "".join(a[i] for i in range(len(a)) if mask >> i & 1)
        if len(s) > best and is_subseq(s, b):
            best = len(s)
    return best

def find_all(t, p):
    return [i for i in range(len(t) + 1) if t.startswith(p, i)]

def merge_oracle(sizes):
    from functools import lru_cache
    @lru_cache(None)
    def f(t):
        if len(t) <= 1: return 0
        return min(t[i] + t[i + 1] + f(t[:i] + (t[i] + t[i + 1],) + t[i + 2:]) for i in range(len(t) - 1))
    return f(tuple(sizes))

def check_plan(sizes, res):
    blocks = {(i, i): sizes[i] for i in range(len(sizes))}
    total = 0
    for l, k, r in res["plan"]:
        assert (l, k) in blocks and (k + 1, r) in blocks, "non-adjacent / not chronological"
        c = blocks.pop((l, k)) + blocks.pop((k + 1, r))
        total += c
        blocks[(l, r)] = c
    return total == res["cost"] and len(res["plan"]) == max(0, len(sizes) - 1)

def mwis_oracle(w, edges):
    n = len(w); best = 0
    for mask in range(1 << n):
        if all(not (mask >> u & 1 and mask >> v & 1) for u, v in edges):
            best = max(best, sum(w[i] for i in range(n) if mask >> i & 1))
    return best

rnd = random.Random(12345)

#LCS
for a, b in [("", ""), ("abc", ""), ("", "abc"), ("tea_time", "team"), ("aaaa", "aa"), ("abc", "cba")]:
    r = A.lcs({"a": a, "b": b})
    check(f"lcs {a!r},{b!r}", r["length"] == lcs_oracle(a, b) == len(r["sequence"]) and is_subseq(r["sequence"], a) and is_subseq(r["sequence"], b))
for _ in range(300):
    a = "".join(rnd.choice("abc") for _ in range(rnd.randint(0, 9)))
    b = "".join(rnd.choice("abc") for _ in range(rnd.randint(0, 9)))
    r = A.lcs({"a": a, "b": b})
    check(f"lcs rnd {a},{b}", r["length"] == lcs_oracle(a, b) == len(r["sequence"]) and is_subseq(r["sequence"], a) and is_subseq(r["sequence"], b))
r = A.lcs({"a": "x" * 1000, "b": "x" * 1000}); check("lcs 1000x1000", r["length"] == 1000)

#merge
check("merge []", A.merge({"sizes": []}) == {"cost": 0, "plan": []})
check("merge [5]", A.merge({"sizes": [5]}) == {"cost": 0, "plan": []})
check("merge example", A.merge({"sizes": [2, 3, 4]})["cost"] == 14)
for _ in range(300):
    s = [rnd.choice([0, 0, 1, 2, 5, 9]) for _ in range(rnd.randint(0, 7))]
    r = A.merge({"sizes": s})
    check(f"merge rnd {s}", r["cost"] == merge_oracle(s) and check_plan(s, r))
big = [10**9] * 200; r = A.merge({"sizes": big}); check("merge 200 big", check_plan(big, r) and r["cost"] > 2**31)

#tree
check("tree empty", A.tree({"n": 0, "weights": [], "edges": []}) == {"weight": 0, "selected": []})
check("tree one neg", A.tree({"n": 1, "weights": [-3], "edges": []})["weight"] == 0)
check("tree one pos", A.tree({"n": 1, "weights": [3], "edges": []}) == {"weight": 3, "selected": [0]})
for _ in range(300):
    n = rnd.randint(1, 10)
    edges = [[rnd.randrange(i), i] for i in range(1, n)]
    perm = list(range(n)); rnd.shuffle(perm)
    edges = [[perm[u], perm[v]] for u, v in edges]
    w = [rnd.randint(-5, 9) for _ in range(n)]
    r = A.tree({"n": n, "weights": w, "edges": edges})
    sel = set(r["selected"])
    ok = len(sel) == len(r["selected"]) and all(not (u in sel and v in sel) for u, v in edges)
    check(f"tree rnd {w} {edges}", ok and sum(w[v] for v in sel) == r["weight"] == mwis_oracle(w, edges))
n = 100000  # deep chain, big sum
r = A.tree({"n": n, "weights": [10**9] * n, "edges": [[i, i + 1] for i in range(n - 1)]})
check("tree chain 1e5", r["weight"] == 50000 * 10**9 and len(r["selected"]) == 50000)

#searches
cases = [("", ""), ("abc", ""), ("", "a"), ("aaaaa", "aaa"), ("abababa", "aba"), ("ab", "abc"),
         ("Hello, World! hello", "hello"), ("a b  c", " "), ("abdj", "ab"), ("abdj", "dj")]
for t, p in cases:
    exp = find_all(t, p)
    for f in (A.naive, A.kmp, A.rk):
        check(f"{f.__name__} {t!r},{p!r}", f({"text": t, "pattern": p})["positions"] == exp)
for _ in range(1000):
    t = "".join(rnd.choice("ab") for _ in range(rnd.randint(0, 25)))
    p = "".join(rnd.choice("ab") for _ in range(rnd.randint(0, 5)))
    exp = find_all(t, p)
    for f in (A.naive, A.kmp, A.rk):
        check(f"{f.__name__} rnd {t},{p}", f({"text": t, "pattern": p})["positions"] == exp)

h = lambda s: __import__("functools").reduce(lambda x, c: (x * 31 + ord(c)) % 101, s, 0)
check("rk collision hash", h("ab") == h("dj") == 75)
# negative remainder: window drop where ht - ord*high < 0
t = "z" + "a" * 30 + "b" * 30
check("rk negative remainder", A.rk({"text": t, "pattern": "ab"})["positions"] == find_all(t, "ab"))

#suffix
def suffix_oracle(s):
    sa = sorted(range(len(s)), key=lambda i: s[i:])
    def lc(a, b):
        k = 0
        while a + k < len(s) and b + k < len(s) and s[a + k] == s[b + k]: k += 1
        return k
    return sa, [0] + [lc(sa[i - 1], sa[i]) for i in range(1, len(sa))]
check("suffix empty", A.suffix({"text": ""}) == {"sa": [], "lcp": [], "repeated": ""})
check("suffix banana", A.suffix({"text": "banana"}) == {"sa": [5, 3, 1, 0, 4, 2], "lcp": [0, 1, 3, 0, 0, 2], "repeated": "ana"})
for s in ["a", "aaaa", "abcd", "abab", "mississippi", "  ~~", "AaAa"]:
    sa, lcp = suffix_oracle(s); r = A.suffix({"text": s})
    check(f"suffix {s!r}", r["sa"] == sa and r["lcp"] == lcp and len(r["repeated"]) == max(lcp))
for _ in range(500):
    s = "".join(rnd.choice("ab c") for _ in range(rnd.randint(1, 20)))
    sa, lcp = suffix_oracle(s); r = A.suffix({"text": s})
    rep = r["repeated"]
    check(f"suffix rnd {s!r}", r["sa"] == sa and r["lcp"] == lcp and len(rep) == max(lcp)
          and (rep == "" or s.count(rep) >= 1 and len(find_all(s, rep)) >= 2))
s = "a" * 50000; r = A.suffix({"text": s}); check("suffix 50000 equal", r["sa"][0] == 49999 and r["repeated"] == "a" * 49999)

#aho
def aho_oracle(pats, texts):
    return [[sum(1 for i in range(len(t)) if t.startswith(p, i)) for p in pats] for t in texts]
check("aho example", A.aho({"patterns": ["he", "she", "he"], "texts": ["sheshe", "sheshe", ""]})["counts"] == [[2, 2, 2], [2, 2, 2], [0, 0, 0]])
check("aho empty dict", A.aho({"patterns": [], "texts": ["ab", ""]})["counts"] == [[], []])
check("aho no texts", A.aho({"patterns": ["a"], "texts": []})["counts"] == [])
for _ in range(500):
    pats = ["".join(rnd.choice("ab") for _ in range(rnd.randint(1, 4))) for _ in range(rnd.randint(0, 6))]
    texts = ["".join(rnd.choice("ab") for _ in range(rnd.randint(0, 15))) for _ in range(rnd.randint(0, 4))]
    check(f"aho rnd {pats} {texts}", A.aho({"patterns": pats, "texts": texts})["counts"] == aho_oracle(pats, texts))

#scale (time) tests
def timed(name, f, req, limit=20):
    t0 = time.time(); r = f(req); dt = time.time() - t0
    print(f"  scale {name}: {dt:.2f}s"); check(f"{name} under {limit}s", dt < limit); return r
r = timed("kmp 200000/100000", A.kmp, {"text": "a" * 200000, "pattern": "a" * 100000})
check("kmp dense count", len(r["positions"]) == 100001)
r = timed("rk 10000x2000 all a", A.rk, {"text": "a" * 10000, "pattern": "a" * 2000})
check("rk dense count", len(r["positions"]) == 8001)
timed("naive 3000/1500 worst", A.naive, {"text": "a" * 3000, "pattern": "a" * 1499 + "b"})
# aho dense: patterns a, aa, aaa, ... total length 100000 -> 446 patterns; plus many duplicates
pats = ["a" * i for i in range(1, 447)]
r = timed("aho dense", A.aho, {"patterns": pats, "texts": ["a" * 2000] * 100})
check("aho dense value", r["counts"][0][0] == 2000 and r["counts"][0][445] == 2000 - 445)
pats = ["".join(rnd.choice("abcdefghij") for _ in range(10)) for _ in range(10000)]
timed("aho 10000 pats", A.aho, {"patterns": pats, "texts": ["".join(rnd.choice("abcdefghij") for _ in range(2000)) for _ in range(100)]})

#stale-state test through the real JSONL process
reqs = [{"task": "aho", "patterns": ["a"], "texts": ["aaa"]}, {"task": "lcs", "a": "ab", "b": "ba"},
        {"task": "aho", "patterns": ["b"], "texts": ["aaa"]}, {"task": "suffix", "text": "aa"},
        {"task": "tree", "n": 0, "weights": [], "edges": []}, {"task": "rk", "text": "abdj", "pattern": "dj"}]
out = subprocess.run([sys.executable, os.path.join(ROOT, "Python", "source", "main.py")], input="\n".join(map(json.dumps, reqs)) + "\n",
                     capture_output=True, text=True, cwd=os.path.join(ROOT, "Python", "source")).stdout.splitlines()
check("jsonl line count", len(out) == len(reqs))
check("jsonl no stale aho", json.loads(out[2]) == {"counts": [[0]]} and json.loads(out[0]) == {"counts": [[3]]})
check("jsonl rk dj", json.loads(out[5]) == {"positions": [2]})

print("ALL PASSED" if fails == 0 else f"{fails} FAILURES")
sys.exit(1 if fails else 0)
