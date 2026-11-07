# Assignment 4 — analysis

## Environment and commands

- Language/runtime: **Python 3.12.3** (`submission.json`: `"language": "Python"`).
- Measurement machine: Linux x86_64 (VM), Intel Xeon @ 2.10 GHz, 1 CPU, ~4 GB RAM.
- Setup/build: `python tools/run.py --setup` (Python has no compile step; this checks startup).
- Public checks: `python tools/run.py --check` (44 public cases + repeated mixed batch: all PASS).
- Own tests: `python tests/student/test_student.py` (prints `ALL PASSED`).
- Benchmark: `python tests/student/benchmark.py > tests/student/benchmark_output.txt`.
- Final commit URL: submitted in Moodle (not stored in this file).

## Algorithm explanations

### lcs
- **State:** `dp[i][j]` = length of an LCS of prefixes `a[:i]` and `b[:j]`; `i` in 0..|a|, `j` in 0..|b|.
- **Base:** `dp[0][j] = dp[i][0] = 0` (empty prefix). Empty input returns `length=0, sequence=""` directly.
- **Transition:** if `a[i-1]==b[j-1]` then `dp[i-1][j-1]+1`, else `max(dp[i-1][j], dp[i][j-1])`.
- **Order:** rows top to bottom, columns left to right; all three cells used (up, left, diagonal) are already computed.
- **Correctness:** on a match, some optimal LCS can end with that character (taking it never hurts); on a mismatch at least one of the two last characters is unused, so the answer is the max of dropping either.
- **Reconstruction/ties:** walk from `(|a|,|b|)`: match -> emit char and go diagonally; else go to the larger neighbour (tie -> up). Reverse the collected characters. Different tie rules give different but equally long LCS (accepted).
- **Complexity:** O(|a|·|b|) time, O((|a|+1)(|b|+1)) memory (full table, needed for reconstruction); output O(length).
- **Boundary test:** `a="tea_time", b="team"` -> `team` (a subsequence, not a substring); catches solutions that compute longest common *substring*. Empty strings catch index errors.

### merge
- **State:** `dp[l][r]` = minimum cost to merge original blocks `l..r` into one block; `split[l][r]` = best last split `k` (final merge is `[l,k]` + `[k+1,r]`).
- **Base:** `dp[i][i]=0`. For n≤1: cost 0, plan `[]`.
- **Transition:** `dp[l][r] = min_{l<=k<r} dp[l][k] + dp[k+1][r] + sum(sizes[l..r])`, sum from prefix sums.
- **Order:** by increasing interval length, so both sub-intervals (shorter) are ready.
- **Correctness:** the last merge of any plan for `l..r` joins two adjacent intervals that were each merged optimally and independently, hence the formula (optimal substructure).
- **Reconstruction:** post-order over the `split` tree (iterative stack): child merges are appended before the parent merge, so the plan is chronological and has n-1 entries `[l,k,r]`. Ties: first smallest `k`.
- **Complexity:** O(n^3) time, O(n^2) memory (`dp`, `split`); n ≤ 200. Python ints avoid overflow for costs up to ~2·10^11·…
- **Boundary test:** `[2,3,4]` -> cost 14 (not 16); catches greedy "merge smallest" / wrong split. `[10^9]*200` checks large totals; zeros check ties.

### tree
- **State:** `take[v]` = best weight in subtree of v if v is chosen; `skip[v]` = best if v is not chosen.
- **Base:** leaf: `take=w[v]`, `skip=0`.
- **Transition:** `take[v] = w[v] + sum skip[c]`; `skip[v] = sum max(take[c], skip[c])`.
- **Order:** BFS order from root 0, then process vertices in reverse BFS order (children before parents). No recursion, so a chain of 100000 vertices is safe.
- **Correctness:** subtrees of different children are independent once v's status is fixed; if v is chosen, children must be skipped.
- **Reconstruction:** go in BFS order (parents first): if the parent was chosen, skip v; otherwise choose v iff `take[v] > skip[v]`. The empty set is allowed since `skip>=0` (all-negative -> weight 0). Ties prefer skipping.
- **Complexity:** O(n) time and auxiliary memory (adjacency lists, arrays); n=0 is O(1).
- **Boundary test:** all-negative weights and `n=0/1`; deep chain of 10^5 with weights 10^9 (sum 5·10^13) detects recursion overflow and 32-bit overflow.

