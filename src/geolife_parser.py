# src/geolife_parser.py
import os
import pandas as pd
from datetime import datetime

def read_plt(plt_path: str) -> pd.DataFrame:
    with open(plt_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    rows = []
    for line in lines[6:]:  # skip Geolife header lines
        parts = line.split(",")
        if len(parts) < 7:
            continue
        try:
            lat = float(parts[0]); lon = float(parts[1])
        except Exception:
            continue
        alt = float(parts[3]) if parts[3] else 0.0
        date_str = parts[5]; time_str = parts[6]
        try:
            ts = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        rows.append((lat, lon, alt, ts))
    return pd.DataFrame(rows, columns=["lat","lon","alt","timestamp"])

def _infer_user_id_from_path(full_path: str) -> str:
    # Expect .../<USERID>/Trajectory/<file.plt>
    parts = os.path.normpath(full_path).split(os.sep)
    # Find 'Trajectory' in path and take the parent as user id
    for i, p in enumerate(parts):
        if p.lower() == "trajectory" and i > 0:
            return parts[i-1]  # e.g., "010"
    # Fallback: last directory name that is not 'Trajectory'
    for p in reversed(parts[:-1]):
        if p.lower() != "trajectory":
            return p
    return "unknown"

def load_user_trips(geolife_root: str, user_id: str=None) -> pd.DataFrame:
    """
    Walks geolife_root to find all .plt files. If user_id is provided (e.g., "010"),
    only include files whose parent user folder matches that id.
    Returns DataFrame with columns: user, date, lat, lon, timestamp
    """
    all_rows = []
    for dirpath, _, filenames in os.walk(geolife_root):
        for fn in filenames:
            if not fn.lower().endswith(".plt"):
                continue
            full = os.path.join(dirpath, fn)
            uid = _infer_user_id_from_path(full)
            if user_id and uid != user_id:
                continue
            df = read_plt(full)
            if df.empty:
                continue
            df["user"] = uid
            df["date"] = df["timestamp"].dt.date.astype(str)
            all_rows.append(df[["user","date","lat","lon","timestamp"]])
    if not all_rows:
        return pd.DataFrame(columns=["user","date","lat","lon","timestamp"])
    return pd.concat(all_rows, ignore_index=True)

def trips_by_day(user_df: pd.DataFrame) -> list:
    trips = []
    if user_df.empty:
        return trips
    for (user, date), g in user_df.sort_values("timestamp").groupby(["user","date"]):
        poly = list(zip(g["lat"].tolist(), g["lon"].tolist()))
        if len(poly) >= 5:
            trips.append({"user": user, "date": date, "polyline": poly})
    return trips
