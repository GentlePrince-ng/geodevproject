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

| # | Dataset | Why it is needed | Status |
|---|---|---|---|
| 1 | 2021–2025 NMSP LGA-level intervention mix | Defines the historical intervention strategy | **Obtained and extracted** |
| 2 | 2026–2030 NMSP subnational intervention strategy | Examines the strategic transition | **Not located** |
| 3 | 2025 Nigeria Malaria Indicator Survey | Observed malaria outcome, end of strategy period | **Partially obtained** (state-level report only) |
| 4 | 2021 Nigeria Malaria Indicator Survey | Baseline outcome, start of strategy period | Available, not yet requested |
| 5 | Nigeria LGA boundaries | Spatial unit of analysis | To verify |
| 6 | Nigeria state boundaries | Spatial reference and aggregation | To verify |
| 7 | Population data | Denominators and population-weighted context | To verify |
| 8 | Settlement extents | Spatial context, urban/rural | Optional, later |
| 9 | Roads / accessibility | Context | Optional, later |
| 10 | Environmental / climate data | Context and confounding | Later |

Items 5–10 are not yet confirmed and are marked as such deliberately. See
`docs/data-sources.md` for the source register.

---

## Data sources

See `docs/data-sources.md` for the full register, including URLs, formats,
geographic units and verification status. Every dataset claimed above either
has a verified source or is explicitly marked *to verify* / *not located*.

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
