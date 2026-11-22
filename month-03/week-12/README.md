# Week 12: rasters with Rasterio

## What this folder contains

Guided scripts, run on the Month 3 teaching data for Ibadan North (DEM in
EPSG:32631, Landsat 9 scene 191/055). Every output matches the learning pack:

- `inspect_raster.py`: the DEM's grid, bands, dtype, CRS, pixel size, bounds, nodata and transform. 241 × 30 m = 7,230 m = right − left
- `read_values.py`: the nodata trap. Plain minimum −9999; with `masked=True` the real minimum is 138.9 m, mean 228.2 m, 1,446 nodata cells
- `pixel_coords.py`: `xy` and `index`. Top-left pixel centre 596,817.3 / 824,996.3; (600000, 820000) is row 167, column 106
- `sample_points.py`: elevation under each facility, with the points brought to the raster's CRS
- `ndvi.py`: NDVI from bands 4 and 5 with the USGS scale factors. Range 0.0 to 0.905, mean 0.533, saved to `data/processed/ndvi.tif`
- `plot_raster.py`: `ndvi_map.png`
- `clip_raster.py`: the DEM clipped to the wards, 241 × 315 → 222 × 296 pixels
- `zonal_stats.py`: mean elevation per ward (Agodi 272.8 m … Samonda 164.5 m)
- `reproject_raster.py`: the DEM to EPSG:4326 with bilinear resampling, pixel size 0.000272°

My independent challenge, on my own project area: **Kano State**, the same
44 LGAs as Week 11, which carry each LGA's malaria intervention mix from the
NMSP 2021–2025.

- `my_inspect.py`: the Step 1 checklist for a Copernicus DEM tile and for my Landsat red band, with the size check
- `my_index.py`: NDVI for my Landsat scene, saved to `data/processed/kano_ndvi.tif` (not committed)
- `my_zonal.py`: mean and median NDVI per LGA, plus how much of each LGA the scene covers
- `my_zonal_kano_ndvi.csv`: the zonal results, 44 rows
- `my_map.py` and `my_map.png`: Kano's dry-season NDVI with LGA boundaries and a colour bar

## How to run it

From the repository root:

```
uv run month-03/week-12/inspect_raster.py
uv run month-03/week-12/read_values.py
uv run month-03/week-12/pixel_coords.py
uv run month-03/week-12/sample_points.py
uv run month-03/week-12/ndvi.py
uv run month-03/week-12/plot_raster.py
uv run month-03/week-12/clip_raster.py
uv run month-03/week-12/zonal_stats.py
uv run month-03/week-12/reproject_raster.py

uv run month-03/week-12/my_inspect.py
uv run month-03/week-12/my_index.py
uv run month-03/week-12/my_zonal.py
uv run month-03/week-12/my_map.py
```

The rasters are not in the repository. `data-notes.md` says where each one
comes from. Run `my_index.py` before `my_zonal.py` and `my_map.py`, because
they read the NDVI it writes.

## My data

- **Landsat scene:** `LC09_L2SP_188052_20260107_20260108_02_T1`. Landsat 9, Collection 2 Level-2 surface reflectance, path 188 row 052, **acquired 7 January 2026**, **cloud cover 0%** (scene and land). Bands 4 (red) and 5 (NIR). I chose January because it is the middle of Kano's dry season, and it is one of nine scenes of this tile with 0% cloud between October 2025 and November 2026.
- **DEM:** Copernicus DEM GLO-30, tile N11 E008, which holds Kano city.

**Did width × resolution equal right − left?** Yes, for both. The DEM is
3,600 × 0.000278° = 1.0° = 8.0 − 9.0° E, and the same for height. The
Landsat band is 7,591 × 30 m = 227,730 m = right − left, and 7,741 × 30 m =
232,230 m = top − bottom. The DEM is in EPSG:4326, so its pixels are in
degrees. That is fine for inspecting it, but I would not measure slope on it
without reprojecting.

## What I found

**The scene covers 30 of Kano's 44 LGAs fully.** Its western edge runs
through the west of the state, and its southern edge cuts off the tip of
Doguwa. Four LGAs (Rogo, Gwarzo, Shanono, Tsanyawa) fall entirely outside
it, and ten more are partly covered. I only compare the 30 that are at
least 95% covered. The rest are in the CSV with their coverage, flagged in
`partial_cover`.

**In January, Kano is brown.** Mean NDVI across the scene is 0.254, against
0.533 for the teaching scene at Ibadan. Most LGAs average 0.21–0.27, bare
soil and dry farmland. The green that remains is in two places. One is
Falgore Game Reserve in Doguwa and Tudun Wada: 28% of Doguwa's covered area
is above 0.4. The other is the river valleys, where land is farmed with
irrigation in the dry season.

**The city LGAs are least green.** Dala (0.129), Nasarawa (0.144), Kano
Municipal (0.155) and Gwale (0.165) are the lowest, which is roofs and roads.
These are the LGAs the plan gives urban nets. By net type, the fully covered
LGAs average 0.240 (standard LLINs, 17 LGAs), 0.209 (PBO, 6) and 0.165 (urban,
7). The urban gap is real. The PBO gap is not about vegetation. It comes
mostly from Rano, whose mean is dragged down by Tiga reservoir.

**Mean and median disagree where there is water.** Rano's mean is 0.169 but
its median is 0.229. Bebeji's are 0.182 and 0.221. Both LGAs border Tiga
reservoir, which has about 52 km² of water (NDVI below 0) in Rano and 49 km²
in Bebeji. Water's negative NDVI pulls the mean down. So a low mean NDVI here
does not mean dry land. Sometimes it means the opposite. For the malaria
question this matters: open water and irrigated land that persist through
the dry season are where breeding continues after the rains stop. An index
of greenness alone would rank Rano as one of the driest LGAs, when it holds
the largest body of standing water in the state. **NDWI (bands 3 and 5)
would be the better index for my question.** Week 14 is a chance to add it.

**What this does not show.** Every LGA in Kano gets SMC, so chemoprevention
cannot be compared across them. One date shows one moment. And the LGA
mean hides the strips of irrigated land along the rivers, which are a few
percent of each LGA's area.

## What went wrong and how I fixed it

My first NDVI run gave a range of −3.545 to 1.846. The pack says that means
the scaling or the nodata handling is wrong. Here it was the nodata handling.
The pack's test `raw > 0` only removes fill. USGS publishes a valid range
for Collection 2 surface reflectance, stored values 7,273 to 43,636, which
is reflectance 0 to 1 after scaling. Outside it the value is not a real
measurement. Over very dark water a band can scale to just below zero, so
NIR + Red gets close to zero and NDVI shoots past ±1. I changed the mask to
the valid range for both bands. That dropped 21 of 40.6 million cells, and
the range became −0.732 to 0.865 with 0 cells outside −1 to 1. The mean did
not change (0.254), so the fix only affected a handful of cells, but it is
the correct rule.

The red band's download also timed out partway through at about 41 of
93 MB. I resumed it and checked the finished file's size against the
server's before using it.
