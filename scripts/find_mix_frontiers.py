#!/usr/bin/env python3
"""Week 4 - find every border where neighbouring LGAs carry different mixes.

Reads  data/processed/nga_snt_analysis_ready.gpkg   (ESRI:102022, Week 3)
Writes data/processed/nga_snt_frontiers.gpkg        layer lga_borders
       data/processed/frontier_checks.json

One spatial operation, in two steps:
  1. spatial join of adm2_lga to itself (predicate "intersects") - which LGAs touch
  2. intersection of each touching pair's boundaries - the border they share,
     as a line

Lengths are measured on the WGS84 ellipsoid, not in Albers metres. Albers is
equal-AREA: it stretches north-south lines and shrinks east-west ones at
Nigeria's latitude, by about 1%. shared_km_albers is kept as the check.

A pair touching at a single point shares no border, so it is recorded and
excluded (rook contiguity, not queen). Lagos Lagoon pairs do not touch at all
and are reported as a sensitivity, not added. See docs/04-spatial-analysis.md.

Run: python scripts/find_mix_frontiers.py
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyproj import Geod
from shapely.ops import linemerge

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "processed" / "nga_snt_analysis_ready.gpkg"
OUT = ROOT / "data" / "processed" / "nga_snt_frontiers.gpkg"
REPORT = ROOT / "data" / "processed" / "frontier_checks.json"

GEOD = Geod(ellps="WGS84")
MIN_SHARED_M = 1.0   # below 1 m of shared edge, a "border" is a vertex touch

# Week 3, section 4.1: shore pairs separated only by the lagoon, mixes differ.
LAGOON_FRONTIERS = [
    ("Epe", "Kosofe"), ("Epe", "Lagos Island"),
    ("Epe", "Lagos Mainland"), ("Epe", "Shomolu"),
]

KEEP = ["adm2_pcode", "adm2_name", "adm1_name", "intervention_mix",
        "net_type", "chemoprevention", "geometry"]

lga = gpd.read_file(SRC, layer="adm2_lga")[KEEP]
assert lga.crs.to_string() == "ESRI:102022", lga.crs
assert len(lga) == 774

# ---------------------------------------------------------------- 1. spatial join
pairs = gpd.sjoin(lga, lga, how="inner", predicate="intersects",
                  lsuffix="a", rsuffix="b")
pairs = pairs[pairs["adm2_pcode_a"] < pairs["adm2_pcode_b"]]   # each pair once, no self
print(f"spatial join: {len(pairs)} pairs of LGAs that intersect")

# ---------------------------------------------------------------- 2. intersection
geom = lga.set_index("adm2_pcode").geometry
shared = [
    geom[a].boundary.intersection(geom[b].boundary)
    for a, b in zip(pairs["adm2_pcode_a"], pairs["adm2_pcode_b"])
]
pairs = pairs.drop(columns=["geometry", "index_b"], errors="ignore")
borders = gpd.GeoDataFrame(pairs.reset_index(drop=True),
                           geometry=gpd.GeoSeries(shared, crs=lga.crs))
borders["shared_km"] = borders.length / 1000

point_only = borders[borders["shared_km"] * 1000 < MIN_SHARED_M]
borders = borders[borders["shared_km"] * 1000 >= MIN_SHARED_M].copy()
print(f"  {len(point_only)} touch at a point only -> excluded")
print(f"  {len(borders)} share a border")

# Keep only the line parts: a boundary intersection can carry stray points
# where the shared edge breaks and resumes.
def lines_only(g):
    parts = getattr(g, "geoms", [g])
    lines = [p for p in parts if p.geom_type in ("LineString", "MultiLineString")]
    return linemerge(lines) if lines else None

borders["geometry"] = borders.geometry.apply(lines_only)
borders["shared_km_albers"] = borders.length / 1000
borders["shared_km"] = [
    GEOD.geometry_length(g) / 1000 for g in borders.geometry.to_crs("EPSG:4326")
]

# ---------------------------------------------------------------- classify
net_moves = borders["net_type_a"] != borders["net_type_b"]
chemo_moves = borders["chemoprevention_a"] != borders["chemoprevention_b"]
borders["axis_changed"] = "same mix"
borders.loc[net_moves & ~chemo_moves, "axis_changed"] = "net type"
borders.loc[chemo_moves & ~net_moves, "axis_changed"] = "chemoprevention"
borders.loc[net_moves & chemo_moves, "axis_changed"] = "both"
borders["is_frontier"] = borders["intervention_mix_a"] != borders["intervention_mix_b"]
borders["crosses_state"] = borders["adm1_name_a"] != borders["adm1_name_b"]
assert (borders["is_frontier"] == (net_moves | chemo_moves)).all()

borders = borders[[
    "adm2_pcode_a", "adm2_name_a", "adm1_name_a", "intervention_mix_a",
    "adm2_pcode_b", "adm2_name_b", "adm1_name_b", "intervention_mix_b",
    "axis_changed", "is_frontier", "crosses_state", "shared_km", "shared_km_albers", "geometry",
]].sort_values(["adm2_pcode_a", "adm2_pcode_b"]).reset_index(drop=True)

OUT.unlink(missing_ok=True)
borders.to_file(OUT, layer="lga_borders", driver="GPKG")
print(f"Wrote {OUT.relative_to(ROOT)}  layer lga_borders  {len(borders)} lines")

# ---------------------------------------------------------------- checks
fr = borders[borders["is_frontier"]]
lga_deg = pd.concat([borders["adm2_pcode_a"], borders["adm2_pcode_b"]]).value_counts()
lagoon_names = {n for p in LAGOON_FRONTIERS for n in p}
lagoon_found = [
    p for p in LAGOON_FRONTIERS
    if ((borders["adm2_name_a"].isin(p) & borders["adm2_name_b"].isin(p))).any()
]

checks = {
    "pairs_intersecting": int(len(pairs)),
    "pairs_point_only": int(len(point_only)),
    "pairs_sharing_border": int(len(borders)),
    "lgas_with_no_neighbour": sorted(set(lga["adm2_pcode"]) - set(lga_deg.index)),
    "mean_neighbours_per_lga": round(2 * len(borders) / len(lga), 2),
    "frontier_pairs": int(len(fr)),
    "frontier_share_pct": round(100 * len(fr) / len(borders), 1),
    "frontier_by_axis": fr["axis_changed"].value_counts().to_dict(),
    "frontier_crossing_state_line": int(fr["crosses_state"].sum()),
    "frontier_km_total": round(fr["shared_km"].sum(), 1),
    "all_borders_km_total": round(borders["shared_km"].sum(), 1),
    "albers_length_error_pct_total": round(
        100 * (borders["shared_km_albers"].sum() / borders["shared_km"].sum() - 1), 3),
    "albers_length_error_pct_worst": round(
        100 * (borders["shared_km_albers"] / borders["shared_km"] - 1).abs().max(), 2),
    "shared_km_median": round(borders["shared_km"].median(), 2),
    "shared_km_min": round(borders["shared_km"].min(), 3),
    "shared_km_max": round(borders["shared_km"].max(), 1),
    "lgas_on_a_frontier": int(pd.concat([fr["adm2_pcode_a"], fr["adm2_pcode_b"]]).nunique()),
    "borders_under_100m": int((borders["shared_km"] < 0.1).sum()),
    "frontiers_under_100m": int((fr["shared_km"] < 0.1).sum()),
    "empty_geometry": int(borders.geometry.is_empty.sum()),
    "null_geometry": int(borders.geometry.isna().sum()),
    "geometry_types": borders.geom_type.value_counts().to_dict(),
    "lagoon_frontier_pairs_found_by_join": len(lagoon_found),
    "lagoon_frontier_pairs_expected_missing": len(LAGOON_FRONTIERS),
}
REPORT.write_text(json.dumps(checks, indent=2, default=str) + "\n")

for k, v in checks.items():
    print(f"  {k:40s} {v}")
