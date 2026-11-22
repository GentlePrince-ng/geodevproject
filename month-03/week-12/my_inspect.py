# Week 12 challenge 1: inspect rasters of my own project area, Kano State.
#
# Two rasters, both described in data-notes.md (they are not committed):
#  - a Copernicus DEM GLO-30 tile, N11 E008, which holds Kano city
#  - band 4 (red) of the Landsat 9 scene I use for NDVI, path 188 row 052
# For each one I print the Step 1 checklist, then check that the grid size
# times the pixel size equals the extent of the bounds.
import rasterio

rasters = [
    "data/raw/Copernicus_DSM_COG_10_N11_00_E008_00_DEM.tif",
    "data/raw/landsat/LC09_L2SP_188052_20260107_20260108_02_T1_SR_B4.TIF",
]

for path in rasters:
    with rasterio.open(path) as src:
        print("==", path)
        print("Width x height:", src.width, "x", src.height)
        print("Bands:", src.count)
        print("Data type:", src.dtypes)
        print("CRS:", src.crs)
        print("Pixel size:", src.res)
        print("Bounds:", src.bounds)
        print("Nodata:", src.nodata)
        print("Transform:")
        print(src.transform)

        # The check: columns x pixel width should equal right - left,
        # and rows x pixel height should equal top - bottom.
        width_extent = src.width * src.res[0]
        height_extent = src.height * src.res[1]
        right_minus_left = src.bounds.right - src.bounds.left
        top_minus_bottom = src.bounds.top - src.bounds.bottom
        print(
            "Width x resolution:", round(width_extent, 6),
            "| right - left:", round(right_minus_left, 6),
            "| agree:", abs(width_extent - right_minus_left) < 1e-6,
        )
        print(
            "Height x resolution:", round(height_extent, 6),
            "| top - bottom:", round(top_minus_bottom, 6),
            "| agree:", abs(height_extent - top_minus_bottom) < 1e-6,
        )
        print()
