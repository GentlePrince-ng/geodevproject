# Week 11 challenge 4: check and repair invalid geometries in my polygon layer.
#
# Validity is checked AFTER reprojecting, because a reprojection can bend a
# boundary into a self-intersection that was not there in the original CRS.
import geopandas as gpd
from shapely.validation import explain_validity

lgas = gpd.read_file("data/processed/nga_snt_analysis_ready.gpkg", layer="adm2_lga")
kano_utm = lgas[lgas["adm1_name"] == "Kano"].to_crs(epsg=32632)

for label, layer in [
    ("All 774 LGAs, Africa Albers", lgas),
    ("Kano's 44 LGAs, UTM 32N", kano_utm),
]:
    layer = layer.copy()
    before = (~layer.is_valid).sum()
    print(f"{label}: {before} invalid before")
    for _, row in layer[~layer.is_valid].iterrows():
        print("  ", row["adm2_name"], explain_validity(row.geometry))
    layer["geometry"] = layer.make_valid()
    after = (~layer.is_valid).sum()
    print(f"{label}: {after} invalid after make_valid")
    print("  Geometry types:", layer.geom_type.value_counts().to_dict())

# The facility points: a point cannot be invalid, but it can be empty.
facilities = gpd.read_file(
    "data/processed/grid3_kano_facilities.gpkg", layer="facilities"
)
print("Facility points empty:", facilities.is_empty.sum(), "of", len(facilities))
