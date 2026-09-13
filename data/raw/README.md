# data/raw

Raw source documents are **not** committed to this repository. Each is a public
document; this file records where to get it and how to verify you have the same
file.

| Local filename | Source | SHA-256 |
|---|---|---|
| `NMSP-Nigeria-2021-2025.pdf` | [mesamalaria.org](https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf) (also mirrored at [WHO CPCD](https://extranet.who.int/cpcd/sites/default/files/public_file_repository/NGA_Nigeria_National-Strategic-Plan-Malaria_2021-2025.pdf)) | `2d363bae79bfca347bff9692c16d589d39924e0ea3d724c91ede44d5992b7fe8` |
| `NMIS-2025-Key-Indicators.pdf` | [Nigeria Health Watch](https://nigeriahealthwatch.com/article/resources/malaria/nigeria-malaria-indicator-survey-nmis-key-indicators-2025/) — no direct public download; released via NMEP | — |
| `nga_admin_boundaries.shp.zip` | [HDX `cod-ab-nga`](https://data.humdata.org/dataset/cod-ab-nga) | `4600b159107bbb5069cecbe2e308310deb8a3c0e0d83e05939c254dfae4d0361` |
| `nga_admpop_2020.xlsx` | [HDX `cod-ps-nga`](https://data.humdata.org/dataset/cod-ps-nga) — the only release with LGA-level population | `ccd4eff57b3ed3fde3afe2303580fca701b089b1a75a5f8336da823e1640b6cd` |
| `nga_admpop_2022.xlsx` | [HDX `cod-ps-nga`](https://data.humdata.org/dataset/cod-ps-nga) — current release, state level only | `c1997c1770a1731b83f8b3f1d6f5da687dca0de37592870f8c1a06b654c2f7b1` |

The three COD files are fetched by `python scripts/download_cod_data.py`, which
resolves them through the HDX API and prints these checksums.

## You do not need to fetch the first one by hand

`scripts/extract_nmsp_annex1.py` downloads it if it is absent and checks it
against the checksum above before extracting:

```bash
python scripts/extract_nmsp_annex1.py
```

If the checksum ever stops matching, the published document has been revised
and the annex page numbers should be re-checked before the output is trusted.

## The second one must be placed here manually

The 2025 NMIS Key Indicators Report is not available as a direct download. Save
it to this folder as `NMIS-2025-Key-Indicators.pdf` to re-run
`scripts/extract_nmis2025_parasitaemia.py`. Its extracted output is committed to
`data/processed/`, so the data are available without it.
