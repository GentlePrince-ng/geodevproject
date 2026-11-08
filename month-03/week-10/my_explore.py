# Week 10 challenge 1: the Step 3 checklist, run on my own Month 1 layer.
# The layer is the 774 Nigerian LGAs I prepared in Week 3
# (data/processed/nga_snt_analysis_ready.gpkg, layer adm2_lga).
import pandas as pd
import geopandas as gpd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)

path = "data/processed/nga_snt_analysis_ready.gpkg"

# 1. What layers are in the file?
print(gpd.list_layers(path))

lgas = gpd.read_file(path, layer="adm2_lga")

# 2. How many features, and which columns?
print("Rows and columns:", lgas.shape)
print("Columns:", list(lgas.columns))
print(lgas[["adm2_name", "adm1_name", "intervention_mix", "pop_total_2020"]].head())

# 3. What geometry type?
print(lgas.geom_type.value_counts())

# 4. What CRS?
print("CRS:", lgas.crs.to_string(), "-", lgas.crs.name)
print("CRS units:", lgas.crs.axis_info[0].unit_name)

# 5. Where is it?
print("Bounds (metres, Africa Albers):", lgas.total_bounds.round(0))

# Albers bounds are metres from the projection's origin, which is hard to
# check by eye. The same box in degrees is the real test: Nigeria runs from
# about 2.7 to 14.7 degrees east and 4.3 to 13.9 degrees north.
print("Bounds (degrees, EPSG:4326):", lgas.to_crs("EPSG:4326").total_bounds.round(2))

# Two extra checks I always run on this layer.
print("Invalid geometries:", (~lgas.is_valid).sum())
print("Unique LGA codes:", lgas["adm2_pcode"].nunique(), "of", len(lgas))
