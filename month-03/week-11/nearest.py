import geopandas as gpd

wards = gpd.read_file("data/processed/wards.gpkg", layer="wards").to_crs(epsg=32631)
facilities = gpd.read_file(
    "data/processed/facilities.gpkg", layer="facilities"
).to_crs(epsg=32631)

centres = wards[["ward_name", "geometry"]].copy()
centres["geometry"] = wards.centroid

nearest = gpd.sjoin_nearest(
    centres, facilities[["name", "geometry"]], how="left", distance_col="distance_m"
)
nearest["distance_km"] = (nearest["distance_m"] / 1000).round(2)
print(nearest[["ward_name", "name", "distance_km"]])
