import geopandas as gpd
import rasterio

with rasterio.open("data/raw/dem.tif") as src:
    facilities = gpd.read_file(
        "data/processed/facilities.gpkg", layer="facilities"
    ).to_crs(src.crs)
    coords = [(p.x, p.y) for p in facilities.geometry]
    facilities["elevation_m"] = [values[0] for values in src.sample(coords)]

print(facilities[["name", "elevation_m"]].head())
