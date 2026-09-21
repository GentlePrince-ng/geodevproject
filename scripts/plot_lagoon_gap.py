#!/usr/bin/env python3
"""Render the one coverage gap QC 4 found, for docs/03-data-preparation.md.

Writes qgis/coverage_gap_lagos_lagoon.png

Run: python scripts/plot_lagoon_gap.py
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon, Polygon

ROOT = Path(__file__).resolve().parent.parent
GPKG = ROOT / "data" / "processed" / "nga_snt_analysis_ready.gpkg"
OUT = ROOT / "qgis" / "coverage_gap_lagos_lagoon.png"

adm2 = gpd.read_file(GPKG, layer="adm2_lga")
study = gpd.read_file(GPKG, layer="study_area")

g = study.geometry.iloc[0]
parts = g.geoms if isinstance(g, MultiPolygon) else [g]
hole = max((Polygon(r) for p in parts for r in p.interiors), key=lambda x: x.area)
gap = gpd.GeoDataFrame(geometry=[hole], crs=adm2.crs)

lagos = adm2[adm2["adm1_name"] == "Lagos"]
shore = adm2[adm2.geometry.intersects(hole.buffer(50))]

fig, ax = plt.subplots(figsize=(9, 6.2))
lagos.plot(ax=ax, facecolor="#eceff1", edgecolor="#90a4ae", linewidth=0.6)
shore.plot(ax=ax, facecolor="#cfd8dc", edgecolor="#546e7a", linewidth=0.9)
gap.plot(ax=ax, facecolor="#c62828", edgecolor="#8e0000", linewidth=1.2, alpha=0.85)

for _, r in shore.iterrows():
    c = r.geometry.representative_point()
    ax.annotate(r["adm2_name"], (c.x, c.y), ha="center", va="center",
                fontsize=7.5, color="#263238")

# Frame on the shore LGAs, not the gap, so Epe - the one shore LGA carrying a
# different intervention mix - is in the picture.
minx, miny, maxx, maxy = shore.total_bounds
pad = 4_000
ax.set_xlim(minx - pad, maxx + pad)
ax.set_ylim(miny - pad, maxy + pad)
ax.set_axis_off()
ax.set_title(
    "QC 4: the one gap in the LGA coverage\n"
    "183.25 km$^2$ of Lagos Lagoon sits inside Lagos State but inside no LGA",
    fontsize=11, color="#263238", pad=12)
ax.annotate("red = assigned to no LGA", (0.02, 0.02), xycoords="axes fraction",
            fontsize=8, color="#c62828")

fig.tight_layout()
fig.savefig(OUT, dpi=170, facecolor="white")
print(f"wrote {OUT.relative_to(ROOT)}")
