"""Export the 774-LGA attribute table to a plain CSV for the Week 8 script.

Reads adm2_lga from the analysis-ready GeoPackage (a GeoPackage is a SQLite
file, so the standard library is enough) and writes nga_lga_snt.csv at the
repository root, without geometry. Missing values stay empty cells: Bakassi
has a boundary but no 2020 population, so its population and density are
blank, not zero.

Run from the repository root:  uv run scripts/export_lga_csv.py
"""

import csv
import sqlite3

GPKG = "data/processed/nga_snt_analysis_ready.gpkg"
OUT = "nga_lga_snt.csv"

COLUMNS = [
    ("adm2_pcode", "adm2_pcode", None),
    ("lga", "adm2_name", None),
    ("state", "adm1_name", None),
    ("net_type", "net_type", None),
    ("chemoprevention", "chemoprevention", None),
    ("pop_total_2020", "pop_total_2020", 0),
    ("pop_u5_2020", "pop_u5_2020", 0),
    ("area_km2_albers", "area_km2_albers", 3),
    ("pop_density_2020", "pop_density_2020", 1),
]


def fmt(value, digits):
    if value is None:
        return ""
    if digits is None:
        return value
    if digits == 0:
        return int(round(value))
    return round(value, digits)


con = sqlite3.connect(f"file:{GPKG}?mode=ro", uri=True)
select = ", ".join(src for _, src, _ in COLUMNS)
rows = con.execute(f"SELECT {select} FROM adm2_lga ORDER BY adm2_pcode").fetchall()
con.close()

with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([name for name, _, _ in COLUMNS])
    for row in rows:
        writer.writerow([fmt(v, d) for v, (_, _, d) in zip(row, COLUMNS)])

print(f"wrote {len(rows)} LGAs to {OUT}")
