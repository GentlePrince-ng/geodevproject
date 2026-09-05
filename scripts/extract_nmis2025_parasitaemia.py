"""
Extract state-level malaria parasitaemia from the 2025 Nigeria Malaria
Indicator Survey Key Indicators Report (p. 4).

Week 1 feasibility test: at what geographic resolution is the 2025 malaria
OUTCOME published? Answer: national, geopolitical zone and state - not LGA.

This script exists to prove that finding rather than assert it: it pulls the
two parasitaemia indicators for all 36 states + FCT and checks the counts.

Usage:
    python scripts/extract_nmis2025_parasitaemia.py
"""

import csv
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data" / "raw" / "NMIS-2025-Key-Indicators.pdf"
OUT = ROOT / "data" / "processed" / "nmis_2025_state_parasitaemia.csv"

PARASITAEMIA_PAGE = 3  # 0-indexed: p. 4

# The report prints each zone's states, then a run of values per indicator.
# Zone membership is fixed, so we assert it rather than infer it.
ZONES = {
    "North Central": ["FCT - Abuja", "Benue", "Kogi", "Kwara", "Nasarawa", "Niger", "Plateau"],
    "North East": ["Adamawa", "Bauchi", "Borno", "Gombe", "Taraba", "Yobe"],
    "North West": ["Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Sokoto", "Zamfara"],
    "South South": ["Akwa Ibom", "Bayelsa", "Cross River", "Delta", "Edo", "Rivers"],
    "South East": ["Abia", "Anambra", "Ebonyi", "Enugu", "Imo"],
    "South West": ["Ekiti", "Lagos", "Ogun", "Ondo", "Osun", "Oyo"],
}
INDICATORS = ["rdt_positive_pct", "microscopy_positive_pct"]
NUM_RE = re.compile(r"^\d+\.\d$")


def parse(pdf_path):
    lines = [ln.strip() for ln in fitz.open(pdf_path)[PARASITAEMIA_PAGE].get_text().splitlines()]
    lines = [ln for ln in lines if ln]

    records, national = {}, {}
    for zone, states in ZONES.items():
        # Each zone prints its state names, then the values for both indicators.
        # The two runs are sometimes contiguous and sometimes split by the
        # indicator label, so collect numbers until we have the expected count.
        cursor = lines.index(zone) + 1 + len(states)

        # The two blocks that open each half-page table repeat the National value
        # ahead of each indicator's state values.
        repeats_national = zone in ("North Central", "South South")
        per_indicator = len(states) + (1 if repeats_national else 0)
        expected = per_indicator * len(INDICATORS)

        values = []
        while len(values) < expected and cursor < len(lines):
            if NUM_RE.match(lines[cursor]):
                values.append(float(lines[cursor]))
            cursor += 1
        if len(values) != expected:
            sys.exit(f"{zone}: got {len(values)} values, expected {expected}")

        for n, indicator in enumerate(INDICATORS):
            run = values[n * per_indicator:(n + 1) * per_indicator]
            if repeats_national:
                national[indicator] = run[0]
                run = run[1:]
            for state, value in zip(states, run):
                records.setdefault(state, {"state": state, "zone": zone})[indicator] = value
    return records, national


def main():
    if not PDF.exists():
        print(f"Source PDF not present: {PDF.name}")
        print("The 2025 NMIS Key Indicators Report is not available as a direct")
        print("public download; it is released via NMEP and republished by Nigeria")
        print("Health Watch behind a subscription. See docs/data-sources.md.")
        print("")
        print("The extracted output is committed at:")
        print(f"  {OUT.relative_to(ROOT)}")
        sys.exit(0)

    records, national = parse(PDF)
    rows = [records[s] for zone in ZONES for s in ZONES[zone]]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["state", "zone", *INDICATORS])
        writer.writeheader()
        writer.writerows(rows)

    print(f"States extracted : {len(rows)} (expected 37: 36 states + FCT)")
    print(f"National RDT     : {national['rdt_positive_pct']}%")
    print(f"National microscopy: {national['microscopy_positive_pct']}%")
    print(f"Written to       : {OUT.relative_to(ROOT)}")
    hi = sorted(rows, key=lambda r: -r["rdt_positive_pct"])[:5]
    lo = sorted(rows, key=lambda r: r["rdt_positive_pct"])[:5]
    print("\nHighest RDT positivity:", ", ".join(f"{r['state']} {r['rdt_positive_pct']}" for r in hi))
    print("Lowest RDT positivity :", ", ".join(f"{r['state']} {r['rdt_positive_pct']}" for r in lo))


if __name__ == "__main__":
    main()
