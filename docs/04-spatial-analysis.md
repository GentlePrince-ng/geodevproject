# Week 4 — One spatial operation: where do neighbouring LGAs get different mixes?

## 1. What I expect — written before running anything

Committed on its own, before the analysis script existed, so the comparison in
§5 is against a prediction rather than a rationalisation.

**Operation.** A spatial join of the 774-LGA layer to itself (`predicate="intersects"`)
to find every pair of LGAs that touch, then an **intersection** of each pair's
boundaries to get the border they share as a line, measured in kilometres in
ESRI:102022. A pair whose intervention mixes differ is a **frontier**.

**Expectations, from what I already know about the data:**

| Quantity | Expected | Reasoning |
|---|---|---|
| Neighbouring LGA pairs (shared border > 0) | **~2,150** (2,000–2,300) | A planar tiling averages just under 6 neighbours per polygon; 774 × 5.6 / 2 ≈ 2,170, pulled down by LGAs on the national border |
| Pairs touching at a single point only | **20–60** | Four-corner junctions; a join on `intersects` will return them, but they share no border |
| Frontier pairs (mix differs) | **350–550**, i.e. 16–25% of pairs | Two axes, both spatially clustered, so most borders sit inside a block of one mix |
| — of which chemoprevention (SMC ↔ IPTi) | **60–100** | One frontier across the middle belt, roughly 35 LGAs wide and ragged |
| — of which net type | **250–450** | PBO nets are likely assigned by state, so their edges follow state lines; 67 urban LGAs are islands inside rural ones |
| Frontier pairs that cross a state line | **more than half** | If PBO follows states, net frontiers are state borders |
| Median shared border length | **~20 km** (range 0.1–150 km) | Median LGA is 714 km²; a hexagon of that area has a side of ~17 km |
| Empty geometries in the output | **0** | Every row comes from a pair that intersects, so its boundary intersection cannot be empty — unless the COD borders do not coincide exactly |
| Lagos Lagoon pairs | **4 frontier pairs missing** | Week 3, §4.1: Epe against Kosofe, Lagos Island, Lagos Mainland and Shomolu do not touch |

## 2. The operation, and why this one

The question is about **neighbouring** LGAs, so the operation has to establish
who neighbours whom and then compare them. Of the four the brief offers:

- **Spatial join** — yes. Joining the LGA layer to itself with `intersects`
  pairs every LGA with every LGA it touches: 2,220 pairs.
- **Intersection** — yes, as the second step. Intersecting the two boundaries
  of each pair turns "these two touch" into *the line they share*, which can
  be measured, mapped and coloured. Without it a frontier is only a pair of
  names; with it, it is a border you can see on the map.
- **Buffer** — no. It would make LGAs across Lagos Lagoon into neighbours by
  inventing contact. That is a ruling, not a fix (see §6).
- **Count points in polygon** — no. There are no point data in this question yet.

Script: [`scripts/find_mix_frontiers.py`](../scripts/find_mix_frontiers.py).
Input: `adm2_lga` from the Week 3 analysis-ready file, in **ESRI:102022**.
Output: [`data/processed/nga_snt_frontiers.gpkg`](../data/processed/nga_snt_frontiers.gpkg),
layer `lga_borders`: **2,210 lines**, one per pair of LGAs sharing a border,
with both LGAs' names, states and mixes, `axis_changed` (same mix / net type /
chemoprevention / both), `is_frontier`, `crosses_state` and `shared_km`.
Every number below is also in
[`data/processed/frontier_checks.json`](../data/processed/frontier_checks.json).

```bash
python scripts/find_mix_frontiers.py
"C:\Program Files\QGIS 3.40.4\bin\python-qgis-ltr.bat" scripts/build_frontier_map.py --export
```

## 3. The four checks

### Check 1 — Look at the map

![Mix frontiers](../qgis/mix_frontiers.png)

[`qgis/mix_frontiers.png`](../qgis/mix_frontiers.png), from the print layout
**Mix frontiers** in [`qgis/frontiers.qgz`](../qgis/frontiers.qgz).