### naive
- **Invariant:** for start `i`, the first `j` characters of the pattern equal `text[i..i+j-1]`.
- **Base:** `m=0` -> all boundaries `0..n`; `m>n` -> `[]` (loop range is empty).
- **Order:** starts `i=0..n-m` increasing, so the output is strictly increasing and includes overlaps.
- **Correctness:** every possible start is tested by direct comparison.
- **Complexity:** O(n·m) time worst case, O(1) auxiliary memory, O(z) output (n+1 for empty pattern).
- **Boundary test:** `aaaaa`/`aaa` -> `[0,1,2]` (last valid start `n-m`, overlaps); empty pattern -> n+1 positions.

### kmp
- **State:** `pi[i]` = length of the longest proper prefix of `p[:i+1]` that is also its suffix; `k` = current matched length.
- **Transition:** on mismatch `k = pi[k-1]` until match or `k=0`; on match `k+=1`. **After a full match (`k==m`)** the next step falls back with `k=pi[m-1]`, which keeps overlapping matches.
- **Order:** text left to right, each character once; pattern prefix function built the same way.
- **Correctness:** `pi` lists all borders of the matched prefix, so no possible start is skipped.
- **Complexity:** O(n+m+z) time (amortized: `k` increases at most n times, so falls ≤ n), O(m) auxiliary memory, O(z) output.
- **Boundary test:** `abababa`/`aba` -> `[0,2,4]` detects missing fallback after a full match. Empty pattern is handled before indexing.

### rk
- **Hash:** base 31, modulus 101, ASCII codes, leftmost character has the highest power: `H(s)=sum ord(s[i])·31^(m-1-i) mod 101`.
- **Rolling update:** `H' = ((H - ord(t[i])·31^(m-1))·31 + ord(t[i+m])) mod 101`. Python's `%` is always non-negative, so negative remainders are normalised (in C/Java add the modulus).
- **Verification:** equal hashes only create a candidate; the characters are compared one by one before reporting. Example: `ab` and `dj` both hash to 75, so `dj` is a false candidate in `abdj` for pattern `ab`.
- **Base cases:** `m=0` -> `0..n`; `m>n` -> `[]` before building a window.
- **Complexity:** O(n+m+c·m) where c = number of equal-hash candidate windows. With modulus 101 collisions are frequent, so in the worst case it is O(n·m); no linear worst-case claim. Auxiliary memory O(1) + output.
- **Boundary test:** `abdj` with `ab` and with `dj` (collision must be rejected / found at the right position); text `z + a*30 + b*30` exercises negative intermediate values.

### suffix
- **Prefix doubling:** after round `k`, `rank[i]` is the rank of the first `2k` characters of suffix `i` (pair `(rank[i], rank[i+k] or -1)` encoded as one integer key). Start with ranks = ASCII codes, k=1, double each round; stop when all ranks are distinct (or `k>=n`). Suffixes are never materialised as strings.
- **Complexity of construction:** each round is a comparison sort -> O(n log n), up to log n rounds -> O(n log^2 n); memory O(n).
- **Kasai:** `lcp[rank[i]]` = LCP of suffix `i` with the previous suffix in SA. Keep `h`; after computing it for `i`, the next suffix `i+1` has LCP ≥ `h-1`, so `h` decreases by at most 1 per step and increases at most 2n times in total -> O(n). `lcp[0]=0`.
- **Repeated substring:** the longest repeat equals the max adjacent LCP (any repeated substring is a common prefix of two suffixes, and the best pair is adjacent in sorted order). Output `text[sa[pos]: sa[pos]+max(lcp)]`; `""` if max is 0. Overlaps allowed (`banana` -> `ana`). Ties: first maximum.
- **Boundary test:** `""` -> empty arrays; `a*50000` (all equal, `sa` descending, max lcp 49999, 16 rounds); no sentinel used. Compared with `sorted(range(n), key=lambda i: s[i:])` on random strings over alphabet `ab c`.

