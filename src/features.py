def detour_minutes(detour_km: float, avg_speed_kmph: float=35.0) -> float:
    speed = max(5.0, float(avg_speed_kmph))
    return 60.0 * detour_km / speed

def charging_minutes(energy_kwh: float, veh_max_kw: float, site_kw: float|None) -> float:
    if site_kw is None or site_kw <= 0:
        site_kw = veh_max_kw
    eff_kw = max(1.0, min(float(veh_max_kw), float(site_kw)))
    return 60.0 * (float(energy_kwh) / eff_kw)

def expected_wait_minutes(default_wait: float=0.0) -> float:
    return float(default_wait)
