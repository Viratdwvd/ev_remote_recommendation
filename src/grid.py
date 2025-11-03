def snap_point(lat: float, lon: float, grid_deg: float=0.001):
    return (round(lat / grid_deg), round(lon / grid_deg))

def snap_polyline(polyline, grid_deg: float=0.001):
    return [snap_point(lat, lon, grid_deg) for (lat, lon) in polyline]

def dedup_consecutive(seq):
    out = []
    prev = None
    for s in seq:
        if s != prev:
            out.append(s)
            prev = s
    return out
