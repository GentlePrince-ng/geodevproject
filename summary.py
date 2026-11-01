import csv


def read_rows(filename):
    with open(filename, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def clean_values(rows, column):
    values = []
    for row in rows:
        raw = row[column].strip()
        # Same rule as Week 8: blanks and NA markers are skipped, not read as zero.
        # Bakassi has no 2020 population, so it drops out of the population columns.
        if raw in ("", "NA", "N/A", "-"):
            continue
        values.append(float(raw.replace(",", "")))
    return values


def summarise(values):
    if len(values) == 0:
        return {"count": 0, "smallest": None, "largest": None, "average": None}
    return {
        "count": len(values),
        "smallest": min(values),
        "largest": max(values),
        "average": round(sum(values) / len(values), 1),
    }


def summarise_all(filename, columns):
    rows = read_rows(filename)
    report = {}
    for column in columns:
        values = clean_values(rows, column)
        report[column] = summarise(values)
    return report


report = summarise_all(
    "nga_lga_snt.csv",
    ["pop_total_2020", "pop_u5_2020", "area_km2_albers", "pop_density_2020"],
)
for column, stats in report.items():
    print(column, "->", stats)
