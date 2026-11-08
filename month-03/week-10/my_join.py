# Week 10 challenge 3 (and my_map.png): join one table to one layer.
#
# Table: the LGA intervention mix from Annex 1 of the National Malaria
#        Strategic Plan 2021-2025 (data/processed/nmsp_2021_2025_lga_intervention_mix.csv,
#        extracted in Week 1). It has state and LGA NAMES only, no codes.
# Layer: the 774 LGA polygons from the COD boundaries (Week 3 output).
#
# The join key is state + LGA name. Two LGAs in different states can share
# a name (there is an Obi in Benue and one in Nasarawa), so the name alone
# is not a safe key.
import re

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

lgas = gpd.read_file("data/processed/nga_snt_analysis_ready.gpkg", layer="adm2_lga")
# Keep only the boundary columns, so this script really does the join
# instead of reusing the mix that Week 3 already attached.
lgas = lgas[["adm2_pcode", "adm2_name", "adm1_name", "geometry"]]

mix = pd.read_csv("data/processed/nmsp_2021_2025_lga_intervention_mix.csv")
print("Layer rows:", len(lgas), " Table rows:", len(mix))

# --- First try: names exactly as they are in each source ------------------
first_try = lgas.merge(
    mix,
    left_on=["adm1_name", "adm2_name"],
    right_on=["state", "lga"],
    how="left",
)
print("Matched on first try:", first_try["intervention_mix"].notna().sum(), "of", len(lgas))


# --- Second try: clean both sides with the same function -----------------
def clean_name(name):
    name = name.strip().upper().replace("-", " ").replace("/", " ")
    name = re.sub(r"\d+$", "", name)  # the NMSP numbers repeated names: Obi1, Obi2
    return " ".join(name.split())  # squeeze double spaces


lgas["state_key"] = lgas["adm1_name"].apply(clean_name)
lgas["lga_key"] = lgas["adm2_name"].apply(clean_name)
mix["state_key"] = mix["state"].apply(clean_name)
mix["lga_key"] = mix["lga"].apply(clean_name)

cleaned = lgas.merge(mix, on=["state_key", "lga_key"], how="left")
print("Matched after cleaning:", cleaned["intervention_mix"].notna().sum(), "of", len(lgas))

missed = cleaned[cleaned["intervention_mix"].isna()]
print("Still unmatched (COD name):", sorted(missed["adm2_name"]))

# --- Third step: a hand-checked spelling table ---------------------------
# Some names are spelled differently in the two sources, and no cleaning
# rule can guess them (Efon-Alayee in the NMSP is Efon in the COD, a town
# standing in for its LGA). I checked each pair by hand in Week 2 and stored
# them in the crosswalk. Only the spelling rows are used here.
crosswalk = pd.read_csv("data/processed/nmsp_lga_name_crosswalk.csv")
spelling = crosswalk[crosswalk["match_method"] == "spelling_table"]
print("Hand-checked spellings available:", len(spelling))

pcode_to_nmsp = dict(zip(spelling["adm2_pcode"], spelling["nmsp_lga"]))
lgas["lga_key"] = [
    clean_name(pcode_to_nmsp.get(code, name))
    for code, name in zip(lgas["adm2_pcode"], lgas["adm2_name"])
]

joined = lgas.merge(mix, on=["state_key", "lga_key"], how="left")
matched = joined["intervention_mix"].notna().sum()
print("Matched after the spelling table:", matched, "of", len(lgas))

# A join can also go wrong the other way: a key that appears twice in the
# table copies a polygon. Same row count in and out means it did not.
print("Rows before and after the join:", len(lgas), len(joined))
print("Table rows used more than once:", joined.duplicated(subset=["state", "lga"]).sum())

if matched != len(lgas) or len(joined) != len(lgas):
    raise SystemExit("The join is incomplete. Fix it before mapping.")

print(joined["intervention_mix"].value_counts())

# --- my_map.png: the joined mixes on a map --------------------------------
# Same colours as my Month 1 QGIS maps: hue = chemoprevention (orange SMC,
# purple IPTi, grey none), lightness = net type (pale standard, mid PBO,
# dark urban).
colours = {
    "CM+IPTp+LLINs+SMC": ("Standard nets + SMC", "#FDD49E"),
    "CM+IPTp+PBO-LLINs+SMC": ("PBO nets + SMC", "#EF8A2C"),
    "CM+IPTp+UrbanLLINs+SMC": ("Urban nets + SMC", "#8C3B00"),
    "CM+IPTp+LLINs+IPTi": ("Standard nets + IPTi", "#D4C2E5"),
    "CM+IPTp+PBO-LLINs+IPTi": ("PBO nets + IPTi", "#8B5FBF"),
    "CM+IPTp+UrbanLLINs+IPTi": ("Urban nets + IPTi", "#3F1D6B"),
    "CM+IPTp+UrbanLLINs": ("Urban nets, no chemoprevention", "#9E9E9E"),
}
counts = joined["intervention_mix"].value_counts()
joined["colour"] = joined["intervention_mix"].map(lambda m: colours[m][1])

states = joined.dissolve(by="adm1_name")

fig, ax = plt.subplots(figsize=(9, 8))
joined.plot(ax=ax, color=joined["colour"], edgecolor="#8A8A8A", linewidth=0.1)
states.boundary.plot(ax=ax, color="white", linewidth=0.8)
ax.set_title(
    "Malaria intervention mix by LGA, Nigeria (NMSP 2021-2025)\n"
    "774 LGAs joined to the plan by state and name"
)
ax.legend(
    handles=[
        Patch(facecolor=c, edgecolor="none", label=f"{label} ({counts.get(m, 0)})")
        for m, (label, c) in colours.items()
    ],
    loc="lower right",
    fontsize=8,
    frameon=False,
    title="Every LGA also gets CM + IPTp",
    title_fontsize=8,
)
ax.set_axis_off()
fig.savefig("month-03/week-10/my_map.png", dpi=150, bbox_inches="tight")
print("Map saved")