What the map shows, and what it rules out:

- **The chemoprevention frontier (orange) is one continuous, ragged line**
  from the Benin border through Oyo, Kwara, Kogi and Benue to Taraba and
  Adamawa at the Cameroon border. This is the SMC/IPTi split drawn as a line.
  Where it turns teal, the net type changes on the same border too.
- **Urban-LLIN LGAs show as small closed rings** of purple in the cities. An
  island of one mix inside another is what a ring of frontier should look like.
- **The small orange loop in Lagos** is the five dense-urban LGAs with no
  chemoprevention at all, against IPTi around them.
- **Nothing is drawn over water or outside the country**, and no line crosses
  Lagos Lagoon. If the join had matched LGAs by bounding box rather than by
  geometry, lines would jump across gaps. None do.
- **Eleven states have no internal line at all**, and they are exactly the
  eleven states assigned a single mix throughout. Two independent routes reach
  the same eleven.

### Check 2 — Row count against the expectation

| Quantity | Expected (§1) | Got | Verdict |
|---|---|---|---|
| Pairs sharing a border | ~2,150 (2,000–2,300) | **2,210** | Inside the range. 5.71 neighbours per LGA |
| Point-only contacts | 20–60 | **10** | Fewer than expected. Excluded: they share no border |
| Frontier pairs | 350–550 (16–25%) | **530 (24.0%)** | Inside the range, near the top |
| — net type only | 250–450 | **452** | Just above the range |
| — chemoprevention only | 60–100 | **63** | Inside the range |
| — both axes | not predicted | **15** | Mostly on the eastern half of the chemoprevention line |
| Frontiers crossing a state line | more than half | **180 of 530 (34%)** | **Wrong.** See §4 |
| Median shared border | ~20 km | **20.7 km** (0.01–153.8) | Right |
| Empty geometries | 0 | **0**, and 0 null | Right |
| LGAs with no neighbour | not predicted | **1: Bakassi** | **Not foreseen.** See §4 |
| Lagoon frontier pairs | 4 missing | **4 missing** | Right, as Week 3 predicted |

### Check 3 — One feature by hand: Kabba/Bunu ↔ Lokoja (Kogi)

This is the longest chemoprevention frontier in the country. I checked it
against sources the script did not use:

| Attribute | In the output | Checked against | Result |
|---|---|---|---|
| Kabba/Bunu mix | `CM+IPTp+LLINs+IPTi` | NMSP Annex 1, p. 84, in the raw extracted table `nmsp_2021_2025_lga_intervention_mix.csv` | Match |
| Lokoja mix | `CM+IPTp+LLINs+SMC` | Same table, p. 84 | Match |
| PCODEs | NG023010, NG023012 | Week 2 name crosswalk, both `exact` matches | Match |
| What changes | chemoprevention only | IPTi against SMC, both on standard LLINs | Match |
| Crosses a state line | no | Both in Kogi | Match |
| Border length | **153.85 km** | Geodesic length of the same border, recomputed from the **archival EPSG:4326** file with `pyproj.Geod` | Match, **after a fix** |

**The fix.** The first run reported **155.38 km** for this border, 1.0% more
than the geodesic 153.85 km. The Week 3 CRS is equal-**area**: Albers keeps
areas exact by stretching distances in one direction and shrinking them in the
other, and at Nigeria's latitude a north–south line comes out long. Week 3
chose the CRS for areas, and I had carried it over to lengths without testing
it. Across all 2,210 borders the total is off by only **0.18%**, but a single
border is off by up to **6.8%**. `shared_km` is now measured on the WGS84
ellipsoid, and the Albers length is kept beside it as `shared_km_albers` so the
difference stays visible.

To repeat this check in QGIS: open `qgis/frontiers.qgz`, click the
Kabba/Bunu–Lokoja line in `Frontiers` with the Identify tool, and read its
ellipsoidal length. It should be 153.8 km.

### Check 4 — Empty geometry

