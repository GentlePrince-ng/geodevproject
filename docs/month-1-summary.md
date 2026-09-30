# Month 1 summary

## The question

**Where in Nigeria does subnational tailoring assign different malaria
intervention mixes to neighbouring LGAs?**

## The answer

**On 530 of the 2,210 borders between neighbouring LGAs (24%), and mostly
inside states rather than along state lines.** 350 of the 530 run through the
middle of a state (Kano alone has 47). The chemoprevention frontier, where SMC
meets IPTi, is one ragged line across the middle belt from Oyo to Adamawa. The
net type changes on most frontiers (452), the chemoprevention on 63, and both
on 15. 415 of the 774 LGAs sit on at least one frontier.

## The operation I ran, and why

A **spatial join** of the 774-LGA layer to itself (`intersects`), followed by
an **intersection** of each touching pair's boundaries, in ESRI:102022 (Africa
Albers Equal Area).

The question is about neighbours, so the first job is to find out which LGAs
touch. The spatial join does that. The intersection then turns each touching
pair into the border line they share, so a place where the mix changes becomes
a line that can be counted, measured and mapped, not just a pair of names. A
pair that meets at a single corner shares no border and is excluded (rook
contiguity).

Script: [`scripts/find_mix_frontiers.py`](../scripts/find_mix_frontiers.py).
Map: [`qgis/mix_frontiers.png`](../qgis/mix_frontiers.png). The four checks in
full: [`docs/04-spatial-analysis.md`](04-spatial-analysis.md).

![Mix frontiers](../qgis/mix_frontiers.png)

## What I expected, and what I got

I wrote the expectations down and committed them before running anything
(commit `24d44a5`).

| | Expected | Got |
|---|---|---|
| Pairs of LGAs sharing a border | ~2,150 | **2,210** |
| Frontiers (mix differs across the border) | 350–550 | **530**, 24% of borders |
| — net type changes | 250–450 | 452 (+15 where both change) |
| — chemoprevention changes | 60–100 | 63 (+15 where both change) |
| Frontiers crossing a state line | more than half | **180 (34%)** |
| Median border length | ~20 km | 20.7 km |
| Empty geometries | 0 | 0 |

The counts landed where I predicted. The pattern did not.

## What surprised me

1. **Two-thirds of frontiers run inside states, not along state lines.** I
   assumed net types were assigned state by state. They are not: Kano has 47
   frontiers inside its own borders. The SMC/IPTi line runs *through* Oyo,
   Kwara, Kogi, Benue, Taraba and Adamawa: 62 of its 78 borders are inside a
   state. Tailoring is genuinely drawn below the state.
2. **More than half the LGAs (415 of 774) sit on at least one frontier**,
   although only a quarter of borders are frontiers.
3. **My working CRS was wrong for lengths.** Albers Equal Area keeps areas
   exact but stretches north–south distances. Checking one border by hand
   against its geodesic length showed 155.4 km instead of 153.8 km. Lengths are
   now measured on the ellipsoid. Choosing a CRS depends on what you will
   measure, not only on where the data are.
4. **Bakassi has no neighbours.** Its boundary is a 4.2 km² remnant separated
   from Akpabuyo by 168 m of creek. Week 2 had already found it has no
   population.
5. **Lagos Lagoon belongs to no LGA**, so four Lagos frontier pairs across the
   water do not touch. I ruled that they are not neighbours rather than invent
   a boundary. Counting them would give 534 frontiers instead of 530.

## What data I still need

- **LGA-level malaria burden.** The 2025 NMIS publishes state estimates only,
  and 37 values cannot say whether 530 LGA frontiers follow real differences in
  burden. Candidates: 2021 NMIS cluster GPS (DHS Program, on request) and
  Malaria Atlas Project prevalence rasters, summarised to LGAs.
- **The NMSP 2026–2030 LGA assignments.** Needed to see whether the frontiers
  moved. Not published. It needs a direct enquiry to NMEP.
- **The reasons behind each assignment**: SMC eligibility (rainfall
  seasonality) and insecticide-resistance data for PBO nets. These would
  explain *why* a frontier sits where it does.
- **Ward boundaries (GRID3)**, if the analysis has to go below LGA. The COD
  admin 3 layer covers only Borno, Adamawa and Yobe.
