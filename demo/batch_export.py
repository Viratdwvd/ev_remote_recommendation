import argparse, os, pandas as pd
from src.geolife_parser import load_user_trips, trips_by_day
from src.recommender import recommend_for_trip

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geolife_dir", required=True)
    ap.add_argument("--chargers_csv", required=True)
    ap.add_argument("--user_id", default=None)
    ap.add_argument("--detour_km", type=float, default=4.0)
    ap.add_argument("--energy_kwh", type=float, default=20.0)
    ap.add_argument("--veh_max_kw", type=float, default=50.0)
    ap.add_argument("--avg_speed_kmph", type=float, default=35.0)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--out_csv", default="batch_recommendations.csv")
    args = ap.parse_args()

    print("[INFO] Loading chargers CSV:", args.chargers_csv)
    if not os.path.exists(args.chargers_csv):
        print("[ERROR] chargers_csv not found.")
        return
    chargers = pd.read_csv(args.chargers_csv)
    print("[INFO] Chargers rows:", len(chargers))

    print("[INFO] Scanning Geolife dir:", args.geolife_dir)
    if not os.path.exists(args.geolife_dir):
        print("[ERROR] geolife_dir not found.")
        return

    df = load_user_trips(args.geolife_dir, user_id=args.user_id)
    if df.empty:
        print("[ERROR] No .plt data found. Check --geolife_dir / --user_id.")
        return

    users = sorted(df["user"].unique().tolist())
    user = args.user_id or (users[0] if users else None)
    print(f"[INFO] Users found: {users} | using: {user}")

    trips = trips_by_day(df[df["user"] == user])
    print(f"[INFO] Trips (days) for {user}: {len(trips)}")
    if not trips:
        print("[ERROR] No daily trips for selected user.")
        return

    out_rows = []
    for idx, t in enumerate(trips, 1):
        if idx % 10 == 0:
            print(f"[INFO] Processing trip {idx}/{len(trips)}: {t['date']}")
        recs = recommend_for_trip(
            t["polyline"], chargers,
            energy_kwh=args.energy_kwh, veh_max_kw=args.veh_max_kw,
            avg_speed_kmph=args.avg_speed_kmph, detour_limit_km=args.detour_km,
            default_wait_min=0.0, top_k=args.topk
        )
        for rank, r in enumerate(recs, 1):
            out_rows.append({
                "user": t["user"], "date": t["date"], "rank": rank,
                "name": r["name"], "lat": r["lat"], "lon": r["lon"],
                "detour_km": r["detour_km"], "total_min": r["total_min"]
            })

    out_df = pd.DataFrame(out_rows)
    out_dir = os.path.dirname(args.out_csv)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    out_df.to_csv(args.out_csv, index=False)
    print(f"[DONE] Wrote {args.out_csv} with {len(out_rows)} rows for user {user}")

if __name__ == "__main__":
    main()
