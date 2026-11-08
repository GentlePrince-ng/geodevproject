# Week 10 challenge 2: turn a CSV of coordinates into a point layer, and
# prove the points land in the right place.
#
# CSV: Kano health facilities from GRID3 NGA Health Facilities v3.0
#      (data/processed/grid3_kano_facilities.csv, extracted from the national
#      file by scripts/extract_grid3_kano.py). Kano is the state I looked at
#      closely in Month 2: all 44 LGAs get SMC, but their nets differ.
# Polygons: my 774 LGAs (Week 3 output), keeping Kano's 44.
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)

table = pd.read_csv("data/processed/grid3_kano_facilities.csv")
print("Rows in the CSV:", len(table))
print(table[["facility_name", "facility_type", "latitude", "longitude"]].head(3))

# --- Check 1: rows with no coordinates ------------------------------------
# A point needs both numbers. points_from_xy would turn a blank into an
# empty geometry with no error, so count the blanks and set them aside.
no_xy = table["latitude"].isna() | table["longitude"].isna()
print("Rows with no coordinates:", no_xy.sum())
located = table[~no_xy].copy()

# --- Build the points: x = longitude first, y = latitude second -----------
facilities = gpd.GeoDataFrame(
    located,
    geometry=gpd.points_from_xy(located["longitude"], located["latitude"]),
    crs="EPSG:4326",
)
print("Points built:", len(facilities), " CRS:", facilities.crs)
print("Bounds:", facilities.total_bounds.round(2))

# --- Check 2: do the points fall inside Kano? -----------------------------
lgas = gpd.read_file("data/processed/nga_snt_analysis_ready.gpkg", layer="adm2_lga")
kano_lgas = lgas[lgas["adm1_name"] == "Kano"].to_crs("EPSG:4326")
kano = kano_lgas.union_all()
print("Kano LGAs:", len(kano_lgas))

facilities["inside_kano"] = facilities.within(kano)
outside = facilities[~facilities["inside_kano"]].copy()
print("Points inside Kano:", facilities["inside_kano"].sum(), "of", len(facilities))
print("Points outside Kano:", len(outside))

# How far outside? Distances need a projected CRS, so measure in my
# Africa Albers working CRS (metres) and report kilometres.
albers = "ESRI:102022"
kano_albers = kano_lgas.to_crs(albers).union_all()
outside["km_outside"] = outside.to_crs(albers).distance(kano_albers) / 1000
print(
    outside.sort_values("km_outside", ascending=False)[
        ["facility_name", "lga_standard", "longitude", "latitude", "km_outside"]
    ]
    .round(2)
    .head(10)
)
print("Outside by under 1 km (on the border line):", (outside["km_outside"] < 1).sum())
print("Outside by more than 10 km:", (outside["km_outside"] > 10).sum())

# --- Save the point layer -------------------------------------------------
facilities.to_file("data/processed/grid3_kano_facilities.gpkg", layer="facilities")
print("Saved", len(facilities), "points to data/processed/grid3_kano_facilities.gpkg")

# --- Plot the points over the polygons ------------------------------------
fig, ax = plt.subplots(figsize=(8, 8))
kano_lgas.plot(ax=ax, color="#F4EFE6", edgecolor="#8A8A8A", linewidth=0.4)
facilities[facilities["inside_kano"]].plot(
    ax=ax, color="#094923", markersize=3, label=f"Inside Kano ({facilities['inside_kano'].sum()})"
)
near = outside[(outside["km_outside"] > 1) & (outside["km_outside"] <= 10)]
if len(near):
    near.plot(ax=ax, color="#C0392B", markersize=14, label=f"1 to 10 km outside Kano ({len(near)})")
# Anything further out would be off the map, so it is named instead of drawn.
far = outside[outside["km_outside"] > 10]
for i, (_, row) in enumerate(far.iterrows()):
    ax.annotate(
        f"Not shown: {row['facility_name']}, {row['km_outside']:.0f} km outside Kano "
        f"(lat {row['latitude']:.5f}, long {row['longitude']:.5f}: the longitude repeats the latitude)",
        xy=(0.0, -0.03 - 0.03 * i),
        xycoords="axes fraction",
        fontsize=7.5,
        color="#C0392B",
    )
# Keep the view on Kano, so one far-away point cannot shrink the map.
xmin, ymin, xmax, ymax = kano_lgas.total_bounds
ax.set_xlim(xmin - 0.1, xmax + 0.1)
ax.set_ylim(ymin - 0.1, ymax + 0.1)
ax.set_title(
    f"GRID3 health facilities in Kano: {len(facilities)} with coordinates\n"
    f"({no_xy.sum()} of {len(table)} rows have none)"
)
ax.legend(loc="lower left", fontsize=8, frameon=False)
ax.set_axis_off()
fig.savefig("month-03/week-10/my_points_map.png", dpi=150, bbox_inches="tight")
print("Map saved")
