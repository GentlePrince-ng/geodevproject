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
