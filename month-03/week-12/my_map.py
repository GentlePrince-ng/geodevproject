# Week 12 challenge 4: map of Kano's dry-season NDVI with a colour bar.
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterio.mask import mask
from rasterio.plot import plotting_extent

lgas = gpd.read_file("data/processed/nga_snt_analysis_ready.gpkg", layer="adm2_lga")
kano = lgas[lgas["adm1_name"] == "Kano"]

with rasterio.open("data/processed/kano_ndvi.tif") as src:
    kano = kano.to_crs(src.crs)
    # Clip to the state so the map shows Kano, not the whole scene.
    clipped, clipped_transform = mask(
        src, kano.dissolve().geometry, crop=True, filled=False
    )
    extent = plotting_extent(clipped[0], clipped_transform)

fig, ax = plt.subplots(figsize=(8, 8))
image = ax.imshow(clipped[0], cmap="RdYlGn", vmin=-0.2, vmax=0.9, extent=extent)
kano.boundary.plot(ax=ax, color="black", linewidth=0.4)
fig.colorbar(image, ax=ax, label="NDVI", shrink=0.7)
ax.set_title("Dry-season vegetation index, Kano State\nLandsat 9, 7 January 2026")
ax.text(
    0.01, 0.01, "Blank areas (the west and the southern tip): outside the Landsat scene",
    transform=ax.transAxes, fontsize=8, color="0.3",
)
ax.set_axis_off()
fig.savefig("month-03/week-12/my_map.png", dpi=150, bbox_inches="tight")
print("Saved my_map.png")
