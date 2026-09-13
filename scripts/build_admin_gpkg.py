"""Build the project GeoPackage from the raw COD downloads.

Inputs (data/raw/, produced by scripts/download_cod_data.py):
    nga_admin_boundaries.shp.zip   OCHA COD-AB, admin 0-3 + senatorial districts
    nga_admpop_2020.xlsx           OCHA COD-PS, LGA population projection

Output (data/processed/nga_cod_admin.gpkg), three layers:
    adm1_state          37 states + FCT
    adm2_lga            774 LGAs, with 2020 population and the NMSP mix joined
    nmsp_name_crosswalk non-spatial; how each NMSP name reaches a PCODE

The join is the point of this script. The NMSP intervention table has no
PCODEs, only names, so every LGA is matched on state + normalised name in
three passes: exact, numeric-suffix strip (the NMSP disambiguates repeated
names as Obi1/Obi2), and a small hand-checked spelling table. Any name that
survives all three is an error, not a warning - the script raises.

    python scripts/build_admin_gpkg.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

BOUNDARIES = RAW / "nga_admin_boundaries.shp.zip"
POPULATION = RAW / "nga_admpop_2020.xlsx"
NMSP = PROCESSED / "nmsp_2021_2025_lga_intervention_mix.csv"
GPKG = PROCESSED / "nga_cod_admin.gpkg"

# NMSP spelling -> COD adm2_name, within the same state. Each one was read off
# the COD list for that state by eye; none is a fuzzy-matcher guess left in.
SPELLINGS = {
    ("Abia", "Isuikwato"): "Isiukwuato",
    ("Abia", "Obi Nwa"): "Obi Ngwa",
    ("Abia", "Umu-Neochi"): "Umu-Nneochi",
    ("Adamawa", "Ganaye"): "Ganye",
    ("Adamawa", "Gireri"): "Girei",
    ("Ekiti", "Efon-Alayee"): "Efon",             # Efon-Alaaye is the town
    ("Ekiti", "Gboyin"): "Aiyekire (Gbonyin)",    # COD keeps the alias in ()
    ("Ekiti", "Idosi-Osi"): "Ido-Osi",
    ("Ekiti", "Ilemeji"): "Ilejemeji",
    ("Kano", "Takali"): "Takai",
    ("Katsina", "Matazuu"): "Matazu",
    ("Kogi", "Ogori/Mangongo"): "Ogori/Magongo",
    ("Niger", "Pailoro"): "Paikoro",
    ("Sokoto", "Dange-Shnsi"): "Dange-Shuni",
    ("Sokoto", "Gawabawa"): "Gwadabawa",
    ("Taraba", "Karin-Lamido"): "Karim-Lamido",
}

# Columns the COD ships that are null in every single row of the Nigeria
# extract: the alternate-name and alternate-language slots, and valid_to.
EMPTY_COLS = [
    "adm0_name1", "adm0_name2", "adm0_name3",
    "adm1_name1", "adm1_name2", "adm1_name3",
    "adm2_name1", "adm2_name2", "adm2_name3",
    "lang1", "lang2", "lang3", "valid_to",
]


def norm(value: object) -> str:
    """Lowercase, strip everything that is not a letter or digit."""
    return re.sub(r"[^a-z0-9]+", "", str(value).lower().strip())


def read_layer(name: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(f"zip://{BOUNDARIES}!{name}.shp")
    return gdf.drop(columns=[c for c in EMPTY_COLS if c in gdf.columns])


def population() -> pd.DataFrame:
    pop = pd.read_excel(POPULATION, sheet_name="nga_admpop_adm2_2020")
    under5 = ["F_00_04", "M_00_04"]
    out = pd.DataFrame({
        "adm2_pcode": pop["ADM2_PCODE"],
        "pop_total_2020": pop["T_TL"].astype("Int64"),
        "pop_u5_2020": pop[under5].sum(axis=1).round().astype("Int64"),
    })
    return out


def crosswalk(nmsp: pd.DataFrame, lga: gpd.GeoDataFrame) -> pd.DataFrame:
    """Attach a PCODE to every NMSP row, recording how it was reached."""
    lookup = {(norm(r.adm1_name), norm(r.adm2_name)): r.adm2_pcode
              for r in lga.itertuples()}

    rows = []
    for r in nmsp.itertuples():
        state = norm(r.state)
        pcode = lookup.get((state, norm(r.lga)))
        method = "exact"
        if pcode is None:
            stripped = re.sub(r"\d+$", "", norm(r.lga))
            pcode = lookup.get((state, stripped))
            method = "suffix_strip"
        if pcode is None:
            cod = SPELLINGS.get((r.state, r.lga))
            pcode = lookup.get((state, norm(cod))) if cod else None
            method = "spelling_table"
        if pcode is None:
            method = "UNMATCHED"
        rows.append({
            "nmsp_state": r.state,
            "nmsp_lga": r.lga,
            "adm2_pcode": pcode,
            "match_method": method,
        })

    out = pd.DataFrame(rows)
    unmatched = out[out.adm2_pcode.isna()]
    if len(unmatched):
        print(unmatched.to_string(), file=sys.stderr)
        raise SystemExit(f"{len(unmatched)} NMSP LGAs did not reach a PCODE")

    duplicated = out[out.adm2_pcode.duplicated(keep=False)]
    if len(duplicated):
        print(duplicated.to_string(), file=sys.stderr)
        raise SystemExit("two NMSP rows landed on the same LGA")

    counts = out.match_method.value_counts()
    for method in ("exact", "suffix_strip", "spelling_table"):
        print(f"  {method:15} {counts.get(method, 0):3d}")
    return out


def main() -> int:
    state = read_layer("nga_admin1")
    lga = read_layer("nga_admin2")
    print(f"boundaries: {len(state)} states, {len(lga)} LGAs, CRS {lga.crs}")

    nmsp = pd.read_csv(NMSP)
    print(f"NMSP mixes: {len(nmsp)} rows")
    walk = crosswalk(nmsp, lga)

    merged = nmsp.merge(walk[["nmsp_state", "nmsp_lga", "adm2_pcode", "match_method"]],
                        left_on=["state", "lga"], right_on=["nmsp_state", "nmsp_lga"])
    merged = merged.drop(columns=["nmsp_state", "nmsp_lga", "state", "lga"])

    lga = lga.merge(merged, on="adm2_pcode", how="left")
    lga = lga.merge(population(), on="adm2_pcode", how="left")

    # The two axes the mixes actually vary on; CM and IPTp are universal.
    # Order matters: the alternatives are tried left to right, so the two
    # qualified net types have to precede bare LLINs, and PBO-LLINs carries a
    # hyphen in the NMSP text.
    lga["net_type"] = lga.intervention_mix.str.extract(
        r"(UrbanLLINs|PBO-LLINs|LLINs)")
    lga["chemoprevention"] = (lga.intervention_mix.str.extract(r"(SMC|IPTi)")
                              .fillna("none"))

    no_pop = int(lga.pop_total_2020.isna().sum())
    print(f"LGAs with no COD population row: {no_pop} "
          f"({', '.join(lga.loc[lga.pop_total_2020.isna(), 'adm2_name'])})")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    if GPKG.exists():
        GPKG.unlink()
    state.to_file(GPKG, layer="adm1_state", driver="GPKG")
    lga.to_file(GPKG, layer="adm2_lga", driver="GPKG")
    walk.to_csv(PROCESSED / "nmsp_lga_name_crosswalk.csv", index=False)

    print(f"wrote {GPKG.relative_to(ROOT)} ({GPKG.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