### aho
- **Trie/automaton:** each pattern is inserted into a trie; `term[state]` stores all dictionary positions ending there, so duplicate patterns share a state and each gets its own column.
- **Failure links:** BFS; `fail[u]` for child `u` of `v` via `c` = state reached by following `fail[v]` chain until a state with edge `c` (else root). Dictionary-based edges + following fail links while querying (amortised O(|text|)).
- **Counting:** during the scan only `cnt[state] += 1` is done. Afterwards states are processed in reverse BFS order and `cnt[fail[v]] += cnt[v]` (reverse-failure propagation), so a pattern that is a suffix of a longer matched pattern (e.g. `he` in `she`) is counted without per-match traversal. Then `row[idx] = cnt[terminal state]` for every duplicate index.
- **Reset:** `cnt` and `row` are created fresh per text; the automaton is built per request, so no state survives between requests or texts.
- **Complexity:** build O(L+S+p) (dict edges, instead of 95·S table); per text O(|text|+S+p); memory O(S+p) plus output O(q·p).
- **Boundary test:** `["he","she","he"]` on `sheshe` -> `[2,2,2]` (suffix pattern + duplicate); empty dictionary -> empty rows; patterns `a, aa, …, a^446` on `a^2000` (dense matches) -> completes in a few ms, detects per-match traversal blow-up.

## Own tests

All tests are in `tests/student/test_student.py`; small inputs are compared with brute-force oracles written independently (exhaustive subsequence search, memoised merge search, exhaustive independent sets, `startswith`, `sorted(key=suffix)`, direct counting).

| Command | Input or fixture path | Expected result | Actual result / log | What it checks |
|---|---|---|---|---|
| `python tools/run.py --check` | `tests/public.json` (44 cases + repeated batch) | all PASS | all PASS | public contract, mixed tasks, state reset |
| `python tests/student/test_student.py` | LCS: empty/empty, one empty, `tea_time`/`team`, 300 random pairs | length = brute force, sequence is subsequence of both | `ALL PASSED` | recurrence, subsequence-vs-substring, reconstruction |
| same | merge: `[]`, `[5]`, `[2,3,4]`, 300 random with zeros, `[10^9]*200` | cost = memoised brute force; plan chronological, adjacent, n-1 steps | `ALL PASSED` | adjacency, plan order, big sums |
| same | tree: `n=0`, `n=1` negative/positive, 300 random trees (shuffled labels), chain n=100000 | weight = exhaustive optimum, no adjacent/duplicate vertices, chain weight 5·10^13 | `ALL PASSED` | take/skip, negatives, deep recursion, large sum |
| same | naive/kmp/rk: empty text/pattern, longer pattern, overlaps, case/space/punctuation, 1000 random binary pairs | identical to `startswith` oracle | `ALL PASSED` | n+1 empty-pattern starts, overlaps, agreement of all three |
| same | rk: `abdj`/`ab`, `abdj`/`dj`, hash(ab)=hash(dj)=75, negative-remainder text | false candidate rejected, correct positions | `ALL PASSED` | candidate verification, normalisation |
| same | suffix: `""`, `a`, `aaaa`, `abcd`, `mississippi`, punctuation, 500 random, `a*50000` | SA and LCP equal oracle; len(repeated)=max lcp | `ALL PASSED` | doubling ranks, Kasai, no sentinel |
| same | aho: example, empty dict, no texts, 500 random dictionaries/texts, dense `a..a^446`, 10000 patterns x 100 texts | counts equal direct counting; each scale run well under 20 s | `ALL PASSED` (scale 0.03 s and 0.39 s) | suffix patterns, duplicates, dense counts, performance |
| same (subprocess) | 6 mixed requests through `Python/source/main.py` | 6 output lines; second `aho` has no stale counts | `ALL PASSED` | JSONL interface, state reset |
| same (scale) | kmp 200000/100000, rk 10000x2000, naive 3000/1500 worst | correct counts, < 20 s | 0.04 s / ~0 s / 0.14 s | scale correctness and time |

## Search comparison

Setup: `python tests/student/benchmark.py`; raw output saved in `tests/student/benchmark_output.txt`.

- **Inputs:** the same request object is passed to naive, KMP and RK. *Random:* seeded generator (`random.Random(2026)`), text of 26 lowercase letters, pattern = a real substring of the text (so one occurrence, pattern distribution: uniformly random start). *Repetitive:* text `a^n`, pattern `a^(m-1)b` (no occurrence; worst case for naive).
- **Sizes:** (n, m) = (500, 50), (1500, 150), (3000, 300), all in the common domain n, m ≤ 3000.
- **Correctness first:** for every case the script compares the position lists of the three algorithms (last column: all identical).
- **Timing scope:** only the algorithm call (`naive`/`kmp`/`rk` on an in-memory dict), `time.perf_counter_ns`; excludes JSON parsing, process start and generation. Python has no compilation/JIT; one untimed warm-up call per algorithm/case, then 3 timed runs. Unit: milliseconds.

