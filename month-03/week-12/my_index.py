# Week 12 challenge 2: NDVI for Kano from my own Landsat 9 scene.
#
# Scene: LC09_L2SP_188052_20260107_20260108_02_T1. Landsat 9, Collection 2
# Level-2, path 188 row 052, acquired 7 January 2026, 0% cloud cover.
# January is the middle of Kano's dry season, so little is green except
# irrigated farmland, river valleys and wetlands. For a malaria question that
# is the point: dry-season green marks water that persists after the
# rain-fed breeding sites have dried out.
import numpy as np
import rasterio

folder = "data/raw/landsat/"
scene = "LC09_L2SP_188052_20260107_20260108_02_T1"

with rasterio.open(folder + scene + "_SR_B4.TIF") as src:
    red_raw = src.read(1)
    profile = src.profile
    print("Scene CRS:", src.crs)

with rasterio.open(folder + scene + "_SR_B5.TIF") as src:
    nir_raw = src.read(1)

# Stored value 0 is fill: the corners outside the tilted scene footprint.
# My first run used the pack's test, raw > 0, and NDVI came out from -3.5 to
# 1.8. USGS publishes a valid range for Collection 2 surface reflectance,
# stored values 7,273 to 43,636, which is reflectance 0 to 1 after scaling.
# Outside it the value is not a real measurement (negative reflectance over
# dark water, or saturation). With both bands inside it, NDVI must sit
# within -1 to 1.
def in_range(band):
    return (band >= 7273) & (band <= 43636)


filled = (red_raw > 0) & (nir_raw > 0)
valid = in_range(red_raw) & in_range(nir_raw)
print("Cells with data:", int(filled.sum()),
      "| outside the USGS valid range, dropped:", int((filled & ~valid).sum()))
red = red_raw.astype("float32") * 0.0000275 - 0.2
nir = nir_raw.astype("float32") * 0.0000275 - 0.2
del red_raw, nir_raw  # a full scene is about 7,800 x 7,900 cells; free memory as I go

ndvi = np.full(red.shape, -9999, dtype="float32")
total = nir + red
ok = valid & (total != 0)
ndvi[ok] = (nir[ok] - red[ok]) / total[ok]

print("Cells in grid:", ndvi.size, "| with valid NDVI:", int(ok.sum()))
low = round(float(ndvi[ok].min()), 3)
high = round(float(ndvi[ok].max()), 3)
print("NDVI range:", low, "to", high)
print("Mean NDVI:", round(float(ndvi[ok].mean()), 3))

# The sanity check from the pack: this must print 0.
outside = int(((ndvi[ok] < -1) | (ndvi[ok] > 1)).sum())
print("Cells outside -1 to 1:", outside)

profile.update(dtype="float32", nodata=-9999, count=1)
with rasterio.open("data/processed/kano_ndvi.tif", "w", **profile) as dst:
    dst.write(ndvi, 1)
print("Saved data/processed/kano_ndvi.tif")
