# Nigeria Malaria SNT Spatial Intelligence System

A GeoDev Lab Africa Cohort 1 project mapping the geography of malaria
intervention assignments under subnational tailoring (SNT) in Nigeria.

## Research question

> **Where in Nigeria does subnational tailoring actually assign different
> malaria intervention mixes to neighbouring LGAs?**

## Study area

**Nigeria — 36 states and the FCT, at Local Government Area level: 774 LGAs.**

The LGA is the unit at which intervention packages are assigned under
subnational tailoring, so it is the unit of analysis. The whole country is in
scope because the question is comparative by construction — it is about where
assignments differ between adjacent places — but every measurement is local,
between an LGA and the LGAs it touches.

## The data

Four datasets, each with its source link, in
[`project-brief.md`](project-brief.md#the-data-i-need):

| # | Dataset | Source |
|---|---|---|
| 1 | NMSP 2021–2025 LGA intervention mix | [mesamalaria.org](https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf) |
| 2 | Nigeria LGA boundaries (admin 2) | [HDX `cod-ab-nga`](https://data.humdata.org/dataset/cod-ab-nga) |
| 3 | Nigeria state boundaries (admin 1) | [HDX `cod-ab-nga`](https://data.humdata.org/dataset/cod-ab-nga) |
| 4 | Nigeria subnational population | [HDX `cod-ps-nga`](https://data.humdata.org/dataset/cod-ps-nga) |

Dataset 1 is obtained and extracted. All four links were checked and returned
HTTP 200 on 5 September 2026.

## Project

Nigeria assigns malaria intervention packages to each of its 774 Local
Government Areas on the basis of epidemiological stratification. Those
assignments exist only as an alphabetical table in a strategic-plan annex, so
their geography has never been laid out. This project maps it, then builds
outward from there.

The goal is a reproducible geospatial intelligence system, not a static map.

## What is in the repository so far

```
├── project-brief.md                  Question, study area, data, and what gets built
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
3. **That mismatch set the scope.** Thirty-seven outcome values cannot support
   774 intervention-effect estimates, so the primary question is about the
   intervention geography itself — fully answerable at LGA level, and needing no
   outcome data. The outcome association becomes Question 2, to be reported at
   the resolution the data actually support. Both are set out in
   [`project-brief.md`](project-brief.md).
4. **The 2026–2030 NMSP could not be located publicly**, so no source link is
   claimed for it. That gap is recorded, not filled with a guess.

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
