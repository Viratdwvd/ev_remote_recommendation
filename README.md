# EV Route Recommender (Beijing demo)

## What this contains
- Parser for Geolife `.plt` files
- Lightweight route mining & near-route charger recommendation
- Folium map to visualize a trip & recommended chargers

## Quickstart (Windows PowerShell)
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Put your Geolife data under data/geolife (UserXXX folders) 
# Put your chargers CSV under data/chargers (already created for you)
# Example run:
python demo\demo_run.py ^
  --geolife_dir "data\geolife" ^
  --chargers_csv "data\chargers\chargers_beijing_osm_translated.csv" ^
  --user_id "User001" ^
  --detour_km 3 ^
  --topk 5
```

## Notes
- For real detour on roads, swap the simple Haversine-based detour with OSRM.
- If your Geolife user folders have different names, pass `--user_id` accordingly or omit to auto-pick the first user found.
