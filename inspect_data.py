import csv


def inspect_column(filename, column):
    with open(filename, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    values = []
    for row in rows:
        raw = row[column].strip()
        if raw in ("", "NA", "N/A", "-"):
            continue
        values.append(float(raw.replace(",", "")))

    if len(values) == 0:
        return {"count": 0, "note": "no numeric values in this column"}

    return {
        "smallest": min(values),
        "largest": max(values),
        "count": len(values),
        "mean": round(sum(values) / len(values), 1),
    }


density_result = inspect_column("nga_lga_snt.csv", "pop_density_2020")
area_result = inspect_column("nga_lga_snt.csv", "area_km2_albers")

print("Population density (people per km2):", density_result)
print("Area (km2):", area_result)
