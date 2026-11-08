"""Download GRID3 NGA Health Facilities v3.0 and extract Kano as a small CSV.

Source: GRID3 NGA - Health Facilities v3.0, Humanitarian Data Exchange,
https://data.humdata.org/dataset/grid3-nga-health-facilities-v3-0
(last modified 27 Aug 2026). One GeoPackage, 41,778 facilities, EPSG:4326.

The national file is 33.5 MB, so it stays in data/raw/ (git-ignored). This
script writes only the Kano rows, with their latitude and longitude as plain
columns, to data/processed/grid3_kano_facilities.csv, which is committed.
Rows with no coordinates are kept on purpose: finding them is the point of
month-03/week-10/my_points.py.

    uv run scripts/extract_grid3_kano.py
"""

import hashlib
import urllib.request
from pathlib import Path

import geopandas as gpd

RAW = Path("data/raw/grid3_nga_health_facilities_v3_0.gpkg")
URL = (
    "https://data.humdata.org/dataset/a1e3e4bc-3699-4fe1-bd17-b38f4e7108d2/"
    "resource/f45c9266-0458-4160-a902-32661a6a67ed/download/"
    "grid3_nga_health_facilities_v3_0.gpkg"
)
SHA256 = "db66a5536009c8fc39b30b25b80fd7b99e9f54d8baba40f9f29a005e839f81bd"
OUT = Path("data/processed/grid3_kano_facilities.csv")
KEEP = [
    "unique_id",
    "facility_name",
    "facility_type",
    "facility_level",
    "facility_ownership",
    "functional",
    "state_standard",
    "lga_standard",
    "ward_standard",
    "latitude",
    "longitude",
]

if not RAW.exists():
    print("Downloading", URL)
    urllib.request.urlretrieve(URL, RAW)

digest = hashlib.sha256(RAW.read_bytes()).hexdigest()
if digest != SHA256:
    raise SystemExit(f"Checksum mismatch: {digest}. GRID3 may have re-issued the file.")

facilities = gpd.read_file(RAW)
print("National facilities:", len(facilities))

kano = facilities[facilities["state_standard"] == "Kano"][KEEP]
kano = kano.sort_values(["lga_standard", "facility_name"])
kano.to_csv(OUT, index=False)
print("Kano facilities written to", OUT, ":", len(kano))
