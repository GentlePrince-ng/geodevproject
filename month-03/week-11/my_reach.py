# Week 11 challenge 3: how much of each Kano LGA is more than 5 km from any
# health facility?
#
# Why the coverage gap and not nearest distance: an LGA is large (Kano's run
# from 13 to 1,489 km2), so the distance from its centre to one facility
# says little. The gap measures how much of the LGA's land is out of reach.
#
# Why 5 km: it is the distance most often used for physical access to primary
# care in Nigeria and sub-Saharan Africa, roughly an hour on foot. Malaria case
# management, which every LGA's intervention mix includes, happens at a
# facility, so this shows where that part of the mix can physically reach.
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import patheffects
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

pd.set_option("display.width", 160)
REACH_M = 5000

lgas = gpd.read_file("data/processed/nga_snt_analysis_ready.gpkg", layer="adm2_lga")
kano = lgas[lgas["adm1_name"] == "Kano"].to_crs(epsg=32632)
kano = kano[["adm2_pcode", "adm2_name", "net_type", "pop_total_2020", "geometry"]].copy()
kano["area_km2"] = kano.area / 1_000_000

facilities = gpd.read_file(
    "data/processed/grid3_kano_facilities.gpkg", layer="facilities"
).to_crs(epsg=32632)

# Buffer every facility, then dissolve the circles into one shape.
reach = facilities[["geometry"]].copy()
reach["geometry"] = reach.buffer(REACH_M)
reach = reach.dissolve()

# Keep the parts of each LGA that the reach shape does not cover.
uncovered = gpd.overlay(kano, reach, how="difference")
uncovered["uncovered_km2"] = uncovered.area / 1_000_000

result = kano.merge(
    uncovered[["adm2_pcode", "uncovered_km2"]], on="adm2_pcode", how="left"
)
result["uncovered_km2"] = result["uncovered_km2"].fillna(0)
result["uncovered_pct"] = (result["uncovered_km2"] / result["area_km2"] * 100).round(1)

cols = ["adm2_name", "net_type", "area_km2", "uncovered_km2", "uncovered_pct"]
print(f"Share of each LGA more than {REACH_M // 1000} km from a facility, worst first:")
worst = result.sort_values("uncovered_pct", ascending=False)[cols].head(8)
print(worst.round(1).to_string(index=False))
print("LGAs fully covered:", (result["uncovered_km2"] == 0).sum(), "of", len(result))

total_gap = result["uncovered_km2"].sum()
total_area = result["area_km2"].sum()
print(
    f"Kano: {total_gap:,.0f} of {total_area:,.0f} km2 uncovered "
    f"({total_gap / total_area * 100:.1f}%)"
)

by_net = result.groupby("net_type")[["area_km2", "uncovered_km2"]].sum()
by_net["uncovered_pct"] = (by_net["uncovered_km2"] / by_net["area_km2"] * 100).round(1)
print("\nBy net type:")
print(by_net.round(1))

# How much does the answer depend on the 5 km choice?
print("\nSensitivity, Kano uncovered share:")
for metres in [3000, 5000, 10000]:
    ring = facilities[["geometry"]].copy()
    ring["geometry"] = ring.buffer(metres)
    gap = gpd.overlay(kano[["geometry"]], ring.dissolve(), how="difference")
    share = gap.area.sum() / 1_000_000 / total_area * 100
    print(f"  {metres // 1000:>2} km: {share:.1f}%")

# Save the result layers (UTM 32N) for later weeks.
out = "data/processed/kano_facility_reach.gpkg"
result.to_file(out, layer="lga_reach", driver="GPKG")
uncovered.to_file(out, layer="uncovered_5km", driver="GPKG")
print(f"\nSaved {out}: lga_reach ({len(result)}) and uncovered_5km ({len(uncovered)})")

# Map: the uncovered land in a strong colour over the LGAs, facilities as dots.
fig, ax = plt.subplots(figsize=(9, 9))
kano.plot(ax=ax, color="#f2f0eb", edgecolor="#9a9a9a", linewidth=0.5)
uncovered.plot(ax=ax, color="#d7301f", edgecolor="none")
facilities.plot(ax=ax, color="#1b3a5c", markersize=1.5)
kano.dissolve().boundary.plot(ax=ax, color="#333333", linewidth=1)

# Label the three LGAs with the largest uncovered share.
halo = [patheffects.withStroke(linewidth=3, foreground="white")]
for _, row in result.nlargest(3, "uncovered_pct").iterrows():
    p = row.geometry.representative_point()
    ax.annotate(
        f"{row['adm2_name']}\n{row['uncovered_pct']:.0f}% uncovered",
        (p.x, p.y), ha="center", fontsize=8, color="#222222", path_effects=halo,
    )

# Zoom to Kano. One facility (Makkha Eye Hospital) has its latitude typed into
# its longitude and sits 277 km away in Yobe, which would stretch the map.
x0, y0, x1, y1 = kano.total_bounds
ax.set_xlim(x0 - 5000, x1 + 5000)
ax.set_ylim(y0 - 5000, y1 + 5000)
ax.plot([x0 + 5000, x0 + 30000], [y0 + 5000, y0 + 5000], color="black", linewidth=3)
ax.text(x0 + 17500, y0 + 8000, "25 km", ha="center", fontsize=9)

ax.legend(
    handles=[
        Patch(color="#d7301f", label=f"More than {REACH_M // 1000} km from any facility"),
        Patch(facecolor="#f2f0eb", edgecolor="#9a9a9a", label="Within 5 km of a facility"),
        Line2D([], [], marker="o", linestyle="", color="#1b3a5c", markersize=3,
               label=f"Health facility, GRID3 v3.0 (n = {len(facilities):,})"),
    ],
    loc="upper left", bbox_to_anchor=(0.0, -0.01), fontsize=8, frameon=False,
)
ax.set_title(
    f"Kano: {total_gap / total_area * 100:.0f}% of the land is more than 5 km "
    "from a health facility\nStraight-line distance, 44 LGAs, UTM zone 32N (EPSG:32632)",
    fontsize=11, loc="left",
)
ax.set_axis_off()
fig.savefig("month-03/week-11/my_reach_map.png", dpi=200, bbox_inches="tight")
print("Saved month-03/week-11/my_reach_map.png")
