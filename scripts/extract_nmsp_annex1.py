"""
Extract Annex 1 (LGA-level intervention mixes) from the Nigeria National
Malaria Strategic Plan 2021-2025.

Week 1 feasibility test: is the LGA intervention layer actually extractable
from the NMSP PDF, and does it cover all 774 LGAs?

The annex runs pp. 75-90 as a five-column table:
    STATE | LGA | city | iccm | mix

PyMuPDF returns the cells in reading order, one per line, so each record is
five consecutive lines anchored on the intervention-mix line (starts "CM+").

Usage:
    python scripts/extract_nmsp_annex1.py
"""

import csv
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data" / "raw" / "NMSP-Nigeria-2021-2025.pdf"
OUT = ROOT / "data" / "processed" / "nmsp_2021_2025_lga_intervention_mix.csv"

ANNEX_PAGES = range(74, 90)  # 0-indexed: pp. 75-90
MIX_RE = re.compile(r"^CM\+")
ICCM_VALUES = {"iCCM", "No iCCM"}
EXPECTED_LGAS = 774


def extract(pdf_path):
    doc = fitz.open(pdf_path)
    rows, problems = [], []

    for page_no in ANNEX_PAGES:
        lines = [ln.strip() for ln in doc[page_no].get_text().splitlines()]
        for i, line in enumerate(lines):
            if not MIX_RE.match(line):
                continue
            # Walk back: iccm, city, lga, state
            iccm, city, lga, state = (lines[i - k] for k in (1, 2, 3, 4))
            if iccm not in ICCM_VALUES:
                problems.append((page_no + 1, line, f"unexpected iccm value {iccm!r}"))
                continue
            rows.append(
                {
                    "state": state,
                    "lga": lga,
                    "city": city or "",
                    "iccm": iccm,
                    "intervention_mix": line,
                    "source_page": page_no + 1,
                }
            )
    return rows, problems


def main():
    if not PDF.exists():
        sys.exit(f"Source PDF not found: {PDF}\nSee docs/data-sources.md for the download link.")

    rows, problems = extract(PDF)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    states = sorted({r["state"] for r in rows})
    mixes = sorted({r["intervention_mix"] for r in rows})

    print(f"Rows extracted : {len(rows)} (expected {EXPECTED_LGAS})")
    print(f"States/FCT     : {len(states)}")
    print(f"Distinct mixes : {len(mixes)}")
    print(f"iCCM LGAs      : {sum(1 for r in rows if r['iccm'] == 'iCCM')}")
    print(f"Written to     : {OUT.relative_to(ROOT)}")
    if problems:
        print(f"\nParse problems ({len(problems)}):")
        for p in problems:
            print("  ", p)
    print("\nDistinct intervention mixes:")
    for m in mixes:
        print(f"  {sum(1 for r in rows if r['intervention_mix'] == m):>4}  {m}")


if __name__ == "__main__":
    main()
