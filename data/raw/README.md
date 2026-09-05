# data/raw

Raw source documents are **not** committed to this repository. Each is a public
document; this file records where to get it and how to verify you have the same
file.

| Local filename | Source | SHA-256 |
|---|---|---|
| `NMSP-Nigeria-2021-2025.pdf` | [mesamalaria.org](https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf) (also mirrored at [WHO CPCD](https://extranet.who.int/cpcd/sites/default/files/public_file_repository/NGA_Nigeria_National-Strategic-Plan-Malaria_2021-2025.pdf)) | `2d363bae79bfca347bff9692c16d589d39924e0ea3d724c91ede44d5992b7fe8` |
| `NMIS-2025-Key-Indicators.pdf` | [Nigeria Health Watch](https://nigeriahealthwatch.com/article/resources/malaria/nigeria-malaria-indicator-survey-nmis-key-indicators-2025/) — no direct public download; released via NMEP | — |

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
