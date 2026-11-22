# Data notes

**Measuring CRS:** EPSG:32632 (WGS 84 / UTM zone 32N) for Kano, which lies
wholly in that zone. For national work across all 774 LGAs: ESRI:102022
(Africa Albers Equal Area), because Nigeria spans UTM zones 31N–33N. Data is
stored in EPSG:4326 as downloaded.

Every dataset this project uses, where it comes from and what is wrong with
it. The full Week 2 notes, with feature counts, key columns and the
name-matching work, are in [`docs/02-data-notes.md`](docs/02-data-notes.md).
The Week 3 preparation and quality checks are in
[`docs/03-data-preparation.md`](docs/03-data-preparation.md). Both stay in
`docs/` because Month 1 work is not moved.

## Project data

| Dataset | Source | In the repository | Known problems |
|---|---|---|---|
| LGA intervention mix, NMSP 2021–2025 Annex 1 | [NMSP 2021–2025 PDF (MESA copy)](https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf), extracted by `scripts/extract_nmsp_annex1.py` | `data/processed/nmsp_2021_2025_lga_intervention_mix.csv` (774 rows) | LGA names only, no codes. 34 names differ from the boundary file and need cleaning or a hand-checked spelling table |
| LGA and state boundaries, OCHA COD-AB | [HDX cod-ab-nga](https://data.humdata.org/dataset/cod-ab-nga) | `data/processed/nga_cod_admin.gpkg`, and the Week 3 analysis-ready `nga_snt_analysis_ready.gpkg` (774 LGAs, ESRI:102022) | The LGA polygons leave out the Lagos Lagoon (183 km²), which the Lagos state polygon includes |
| LGA population 2020, OCHA COD-PS | [HDX cod-ps-nga](https://data.humdata.org/dataset/cod-ps-nga) | Joined into the analysis-ready layer | Bakassi has a boundary but no population |
| Health facilities, GRID3 NGA v3.0 | [HDX grid3-nga-health-facilities-v3-0](https://data.humdata.org/dataset/grid3-nga-health-facilities-v3-0), last modified 27 Aug 2026 | National file (41,778 facilities, 33.5 MB, SHA-256 `db66a553…`) **not committed**; Kano extract `data/processed/grid3_kano_facilities.csv` (2,124 rows) and `.gpkg` (1,858 points) committed | 6,004 facilities nationally have no point geometry, and 266 Kano rows have no coordinates. One Kano record has its latitude copied into its longitude (Makkha Eye Hospital) |

## Project rasters (Week 12, not committed)

Both stay on the laptop. `.gitignore` excludes `*.tif` and `*.TIF`.

| Raster | Source | Details | Known problems |
|---|---|---|---|
| Landsat 9 surface reflectance, bands 4 and 5: `data/raw/landsat/LC09_L2SP_188052_20260107_20260108_02_T1_SR_B4.TIF` and `..._SR_B5.TIF` | USGS Landsat Collection 2 Level-2 (product "Landsat 8-9 OLI/TIRS C2 L2"). Downloaded on 22 Nov 2026 from the [Microsoft Planetary Computer copy](https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2) of the USGS archive, which has the same files and file names as [EarthExplorer](https://earthexplorer.usgs.gov/) and needs no login | Path 188 row 052, **acquired 7 Jan 2026**, processed 8 Jan 2026, Tier 1. **Cloud cover 0%** (scene and land). EPSG:32632, 30 m, 7,591 × 7,741 cells, uint16, nodata 0. B4 93.0 MB, SHA-256 `c406fb2e…`; B5 93.4 MB, SHA-256 `bde8173d…` | The scene covers 30 of Kano's 44 LGAs fully and misses Rogo, Gwarzo, Shanono and Tsanyawa. 21 cells fall outside the USGS valid range (7,273–43,636) and are masked |
| Copernicus DEM GLO-30, tile N11 E008: `data/raw/Copernicus_DSM_COG_10_N11_00_E008_00_DEM.tif` | ESA Copernicus DEM, 30 m. Downloaded on 22 Nov 2026 from the [AWS Open Data copy](https://registry.opendata.aws/copernicus-dem/) (the same product OpenTopography serves) | 1° × 1° tile, 8–9° E, 11–12° N, which holds Kano city. EPSG:4326, 3,600 × 3,600 cells of 0.000278°, float32, no nodata value set. 38.6 MB, SHA-256 `00ad81e5…` | One tile covers only the middle of Kano. Its pixels are in degrees, so it is not suitable for slope without reprojecting. Used for inspection only this week |

## Month 3 teaching data

`GeoDev_Lab_Month3_Starter_Data.zip` from Google Classroom, Month 03
materials. It covers Ibadan North and was generated for teaching, so none of
its figures describe the real place. The CSVs and GeoPackages are committed so
the guided scripts run. These rasters are not committed:

- `data/raw/dem.tif`: elevation model, EPSG:32631, 30 m, nodata −9999
- `data/raw/landsat/LC09_L2SP_191055_20260115_20260117_02_T1_SR_B4.TIF` and `..._SR_B5.TIF`: Landsat 9-style red and near-infrared bands, uint16, nodata 0

To get them, download the starter zip from Classroom and copy its `data`
folder into the repository root.