| Case | n | m | Seed/generator | Algorithm | Run 1 (ms) | Run 2 (ms) | Run 3 (ms) | Median (ms) | Correct outputs checked |
|---|---|---|---|---|---|---|---|---|---|
| random | 500 | 50 | seed 2026 | naive | 0.058 | 0.057 | 0.057 | 0.057 | 1 start(s); naive=kmp=rk: True |
| random | 500 | 50 | seed 2026 | kmp | 0.060 | 0.055 | 0.057 | 0.057 | 1 start(s); naive=kmp=rk: True |
| random | 500 | 50 | seed 2026 | rk | 0.174 | 0.155 | 0.153 | 0.155 | 1 start(s); naive=kmp=rk: True |
| random | 1500 | 150 | seed 2026 | naive | 0.194 | 0.194 | 0.196 | 0.194 | 1 start(s); naive=kmp=rk: True |
| random | 1500 | 150 | seed 2026 | kmp | 0.184 | 0.179 | 0.185 | 0.184 | 1 start(s); naive=kmp=rk: True |
| random | 1500 | 150 | seed 2026 | rk | 0.541 | 0.499 | 0.482 | 0.499 | 1 start(s); naive=kmp=rk: True |
| random | 3000 | 300 | seed 2026 | naive | 0.409 | 0.397 | 0.299 | 0.397 | 1 start(s); naive=kmp=rk: True |
| random | 3000 | 300 | seed 2026 | kmp | 0.354 | 0.368 | 0.356 | 0.356 | 1 start(s); naive=kmp=rk: True |
| random | 3000 | 300 | seed 2026 | rk | 0.973 | 0.989 | 0.980 | 0.980 | 1 start(s); naive=kmp=rk: True |
| repetitive | 500 | 50 | a^n / a^(m-1)b | naive | 2.030 | 2.016 | 1.471 | 2.016 | 0 start(s); naive=kmp=rk: True |
| repetitive | 500 | 50 | a^n / a^(m-1)b | kmp | 0.069 | 0.078 | 0.068 | 0.069 | 0 start(s); naive=kmp=rk: True |
| repetitive | 500 | 50 | a^n / a^(m-1)b | rk | 0.073 | 0.074 | 0.079 | 0.074 | 0 start(s); naive=kmp=rk: True |
| repetitive | 1500 | 150 | a^n / a^(m-1)b | naive | 19.940 | 18.185 | 18.109 | 18.185 | 0 start(s); naive=kmp=rk: True |
| repetitive | 1500 | 150 | a^n / a^(m-1)b | kmp | 0.251 | 0.221 | 0.228 | 0.228 | 0 start(s); naive=kmp=rk: True |
| repetitive | 1500 | 150 | a^n / a^(m-1)b | rk | 0.251 | 0.238 | 0.236 | 0.238 | 0 start(s); naive=kmp=rk: True |
| repetitive | 3000 | 300 | a^n / a^(m-1)b | naive | 43.747 | 43.331 | 43.274 | 43.331 | 0 start(s); naive=kmp=rk: True |
| repetitive | 3000 | 300 | a^n / a^(m-1)b | kmp | 0.476 | 0.464 | 0.475 | 0.475 | 0 start(s); naive=kmp=rk: True |
| repetitive | 3000 | 300 | a^n / a^(m-1)b | rk | 0.481 | 0.467 | 0.470 | 0.470 | 0 start(s); naive=kmp=rk: True |

**Observations.** On repetitive input the naive time grows 2.0 -> 18.2 -> 43.3 ms when n and m both grow, which is consistent with its quadratic worst case (n·m grows 1:9:36 here) while KMP and RK stay around 0.07–0.48 ms and grow roughly with n. On random input all three are about the same order, because naive almost always mismatches at the first character; RK is about 2.5x slower in this Python implementation because it performs arithmetic and a modulo per window. These are three runs on one machine and one language implementation; they illustrate behaviour but do not prove asymptotic complexity.

**Effect of the small modulus.** With mod 101 there are only 101 possible hash values, so unrelated windows collide often (e.g. `ab` and `dj`, both 75). Each collision creates a candidate that costs up to O(m) to verify, so the c·m term can dominate; a test with many collisions can make RK quadratic. This is specific to this deliberately small modulus; production implementations use large (or randomised) moduli, where collisions are rare. The known collision `ab`/`dj` is included as a correctness test.

## Sources and AI assistance

- Use of AI: I used the AI ​​tool Claude. It helped me when I was struggling—there were some parts of the assignment I didn’t understand, and it explained them to me. To be honest, it also helped me write an ANALYSIS.md