- **0 empty and 0 null** geometries in the 2,210 output rows.
- **2,178 LineStrings and 32 MultiLineStrings.** A MultiLineString here is a
  border shared in more than one stretch, broken where a third LGA pinches in
  between. That is real, not an error, so these rows are kept whole.
- **10 pairs intersect at a single point**, where four LGAs meet at a corner.
  The spatial join returns them, but their boundary intersection is a point of
  zero length. They are dropped by rule (shared border under 1 m), so the
  analysis uses **rook** contiguity: neighbours share an edge, not just a
  corner.
- **3 borders are shorter than 100 m** (the shortest is 9.8 m, Ibadan North
  West against Ibadan South East). None of the three is a frontier, so whether
  they are real edges or digitising noise changes no result.

## 4. What surprised me

1. **Frontiers mostly run inside states: 350 of 530 (66%).** I expected the
   net-type frontier to follow state lines, on the assumption that PBO nets
   are assigned state by state from insecticide-resistance data. They are
   not. Kano alone has 47 frontiers inside its own borders, Kaduna 27 and Oyo
   25. The SMC/IPTi line is even more internal: **50 of its 66 borders
   run through the middle of a state**, splitting Oyo, Kwara, Kogi, Benue,
   Taraba and Adamawa. Subnational tailoring really is subnational. The
   decisions are drawn below the state. (The other 12 of the 78 chemoprevention frontiers are Lagos: its five LGAs with no chemoprevention against IPTi around them.)
2. **Most LGAs are on a frontier even though most borders are not.** Only 24%
   of borders are frontiers, but **415 of 774 LGAs (54%) have at least one**.
   The frontiers are spread thinly across many LGAs rather than packed into a
   few blocks.
3. **Bakassi has no neighbour at all.** The COD polygon is a 4.2 km² remnant in
   two parts, **168 m of creek** away from Akpabuyo. The rest of the peninsula
   went to Cameroon under the 2002 ICJ ruling. Week 2 found it had no
   population. Now it turns out to have no neighbours either. It stays in the
   data, and it drops out of any adjacency question.
4. **An equal-area CRS is not an equal-distance CRS.** See check 3. The right
   CRS depends on what you measure.
5. **Borders that change the mix are no shorter than borders that don't**
   (median 20.0 km against 20.9 km). A frontier is not a marginal corner
   touch. It is a full LGA border.

## 5. Expected against got, in one line

The totals came out where I predicted: 2,210 pairs and 530 frontiers. The
**structure** did not. I expected frontiers to run along state lines, and
two-thirds of them run inside states.

## 6. The Lagos Lagoon ruling

Week 3 left this open. **Ruling: strict contiguity, no lagoon neighbours.** Two
LGAs are neighbours only if their polygons share a border. The four lagoon
pairs (Epe against Kosofe, Lagos Island, Lagos Mainland and Shomolu, all
standard LLINs against urban LLINs) are therefore **not** counted. That is
recorded here as a decision, not inherited from a library default.

Why: the lagoon belongs to no LGA in the COD, and making the pairs touch, by
buffering, snapping or assigning the water, would invent a boundary no source
contains. **Sensitivity:** counting them would give 534 frontiers instead of
530. No conclusion above changes.

## 7. Where the outputs live

| File | What |
|---|---|
| [`data/processed/nga_snt_frontiers.gpkg`](../data/processed/nga_snt_frontiers.gpkg) | `lga_borders`: 2,210 shared borders, 530 flagged as frontiers, ESRI:102022 |
| [`data/processed/frontier_checks.json`](../data/processed/frontier_checks.json) | Every check number |
| [`qgis/mix_frontiers.png`](../qgis/mix_frontiers.png) | The map |
| [`qgis/frontiers.qgz`](../qgis/frontiers.qgz) | QGIS project, layout **Mix frontiers** |
| [`scripts/find_mix_frontiers.py`](../scripts/find_mix_frontiers.py) | The operation and the checks |
| [`scripts/build_frontier_map.py`](../scripts/build_frontier_map.py) | The map (needs the QGIS Python) |

The month's summary is in [`month-1-summary.md`](month-1-summary.md).
