# Data source register

Every dataset the project claims to need appears here with either a verified
source or an explicit *to verify* / *not located* marker. No invented links.

Verification status was checked on **5 September 2026**.

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

## To verify

| Dataset | Candidate source | Why unverified |
|---|---|---|
| Nigeria LGA boundaries | [GRID3 data portal](https://data.grid3.org/) (responds) | Specific boundary layer, vintage and licence not yet checked |
| Nigeria state boundaries | GRID3, as above | As above |
| Population data | GRID3 / WorldPop | Not yet checked |
| Settlement extents | GRID3 | Optional; not yet checked |
| Roads / accessibility | OpenStreetMap | Optional; not yet checked |
| Environmental / climate | To be identified | Later-stage requirement |

The boundary layer matters more than its position in this table suggests: the
NMSP LGA names will have to join to it, and the names are known to be
non-standard (see `docs/data-feasibility.md`).

---

## Not located

| Dataset | Status |
|---|---|
| NMSP 2026–2030 subnational intervention strategy | **Not located as of 5 Sep 2026.** No public PDF found via general search. The document may not be published, may be restricted, or may exist only inside NMEP/Global Fund funding-request material. Needs a direct enquiry rather than more searching. |

Until this is obtained, the third clause of the research question — how the
2026–2030 strategy responds to remaining burden — cannot be answered. The first
two clauses can.

---

## Rejected sources

| Source | Reason for rejection |
|---|---|
| `Final_High-Quality_Malaria_Interventions_by_State.csv` and `Malaria_Interventions_by_State.csv` (local files, Feb 2025) | **Unreliable.** The Kano row lists Ilorin LGAs (which are in Kwara) and the Katsina row lists Lagos LGAs (Mushin, Oshodi-Isolo, Surulere, Ikeja). These state-to-LGA assignments are wrong. The files appear to be a generated summary rather than an extraction from the NMSP, and are not used. Annex 1 of the NMSP is used instead. |
