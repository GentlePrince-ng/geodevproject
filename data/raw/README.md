# data/raw

Raw source documents are **not** committed to this repository. Each is a
public download; the table below records where to get it and how to verify
you have the same file.

| Local filename | Source URL | SHA-256 |
|---|---|---|
| `NMSP-Nigeria-2021-2025.pdf` | https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf | `2d363bae79bfca347bff9692c16d589d39924e0ea3d724c91ede44d5992b7fe8` |
| `NMIS-2025-Key-Indicators.pdf` | Nigeria Malaria Indicator Survey 2025 Key Indicators Report (NMEP/NPC/WHO/CMS, Feb 2026) — see `docs/data-sources.md` | — |

To reproduce:

```bash
curl -L -o data/raw/NMSP-Nigeria-2021-2025.pdf \
  "https://mesamalaria.org/wp-content/uploads/2024/07/NATIONAL-MALARIA-STRATEGIC-PLAN-Nigeria-2021-2025-Final.pdf"
sha256sum data/raw/NMSP-Nigeria-2021-2025.pdf
```

Then run the extractors in `scripts/`.
