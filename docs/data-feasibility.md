# Data feasibility log

Week 1 of GeoDev Lab Africa asks one question: **does this data exist, and can
I work with it?** This log records what was actually tested on
**5 September 2026**, not what was hoped for.

---

## Test 1 — The 2021–2025 LGA intervention mix

### What I expected

An LGA-level intervention assignment, probably buried in a PDF, probably
incomplete, probably requiring manual transcription.

### What I found

Annex 1 of the National Malaria Strategic Plan 2021–2025 (pp. 75–90) is a
five-column table headed *"LGA Level Intervention Mixes based on
Epidemiological Stratification"*:

```
STATE | LGA | city | iccm | mix
```

It extracts cleanly with PyMuPDF. Cells arrive in reading order, one per line,
so each record is five consecutive lines anchored on the mix value.

### Format

PDF, 106 pages, text-based (not scanned). Extractor:
`scripts/extract_nmsp_annex1.py`. Output:
`data/processed/nmsp_2021_2025_lga_intervention_mix.csv`.

### Coverage

| Check | Result |
|---|---|
| Rows extracted | **774 / 774** |
| Parse failures | **0** |
| States + FCT | 37 |
| Duplicate state+LGA pairs | 0 |
| LGAs flagged for iCCM | 12 |
| Distinct intervention mixes | 7 |

State counts match expectation throughout (Kano 44, Katsina 34, Oyo 33,
Osun 30, Bayelsa 8, FCT 6).

### The seven intervention packages

| LGAs | Mix |
|---:|---|
| 319 | CM + IPTp + LLINs + IPTi |
| 258 | CM + IPTp + PBO-LLINs + SMC |
| 106 | CM + IPTp + LLINs + SMC |
| 43 | CM + IPTp + UrbanLLINs + IPTi |
| 24 | CM + IPTp + PBO-LLINs + IPTi |
| 19 | CM + IPTp + UrbanLLINs + SMC |
| 5 | CM + IPTp + UrbanLLINs |

Case management and IPTp are universal. The stratification is therefore
entirely about the **net type** (standard, PBO, urban) and the **chemo-
prevention** (SMC vs IPTi) — a cleaner two-axis structure than expected, and a
good basis for a typology.

### Problems found

1. **Non-standard LGA names.** Twelve LGA names carry numeric disambiguation
   suffixes where a name repeats across states: `Obi1` (Benue) / `Obi2`
   (Nasarawa), `Bassa1` (Kogi) / `Bassa2` (Plateau), `Ifelodun1` (Kwara) /
   `Ifelodun2` (Osun), `Irepodun1` / `Irepodun2`, `Surulere1` (Lagos) /
   `Surulere2` (Oyo), `Nasarawa1` (Kano) / `Nasarawa2` (Nasarawa). These will
   not join to any standard boundary file without cleaning.
2. **Spelling variants.** e.g. `Umu-Neochi` (Umunneochi), `Ganaye` (Ganye),
   `Gireri` (Girei), `Isuikwato` (Isuikwuato), `Yenegoa` (Yenagoa),
   `Obi Nwa` (Obingwa), `Oturkpo` (Otukpo). The `city` column has `Iilorin`
   for Ilorin.
3. **No codes.** There is no LGA PCODE anywhere in the annex — the join to
   boundaries has to go through names. This is the single biggest technical
   risk in Month 2.
4. **The `city` column is sparse** — 16 named cities, blank elsewhere. It is
   the urban-LLIN trigger, not a general urban classification.

### Decision

**Proceed.** The intervention layer is complete, machine-readable and better
structured than anticipated. Name-to-boundary reconciliation is a known,
bounded Month 2 task.

---

## Test 2 — The 2025 malaria outcome

### What I expected

Either 2025 NMIS microdata with cluster GPS, or at worst a state-level report.

### What I found

**No 2025 NMIS microdata are currently distributed.** The DHS Program page for
the Nigeria MIS 2025 (`survey-display-632.cfm`) returns *"This page is in the
process of being created or has temporarily been inactivated."* The 2021 survey
page by contrast is fully live with reports and dataset listings.

What does exist is the **2025 NMIS Key Indicators Report** (NMEP/NPC/WHO/CMS,
February 2026, 6 pages). Fieldwork ran August–November 2025; 20,312 households
and 23,815 de facto women.

Its geographic breakdowns are **national, geopolitical zone, and state**. The
strings "LGA", "local government", "cluster" and "GPS" do not appear anywhere in
the document.

### Format

PDF, 6 pages. Extractor:
`scripts/extract_nmis2025_parasitaemia.py`. Output:
`data/processed/nmis_2025_state_parasitaemia.csv` — 37 rows (36 states + FCT),
RDT and microscopy positivity in children 6–59 months.

### Coverage

| Check | Result |
|---|---|
| States extracted | **37 / 37** |
| National RDT positivity | 35.1% |
| National microscopy positivity | 15.2% |
| Highest RDT | Ebonyi 67.7, Zamfara 63.9, Taraba 52.3, Bauchi 50.7, Sokoto 50.1 |
| Lowest RDT | Lagos 1.5, Plateau 13.5, Delta 17.6, Borno 18.8, Ogun 19.7 |

**Note on the headline figure.** Public commentary citing "about 15% prevalence"
is quoting the *microscopy* result. The *RDT* result is 35.1%. Both are in the
report; they are different tests, not different estimates of the same thing.
Any figure used in this project must state which.

### Problems found

1. **Resolution mismatch — the central problem.** The intervention layer is
   774 LGAs; the 2025 outcome layer is 37 states. See `project-brief.md` for
   what this does to the question and the three routes forward.
2. **No microdata means no re-analysis.** Without the household file we cannot
   compute any indicator the report did not print, apply our own definitions,
   or produce subnational estimates below state.
3. **Sampling design not yet examined.** The Key Indicators Report does not
   describe the sample design. Whether the survey was even *powered* for state
   estimates in every state needs checking against the final report when it is
   published.
4. **Baseline comparability unresolved.** Comparing 2025 to 2021 requires the
   2021 survey's state estimates on a matching definition. Not yet done.

### Decision

**Proceed, with the question's scope restated.** Clauses 1 and 2 of the research
question are answerable now. Clause 3 depends on the 2026–2030 NMSP, which has
not been located.

---

## Test 3 — Local files rejected

Two local CSVs (`Final_High-Quality_Malaria_Interventions_by_State.csv`,
`Malaria_Interventions_by_State.csv`, Feb 2025) claimed to hold state-level
intervention mixes. They were checked against the NMSP and **rejected**: the
Kano row lists Ilorin LGAs, which are in Kwara, and the Katsina row lists
Mushin, Oshodi-Isolo, Surulere and Ikeja, which are in Lagos. The
state-to-LGA assignments are wrong.

This is worth recording as a method point: the convenient pre-made file was
wrong, and the 106-page PDF was right. The extraction cost about an hour.

---

## Open questions for Month 2

1. Which authoritative LGA boundary file, at which vintage, and does it carry
   PCODEs? (GRID3 is the candidate.)
2. How many of the 774 NMSP LGA names join to it cleanly, and what is the
   reconciliation rule for the rest?
3. Does the 2026–2030 NMSP exist publicly, and if not, who do we ask?
4. Can 2021 NMIS cluster GPS data be obtained, and what would it legitimately
   support at subnational level?
5. Is there a routine-data (DHIS2/HMIS) LGA outcome series, and what is its
   quality?
6. Do the LGA-level modelled surfaces produced for Nigeria's SNT process exist
   in an obtainable form? They would resolve the mismatch directly — but they
   are model output, not observation, and would have to be treated as such.
