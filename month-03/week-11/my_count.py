# Week 11 challenge 2: count health facilities in each of Kano's 44 LGAs.
import geopandas as gpd
import pandas as pd

pd.set_option("display.width", 160)

lgas = gpd.read_file("data/processed/nga_snt_analysis_ready.gpkg", layer="adm2_lga")
kano = lgas[lgas["adm1_name"] == "Kano"].to_crs(epsg=32632)
facilities = gpd.read_file(
    "data/processed/grid3_kano_facilities.gpkg", layer="facilities"
).to_crs(epsg=32632)
print("Kano LGAs:", len(kano), " Facilities with coordinates:", len(facilities))

# Points on the left, polygons on the right, predicate "within".
# I join on the LGA code, not the name: codes are unique, names need not be.
# I count every facility. GRID3 has a "functional" column, but 781 of the
# 1,858 Kano points say Unknown and only 10 say Not-Functional, so filtering
# on it would measure who filled the column in, not which clinics work.
joined = gpd.sjoin(
    facilities[["facility_name", "geometry"]],
    kano[["adm2_pcode", "geometry"]],
    how="inner",
    predicate="within",
)
counts = joined.groupby("adm2_pcode").size().rename("facility_count").reset_index()

kano = kano.merge(counts, on="adm2_pcode", how="left")
kano["facility_count"] = kano["facility_count"].fillna(0).astype(int)

# A raw count favours big, populous LGAs, so add two rates.
kano["per_10k_people"] = (kano["facility_count"] / kano["pop_total_2020"] * 10_000).round(2)
kano["area_km2"] = kano.area / 1_000_000
kano["per_100_km2"] = (kano["facility_count"] / kano["area_km2"] * 100).round(2)

cols = ["adm2_name", "net_type", "facility_count", "per_10k_people", "per_100_km2"]
table = kano[cols].sort_values("per_10k_people")
print("\nFewest facilities per 10,000 people:")
print(table.head(5).to_string(index=False))
print("\nMost facilities per 10,000 people:")
print(table.tail(5).to_string(index=False))
print("\nLGAs with zero facilities:", (kano["facility_count"] == 0).sum())

print("\nTotal counted:", kano["facility_count"].sum(), "of", len(facilities))
outside = facilities[~facilities.index.isin(joined.index)]
print("Not inside any Kano LGA:", len(outside))

# By net type: the axis that splits Kano in the intervention plan.
by_net = kano.groupby("net_type").agg(
    lgas=("adm2_pcode", "size"),
    facilities=("facility_count", "sum"),
    people=("pop_total_2020", "sum"),
)
by_net["per_10k_people"] = (by_net["facilities"] / by_net["people"] * 10_000).round(2)
print("\nBy net type:")
print(by_net)
