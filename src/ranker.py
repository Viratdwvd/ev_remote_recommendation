def score_candidate(total_time_min, price_per_kwh=0.0, reliability=0.95, connector_ok=True,
                    w=(0.7, 0.15, 0.1, 0.05)):
    w1, w2, w3, w4 = w
    conn_pen = 0.0 if connector_ok else 1.0
    return (w1*total_time_min
            + w2*price_per_kwh
            + w3*(1.0 - reliability)
            + w4*conn_pen)

def rank(cands):
    for c in cands:
        c["score"] = score_candidate(**c["score_inputs"])
    return sorted(cands, key=lambda x: x["score"])
