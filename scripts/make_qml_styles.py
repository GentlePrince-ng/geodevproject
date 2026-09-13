"""Write the QGIS layer styles for adm2_lga.

Three styles, all categorized, all for the same layer:

  qgis/adm2_intervention_mix.qml   all seven mixes, on a two-axis palette
  qgis/adm2_net_type.qml           net type alone
  qgis/adm2_chemoprevention.qml    chemoprevention alone

The palette is the argument this script exists to make. The mixes are not
seven unrelated things - they are two axes crossed, net type by
chemoprevention. So hue carries chemoprevention (warm = SMC, cool = IPTi,
grey = neither) and lightness carries net type (pale = standard nets, mid =
PBO, dark = urban). Read a border on the finished map and the change tells
you which axis moved: a hue change is a different chemoprevention, a shade
change is a different net. An arbitrary seven-colour ramp cannot say that.

The single-axis styles keep the same hues, so the three maps agree with each
other: orange still means SMC in every one of them.

Legend labels carry the LGA count, read from the GeoPackage at write time so
the numbers cannot drift from the data.

    python scripts/make_qml_styles.py

Load in QGIS: Layer Properties > Style (bottom left) > Load Style > pick the
file. styleCategories="Symbology" means only the symbology is replaced -
layer name, joins and field aliases are left alone.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent
GPKG = ROOT / "data" / "processed" / "nga_cod_admin.gpkg"
QGIS_DIR = ROOT / "qgis"

QGIS_VERSION = "3.40.4-Bratislava"

# Hairline grey. The previous style drew 774 black outlines at 0.26mm, which
# put about as much ink on the page as the fills did.
OUTLINE_RGB = (120, 120, 120)
OUTLINE_WIDTH_MM = "0.06"

# (attribute, output filename, [(value, label, hex), ...])
# Order is legend order: the intervention_mix style groups the SMC block, then
# the IPTi block, then the one mix with no chemoprevention at all.
STYLES = [
    (
        "intervention_mix",
        "adm2_intervention_mix.qml",
        [
            ("CM+IPTp+LLINs+SMC",       "Standard nets · SMC",  "#FDD49E"),
            ("CM+IPTp+PBO-LLINs+SMC",   "PBO nets · SMC",       "#EF8A2C"),
            ("CM+IPTp+UrbanLLINs+SMC",  "Urban nets · SMC",     "#8C3B00"),
            ("CM+IPTp+LLINs+IPTi",      "Standard nets · IPTi", "#D4C2E5"),
            ("CM+IPTp+PBO-LLINs+IPTi",  "PBO nets · IPTi",      "#8B5FBF"),
            ("CM+IPTp+UrbanLLINs+IPTi", "Urban nets · IPTi",    "#3F1D6B"),
            ("CM+IPTp+UrbanLLINs",      "Urban nets · no chemoprevention",
                                                                "#9E9E9E"),
        ],
    ),
    (
        "net_type",
        "adm2_net_type.qml",
        [
            # Not the #DEEBF7 bottom step of the Blues ramp: 425 LGAs is more
            # than half the country, and that near-white loses both the fill
            # and the white state borders drawn over it.
            ("LLINs",      "Standard LLINs", "#C6DBEF"),
            ("PBO-LLINs",  "PBO LLINs",      "#6BAED6"),
            ("UrbanLLINs", "Urban LLINs",    "#08519C"),
        ],
    ),
    (
        "chemoprevention",
        "adm2_chemoprevention.qml",
        [
            ("SMC",  "SMC — seasonal, children under 5", "#E6842A"),
            ("IPTi", "IPTi — perennial, infants",        "#7B5AA6"),
            ("none", "No chemoprevention",               "#BDBDBD"),
        ],
    ),
]


def qgis_colour(hex_colour: str, alpha: int = 255) -> str:
    """QGIS stores a colour twice: 8-bit RGBA, then the same as floats."""
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return (f"{r},{g},{b},{alpha},"
            f"rgb:{r / 255:.17f},{g / 255:.17f},{b / 255:.17f},{alpha / 255:.0f}")


def symbol(index: int, hex_colour: str) -> str:
    return f"""      <symbol force_rhr="0" name="{index}" type="fill" alpha="1" frame_rate="10" clip_to_extent="1" is_animated="0">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" value="" type="QString"/>
            <Option name="properties"/>
            <Option name="type" value="collection" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" class="SimpleFill" id="{{{uuid.uuid4()}}}" locked="0" enabled="1">
          <Option type="Map">
            <Option name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
            <Option name="color" value="{qgis_colour(hex_colour)}" type="QString"/>
            <Option name="joinstyle" value="bevel" type="QString"/>
            <Option name="offset" value="0,0" type="QString"/>
            <Option name="offset_map_unit_scale" value="3x:0,0,0,0,0,0" type="QString"/>
            <Option name="offset_unit" value="MM" type="QString"/>
            <Option name="outline_color" value="{qgis_colour('#%02X%02X%02X' % OUTLINE_RGB)}" type="QString"/>
            <Option name="outline_style" value="solid" type="QString"/>
            <Option name="outline_width" value="{OUTLINE_WIDTH_MM}" type="QString"/>
            <Option name="outline_width_unit" value="MM" type="QString"/>
            <Option name="style" value="solid" type="QString"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" value="" type="QString"/>
              <Option name="properties"/>
              <Option name="type" value="collection" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>"""


def escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def build(attribute: str, classes: list[tuple[str, str, str]],
          counts: dict[str, int]) -> str:
    categories, symbols = [], []
    for index, (value, label, hex_colour) in enumerate(classes):
        n = counts.get(value, 0)
        categories.append(
            f'      <category symbol="{index}" value="{escape(value)}" '
            f'type="string" render="true" '
            f'label="{escape(label)}  ({n} LGAs)" '
            f'uuid="{{{uuid.uuid4()}}}"/>'
        )
        symbols.append(symbol(index, hex_colour))

    return f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="{QGIS_VERSION}" styleCategories="Symbology">
  <renderer-v2 forceraster="0" enableorderby="0" symbollevels="0" type="categorizedSymbol" attr="{attribute}" referencescale="-1">
    <categories>
{chr(10).join(categories)}
    </categories>
    <symbols>
{chr(10).join(symbols)}
    </symbols>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>2</layerGeometryType>
</qgis>
"""


def main() -> int:
    lga = gpd.read_file(GPKG, layer="adm2_lga")
    QGIS_DIR.mkdir(exist_ok=True)

    for attribute, filename, classes in STYLES:
        counts = lga[attribute].value_counts().to_dict()
        listed = {value for value, _, _ in classes}
        unlisted = set(counts) - listed
        if unlisted:
            raise SystemExit(
                f"{attribute}: the data holds values the style does not "
                f"colour: {sorted(unlisted)}"
            )
        empty = [value for value in listed if counts.get(value, 0) == 0]
        if empty:
            raise SystemExit(
                f"{attribute}: the style colours classes with no features: "
                f"{sorted(empty)}"
            )

        path = QGIS_DIR / filename
        path.write_text(build(attribute, classes, counts), encoding="utf-8")
        total = sum(counts.get(value, 0) for value, _, _ in classes)
        print(f"{path.relative_to(ROOT)}  {len(classes)} classes, "
              f"{total} LGAs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
