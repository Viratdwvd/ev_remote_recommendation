import argparse, os, pandas as pd, folium
from src.geolife_parser import load_user_trips, trips_by_day
from src.grid import snap_polyline, dedup_consecutive
from src.seq_mine import mine_frequent_ngrams
from src.recommender import recommend_for_trip

def save_map(route_polyline, recs, out_html):
    if not route_polyline:
        return
    m = folium.Map(location=route_polyline[0], zoom_start=12)
    folium.PolyLine(route_polyline, weight=4, opacity=0.8).add_to(m)
    for r in recs:
        folium.Marker(
            [r["lat"], r["lon"]],
            popup=f"{r['name']}<br>total={r['total_min']} min<br>detour={r['detour_min']} min"
        ).add_to(m)
    m.save(out_html)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geolife_dir", required=True)
    ap.add_argument("--chargers_csv", required=True)
    ap.add_argument("--user_id", default=None)
    ap.add_argument("--detour_km", type=float, default=3.0)
    ap.add_argument("--energy_kwh", type=float, default=20.0)
    ap.add_argument("--veh_max_kw", type=float, default=50.0)
    ap.add_argument("--avg_speed_kmph", type=float, default=35.0)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--map_out", default="demo_map.html")
    args = ap.parse_args()

    chargers = pd.read_csv(args.chargers_csv)
    df = load_user_trips(args.geolife_dir, user_id=args.user_id)
    if df.empty:
        print("No .plt data found; check your geolife_dir path.")
        return

    users = sorted(df["user"].unique().tolist())
    chosen_user = args.user_id or (users[0] if users else None)
    day_trips = trips_by_day(df[df["user"] == chosen_user])
    if not day_trips:
        print("No trips for user", chosen_user); return
    print(f"Found {len(day_trips)} daily trips for {chosen_user}")

    snapped_routes = [dedup_consecutive(snap_polyline(t["polyline"], 0.001)) for t in day_trips]
    patterns = mine_frequent_ngrams(snapped_routes, min_support=3, n_min=3, n_max=6, top_k=20)
    if patterns:
        print("Top frequent patterns (n-gram length, support):")
        for seq, c in patterns[:5]:
            print(f"  n={len(seq)}, support={c}")
    else:
        print("No frequent patterns found (dataset may be small)")

    current = day_trips[-1]["polyline"]
    recs = recommend_for_trip(
        current, chargers,
        energy_kwh=args.energy_kwh, veh_max_kw=args.veh_max_kw,
        avg_speed_kmph=args.avg_speed_kmph, detour_limit_km=args.detour_km,
        default_wait_min=0.0, top_k=args.topk
    )
    if not recs:
        print("No candidate chargers within detour limit. Try increasing --detour_km."); return

    print("\nTop-K recommendations:")
    for i, r in enumerate(recs, 1):
        print(f"{i}. {r['name']}  @({r['lat']:.5f},{r['lon']:.5f})")
        print(f"   detour: {r['detour_km']} km | time: detour {r['detour_min']}m + charge {r['charge_min']}m + wait {r['wait_min']}m = {r['total_min']}m")

    try:
        save_map(current, recs, args.map_out)
        print(f"\nSaved map to {args.map_out}")
    except Exception as e:
        print("Map save failed:", e)

if __name__ == "__main__":
    main()
