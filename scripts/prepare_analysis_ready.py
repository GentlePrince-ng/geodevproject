#!/usr/bin/env python3
"""Week 3 - reproject, clip and quality-check the SNT layers.

Reads  data/processed/nga_cod_admin.gpkg            (EPSG:4326, built in Week 2)
Writes data/processed/nga_snt_analysis_ready.gpkg   (ESRI:102022)
       data/processed/qc_report.json

The working CRS is Africa Albers Equal Area Conic. Nigeria spans three UTM
zones, so no single zone works nationally; Albers reproduces the geodesic area
of every LGA to better than 0.03 per cent. See docs/03-data-preparation.md.

Run: python scripts/prepare_analysis_ready.py
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import CRS, Geod
from shapely.geometry import MultiPolygon, Polygon

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "processed" / "nga_cod_admin.gpkg"
OUT = ROOT / "data" / "processed" / "nga_snt_analysis_ready.gpkg"
REPORT = ROOT / "data" / "processed" / "qc_report.json"

SOURCE_CRS = "EPSG:4326"
WORKING_CRS = "ESRI:102022"          # Africa Albers Equal Area Conic
SLIVER_TOLERANCE_M2 = 1_000.0        # 0.001 km2: below this an overlap is float noise

GEOD = Geod(ellps="WGS84")

qc: dict = {}
problems: list[dict] = []


def flag(check: str, severity: str, detail: str, action: str) -> None:
    problems.append(
        {"check": check, "severity": severity, "detail": detail, "action": action}
    )
    print(f"    [{severity.upper()}] {detail} -> {action}")


def geodesic_area_km2(geoms) -> np.ndarray:
    return np.array([abs(GEOD.geometry_area_perimeter(g)[0]) for g in geoms]) / 1e6


def interior_rings(geom) -> list:
    """Holes in a dissolved coverage - i.e. gaps between the polygons."""
    parts = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    return [Polygon(ring) for part in parts for ring in part.interiors]


# ---------------------------------------------------------------- load
print(f"Reading {SRC.relative_to(ROOT)}")
adm1_src = gpd.read_file(SRC, layer="adm1_state")
adm2_src = gpd.read_file(SRC, layer="adm2_lga")
print(f"  adm1_state {len(adm1_src):>4} features, CRS {adm1_src.crs}")
print(f"  adm2_lga   {len(adm2_src):>4} features, CRS {adm2_src.crs}")

# Ground truth measured on the ellipsoid, before any projection touches it.
truth_km2 = geodesic_area_km2(adm2_src.geometry)


# ------------------------------------------------- QC 1: CRS integrity
print("\nQC 1  CRS and projection integrity")
qc1: dict = {
    "working_crs": WORKING_CRS,
    "working_crs_name": CRS.from_user_input(WORKING_CRS).name,
}

for name, gdf in (("adm1_state", adm1_src), ("adm2_lga", adm2_src)):
    if gdf.crs is None:
        flag("QC1", "fatal", f"{name} has no CRS defined", "cannot proceed")
        raise SystemExit(1)
    if gdf.crs != CRS.from_user_input(SOURCE_CRS):
        flag("QC1", "warning", f"{name} is {gdf.crs}, expected {SOURCE_CRS}",
             "reprojected anyway")

adm1 = adm1_src.to_crs(WORKING_CRS)
adm2 = adm2_src.to_crs(WORKING_CRS)

proj_km2 = adm2.area.values / 1e6
err_pct = (proj_km2 - truth_km2) / truth_km2 * 100
qc1.update(
    source_crs=SOURCE_CRS,
    geodesic_total_km2=round(float(truth_km2.sum()), 1),
    projected_total_km2=round(float(proj_km2.sum()), 1),
    national_area_error_pct=round(
        float((proj_km2.sum() - truth_km2.sum()) / truth_km2.sum() * 100), 5),
    worst_lga_area_error_pct=round(float(np.abs(err_pct).max()), 4),
    mean_abs_lga_area_error_pct=round(float(np.abs(err_pct).mean()), 5),
)
print(f"  {qc1['working_crs_name']} ({WORKING_CRS}), units metre")
print(f"  national area  geodesic  {qc1['geodesic_total_km2']:>11,.1f} km2")
print(f"                 projected {qc1['projected_total_km2']:>11,.1f} km2"
      f"  ({qc1['national_area_error_pct']:+.5f}%)")
print(f"  per-LGA area error: worst {qc1['worst_lga_area_error_pct']:.4f}%,"
      f" mean |err| {qc1['mean_abs_lga_area_error_pct']:.5f}%")
if qc1["worst_lga_area_error_pct"] > 0.5:
    flag("QC1", "warning",
         f"worst LGA area error {qc1['worst_lga_area_error_pct']:.2f}%",
         "CRS choice needs review")
qc["qc1_crs_integrity"] = qc1


# --------------------------------------------- QC 2: geometry validity
print("\nQC 2  Geometry validity")
qc2: dict = {}
for name, gdf in (("adm1_state", adm1), ("adm2_lga", adm2)):
    invalid = int((~gdf.geometry.is_valid).sum())
    empty = int(gdf.geometry.is_empty.sum())
    null = int(gdf.geometry.isna().sum())
    qc2[name] = {"features": len(gdf), "invalid": invalid,
                 "empty": empty, "null": null}
    print(f"  {name:<11} {len(gdf):>4} features: {invalid} invalid,"
          f" {empty} empty, {null} null")
    if invalid:
        key = "adm2_pcode" if name == "adm2_lga" else "adm1_pcode"
        bad = list(gdf.loc[~gdf.geometry.is_valid, key])
        flag("QC2", "error", f"{invalid} invalid geometries in {name}: {bad}",
             "repaired with make_valid")
        gdf.geometry = gdf.geometry.make_valid()
qc["qc2_geometry_validity"] = qc2


# -------------------------------------------------- clip to study area
print("\nClip to study area")
study_area = gpd.GeoDataFrame(
    {"name": ["Nigeria - 36 states and the FCT"], "lga_count": [len(adm2)]},
    geometry=[adm2.geometry.union_all()],
    crs=WORKING_CRS,
)
sa_km2 = float(study_area.area.iloc[0]) / 1e6
print(f"  study area = dissolve(adm2_lga): {sa_km2:,.1f} km2")

n1_before, n2_before = len(adm1), len(adm2)
a1_before, a2_before = float(adm1.area.sum()), float(adm2.area.sum())

adm1_clip = gpd.clip(adm1, study_area, keep_geom_type=True)
adm2_clip = gpd.clip(adm2, study_area, keep_geom_type=True)

qc_clip = {
    "study_area_km2": round(sa_km2, 1),
    "adm1_features_before": n1_before, "adm1_features_after": len(adm1_clip),
    "adm2_features_before": n2_before, "adm2_features_after": len(adm2_clip),
    "adm1_area_km2_before": round(a1_before / 1e6, 3),
    "adm1_area_km2_after": round(float(adm1_clip.area.sum()) / 1e6, 3),
    "adm2_area_km2_before": round(a2_before / 1e6, 3),
    "adm2_area_km2_after": round(float(adm2_clip.area.sum()) / 1e6, 3),
}
qc_clip["adm1_area_removed_km2"] = round(
    qc_clip["adm1_area_km2_before"] - qc_clip["adm1_area_km2_after"], 3)
qc_clip["adm2_area_removed_km2"] = round(
    qc_clip["adm2_area_km2_before"] - qc_clip["adm2_area_km2_after"], 3)
print(f"  adm1_state {n1_before} -> {len(adm1_clip)} features,"
      f" {qc_clip['adm1_area_removed_km2']:+.3f} km2 removed")
print(f"  adm2_lga   {n2_before} -> {len(adm2_clip)} features,"
      f" {qc_clip['adm2_area_removed_km2']:+.3f} km2 removed")

if len(adm2_clip) != n2_before:
    flag("clip", "error",
         f"clip changed the LGA count {n2_before} -> {len(adm2_clip)}",
         "investigate before use")
if abs(qc_clip["adm1_area_removed_km2"]) > 1.0:
    flag("clip", "warning",
         f"clipping adm1_state removed {qc_clip['adm1_area_removed_km2']:.3f} km2",
         "state and LGA layers do not cover the same ground")
qc["clip"] = qc_clip

adm1 = adm1_clip.reset_index(drop=True)
adm2 = adm2_clip.reset_index(drop=True)


# ------------------------------------- QC 3: identity and completeness
print("\nQC 3  Identity and completeness")
qc3 = {
    "adm2_expected": 774,
    "adm2_actual": len(adm2),
    "adm2_pcode_unique": int(adm2["adm2_pcode"].nunique()),
    "adm2_pcode_null": int(adm2["adm2_pcode"].isna().sum()),
    "adm1_expected": 37,
    "adm1_actual": len(adm1),
    "adm1_pcode_unique": int(adm1["adm1_pcode"].nunique()),
}
orphans = sorted(set(adm2["adm1_pcode"]) - set(adm1["adm1_pcode"]))
qc3["lga_state_codes_not_in_adm1"] = orphans
print(f"  adm2_lga   {qc3['adm2_actual']}/774 features,"
      f" {qc3['adm2_pcode_unique']} unique PCODEs, {qc3['adm2_pcode_null']} null")
print(f"  adm1_state {qc3['adm1_actual']}/37 features,"
      f" {qc3['adm1_pcode_unique']} unique PCODEs")
print(f"  LGA state codes with no matching state: {len(orphans)}")
for cond, msg in (
    (qc3["adm2_actual"] != 774, f"LGA count is {qc3['adm2_actual']}, expected 774"),
    (qc3["adm2_pcode_unique"] != qc3["adm2_actual"], "duplicate adm2_pcode values"),
    (qc3["adm2_pcode_null"] > 0, f"{qc3['adm2_pcode_null']} null adm2_pcode values"),
    (bool(orphans), f"orphan state codes: {orphans}"),
):
    if cond:
        flag("QC3", "error", msg, "blocks the adjacency analysis")
qc["qc3_identity_completeness"] = qc3


# --------------------------- QC 4: topology of the coverage
print("\nQC 4  Coverage topology - gaps and overlaps")
keys = adm2[["adm2_pcode", "adm2_name", "geometry"]]
pairs = gpd.sjoin(keys, keys, how="inner", predicate="overlaps")
pairs = pairs[pairs["adm2_pcode_left"] < pairs["adm2_pcode_right"]]

by_pcode = dict(zip(adm2["adm2_pcode"], adm2["geometry"]))
overlaps = []
for _, r in pairs.iterrows():
    area = by_pcode[r["adm2_pcode_left"]].intersection(
        by_pcode[r["adm2_pcode_right"]]).area
    if area > SLIVER_TOLERANCE_M2:
        overlaps.append({
            "a": f"{r['adm2_name_left']} ({r['adm2_pcode_left']})",
            "b": f"{r['adm2_name_right']} ({r['adm2_pcode_right']})",
            "overlap_km2": round(area / 1e6, 6),
        })
overlaps.sort(key=lambda o: -o["overlap_km2"])

gaps = interior_rings(study_area.geometry.iloc[0])
gaps_over_tol = [g for g in gaps if g.area > SLIVER_TOLERANCE_M2]
sum_parts = float(adm2.area.sum())

qc4 = {
    "candidate_overlap_pairs_tested": int(len(pairs)),
    "overlaps_above_tolerance": len(overlaps),
    "overlap_detail": overlaps[:20],
    "interior_holes_in_coverage": len(gaps),
    "holes_above_tolerance": len(gaps_over_tol),
    "largest_hole_km2": round(max((g.area for g in gaps), default=0.0) / 1e6, 6),
    "sum_of_lga_areas_km2": round(sum_parts / 1e6, 3),
    "dissolved_coverage_km2": round(sa_km2, 3),
    "double_counted_km2": round((sum_parts - sa_km2 * 1e6) / 1e6, 3),
    "sliver_tolerance_m2": SLIVER_TOLERANCE_M2,
}
print(f"  candidate overlapping pairs tested: {qc4['candidate_overlap_pairs_tested']}")
print(f"  overlaps above {SLIVER_TOLERANCE_M2:,.0f} m2: {qc4['overlaps_above_tolerance']}")
print(f"  interior holes in the dissolved coverage: {len(gaps)}"
      f" ({len(gaps_over_tol)} above tolerance),"
      f" largest {qc4['largest_hole_km2']:.6f} km2")
print(f"  sum of LGA areas {qc4['sum_of_lga_areas_km2']:,.3f} km2"
      f" vs dissolved {qc4['dissolved_coverage_km2']:,.3f} km2"
      f" -> {qc4['double_counted_km2']:+.3f} km2")
if overlaps:
    flag("QC4", "warning",
         f"{len(overlaps)} LGA pairs overlap above tolerance, largest"
         f" {overlaps[0]['overlap_km2']:.6f} km2",
         "flagged, not dissolved - see docs/03-data-preparation.md")
if gaps_over_tol:
    flag("QC4", "warning",
         f"{len(gaps_over_tol)} gaps in the LGA coverage,"
         f" largest {qc4['largest_hole_km2']:.6f} km2",
         "flagged, not filled - see docs/03-data-preparation.md")
qc["qc4_coverage_topology"] = qc4


# ------------------------------- QC 5: attribute domains and null audit
print("\nQC 5  Attribute domains and nulls")
domains = {
    "intervention_mix": 7,
    "net_type": 3,
    "chemoprevention": 3,
    "match_method": 3,
    "iccm": 2,
}
qc5: dict = {"domains": {}, "nulls": {}}
for col, expected in domains.items():
    counts = adm2[col].value_counts(dropna=False).to_dict()
    counts = {("<null>" if pd.isna(k) else str(k)): int(v)
              for k, v in counts.items()}
    qc5["domains"][col] = {"expected_classes": expected,
                           "observed_classes": len(counts), "counts": counts}
    print(f"  {col:<18} {len(counts)} classes (expected {expected}): {counts}")
    if len(counts) != expected:
        flag("QC5", "warning",
             f"{col} has {len(counts)} classes, expected {expected}",
             "check the extraction")

for col in adm2.columns:
    if col == "geometry":
        continue
    n = int(adm2[col].isna().sum())
    if n:
        qc5["nulls"][col] = n
print(f"  columns with nulls: {qc5['nulls']}")

pop_null = adm2.loc[adm2["pop_total_2020"].isna(), "adm2_name"].tolist()
qc5["lgas_without_population"] = pop_null
if pop_null:
    flag("QC5", "known",
         f"{len(pop_null)} LGA(s) with no population: {pop_null}",
         "kept and flagged; excluded from per-capita measures")
qc5["national_pop_2020"] = int(adm2["pop_total_2020"].sum())
qc5["national_pop_u5_2020"] = int(adm2["pop_u5_2020"].sum())
print(f"  population carried through: {qc5['national_pop_2020']:,} total,"
      f" {qc5['national_pop_u5_2020']:,} under five")
qc["qc5_attribute_domains"] = qc5


# --------------------------------------------------------------- write
print(f"\nWriting {OUT.relative_to(ROOT)}")
adm2["area_km2_albers"] = adm2.area / 1e6
adm1["area_km2_albers"] = adm1.area / 1e6
adm2["pop_density_2020"] = adm2["pop_total_2020"] / adm2["area_km2_albers"]

if OUT.exists():
    OUT.unlink()
layers = (("study_area", study_area), ("adm1_state", adm1), ("adm2_lga", adm2))
for layer, gdf in layers:
    gdf.to_file(OUT, layer=layer, driver="GPKG")
    print(f"  {layer:<11} {len(gdf):>4} features,"
          f" {len(gdf.columns) - 1} attributes, {gdf.crs.to_string()}")

qc["output"] = {
    "path": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    "size_bytes": OUT.stat().st_size,
    "crs": WORKING_CRS,
    "layers": {k: len(v) for k, v in layers},
}
qc["problems"] = problems
REPORT.write_text(json.dumps(qc, indent=2), encoding="utf-8")
print(f"Writing {REPORT.relative_to(ROOT)}")

blocking = sum(1 for p in problems if p["severity"] in ("error", "fatal"))
print(f"\n{len(problems)} problem(s) recorded; {blocking} blocking.")
