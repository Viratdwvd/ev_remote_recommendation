import math

def haversine_km(a, b):
    R = 6371.0
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2-lat1, lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*R*math.asin(min(1, math.sqrt(h)))

def min_distance_polyline_km(polyline, point):
    return min(haversine_km((lat,lon), point) for (lat,lon) in polyline)

def detour_km(polyline, charger_latlon, factor=2.0):
    dmin = min_distance_polyline_km(polyline, charger_latlon)
    return factor * dmin
