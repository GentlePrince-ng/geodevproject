# Data source register

Every dataset the project claims to need appears here with either a verified
source or an explicit *not located* marker. No invented links.

The **four datasets required for the primary question** are all in the first and
third sections below, each with a working link:

1. NMSP 2021-2025 LGA intervention mix
2. Nigeria LGA boundaries (admin 2)
3. Nigeria state boundaries (admin 1)
4. Nigeria subnational population

Everything else in this file is either already-extracted supporting data, a
later-phase dataset, or a source that was checked and rejected.

All links were checked on **5 September 2026** and returned HTTP 200.

---

## Confirmed and on the machine

| Dataset | Source | Format | Geographic unit | Status |
|---|---|---|---|---|
| NMSP 2021–2025, Annex 1: LGA-level intervention mixes | [MESA resource hub copy](https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf) | PDF (pp. 75–90), extracted to CSV | LGA (774) | **Verified** |
| NMIS 2025 Key Indicators Report | NMEP/NPC/WHO/CMS/Next-Gen DPs, Feb 2026. Republished by [Nigeria Health Watch](https://nigeriahealthwatch.com/article/resources/malaria/nigeria-malaria-indicator-survey-nmis-key-indicators-2025/) | PDF (6 pp.), extracted to CSV | National, zone, state (37) | **Verified** |

The NMSP PDF was confirmed byte-identical to the MESA copy by SHA-256
checksum — see `data/raw/README.md`. A second identical copy is mirrored at
the [WHO CPCD repository](https://extranet.who.int/cpcd/sites/default/files/public_file_repository/NGA_Nigeria_National-Strategic-Plan-Malaria_2021-2025.pdf).

Recommended citation for the survey report: National Malaria Elimination
Programme (NMEP) [Nigeria], National Population Commission (NPC) [Nigeria],
World Health Organization (WHO), Corona Management Systems (CMS), and Next-Gen
DPs LLC. 2026. *Nigeria Malaria Indicator Survey 2025 Key Indicators Report.*
Abuja, Nigeria.

---

## Available, not yet requested

| Dataset | Source | Format | Geographic unit | Status |
|---|---|---|---|---|
| 2021 Nigeria MIS — full microdata | [DHS Program, Nigeria MIS 2021](https://dhsprogram.com/methodology/survey/survey-display-576.cfm) | Survey datasets (registration required) | Survey clusters, state, zone | Page live; access requires a DHS project request |
| 2021 Nigeria MIS — GPS cluster data | Same survey page, GPS dataset | Shapefile of cluster centroids (displaced) | Cluster | Listed; access requires approval |
| 2021 Nigeria MIS — Atlas of Key Indicators (ATR22) | Same survey page | PDF | State | Public download |

**Note on restricted data.** DHS microdata are licensed to a named project and
must not be redistributed. Nothing from a DHS dataset will be committed to this
repository — only derived aggregates, if the licence permits.

---

## Source verified, not yet downloaded

All links below returned HTTP 200 on 5 September 2026.

| Dataset | Source | Format | Geographic unit | Licence |
|---|---|---|---|---|
| Nigeria subnational administrative boundaries (admin 0-2) | [HDX `cod-ab-nga`](https://data.humdata.org/dataset/cod-ab-nga) | Geodatabase, SHP, GeoJSON, XLSX | LGA (admin 2) and state (admin 1) | CC BY-IGO |
| Nigeria operational LGA boundaries | [GRID3 Data Hub](https://data.grid3.org/datasets/GRID3::grid3-nga-operational-lga-boundaries/about) | Feature layer / SHP / GeoJSON | LGA (774 records) | CC BY 4.0 |
| Nigeria operational state boundaries | [GRID3 Data Hub](https://data.grid3.org/datasets/GRID3::grid3-nga-operational-state-boundaries-/about) | Feature layer / SHP / GeoJSON | State | CC BY 4.0 |
| Nigeria subnational population statistics | [HDX `cod-ps-nga`](https://data.humdata.org/dataset/cod-ps-nga) | XLSX / CSV | LGA | CC BY-IGO |
| GRID3 NGA Settlement Extents v4.0 | [HDX](https://data.humdata.org/dataset/grid3-nga-settlement-extents-v4-0) | SHP / GeoJSON | Settlement | See dataset page |
| GRID3 NGA Roads v1.0 | [HDX](https://data.humdata.org/dataset/grid3-nga-roads-v1-0) | SHP / GeoJSON | Network | See dataset page |

**Why the OCHA Common Operational Dataset (`cod-ab-nga`) is listed first.** It
is the boundary set most likely to carry admin-2 **PCODEs**, and the NMSP
intervention table has no codes at all — only names, some of them
non-standard. The join key is the central technical problem of Month 2, so the
boundary source is chosen for its identifiers, not just its geometry. The
GRID3 operational boundaries carry 774 LGA records and are the cross-check.

Nothing in this group has been downloaded yet. Downloading and testing the
name join is the first Month 2 task.

---

## Not located

| Dataset | Status |
|---|---|
| NMSP 2026–2030 subnational intervention strategy | **Not located as of 5 Sep 2026.** No public PDF found via general search. The document may not be published, may be restricted, or may exist only inside NMEP/Global Fund funding-request material. Needs a direct enquiry rather than more searching. |

This document is **not** required for the primary question. It gates Question 3
in `project-brief.md` — how the 2026-2030 strategy responds to remaining burden
— which is deferred until the document can be obtained. It is listed here so
that the gap is on the record rather than quietly dropped.

---

## Rejected sources

| Source | Reason for rejection |
|---|---|
| `Final_High-Quality_Malaria_Interventions_by_State.csv` and `Malaria_Interventions_by_State.csv` (local files, Feb 2025) | **Unreliable.** The Kano row lists Ilorin LGAs (which are in Kwara) and the Katsina row lists Lagos LGAs (Mushin, Oshodi-Isolo, Surulere, Ikeja). These state-to-LGA assignments are wrong. The files appear to be a generated summary rather than an extraction from the NMSP, and are not used. Annex 1 of the NMSP is used instead. |
