# Week 12 challenge 3: mean NDVI per Kano LGA.
#
# Polygons: the 44 Kano LGAs from my Week 3 layer, which carry each LGA's
# intervention mix from the NMSP 2021-2025 annex. As the pack teaches, I bring
# the polygons to the raster's CRS (UTM 32N) and leave the raster untouched.
#
# The scene does not cover all of Kano: its western edge cuts through the
# western LGAs. So beside the mean I record how much of each LGA the scene
# actually covers, and flag any LGA where that is under 95%.
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask

lgas = gpd.read_file("data/processed/nga_snt_analysis_ready.gpkg", layer="adm2_lga")
kano = lgas[lgas["adm1_name"] == "Kano"].copy()
kano = kano[["adm2_pcode", "adm2_name", "net_type", "chemoprevention", "geometry"]]

with rasterio.open("data/processed/kano_ndvi.tif") as src:
    kano = kano.to_crs(src.crs)
    cell_km2 = src.res[0] * src.res[1] / 1_000_000
    means, medians, valid_cells = [], [], []
    for geom in kano.geometry:
        cells, _ = mask(src, [geom], crop=True, filled=False)
        values = cells.compressed()  # only the unmasked cells, as a flat array
        valid_cells.append(values.size)
        means.append(float(values.mean()) if values.size else np.nan)
        medians.append(float(np.median(values)) if values.size else np.nan)

kano["area_km2"] = kano.area / 1_000_000
kano["covered_pct"] = np.array(valid_cells) * cell_km2 / kano["area_km2"] * 100
kano["mean_ndvi"] = means
kano["median_ndvi"] = medians
kano["partial_cover"] = kano["covered_pct"] < 95

result = (
    kano.drop(columns="geometry")
    .round({"area_km2": 1, "covered_pct": 1, "mean_ndvi": 3, "median_ndvi": 3})
    .sort_values("mean_ndvi", ascending=False)
)
result.to_csv("month-03/week-12/my_zonal_kano_ndvi.csv", index=False)

cols = ["adm2_name", "net_type", "covered_pct", "mean_ndvi", "median_ndvi"]
full = result[~result["partial_cover"]]
print("Highest mean NDVI (fully covered LGAs):")
print(full[cols].head(5).to_string(index=False))
print("\nLowest mean NDVI (fully covered LGAs):")
print(full[cols].tail(5).to_string(index=False))
print("\nLGAs the scene covers less than 95%:")
print(result.loc[result["partial_cover"], cols].to_string(index=False))

print("\nFully covered LGAs:", len(full), "of", len(result))
print("\nMean NDVI by net type (fully covered LGAs only):")
print(full.groupby("net_type")["mean_ndvi"].agg(["count", "mean"]).round(3))
print("\nMean NDVI by chemoprevention (fully covered LGAs only):")
print(full.groupby("chemoprevention")["mean_ndvi"].agg(["count", "mean"]).round(3))
print("\nSaved month-03/week-12/my_zonal_kano_ndvi.csv")
