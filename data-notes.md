# Data notes

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

## Month 3 teaching data

`GeoDev_Lab_Month3_Starter_Data.zip` from Google Classroom, Month 03
materials. It covers Ibadan North and was generated for teaching, so none of
its figures describe the real place. The CSVs and GeoPackages are committed so
the guided scripts run. These rasters are not committed:

- `data/raw/dem.tif`: elevation model, EPSG:32631, 30 m, nodata −9999
- `data/raw/landsat/LC09_L2SP_191055_20260115_20260117_02_T1_SR_B4.TIF` and `..._SR_B5.TIF`: Landsat 9-style red and near-infrared bands, uint16, nodata 0

To get them, download the starter zip from Classroom and copy its `data`
folder into the repository root.
