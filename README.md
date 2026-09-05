# Nigeria Malaria SNT Spatial Intelligence System

A GeoDev Lab Africa Cohort 1 project examining the spatial evolution of malaria
intervention strategies under subnational tailoring (SNT) in Nigeria.

## Research question

How have LGA-level malaria intervention strategies evolved under subnational
tailoring in Nigeria, how are these intervention trajectories associated with
observed malaria outcomes, and how does the 2026–2030 strategy respond to the
remaining spatial distribution of malaria burden?

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
# fetch the sources listed in data/raw/README.md, then:
python scripts/extract_nmsp_annex1.py
python scripts/extract_nmis2025_parasitaemia.py
```

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
