# Week 10: GeoPandas, layers as tables

## What this folder contains

Guided scripts, run on the Month 3 teaching data for Ibadan North:

- `explore_pandas.py`: first look at the ward population table (head, shape, columns, dtypes, describe)
- `filter_sort.py`: filters wards over 35,000, sorts by population and adds a column in thousands
- `explore_layer.py`: the layer checklist on `wards.gpkg`: layers, rows, geometry types, CRS and bounds
- `geom_props.py`: looks inside one ward polygon: its type, WKT, validity and centroid
- `csv_to_points.py`: turns `health_facilities.csv` into 41 points and saves `data/processed/facilities.gpkg`
- `join_population.py`: joins population to wards. 9 of 12 match first time, 12 of 12 after cleaning the names
- `make_map.py`: draws the wards and facilities and saves `facilities_map.png`
- `save_outputs.py`: saves a GeoPackage copy of the wards and `wards_table.csv`

My independent challenge, on my own project data (Nigeria's 774 LGAs and their malaria intervention mixes):

- `my_explore.py`: the same checklist on my Week 3 LGA layer (`data/processed/nga_snt_analysis_ready.gpkg`, layer `adm2_lga`)
- `my_points.py`: turns the GRID3 health facility list for Kano into points, checks that they land in Kano, saves `data/processed/grid3_kano_facilities.gpkg` and draws `my_points_map.png`
- `my_join.py`: joins the National Malaria Strategic Plan 2021–2025 intervention mix table to the 774 LGA polygons by state and LGA name, and draws `my_map.png`
- `my_map.png`: the joined intervention mix for every LGA in Nigeria
- `my_points_map.png`: the Kano facility points over Kano's 44 LGAs

## How to run it

From the repository root:

```
uv run month-03/week-10/explore_pandas.py
uv run month-03/week-10/filter_sort.py
uv run month-03/week-10/explore_layer.py
uv run month-03/week-10/geom_props.py
uv run month-03/week-10/csv_to_points.py
uv run month-03/week-10/join_population.py
uv run month-03/week-10/make_map.py
uv run month-03/week-10/save_outputs.py

uv run month-03/week-10/my_explore.py
uv run month-03/week-10/my_points.py
uv run month-03/week-10/my_join.py
```

Run `csv_to_points.py` before `make_map.py`, because the map reads the
facilities layer it saves. Every file the challenge scripts read is committed
in `data/processed/`. The Kano CSV comes from the national GRID3 file, which
is 33.5 MB and not committed. `uv run scripts/extract_grid3_kano.py`
downloads it, checks its SHA-256 and rebuilds the CSV.

## What I found

My LGA layer passes the checklist: 774 MultiPolygons, all valid, 774 unique
codes, in Africa Albers (ESRI:102022). The bounds come out in metres
(−2,323,726 to −1,076,176 east, 498,512 to 1,620,294 north), so I could not
check them by eye. Converted to degrees they are 2.67–14.68°E and
4.27–13.89°N, which is where Nigeria is.

The intervention mix table matched 740 of 774 LGAs on the names as written,
758 after cleaning both sides the same way, and 774 after adding 16 spellings
I checked by hand in Week 2. No LGA was matched twice. The counts agree with
Month 1: 425 standard-net LGAs, 282 PBO and 67 urban; 383 SMC and 386 IPTi.

In Kano, 266 of the 2,124 GRID3 facilities (13%) have no coordinates at all,
so they cannot be mapped. Of the 1,858 that can, 1,842 fall inside Kano. 12
of the other 16 are less than 1 km outside, on the state border. One is a
plain data-entry error: Makkha Eye Hospital, in Sharada ward of Kano
Municipal, has longitude 11.98007 against latitude 11.98013. The latitude was
typed into the longitude, which puts the hospital 277 km away, in Damaturu
LGA, Yobe. I
flagged it and did not change it.

## What went wrong and how I fixed it

My first join matched only 740 LGAs. The script gave no error; only the match
count showed it. Cleaning got it to 758. The last 16 needed my Week 2 spelling
table, because no rule can guess that the plan's Efon-Alayee is the boundary
file's Efon.

My Month 1 `.gitignore` ignored everything in `data/raw/`, so the teaching
CSVs could not be committed. I added exceptions for those files only, and I
added the setup guide's `*.tif` and `*.zip` rules so rasters still stay off
GitHub.
