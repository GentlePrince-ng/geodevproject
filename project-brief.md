# Nigeria Malaria SNT Spatial Intelligence System

*GeoDev Lab Africa, Cohort 1 — Week 1 project brief*

---

## The question

> **Where in Nigeria does subnational tailoring actually assign different
> malaria intervention mixes to neighbouring LGAs?**

Nigeria's malaria programme assigns an intervention package to each of its 774
Local Government Areas on the basis of epidemiological stratification. The
premise of subnational tailoring is that the right mix differs from place to
place. This question asks where that premise shows up on the ground: which LGA
boundaries are also intervention boundaries, and which parts of the country
receive a uniform package across wide areas.

It is answerable with data already obtained and verified. Every dataset it
requires is listed below with a working source link.

---

## The study area

**Nigeria — all 36 states and the Federal Capital Territory, analysed at Local
Government Area level: 774 LGAs.**

The LGA is the unit at which intervention packages are actually assigned under
subnational tailoring, so it is the unit of analysis. The extracted dataset in
this repository covers all 774.

The whole country is in scope rather than a single state or LGA because the
question is comparative by construction: it is about where intervention
assignments differ *between adjacent places*. Restricting the study area to one
LGA would remove the comparison the question is made of. The analysis is
nonetheless local — every measurement is between an LGA and the LGAs it touches,
not a national average.

---

## Why it matters

Subnational tailoring is meant to replace uniform national malaria policy with
locally-appropriate intervention mixes. Nigeria has done the tailoring: the
2021–2025 National Malaria Strategic Plan lists a package for every LGA, built
from case management, IPTp, three different net types, seasonal malaria
chemoprevention, IPTi and iCCM.

What nobody has laid out is the resulting **geography**. The assignments exist
as a 16-page table in a strategic-plan annex, ordered alphabetically by state.
In that form it is impossible to see whether tailoring produced genuinely local
differentiation, or whether in practice it mostly follows state lines — which
would mean the country is running state-level policy under a subnational label.

That distinction matters for planning. If intervention boundaries sit inside
states, then states are the wrong unit for procurement, campaign logistics and
supervision, and LGAs on either side of an internal boundary need different
things from the same state programme. If the boundaries mostly follow state
lines, the tailoring is coarser than it appears and the next planning round can
say so.

The intended users are malaria programme decision-makers, researchers, policy
stakeholders and health intelligence teams.

---

## The data I need

Four datasets. Every one has a source link beside it, and every link was checked
and returned HTTP 200 on 5 September 2026.

| # | Dataset | Source link | Format | Geographic unit | Status |
|---|---|---|---|---|---|
| 1 | NMSP 2021–2025 LGA intervention mix (Annex 1, pp. 75–90) | [mesamalaria.org](https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf) · [WHO mirror](https://extranet.who.int/cpcd/sites/default/files/public_file_repository/NGA_Nigeria_National-Strategic-Plan-Malaria_2021-2025.pdf) | PDF to CSV | LGA (774) | **Obtained, extracted, 774/774** |
| 2 | Nigeria LGA boundaries (admin 2) | [HDX `cod-ab-nga`](https://data.humdata.org/dataset/cod-ab-nga) · [GRID3 operational LGA boundaries](https://data.grid3.org/datasets/GRID3::grid3-nga-operational-lga-boundaries/about) | GeoPackage / SHP / GeoJSON | LGA (774) | Source verified, not yet downloaded |
| 3 | Nigeria state boundaries (admin 1) | [HDX `cod-ab-nga`](https://data.humdata.org/dataset/cod-ab-nga) · [GRID3 operational state boundaries](https://data.grid3.org/datasets/GRID3::grid3-nga-operational-state-boundaries-/about) | GeoPackage / SHP / GeoJSON | State (37) | Source verified, not yet downloaded |
| 4 | Nigeria subnational population | [HDX `cod-ps-nga`](https://data.humdata.org/dataset/cod-ps-nga) | XLSX / CSV | LGA | Source verified, not yet downloaded |

Dataset 1 is the intervention assignment. Datasets 2 and 3 supply the geometry
that defines adjacency, and let internal boundaries be told apart from state
boundaries. Dataset 4 turns a count of LGAs into a count of people, so that
"where does the mix change" can also answer "how many people live on each side".

Nothing else is required to answer the question as stated.

`docs/data-sources.md` holds the fuller register: licences, the SHA-256 checksum
proving the NMSP PDF matches its published original, access conditions for
restricted survey microdata, and the sources that were checked and **rejected**.

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
| 1–2 | Acquire and clean the spatial and intervention datasets; answer the primary question |
| 3–4 | Reproducible processing workflow |
| 5 | Map interface |
| 6 | Spatial database and API |
| 7 | Automated testing |
| 8–10 | Analytics and modelling |
| 11 | AI agent over the system |
| 12 | Consolidation and documentation |

---

## Where this goes next

The primary question is deliberately the one the available data can answer
properly. The wider programme it opens onto has two further questions, each
gated on data this project does not yet hold. They are **not** part of the
required data list above.

**Question 2 — do intervention mixes track observed malaria burden?**
The 2025 Nigeria Malaria Indicator Survey is already extracted in this
repository ([Key Indicators Report](https://nigeriahealthwatch.com/article/resources/malaria/nigeria-malaria-indicator-survey-nmis-key-indicators-2025/),
37 states), and the 2021 survey with cluster GPS is obtainable from the
[DHS Program](https://dhsprogram.com/methodology/survey/survey-display-576.cfm)
on request. The constraint is resolution, set out in the next section.

**Question 3 — how does the 2026–2030 strategy respond to remaining burden?**
Blocked. **No public source for the NMSP 2026–2030 could be located as of
5 September 2026.** It may be unpublished, restricted, or embedded in
funding-request material. This needs a direct enquiry to NMEP, not more
searching. No URL is given because none was found, and an invented one would be
worse than an honest gap. Until the document is obtained, Question 3 cannot be
attempted.

Environmental and climate covariates would also belong to this later phase. No
source has been selected yet, so none is claimed.

---

## The constraint that shaped this brief

Week 1 feasibility testing surfaced one finding that determined the scope above,
and it is worth stating plainly rather than discovering in Month 3.

**The intervention layer and the outcome layer are not at the same geographic
resolution.**

- Interventions are assigned at **LGA** level — all 774, confirmed and extracted
  from the strategic plan.
- The 2025 malaria outcome is published at **state** level — 37 units, from a
  survey of 20,312 households designed to be representative nationally, by
  residence, by geopolitical zone and by state. The DHS Program page for the
  2025 survey is inactive, so no microdata are currently distributed.

Thirty-seven outcome values cannot support 774 independent intervention-effect
estimates. Any analysis that assigns a state's parasitaemia to each of its LGAs
and then correlates that against LGA intervention mix is measuring state-level
variation while claiming LGA-level insight.

This is why the primary question is about the intervention geography itself.
That question is fully answerable at LGA level, needs no outcome data, and is
genuinely under-described. The outcome association is Question 2, and when it is
attempted it will be reported at the resolution the data actually support.

Full detail of what was tested and found is in `docs/data-feasibility.md`.

---

*Last updated: 5 September 2026*
