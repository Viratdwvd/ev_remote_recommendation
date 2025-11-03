import pandas as pd
from .geometry import detour_km
from .features import detour_minutes, charging_minutes, expected_wait_minutes
from .ranker import rank

def recommend_for_trip(route_polyline, chargers_df: pd.DataFrame,
                       energy_kwh=20.0, veh_max_kw=50.0,
                       avg_speed_kmph=35.0, detour_limit_km=3.0,
                       default_wait_min=0.0, top_k=5):
    cands = []
    for _, row in chargers_df.iterrows():
        try:
            lat = float(row["lat"]); lon = float(row["lon"])
        except Exception:
            continue
        name = None
        for key in ["name_en","name","title"]:
            if key in row and pd.notnull(row[key]):
                name = row[key]; break
        name = name or "Charger"
        site_kw = None
        for key in ["power_kw_or_capacity","power_kw","power"]:
            if key in row and pd.notnull(row[key]):
                try:
                    site_kw = float(row[key]); break
                except Exception:
                    pass

        d_km = detour_km(route_polyline, (lat, lon))
        if d_km > detour_limit_km:
            continue

        t_detour = detour_minutes(d_km, avg_speed_kmph)
        t_wait   = expected_wait_minutes(default_wait_min)
        t_charge = charging_minutes(energy_kwh, veh_max_kw, site_kw)
        total    = t_detour + t_wait + t_charge

        cands.append({
            "name": name,
            "lat": lat, "lon": lon,
            "detour_km": round(d_km, 3),
            "detour_min": round(t_detour, 1),
            "wait_min": round(t_wait, 1),
            "charge_min": round(t_charge, 1),
            "total_min": round(total, 1),
            "score_inputs": {
                "total_time_min": total,
                "price_per_kwh": 0.0,
                "reliability": 0.95,
                "connector_ok": True
            }
        })

    ranked = rank(cands)
    return ranked[:top_k]
