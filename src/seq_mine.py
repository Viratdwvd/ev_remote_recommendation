from collections import Counter

def mine_frequent_ngrams(snapped_routes, min_support=3, n_min=3, n_max=6, top_k=50):
    counts = Counter()
    for route in snapped_routes:
        L = len(route)
        for n in range(n_min, n_max+1):
            for i in range(0, L-n+1):
                counts[tuple(route[i:i+n])] += 1
    patterns = [(seq, c) for seq, c in counts.items() if c >= min_support]
    patterns.sort(key=lambda x: (-x[1], -len(x[0])))
    return patterns[:top_k]
