# Week 11: coordinate reference systems and spatial operations

## What this folder contains

Guided scripts, run on the Month 3 teaching data for Ibadan North (UTM zone
31N, EPSG:32631). Every output matches the learning pack:

- `area_wrong_and_right.py`: ward area in square degrees (0.0004, with GeoPandas' warning), then in km² after `to_crs`. Ibadan North totals 58.6 km²
- `set_vs_to.py`: the same corner after `to_crs` (599,327 m E, 815,857 m N) and after a wrong `set_crs` (still 3.9, 7.38, now labelled as metres)
- `one_point.py`: one coordinate to UTM with pyproj, `always_xy=True`
- `spatial_ops.py`: 2 km buffers, then facilities per ward with `sjoin` and `groupby`. 41 of 41 counted
- `coverage_gap.py`: buffer, dissolve, `overlay(how="difference")`. Samonda and Agbowo are 100% outside 2 km
- `nearest.py`: `sjoin_nearest` from each ward centre. Agbowo is furthest, 3.87 km
- `clip_dissolve.py`: roads clipped to Agodi (2 roads, 1.21 km), and the wards dissolved into one LGA (58.6 km², the same as Step 1)
- `fix_geometry.py`: a bow-tie polygon, why it is invalid, and `make_valid`

My independent challenge, on my own project data: the 44 LGAs of Kano State
from my Week 3 layer, and the 1,858 GRID3 health facilities with coordinates
that I turned into points in Week 10.

- `my_crs.py`: checks both layers' CRS, asks GeoPandas for a UTM zone, reprojects Kano to EPSG:32632 and tests its areas against the true area on the curved Earth
- `my_count.py`: facilities per LGA with `sjoin` and `groupby`, merged back so every LGA has a count, plus facilities per 10,000 people and per 100 km²
- `my_reach.py`: how much of each LGA is more than 5 km from any facility. Saves the result layers and draws `my_reach_map.png`
- `my_validity.py`: invalid geometries before and after `make_valid`
- `my_reach_map.png`: the land more than 5 km from a facility, in red, over Kano's LGAs

Result layer: `data/processed/kano_facility_reach.gpkg` (EPSG:32632), with
`lga_reach` (44 LGAs with area, uncovered km² and uncovered %) and
`uncovered_5km` (the 14 pieces of uncovered land).

## How to run it

From the repository root:

```
uv run month-03/week-11/area_wrong_and_right.py
uv run month-03/week-11/set_vs_to.py
uv run month-03/week-11/one_point.py
uv run month-03/week-11/spatial_ops.py
uv run month-03/week-11/coverage_gap.py
uv run month-03/week-11/nearest.py
uv run month-03/week-11/clip_dissolve.py
uv run month-03/week-11/fix_geometry.py

uv run month-03/week-11/my_crs.py
uv run month-03/week-11/my_count.py
uv run month-03/week-11/my_reach.py
uv run month-03/week-11/my_validity.py
```

The guided scripts read `data/processed/facilities.gpkg`, which Week 10's
`csv_to_points.py` creates. Every file the challenge scripts read is
committed in `data/processed/`.

## Which CRS, and why

**EPSG:32632, WGS 84 / UTM zone 32N, for Kano.** Kano runs from 7.69 to
9.37° east, wholly inside zone 32N (6–12° E), and `estimate_utm_crs()`
suggests the same zone. Tested against the true area on the curved Earth,
UTM 32N measures Kano's 20,325 km² to within 0.07%, and no LGA is off by more
than 0.08%. That is well inside what this work needs.

**Nationally I keep Africa Albers (ESRI:102022), my Week 3 choice.** For all
774 LGAs `estimate_utm_crs()` also says 32N, but that only describes the
middle of the country. Nigeria spans zones 31N, 32N and 33N, and in Week 3
UTM 32N was off by up to 1.09% on single LGAs, against 0.025% for Albers. The
pack's rule is to use one UTM zone when a project area sits in one zone.
Kano does, so this week's work uses 32N.

## What I found

**Counting.** All 44 LGAs have at least one facility, and 1,842 of the 1,858
points were counted. The other 16 fall outside every Kano LGA: 12 sit within
1 km of the state border, and one is Makkha Eye Hospital, whose latitude was
typed into its longitude (found in Week 10). Per head, the fewest facilities
are in Kano city: Nasarawa (0.63 per 10,000 people), Dala (0.66) and Gwale
(0.79). These are the dense urban LGAs where the plan sends urban nets. Per
km² they have the most, so the two rates tell opposite stories, and which one
matters depends on whether the barrier is distance or crowding.

**Reach.** 30 of the 44 LGAs are fully within 5 km of a facility. Across
Kano, 1,201 of 20,310 km² (5.9%) is further than that, and nearly all of it is
in the south: Doguwa (42% of its land), Tudun Wada (29%) and Sumaila (7%).
Doguwa and Tudun Wada hold Falgore Game Reserve, so much of that red land is
protected bush where few people live. The gap in land is not the same as a
gap in people.

By net type, 9.7% of the land in PBO-net LGAs is uncovered against 4.2% in
standard-net LGAs and 0% in the urban ones. Doguwa alone drives the PBO
figure. Doguwa and Tudun Wada also share the border I used in Month 2 to show
two neighbours with different nets, so the LGA pair at the edge of Kano's
facility reach is also one of its intervention frontiers.

**The distance choice matters a lot.** At 3 km, 19.9% of Kano is out of
reach. At 10 km, 2.0%. I chose 5 km because it is the distance most often
used for physical access to primary care in Nigeria, about an hour on foot,
and malaria case management, which every LGA's mix includes, is delivered at
a facility.

**Validity.** 0 invalid geometries before and after `make_valid`, both for
all 774 LGAs in Albers and for Kano's 44 after reprojecting to UTM 32N. I
checked after reprojecting because a transform can bend a boundary into a
self-intersection. The 1,858 facility points have no empty geometries.

## Limitation of the method

The 5 km buffer is a straight line, but people walk or ride along roads and
cross rivers where there are bridges, so a facility 4 km away may be much
further in practice. The buffers also only use Kano's own facilities. Someone
in southern Doguwa may live closer to a clinic in Kaduna or Bauchi State, so
the uncovered share at the state edge is overstated. And GRID3 has no
coordinates for 266 of Kano's 2,124 facilities (13%), so every count and
every buffer here leaves those out. The uncovered area measures land, not
people. A population raster would turn it into people out of reach, which is
the number that matters for malaria case management.

## What went wrong and how I fixed it

The first map was squashed into the left half of the page. One facility, the
mislocated Makkha Eye Hospital, sits 277 km east in Yobe, and the map
stretched to include it. I set the map extent to Kano's own bounds instead of
deleting the point, because the record is wrong at source and I flagged it in
Week 10 rather than fixing it.

GRID3's `functional` column looked like a useful filter, but 781 of the 1,858
Kano points say Unknown and only 10 say Not-Functional. Filtering on it would
have measured who filled in the column, not which clinics work, so I counted
every facility.
