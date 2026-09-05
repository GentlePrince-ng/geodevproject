# Nigeria Malaria SNT Spatial Intelligence System

A GeoDev Lab Africa Cohort 1 project examining the spatial evolution of malaria
intervention strategies under subnational tailoring (SNT) in Nigeria.

## Research question

How have LGA-level malaria intervention strategies evolved under subnational
tailoring in Nigeria, how are these intervention trajectories associated with
observed malaria outcomes, and how does the 2026–2030 strategy respond to the
remaining spatial distribution of malaria burden?

## Study area

**Nigeria — 36 states and the FCT, at Local Government Area level: 774 LGAs.**

The LGA is the unit at which intervention packages are assigned under
subnational tailoring, so it is the unit of analysis. Where outcome data are
only published at state level, results are reported at state level (37 units)
and labelled as such.

## Project

Nigeria assigns malaria intervention packages to each of its 774 Local
Government Areas on the basis of epidemiological stratification. This project
combines that intervention geography with observed malaria outcomes, boundary
data and contextual layers to examine the relationship between intervention
choice, intervention trajectories and observed burden.

The goal is a reproducible geospatial intelligence system, not a static map.

## What is in the repository so far

```
├── project-brief.md                  Five-part project definition (Week 1 milestone)
├── docs/
│   ├── data-sources.md               Source register for every dataset claimed
│   └── data-feasibility.md           Log of what was actually tested and found
├── scripts/
│   ├── extract_nmsp_annex1.py        NMSP 2021–2025 Annex 1 → LGA intervention mix
│   └── extract_nmis2025_parasitaemia.py   NMIS 2025 → state-level parasitaemia
└── data/
    ├── raw/                          Public source PDFs (not committed; see data/raw/README.md)
    └── processed/                    Extracted, machine-readable tables
```

## Week 1 headline findings

1. **The intervention layer is real and complete.** Annex 1 of the National
   Malaria Strategic Plan 2021–2025 gives the intervention mix for all
   **774 LGAs** across 36 states and the FCT, and it extracts cleanly from the
   PDF — 774/774 rows, no parse failures, seven distinct intervention packages.
2. **The 2025 outcome layer is state-level, not LGA-level.** The 2025 NMIS Key
   Indicators Report publishes national, geopolitical-zone and state estimates
   only. The DHS Program page for the 2025 Nigeria MIS is not yet active, so no
   microdata are currently distributed.
3. **This mismatch is the central methodological problem of the project**, and
   it is stated openly in `project-brief.md` rather than assumed away.

## Reproducing the extractions

```bash
git clone https://github.com/GentlePrince-ng/geodevproject.git
cd geodevproject
pip install pymupdf
python scripts/extract_nmsp_annex1.py
```

The first script needs nothing else: it downloads the National Malaria
Strategic Plan from its published URL, verifies the file against a recorded
SHA-256 checksum, and rebuilds the 774-row intervention table. Expected output:

```
Source verified: SHA-256 2d363bae79bfca34...
Rows extracted : 774 (expected 774)
States/FCT     : 37
Distinct mixes : 7
```

```bash
python scripts/extract_nmis2025_parasitaemia.py
```

The second needs the 2025 NMIS Key Indicators Report, which has no direct
public download (see `docs/data-sources.md`). Without it the script explains
where to get the report and exits cleanly — its extracted output is committed,
so the data are in the repository either way.

Requires Python 3 and `pymupdf`.

## Data ethics

This repository contains only data derived from public documents. Restricted
survey microdata and Nigeria Health Watch project data are never committed —
see `.gitignore`.

## Programme

Built through GeoDev Lab Africa, Cohort 1.
See `project-brief.md` for the initial project definition.

## Status

Month 1 — project definition and data feasibility.
