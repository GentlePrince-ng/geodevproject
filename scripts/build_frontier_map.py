"""Week 4 map: the borders where neighbouring LGAs get different mixes.

    "C:\\Program Files\\QGIS 3.40.4\\bin\\python-qgis-ltr.bat" scripts/build_frontier_map.py --export

Writes qgis/frontiers.qgz, a project of its own so qgis/snt.qgz (Weeks 2-3)
is never touched, with a print layout called "Mix frontiers": title, legend,
scale bar, north arrow. --export also writes qgis/mix_frontiers.png.

Reads the output of scripts/find_mix_frontiers.py. Everything is drawn in
ESRI:102022, the working CRS, so the scale bar measures Albers metres - true
to within about 1% anywhere in Nigeria (docs/04-spatial-analysis.md, check 3).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from qgis.core import (QgsApplication, QgsProject, QgsVectorLayer,
                       QgsCoordinateReferenceSystem, QgsPrintLayout,
                       QgsLayoutItemMap, QgsLayoutItemLegend,
                       QgsLayoutItemLabel, QgsLayoutItemScaleBar,
                       QgsLayoutItemPicture, QgsLayoutPoint, QgsLayoutSize,
                       QgsLayoutExporter, QgsUnitTypes, QgsLayerTree,
                       QgsRectangle, QgsFillSymbol, QgsLineSymbol,
                       QgsRendererCategory, QgsCategorizedSymbolRenderer,
                       QgsLegendStyle)
from qgis.PyQt.QtGui import QColor, QFont

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "data" / "processed" / "nga_snt_analysis_ready.gpkg"
FRONTIERS = ROOT / "data" / "processed" / "nga_snt_frontiers.gpkg"
CHECKS = ROOT / "data" / "processed" / "frontier_checks.json"
QGIS_DIR = ROOT / "qgis"
PROJECT = QGIS_DIR / "frontiers.qgz"
PNG = QGIS_DIR / "mix_frontiers.png"
LAYOUT_NAME = "Mix frontiers"

# Validated with the dataviz palette checker: CVD and normal-vision separation,
# chroma and contrast all pass on white. Counts are filled in from the data.
AXES = [
    ("net type", "#7B3294", 0.45, "Net type changes|(LLIN, PBO-LLIN, urban LLIN)"),
    ("chemoprevention", "#E66101", 0.75, "Chemoprevention changes|(SMC to IPTi or none)"),
    ("both", "#008C7E", 0.75, "Both change"),
]

TITLE = "Where neighbouring LGAs are assigned different malaria interventions"
SUBTITLE = ("Each line is a border shared by two LGAs whose NMSP 2021-2025 "
            "intervention mixes differ, coloured by what changes across it")
CREDIT = ("Spatial join + boundary intersection of 774 LGAs, ESRI:102022 "
          "(Africa Albers Equal Area).  Mixes: National Malaria Strategic Plan "
          "2021-2025, Annex 1.  Boundaries: OCHA COD-AB (HDX cod-ab-nga).  "
          "Lagos Lagoon pairs are not drawn: they share no border.")

PAGE_W, PAGE_H = 297.0, 218.0          # mm; A4 wide, cropped to Nigeria
MARGIN = 10.0
MAP_TOP = 30.0
MAP_W = 200.0
MAP_H = MAP_W * 0.80                   # Nigeria's extent is 0.80 as tall as wide


def label(layout, text, x, y, w, h, size, bold=False, colour="#1a1a1a"):
    item = QgsLayoutItemLabel(layout)
    item.setText(text)
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    item.setFont(font)
    item.setFontColor(QColor(colour))
    layout.addLayoutItem(item)
    item.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    item.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    return item


def load(path: Path, layer: str, name: str) -> QgsVectorLayer:
    lyr = QgsVectorLayer(f"{path}|layername={layer}", name, "ogr")
    if not lyr.isValid():
        raise SystemExit(f"{layer} failed to load from {path}")
    return lyr


def main() -> int:
    app = QgsApplication([], False)
    app.initQgis()

    project = QgsProject.instance()
    project.clear()
    project.setCrs(QgsCoordinateReferenceSystem("ESRI:102022"))
    project.writeEntryBool("Paths", "/Absolute", False)
    # So the Identify tool reports ellipsoidal lengths, matching shared_km.
    project.setEllipsoid("EPSG:7030")

    lga = load(READY, "adm2_lga", "LGAs")
    lga.renderer().setSymbol(QgsFillSymbol.createSimple({
        "color": "#f1f1ee", "outline_color": "#c8c8c4",
        "outline_width": "0.06"}))

    state = load(READY, "adm1_state", "State boundaries")
    state.renderer().setSymbol(QgsFillSymbol.createSimple({
        "style": "no", "outline_color": "#7a7a76", "outline_width": "0.3"}))

    borders = load(FRONTIERS, "lga_borders", "Frontiers")
    borders.setSubsetString('"is_frontier" = 1')
    counts = {}
    for f in borders.getFeatures():
        counts[f["axis_changed"]] = counts.get(f["axis_changed"], 0) + 1
    categories = []
    for value, colour, width, text in AXES:
        symbol = QgsLineSymbol.createSimple({
            "color": colour, "width": str(width), "capstyle": "round"})
        categories.append(QgsRendererCategory(
            value, symbol, f"{text}|{counts.get(value, 0)} borders"))
    borders.setRenderer(QgsCategorizedSymbolRenderer("axis_changed", categories))

    for lyr in (lga, state, borders):
        project.addMapLayer(lyr)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(LAYOUT_NAME)
    layout.pageCollection().page(0).setPageSize(
        QgsLayoutSize(PAGE_W, PAGE_H, QgsUnitTypes.LayoutMillimeters))

    label(layout, TITLE, MARGIN, 8.0, PAGE_W - 2 * MARGIN, 9.0, 17, bold=True)
    label(layout, SUBTITLE, MARGIN, 17.5, PAGE_W - 2 * MARGIN, 6.0, 10,
          colour="#555555")

    frame = QgsLayoutItemMap(layout)
    frame.setFrameEnabled(False)
    layout.addLayoutItem(frame)
    frame.attemptMove(QgsLayoutPoint(MARGIN, MAP_TOP,
                                     QgsUnitTypes.LayoutMillimeters))
    frame.attemptResize(QgsLayoutSize(MAP_W, MAP_H,
                                      QgsUnitTypes.LayoutMillimeters))
    frame.setCrs(QgsCoordinateReferenceSystem("ESRI:102022"))
    frame.setKeepLayerSet(True)
    frame.setLayers([borders, state, lga])
    extent = QgsRectangle(lga.extent())
    extent.scale(1.03)
    frame.zoomToExtent(extent)

    side_x = MARGIN + MAP_W + 6.0
    side_w = PAGE_W - side_x - MARGIN

    # QgsLegendModel.setRootGroup() does not take ownership: this tree must
    # outlive the export or the process dies silently mid-render.
    tree = QgsLayerTree()
    tree.addLayer(borders)
    tree.addLayer(state)
    legend = QgsLayoutItemLegend(layout)
    legend.setLinkedMap(frame)
    legend.setTitle("What changes across the border")
    legend.setAutoUpdateModel(False)
    legend.model().setRootGroup(tree)
    tree.findLayers()[0].setCustomProperty("legend/title-style", "hidden")
    legend.setStyleFont(QgsLegendStyle.Title, QFont("Segoe UI", 11, QFont.Bold))
    legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont("Segoe UI", 9))
    legend.setSymbolWidth(9.0)
    # Category labels are split with "|"; the wrap string turns it into a line
    # break inside the legend.
    legend.setWrapString("|")
    legend.setBoxSpace(0.0)
    layout.addLayoutItem(legend)
    legend.attemptMove(QgsLayoutPoint(side_x, MAP_TOP + 4.0,
                                      QgsUnitTypes.LayoutMillimeters))

    scale = QgsLayoutItemScaleBar(layout)
    scale.setLinkedMap(frame)
    scale.setStyle("Single Box")
    scale.setUnits(QgsUnitTypes.DistanceKilometers)
    scale.setUnitLabel("km")
    scale.setUnitsPerSegment(100.0)
    scale.setNumberOfSegments(2)
    scale.setNumberOfSegmentsLeft(0)
    scale.setFont(QFont("Segoe UI", 8))
    layout.addLayoutItem(scale)
    scale.attemptMove(QgsLayoutPoint(MARGIN + 4.0, MAP_TOP + MAP_H - 12.0,
                                     QgsUnitTypes.LayoutMillimeters))

    arrow = QgsLayoutItemPicture(layout)
    svg = next((p for d in QgsApplication.svgPaths()
                for p in [Path(d) / "arrows" / "NorthArrow_02.svg"]
                if p.exists()), None)
    if svg:
        arrow.setPicturePath(str(svg))
        layout.addLayoutItem(arrow)
        arrow.attemptMove(QgsLayoutPoint(MARGIN + MAP_W - 14.0, MAP_TOP + 2.0,
                                         QgsUnitTypes.LayoutMillimeters))
        arrow.attemptResize(QgsLayoutSize(10.0, 14.0,
                                          QgsUnitTypes.LayoutMillimeters))

    c = json.loads(CHECKS.read_text())
    axis = c["frontier_by_axis"]
    inside = c["frontier_pairs"] - c["frontier_crossing_state_line"]
    label(layout, (f"{c['frontier_pairs']:,} of {c['pairs_sharing_border']:,} "
                   f"shared LGA borders are frontiers "
                   f"({c['frontier_share_pct']:.0f}%).\n\n"
                   f"Net type moves on {axis['net type'] + axis['both']} of them; "
                   f"chemoprevention on {axis['chemoprevention'] + axis['both']}, "
                   "as one ragged line across the middle belt.\n\n"
                   f"{inside} of the {c['frontier_pairs']} frontiers lie inside "
                   "a single state: tailoring is drawn below the state, not "
                   "along state lines."),
          side_x, MAP_TOP + 62.0, side_w, 60.0, 9, colour="#333333")

    label(layout, CREDIT, MARGIN, PAGE_H - 14.0, PAGE_W - 2 * MARGIN, 12.0, 7,
          colour="#666666")

    project.layoutManager().addLayout(layout)
    if not project.write(str(PROJECT)):
        raise SystemExit(f"could not write {PROJECT}")
    print(f"wrote {PROJECT.relative_to(ROOT)} with layout {LAYOUT_NAME!r}")
    print("frontier counts:", counts)

    if "--export" in sys.argv:
        settings = QgsLayoutExporter.ImageExportSettings()
        settings.dpi = 200
        settings.generateWorldFile = False
        result = QgsLayoutExporter(layout).exportToImage(str(PNG), settings)
        if result != QgsLayoutExporter.Success:
            raise SystemExit(f"export failed with code {result}")
        print(f"wrote {PNG.relative_to(ROOT)} ({PNG.stat().st_size / 1e6:.1f} MB)")

    project.clear()
    app.exitQgis()
    return 0


if __name__ == "__main__":
    sys.exit(main())
