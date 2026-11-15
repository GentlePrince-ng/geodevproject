# Week 11 challenge 1: check my layers' CRS, choose a UTM zone, measure area.
#
# My layers: the 774 LGAs (Week 3 output, already projected to Africa Albers)
# and the GRID3 health facilities for Kano (Week 10 output, EPSG:4326).
# The challenge work this week is in Kano, so the question is which UTM zone
# suits Kano, and whether it measures area as well as my national CRS does.
import geopandas as gpd
from pyproj import Geod

lgas = gpd.read_file("data/processed/nga_snt_analysis_ready.gpkg", layer="adm2_lga")
facilities = gpd.read_file(
    "data/processed/grid3_kano_facilities.gpkg", layer="facilities"
)
print("LGA layer CRS:", lgas.crs.to_string())
print("Facility layer CRS:", facilities.crs)

# estimate_utm_crs looks at the middle of the data. For all of Nigeria it
# returns 32N, but Nigeria runs from 2.7 to 14.7 degrees east, across three
# zones (31N, 32N, 33N), so no single zone is right nationally.
print("Suggested UTM, all of Nigeria:", lgas.estimate_utm_crs())

kano = lgas[lgas["adm1_name"] == "Kano"].copy()
west, south, east, north = kano.to_crs(epsg=4326).total_bounds
print("Kano LGAs:", len(kano))
print(f"Kano spans {west:.2f} to {east:.2f} degrees east")
print("Suggested UTM, Kano:", kano.estimate_utm_crs())

# Kano sits wholly inside 6-12 degrees east, so UTM zone 32N fits all of it.
kano_utm = kano.to_crs(epsg=32632)
kano_utm["area_km2_utm"] = kano_utm.area / 1_000_000

# Check against the true area on the curved Earth (the same check as Week 3).
geod = Geod(ellps="WGS84")
kano_utm["area_km2_true"] = [
    abs(geod.geometry_area_perimeter(g)[0]) / 1_000_000
    for g in kano.to_crs(epsg=4326).geometry
]
kano_utm["utm_error_pct"] = (
    (kano_utm["area_km2_utm"] / kano_utm["area_km2_true"] - 1) * 100
)

print(
    kano_utm[["adm2_name", "area_km2_true", "area_km2_utm", "utm_error_pct"]]
    .sort_values("area_km2_true", ascending=False)
    .head(5)
    .round(3)
    .to_string(index=False)
)
total_true = kano_utm["area_km2_true"].sum()
total_utm = kano_utm["area_km2_utm"].sum()
total_albers = kano_utm["area_km2_albers"].sum()
print("Kano total, true:", round(total_true, 1), "km2")
print(
    "Kano total, UTM 32N:", round(total_utm, 1), "km2",
    f"({(total_utm / total_true - 1) * 100:+.3f}%)",
)
print(
    "Kano total, Albers:", round(total_albers, 1), "km2",
    f"({(total_albers / total_true - 1) * 100:+.3f}%)",
)
print("Worst LGA error in UTM 32N:", round(kano_utm["utm_error_pct"].abs().max(), 3), "%")

# The facilities are only points, so there is nothing to measure yet, but
# they need the same CRS before any join or buffer. Reproject them too.
facilities_utm = facilities.to_crs(epsg=32632)
print("Facilities now in:", facilities_utm.crs, "first point:",
      [round(v) for v in facilities_utm.geometry.iloc[0].coords[0]])
