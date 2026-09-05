# Nigeria Malaria SNT Spatial Intelligence System

*GeoDev Lab Africa, Cohort 1 — Week 1 project brief*

---

## The question

How have LGA-level malaria intervention strategies evolved under subnational
tailoring in Nigeria, how are these intervention trajectories associated with
observed malaria outcomes, and how does the 2026–2030 strategy respond to the
remaining spatial distribution of malaria burden?

This is a Week 1 framing. It is deliberately specific enough to test data
feasibility and deliberately does not yet promise causal effects, LGA-level
prevalence estimates, or projection to 2030.

---

## The study area

**Nigeria — all 36 states and the Federal Capital Territory, analysed at Local
Government Area (LGA) level: 774 LGAs.**

The LGA is the unit at which malaria intervention packages are actually
assigned under subnational tailoring, so it is the natural unit of analysis.
The 2021-2025 National Malaria Strategic Plan assigns a package to every one
of the 774, and the extracted dataset in this repository covers all of them.

The whole country is in scope rather than a single state or LGA because the
research question is explicitly comparative: it asks how intervention
strategies vary across the country and how that variation relates to burden.
Restricting the study area to one LGA would remove the variation the question
depends on.

Where the outcome data force a coarser unit, analysis is reported at state
level (37 units) and labelled as such. See *The honest problem with this
question* below.

---

## Why it matters

Nigeria's malaria response increasingly uses subnational tailoring, recognising
that malaria burden and the appropriate intervention mix vary geographically.
The National Malaria Strategic Plan 2021–2025 assigns an intervention package
to every one of the country's 774 Local Government Areas on the basis of
epidemiological stratification — case management and IPTp everywhere, then
different combinations of standard LLINs, PBO-LLINs, urban LLINs, seasonal
malaria chemoprevention, IPTi and iCCM.

Intervention choices, observed outcomes and subsequent strategic changes are
rarely examined together as a single spatial evidence chain. Stratification
decisions are documented in strategic-plan annexes; outcomes are reported in
survey reports; the next strategy is written separately again. Nobody holds
the three side by side at subnational level.

This project connects LGA-level intervention strategies with observed malaria
outcomes and the 2026–2030 strategic response.

The intended users are malaria programme decision-makers, researchers, policy
stakeholders and health intelligence teams who need to understand not only
where malaria burden remains, but how intervention choices and changing
strategies relate to that geography.

---

## The data I need

Every dataset with its source link beside it. Status is as verified on
5 September 2026; `docs/data-sources.md` holds the fuller register, including
licences and rejected sources.

