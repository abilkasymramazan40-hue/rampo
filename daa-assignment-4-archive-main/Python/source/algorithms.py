"Assignment 4 algorithms. See docs/guide/CONTRACTS.md; inputs and outputs are dictionaries."
from collections import deque

#Part 1: LCS
def lcs(request):
    a, b = request["a"], request["b"]
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return {"length": 0, "sequence": ""}
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ai = a[i - 1]
        row, prev = dp[i], dp[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                row[j] = prev[j - 1] + 1
            else:
                row[j] = prev[j] if prev[j] >= row[j - 1] else row[j - 1]
    out = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    out.reverse()
    return {"length": dp[n][m], "sequence": "".join(out)}


#Part 2: interval DP (merge)
def merge(request):
    s = request["sizes"]
    n = len(s)
    if n <= 1:
        return {"cost": 0, "plan": []}
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + s[i]
    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for l in range(0, n - length + 1):
            r = l + length - 1
            best, bk = INF, l
            for k in range(l, r):
                c = dp[l][k] + dp[k + 1][r]
                if c < best:
                    best, bk = c, k
            dp[l][r] = best + pre[r + 1] - pre[l]
            split[l][r] = bk
    plan = []
    stack = [(0, n - 1, False)]
    while stack:
        l, r, done = stack.pop()
        if l == r:
            continue
        k = split[l][r]
        if done:
            plan.append([l, k, r])
        else:
            stack.append((l, r, True))
            stack.append((k + 1, r, False))
            stack.append((l, k, False))
    return {"cost": dp[0][n - 1], "plan": plan}


#Part 3: tree DP (MWIS)
def tree(request):
    n = request["n"]
    if n == 0:
        return {"weight": 0, "selected": []}
    w = request["weights"]
    adj = [[] for _ in range(n)]
    for u, v in request["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    parent = [-1] * n
    order = [0]
    seen = [False] * n
    seen[0] = True
    for v in order:
        for u in adj[v]:
            if not seen[u]:
                seen[u] = True
                parent[u] = v
                order.append(u)
    take = w[:]
    skip = [0] * n
    for v in reversed(order):
        p = parent[v]
        if p >= 0:
            take[p] += skip[v]
            skip[p] += take[v] if take[v] > skip[v] else skip[v]
    chosen = [False] * n
    selected = []
    for v in order:
        p = parent[v]
        if p >= 0 and chosen[p]:
            continue
        if take[v] > skip[v]:
            chosen[v] = True
            selected.append(v)
    return {"weight": max(take[0], skip[0]), "selected": selected}


#Part 4: searches
def naive(request):
    t, p = request["text"], request["pattern"]
    n, m = len(t), len(p)
    if m == 0:
        return {"positions": list(range(n + 1))}
    res = []
    for i in range(n - m + 1):
        j = 0
        while j < m and t[i + j] == p[j]:
            j += 1
        if j == m:
            res.append(i)
    return {"positions": res}


def _prefix_function(p):
    m = len(p)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and p[i] != p[k]:
            k = pi[k - 1]
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    return pi


def kmp(request):
    t, p = request["text"], request["pattern"]
    n, m = len(t), len(p)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}
    pi = _prefix_function(p)
    res = []
    k = 0
    for i in range(n):
        while k > 0 and (k == m or t[i] != p[k]):
            k = pi[k - 1]
        if t[i] == p[k]:
            k += 1
        if k == m:
            res.append(i - m + 1)
    return {"positions": res}


def rk(request):
    t, p = request["text"], request["pattern"]
    n, m = len(t), len(p)
    if m == 0:
        return {"positions": list(range(n + 1))}
    if m > n:
        return {"positions": []}
    B, M = 31, 101
    high = pow(B, m - 1, M)
    hp = ht = 0
    for i in range(m):
        hp = (hp * B + ord(p[i])) % M
        ht = (ht * B + ord(t[i])) % M
    res = []
    for i in range(n - m + 1):
        if hp == ht:
            j = 0
            while j < m and t[i + j] == p[j]:
                j += 1
            if j == m:
                res.append(i)
        if i + m < n:
            ht = ((ht - ord(t[i]) * high) * B + ord(t[i + m])) % M
    return {"positions": res}


#Part 5: suffix array + Kasai LCP
def suffix(request):
    s = request["text"]
    n = len(s)
    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}
    sa = list(range(n))
    rank = [ord(c) for c in s]
    k = 1
    while True:
        key = [rank[i] * (n + 200) + (rank[i + k] + 1 if i + k < n else 0) for i in range(n)]
        sa.sort(key=key.__getitem__)
        new = [0] * n
        r = 0
        for idx in range(1, n):
            if key[sa[idx]] != key[sa[idx - 1]]:
                r += 1
            new[sa[idx]] = r
        rank = new
        if r == n - 1 or k >= n:
            break
        k *= 2
    
    lcp = [0] * n
    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h > 0:
                h -= 1
        else:
            h = 0
    best = max(lcp)
    rep = ""
    if best > 0:
        pos = lcp.index(best)
        rep = s[sa[pos]:sa[pos] + best]
    return {"sa": sa, "lcp": lcp, "repeated": rep}


#Part 6: Aho-Corasick
def aho(request):
    patterns, texts = request["patterns"], request["texts"]
    nxt = [{}]
    term = [[]]
    for idx, p in enumerate(patterns):
        v = 0
        for c in p:
            d = nxt[v]
            u = d.get(c)
            if u is None:
                u = len(nxt)
                nxt.append({})
                term.append([])
                d[c] = u
            v = u
        term[v].append(idx)
    S = len(nxt)
    fail = [0] * S
    bfs = []
    q = deque()
    for c, u in nxt[0].items():
        q.append(u)
    while q:
        v = q.popleft()
        bfs.append(v)
        for c, u in nxt[v].items():
            f = fail[v]
            while f and c not in nxt[f]:
                f = fail[f]
            fail[u] = nxt[f].get(c, 0)
            q.append(u)
    term_states = [v for v in range(S) if term[v]]
    result = []
    for text in texts:
        row = [0] * len(patterns)
        if patterns and text:
            cnt = [0] * S
            v = 0
            for c in text:
                while v and c not in nxt[v]:
                    v = fail[v]
                v = nxt[v].get(c, 0)
                cnt[v] += 1
            for v in reversed(bfs):
                if cnt[v]:
                    cnt[fail[v]] += cnt[v]
            for v in term_states:
                c = cnt[v]
                if c:
                    for idx in term[v]:
                        row[idx] = c
        result.append(row)
    return {"counts": result}
