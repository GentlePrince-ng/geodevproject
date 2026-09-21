"""Download the OCHA Common Operational Datasets for Nigeria.

Two datasets, both from the Humanitarian Data Exchange, both CC BY-IGO:

  cod-ab-nga  Subnational administrative boundaries (admin 0-2)
  cod-ps-nga  Subnational population statistics (2022 projection)

Resources are resolved through the HDX CKAN API rather than hard-coded
download URLs, so the script keeps working when HDX re-issues a resource id.
Every file is written to data/raw/ (git-ignored) and its SHA-256 printed, so
a later run on another machine can prove it has the same bytes.

    python scripts/download_cod_data.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
API = "https://data.humdata.org/api/3/action/package_show?id="

# dataset id -> resource names to fetch, in the order they matter to us
WANTED = {
    "cod-ab-nga": ["nga_admin_boundaries.shp.zip"],
    # The 2022 release is the current one but stops at admin 1. LGA-level
    # population only exists in the 2020 workbook, so both are fetched and
    # the 2020 sheet is the one the build script reads. See docs/02-data-notes.md.
    "cod-ps-nga": ["nga_admpop_2022.xlsx", "nga_admpop_2020.xlsx"],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resources(dataset: str) -> dict[str, dict]:
    with urllib.request.urlopen(API + dataset, timeout=120) as resp:
        payload = json.load(resp)
    if not payload.get("success"):
        raise SystemExit(f"HDX API refused {dataset}")
    result = payload["result"]
    print(f"{dataset}: {result['title']}")
    print(f"  licence   {result.get('license_title')}")
    print(f"  updated   {result.get('last_modified')}")
    return {r["name"]: r for r in result["resources"]}


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    for dataset, names in WANTED.items():
        available = resources(dataset)
        for name in names:
            resource = available.get(name)
            if resource is None:
                raise SystemExit(
                    f"  resource {name!r} is gone from {dataset}; "
                    f"available now: {sorted(available)}"
                )
            target = RAW / name
            if target.exists():
                print(f"  have      {name}  ({target.stat().st_size:,} bytes)")
            else:
                print(f"  fetching  {name} ...", end=" ", flush=True)
                urllib.request.urlretrieve(resource["url"], target)
                print(f"{target.stat().st_size:,} bytes")
            print(f"  sha256    {sha256(target)}")
            print(f"  source    {resource['url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