| # | Dataset | Source link | Geographic unit | Status |
|---|---|---|---|---|
| 1 | NMSP 2021-2025 LGA intervention mix (Annex 1) | [mesamalaria.org PDF](https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf) · [WHO mirror](https://extranet.who.int/cpcd/sites/default/files/public_file_repository/NGA_Nigeria_National-Strategic-Plan-Malaria_2021-2025.pdf) | LGA (774) | **Obtained and extracted** |
| 2 | NMIS 2025 Key Indicators Report | [Nigeria Health Watch](https://nigeriahealthwatch.com/article/resources/malaria/nigeria-malaria-indicator-survey-nmis-key-indicators-2025/) | National, zone, state (37) | **Obtained and extracted** |
| 3 | NMIS 2025 microdata | [DHS Program, Nigeria MIS 2025](https://dhsprogram.com/methodology/survey/survey-display-632.cfm) | Would be cluster/state | **Not yet released** — DHS page inactive |
| 4 | NMIS 2021 microdata and cluster GPS | [DHS Program, Nigeria MIS 2021](https://dhsprogram.com/methodology/survey/survey-display-576.cfm) | Cluster, state, zone | Available; requires a DHS project request |
| 5 | Nigeria LGA boundaries (admin 2) | [HDX: Nigeria Subnational Administrative Boundaries](https://data.humdata.org/dataset/cod-ab-nga) · [GRID3 operational LGA boundaries](https://data.grid3.org/datasets/GRID3::grid3-nga-operational-lga-boundaries/about) | LGA (774) | Source verified, not yet downloaded |
| 6 | Nigeria state boundaries (admin 1) | [HDX, as above](https://data.humdata.org/dataset/cod-ab-nga) · [GRID3 operational state boundaries](https://data.grid3.org/datasets/GRID3::grid3-nga-operational-state-boundaries-/about) | State (37) | Source verified, not yet downloaded |
| 7 | Subnational population | [HDX: Nigeria Subnational Population Statistics](https://data.humdata.org/dataset/cod-ps-nga) | LGA | Source verified, not yet downloaded |
| 8 | Settlement extents | [GRID3 NGA Settlement Extents v4.0](https://data.humdata.org/dataset/grid3-nga-settlement-extents-v4-0) | Settlement | Optional, later |
| 9 | Roads / accessibility | [GRID3 NGA Roads v1.0](https://data.humdata.org/dataset/grid3-nga-roads-v1-0) | Network | Optional, later |
| 10 | NMSP 2026-2030 subnational strategy | No public source located | LGA or state | **Not located** — see below |
| 11 | Environmental / climate covariates | Source not yet identified | Grid / LGA | Later-stage requirement |

Two entries are deliberately without a link. Item 10 could not be found
publicly as of 5 September 2026 and needs a direct enquiry to NMEP rather than
more searching; item 11 is a later-stage requirement that has not been scoped.
Neither has been given an invented URL.

---

## Data sources

The table above carries a source link beside every dataset that has one. All
links were checked and returned HTTP 200 on 5 September 2026.

`docs/data-sources.md` holds the fuller register: formats, licences, the
checksum proving the NMSP PDF matches its published original, access
conditions for restricted survey microdata, and the sources that were checked
and **rejected**.

---

## What I would build

A geospatial intelligence system that lets a user explore malaria intervention
strategies and outcomes across Nigeria's subnational units.

The system will connect intervention profiles, intervention trajectories,
observed malaria outcomes and relevant contextual information. It will
eventually provide an interactive map and an API, with an AI-assisted interface
that can answer evidence-based questions about individual LGAs while showing
data provenance and the uncertainty attached to each answer.

Provisional progression over the twelve months:

| Months | Focus |
|---|---|
| 1–2 | Acquire and clean the spatial and intervention datasets |
| 3–4 | Reproducible processing workflow |
| 5 | Map interface |
| 6 | Spatial database and API |
| 7 | Automated testing |
| 8–10 | Analytics and modelling |
| 11 | AI agent over the system |
| 12 | Consolidation and documentation |

---

## The honest problem with this question

The Week 1 feasibility work surfaced one issue that the project must confront
rather than paper over.

**The intervention layer and the outcome layer are not at the same geographic
resolution.**

- The intervention strategy is assigned at **LGA** level — all 774 of them,
  confirmed and extracted.
- The 2025 malaria outcome is published at **state** level — 36 states and the
  FCT, from a survey of 20,312 households designed to be representative
  nationally, by residence, by geopolitical zone and by state.

Thirty-seven outcome values cannot support 774 independent intervention-effect
estimates. Any analysis that assigns a state's parasitaemia to each of its LGAs
and then correlates that with LGA intervention mix is measuring state-level
variation while claiming LGA-level insight.

This does not sink the project. It changes what the project can honestly claim,
and the choice between the available routes is a Month 2 decision:

1. **Analyse the intervention geography in its own right.** How the mix is
   distributed, how much within-state heterogeneity the stratification actually
   produces, which LGAs are treated unlike their neighbours. This needs no
   outcome data at all and is genuinely under-described.
2. **Do the outcome association at state level**, stating that resolution
   plainly, using LGA data aggregated to state (for example, the share of a
   state's LGAs receiving SMC) as the exposure.
3. **Pursue finer outcome data** — 2021 NMIS cluster GPS points, routine
   DHIS2/HMIS LGA data, or the modelled LGA-level surfaces produced for the SNT
   process — and treat each on its own merits, including its own error.

Week 1 is where this was found. Deciding it is Month 2.

---

*Last updated: 5 September 2026*
