# Data note — Week 2 (data acquisition)

*Nigeria Malaria SNT Spatial Intelligence System. Written 13 September 2026.*

**Question this data serves:** where in Nigeria does subnational tailoring
actually assign different malaria intervention mixes to neighbouring LGAs?

Answering it needs three things: the intervention mix per LGA (a table), LGA
and state boundaries (so "neighbouring" means something), and population (so a
difference between two LGAs can be weighted by who lives there). Those are the
three datasets below. All are downloaded, opened in QGIS, and joined into one
GeoPackage.

Everything here was downloaded on **13 September 2026** by
`scripts/download_cod_data.py`, which resolves each file through the HDX API
and prints its SHA-256. Raw downloads are git-ignored; the derived GeoPackage
is committed, so the repository can be opened without downloading anything.

| # | Dataset | Features | Geometry | Source |
|---|---|---|---|---|
| 1 | NMSP 2021–2025 Annex 1 intervention mixes | 774 rows | none (table) | [MESA copy of the NMSP](https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf) |
| 2 | Nigeria administrative boundaries (COD-AB) | 774 LGAs, 37 states | MultiPolygon | [HDX `cod-ab-nga`](https://data.humdata.org/dataset/cod-ab-nga) |
| 3 | Nigeria subnational population (COD-PS) | 773 LGA rows | none (table) | [HDX `cod-ps-nga`](https://data.humdata.org/dataset/cod-ps-nga) |

---

## 1. NMSP 2021–2025, Annex 1 — intervention mix by LGA

**Source.** National Malaria Strategic Plan 2021–2025, Annex 1, pages 75–90.
Link: <https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf>
(mirrored at [WHO CPCD](https://extranet.who.int/cpcd/sites/default/files/public_file_repository/NGA_Nigeria_National-Strategic-Plan-Malaria_2021-2025.pdf)).
Extracted in Week 1 by `scripts/extract_nmsp_annex1.py`, which checks the PDF's
SHA-256 (`2d363bae…`) before parsing.

**Features.** 774 rows, one per LGA. No geometry — this is the attribute table
the whole project hangs on.

**Key columns.** `state`, `lga`, `city`, `iccm`, `intervention_mix`,
`source_page`.

**What is in it.** Seven distinct mixes across 774 LGAs:

| Intervention mix | LGAs |
|---|---|
| CM+IPTp+LLINs+IPTi | 319 |
| CM+IPTp+PBO-LLINs+SMC | 258 |
| CM+IPTp+LLINs+SMC | 106 |
| CM+IPTp+UrbanLLINs+IPTi | 43 |
| CM+IPTp+PBO-LLINs+IPTi | 24 |
| CM+IPTp+UrbanLLINs+SMC | 19 |
| CM+IPTp+UrbanLLINs | 5 |

Case management and IPTp appear in all 774, so the tailoring is really two
axes, and the GeoPackage splits them into their own columns:

- `net_type` — LLINs 425, PBO-LLINs 282, UrbanLLINs 67
- `chemoprevention` — IPTi 386, SMC 383, none 5

**Gaps and things noticed.**

- **No PCODEs.** Not one code anywhere in the annex — LGAs are identified by
  name only. This is the central technical problem of the project and is dealt
  with in section 4.
- `city` is populated for only 67 of 774 rows; it is filled in exactly for the
  urban-net LGAs and blank elsewhere. It is not a missing value, it is a field
  that only applies to urban tailoring.
- `iccm` is "No iCCM" for 762 LGAs and "iCCM" for 12. Worth confirming against
  the NMSP text before drawing anything from it — 12 is a suspiciously small
  number for a national strategy.
- The five LGAs with no chemoprevention at all are all in Lagos
  (Ajeromi-Ifelodun, Apapa, Mushin, Oshodi-Isolo, Surulere). Dense urban Lagos
  getting urban nets and no SMC or IPTi is plausible, not an extraction error.

---

## 2. OCHA Common Operational Dataset — administrative boundaries

**Source.** HDX dataset `cod-ab-nga`, "Nigeria - Subnational Administrative
Boundaries". Link: <https://data.humdata.org/dataset/cod-ab-nga>.
Resource used: `nga_admin_boundaries.shp.zip`, 10,272,752 bytes, SHA-256
`4600b159107bbb5069cecbe2e308310deb8a3c0e0d83e05939c254dfae4d0361`.
Licence CC BY-IGO. HDX last modified 16 April 2026; boundaries themselves are
version `v01`, valid from **17 April 2019**.

**Why this source and not GRID3.** The COD carries admin-2 PCODEs. The NMSP
table has no codes, so the boundary layer has to supply the identifier that
everything downstream joins on. GRID3's operational boundaries remain the
cross-check, not the base.

**Features and geometry.** The zip holds ten layers. Two are used:

| Layer | Features | Geometry | Used |
|---|---|---|---|
| `nga_admin1` | 37 | Polygon / MultiPolygon | yes — states + FCT |
| `nga_admin2` | 774 | Polygon / MultiPolygon | yes — LGAs |
| `nga_admin0` | 1 | MultiPolygon | no |
| `nga_admin3` | 714 | Polygon / MultiPolygon | no — see below |
| `nga_senatorialdistricts` | 109 | Polygon / MultiPolygon | no |
| `nga_admincapitals` | 714 | Point | no |

CRS is **EPSG:4326** on every layer. All 774 LGA geometries and all 37 state
geometries pass `is_valid` — no self-intersections to repair. Total area sums
to 909,750 km²; bounding box 2.67–14.68 E, 4.27–13.89 N, which is Nigeria.

**Key columns (admin 2).** `adm2_pcode` (the join key, e.g. `NG001001`),
`adm2_name`, `adm1_name`, `adm1_pcode`, `area_sqkm`, `sendist_en`,
`center_lat`, `center_lon`.

**Gaps and things noticed.**

- **Thirteen columns are null in all 774 rows** — the alternate-name slots
  (`adm2_name1/2/3` and the same for adm0/adm1), the alternate-language slots
  (`lang1/2/3`) and `valid_to`. They are schema placeholders the Nigeria
  extract never fills. `scripts/build_admin_gpkg.py` drops them rather than
  ship 13 empty fields. Losing the alternate-name slots is a real cost: they
  are exactly where a spelling crosswalk would have lived if OCHA had filled
  them, and their emptiness is why section 4 has to be done by hand.
- **`nga_admin3` is not a national ward layer.** It has 714 features covering
  only Borno (310), Adamawa (226) and Yobe (178) — the three BAY states of the
  humanitarian response. Nigeria has roughly 8,800 wards. Anyone treating this
  as "wards" would silently analyse 3 states and call it a country.
- The boundaries are **valid from 2019**, while the NMSP was published in 2021.
  Both count 774 LGAs, and Nigeria has not created an LGA since 1996, so the
  vintage gap is recorded rather than treated as a problem.

---

## 3. OCHA Common Operational Dataset — subnational population

**Source.** HDX dataset `cod-ps-nga`, "Nigeria - Subnational Population
Statistics". Link: <https://data.humdata.org/dataset/cod-ps-nga>.
Resource used: `nga_admpop_2020.xlsx`, 1,672,647 bytes, SHA-256
`ccd4eff57b3ed3fde3afe2303580fca701b089b1a75a5f8336da823e1640b6cd`, sheet
`nga_admpop_adm2_2020`. Licence CC BY-IGO.

**Features.** 773 rows, one per LGA. No geometry; joins to the boundaries on
`ADM2_PCODE`.

**Key columns.** `ADM2_PCODE`, `ADM2_NAME`, `ADM1_NAME`, `T_TL` (total),
`F_TL` / `M_TL`, and 5-year age-sex bands `F_00_04` … `M_80plus`. Only two are
carried into the GeoPackage: `pop_total_2020` and `pop_u5_2020` (`F_00_04` +
`M_00_04`), because SMC targets children 3–59 months and the under-5 count is
the denominator the chemoprevention axis is actually about.

Totals: **204,909,220** people, of whom **32,207,346** are under five.

**Gaps and things noticed — three, and the first one nearly cost a day.**

- **The current release has no LGA data.** `nga_admpop_2022.xlsx` is the
  headline resource on the dataset page and it stops at admin 1: 37 rows and
  nothing below. LGA population only exists in the older
  `nga_admpop_2020.xlsx`. Taking the newest file would have left the project
  with no LGA denominator at all. The downloader fetches both and the build
  script reads the 2020 sheet.
- **773 LGAs, not 774. Bakassi (`NG009005`, Cross River) has no population
  row.** Bakassi was ceded to Cameroon under the 2002 ICJ ruling and the 2006
  census did not enumerate it, so the projection has nothing to project from.
  The boundary layer still draws it. In the GeoPackage Bakassi is the one LGA
  with a null `pop_total_2020` — kept, not dropped, and any per-capita measure
  has to exclude it explicitly.
- **The `nga_admpop_adm1_2020` sheet has 774 rows but only 37 of them contain
  data.** 737 rows are blank padding, presumably left over from a copy of the
  LGA sheet. Reading that sheet with a naive row count gives a state table that
  claims 774 states.

---

## 4. The join — the thing that could have sunk the project

The NMSP has names, the boundaries have PCODEs, and nothing connects them.
Testing that join before building anything was the whole point of this week.

`scripts/build_admin_gpkg.py` matches on **state + normalised LGA name** in
three passes, and raises rather than warns if anything is left over:

| Pass | Matched | What it handles |
|---|---|---|
| Exact, after lowercasing and stripping punctuation | 746 | the ordinary case |
| Numeric-suffix strip | 12 | `Obi1`/`Obi2`, `Bassa1`/`Bassa2`, `Nasarawa1`/`Nasarawa2`, `Surulere1`/`Surulere2`, `Ifelodun1`/`Ifelodun2`, `Irepodun1`/`Irepodun2` — the NMSP's way of disambiguating a name reused in two states |
| Hand-checked spelling table | 16 | see below |
| **Unmatched** | **0** | |

**774 of 774, no collisions.** Two rows never land on the same LGA — the script
checks for that as well, because a suffix strip could easily merge `Obi1` and
`Obi2` onto one polygon if the state key were dropped.

The 16 spelling fixes, each read off the COD list for that state by eye rather
than accepted from a fuzzy matcher:

| NMSP | COD | | NMSP | COD |
|---|---|---|---|---|
| Isuikwato | Isiukwuato | | Takali | Takai |
| Obi Nwa | Obi Ngwa | | Matazuu | Matazu |
| Umu-Neochi | Umu-Nneochi | | Ogori/Mangongo | Ogori/Magongo |
| Ganaye | Ganye | | Pailoro | Paikoro |
| Gireri | Girei | | Dange-Shnsi | Dange-Shuni |
| Efon-Alayee | Efon | | Gawabawa | Gwadabawa |
| Gboyin | Aiyekire (Gbonyin) | | Karin-Lamido | Karim-Lamido |
| Idosi-Osi | Ido-Osi | | Ilemeji | Ilejemeji |

Two of those are worth keeping in mind. **Efon-Alayee → Efon** is a
town-for-LGA substitution (Efon-Alaaye is the town in Efon LGA), not a
misspelling. **Gboyin → Aiyekire (Gbonyin)** only works because the COD name
carries the alias in brackets. A sequence matcher scores both pairs at 0.57,
below any sane auto-accept threshold, so both would have been silent losses.

Every row and its match method is written to
`data/processed/nmsp_lga_name_crosswalk.csv`, so the 28 non-exact matches can
be audited without re-running anything.

---

## What is in the repository

| Path | What it is |
|---|---|
| `data/processed/nga_cod_admin.gpkg` | the project GeoPackage, 3.7 MB, two layers |
| `data/processed/nmsp_lga_name_crosswalk.csv` | 774 rows: NMSP name → PCODE → match method |
| `data/processed/nmsp_2021_2025_lga_intervention_mix.csv` | Week 1 extraction, unchanged |
| `scripts/download_cod_data.py` | fetches the raw files, prints checksums |
| `scripts/build_admin_gpkg.py` | builds the GeoPackage, fails loudly on an unmatched name |
| `scripts/make_qml_styles.py` | writes the three QGIS styles below |
| `scripts/build_qgis_project.py` | rebuilds `qgis/snt.qgz` from the GeoPackage and the styles |
| `scripts/build_qgis_layout.py` | adds the three-panel print layout and exports it |
| `qgis/snt.qgz` | the QGIS project — both layers, LGAs styled by `intervention_mix`, plus the "Three axes" layout |
| `qgis/three_axes.png` | the three-panel figure |
| `qgis/adm2_intervention_mix.qml` | all seven mixes, two-axis palette |
| `qgis/adm2_net_type.qml` | net type alone, three classes |
| `qgis/adm2_chemoprevention.qml` | chemoprevention alone, three classes |
| `qgis/intervention_mix_by_lga.png` | map export from that project |

**A note on the palette.** The seven mixes are not seven unrelated things —
they are two axes crossed. So hue carries chemoprevention (warm = SMC,
cool = IPTi, grey = neither) and lightness carries net type (pale = standard,
mid = PBO, dark = urban). Every border on the finished map then says which
axis moved: a hue change is a different chemoprevention, a shade change is a
different net. The two single-axis styles keep the same hues, so all three
maps agree — orange means SMC in every one of them. LGA outlines are 0.06 mm
grey hairlines: at national extent, 774 black borders put more ink on the page
than the fills do.

**GeoPackage layers.**

- `adm1_state` — 37 features, MultiPolygon, EPSG:4326, 11 attributes.
- `adm2_lga` — 774 features, MultiPolygon, EPSG:4326, 24 attributes: the COD
  identifiers, then `intervention_mix`, `net_type`, `chemoprevention`, `iccm`,
  `city`, `source_page`, `match_method`, `pop_total_2020`, `pop_u5_2020`.
  Nulls: `city` 707 (only urban LGAs carry one), `pop_total_2020` and
  `pop_u5_2020` 1 each (Bakassi).

To reproduce from a clean clone:

```bash
python scripts/download_cod_data.py
python scripts/build_admin_gpkg.py
```

Then open `qgis/snt.qgz`, or drag `data/processed/nga_cod_admin.gpkg` into
QGIS and load both layers.

---

## What comes next

The mix is now on the map, which is what makes the question askable. The next
step is adjacency: build the LGA neighbour list from the polygons and count how
often two neighbours carry different values of `net_type` or
`chemoprevention`. That is the answer to the primary question, and it needs
nothing that is not already in this GeoPackage.
