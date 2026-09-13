"""Add a three-panel print layout to qgis/snt.qgz.

    "C:\\Program Files\\QGIS 3.40.4\\bin\\python-qgis-ltr.bat" scripts/build_qgis_layout.py

The same LGA layer is added to the project three times, once per style: the
full seven-way intervention mix, then each axis on its own. A print layout
called "Three axes" puts them side by side, each map frame locked to its own
layer set, each with its own legend.

Reading left to right is the argument: the seven mixes look complicated, and
then the two single-axis panels show they are only two decisions crossed.

The layout is A3 landscape. Export from QGIS with Layout > Export as Image,
or re-run this script with --export to write qgis/three_axes.png directly.
"""

from __future__ import annotations

import sys
from pathlib import Path

from qgis.core import (QgsApplication, QgsProject, QgsVectorLayer, QgsLayout,
                       QgsPrintLayout, QgsLayoutItemMap, QgsLayoutItemLegend,
                       QgsLayoutItemLabel, QgsLayoutPoint, QgsLayoutSize,
                       QgsLayoutExporter, QgsUnitTypes, QgsLayerTree,
                       QgsRectangle, QgsSimpleLineSymbolLayer, QgsFillSymbol,
                       QgsLegendStyle)
from qgis.PyQt.QtGui import QColor, QFont

ROOT = Path(__file__).resolve().parent.parent
GPKG = ROOT / "data" / "processed" / "nga_cod_admin.gpkg"
QGIS_DIR = ROOT / "qgis"
PROJECT = QGIS_DIR / "snt.qgz"
LAYOUT_NAME = "Three axes"

PANELS = [
    ("Intervention mix", "adm2_intervention_mix.qml",
     "Seven mixes, two axes crossed"),
    ("Net type", "adm2_net_type.qml",
     "Which net an LGA is assigned"),
    ("Chemoprevention", "adm2_chemoprevention.qml",
     "Which chemoprevention, if any"),
]

TITLE = "Malaria intervention tailoring by LGA, Nigeria"
CREDIT = ("Intervention mixes: National Malaria Strategic Plan 2021-2025, "
          "Annex 1.  Boundaries: OCHA COD-AB (HDX cod-ab-nga), CC BY-IGO.  "
          "774 LGAs, EPSG:4326.")

# Millimetres. The page is A3 wide but cropped in height: Nigeria's extent
# is 12.01 by 9.62 degrees, so a frame taller than 0.80 of its width is dead
# space above and below the country, not a bigger map.
PAGE_W = 420.0
MARGIN = 12.0
GUTTER = 6.0
MAP_W = (PAGE_W - 2 * MARGIN - 2 * GUTTER) / 3
MAP_H = MAP_W * 0.80
MAP_TOP = 34.0
LEGEND_TOP = MAP_TOP + MAP_H + 4.0
# 62mm below the legends: the widest legend has seven entries.
PAGE_H = LEGEND_TOP + 62.0


def white_outline_symbol() -> QgsFillSymbol:
    outline = QgsSimpleLineSymbolLayer(QColor("white"))
    outline.setWidth(0.46)
    symbol = QgsFillSymbol()
    symbol.changeSymbolLayer(0, outline)
    return symbol


def add_label(layout: QgsLayout, text: str, x: float, y: float,
              width: float, height: float, size: int, bold: bool = False,
              colour: str = "#1a1a1a") -> None:
    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    label.setFont(font)
    label.setFontColor(QColor(colour))
    layout.addLayoutItem(label)
    label.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    label.attemptResize(QgsLayoutSize(width, height,
                                      QgsUnitTypes.LayoutMillimeters))


def main() -> int:
    app = QgsApplication([], False)
    app.initQgis()

    project = QgsProject.instance()
    if not project.read(str(PROJECT)):
        raise SystemExit(f"could not open {PROJECT}")
    project.writeEntryBool("Paths", "/Absolute", False)

    # Start from a clean slate so re-running does not stack up duplicates.
    for layer in list(project.mapLayers().values()):
        project.removeMapLayer(layer)
    manager = project.layoutManager()
    for existing in manager.printLayouts():
        if existing.name() == LAYOUT_NAME:
            manager.removeLayout(existing)

    state = QgsVectorLayer(f"{GPKG}|layername=adm1_state", "States", "ogr")
    if not state.isValid():
        raise SystemExit("state layer failed to load")
    state.renderer().setSymbol(white_outline_symbol())
    project.addMapLayer(state)

    panels = []
    for name, qml, subtitle in PANELS:
        lga = QgsVectorLayer(f"{GPKG}|layername=adm2_lga", name, "ogr")
        if not lga.isValid():
            raise SystemExit(f"LGA layer failed to load for {name}")
        message, ok = lga.loadNamedStyle(str(QGIS_DIR / qml))
        if not ok:
            raise SystemExit(f"{qml} did not load: {message}")
        project.addMapLayer(lga)
        panels.append((lga, name, subtitle))

    extent = QgsRectangle(state.extent())
    extent.scale(1.04)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(PAGE_W, PAGE_H,
                                   QgsUnitTypes.LayoutMillimeters))
    layout.setName(LAYOUT_NAME)

    # The legend models below hold raw pointers to their layer trees without
    # taking ownership. Drop the Python references and rendering reads freed
    # memory - the process dies during export with no traceback, having
    # written a project file that looks fine. Keep them alive for the run.
    legend_trees = []

    add_label(layout, TITLE, MARGIN, 10.0, PAGE_W - 2 * MARGIN, 10.0,
              20, bold=True)

    for index, (lga, name, subtitle) in enumerate(panels):
        x = MARGIN + index * (MAP_W + 6.0)

        add_label(layout, name, x, MAP_TOP - 12.0, MAP_W, 6.0, 13, bold=True)
        add_label(layout, subtitle, x, MAP_TOP - 6.0, MAP_W, 5.0, 9,
                  colour="#666666")

        panel = QgsLayoutItemMap(layout)
        panel.setFrameEnabled(False)
        layout.addLayoutItem(panel)
        panel.attemptMove(QgsLayoutPoint(x, MAP_TOP,
                                         QgsUnitTypes.LayoutMillimeters))
        panel.attemptResize(QgsLayoutSize(MAP_W, MAP_H,
                                          QgsUnitTypes.LayoutMillimeters))
        # Each frame keeps its own layer set, which is what lets one project
        # show three different styles of the same data at once.
        panel.setKeepLayerSet(True)
        panel.setLayers([state, lga])
        panel.zoomToExtent(extent)

        legend = QgsLayoutItemLegend(layout)
        legend.setLinkedMap(panel)
        legend.setTitle("")
        legend.setAutoUpdateModel(False)
        # Prune the legend to this panel's LGA layer: without this every
        # legend lists all three styles plus the state outline.
        tree = QgsLayerTree()
        tree.addLayer(lga)
        legend_trees.append(tree)
        legend.model().setRootGroup(tree)
        # The layer node would print its name above the swatches, repeating
        # the panel heading two centimetres higher up.
        tree.findLayers()[0].setCustomProperty("legend/title-style", "hidden")
        legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont("Segoe UI", 9))
        legend.setSymbolWidth(6.0)
        legend.setSymbolHeight(3.6)
        legend.setBoxSpace(0.0)
        layout.addLayoutItem(legend)
        legend.attemptMove(QgsLayoutPoint(x, LEGEND_TOP,
                                          QgsUnitTypes.LayoutMillimeters))

    add_label(layout, CREDIT, MARGIN, PAGE_H - 10.0, PAGE_W - 2 * MARGIN,
              10.0, 8, colour="#666666")

    manager.addLayout(layout)
    if not project.write(str(PROJECT)):
        raise SystemExit(f"could not write {PROJECT}")
    print(f"wrote {PROJECT.relative_to(ROOT)} with layout {LAYOUT_NAME!r}")

    if "--export" in sys.argv:
        settings = QgsLayoutExporter.ImageExportSettings()
        settings.dpi = 200
        # Without this GDAL tries to write a world file next to the PNG and
        # logs "ERROR 6: The PNG driver does not support update access".
        settings.generateWorldFile = False
        target = QGIS_DIR / "three_axes.png"
        exporter = QgsLayoutExporter(layout)
        result = exporter.exportToImage(str(target), settings)
        if result != QgsLayoutExporter.Success:
            raise SystemExit(f"export failed with code {result}")
        print(f"wrote {target.relative_to(ROOT)} "
              f"({target.stat().st_size / 1e6:.1f} MB)")

    project.clear()
    app.exitQgis()
    return 0


if __name__ == "__main__":
    sys.exit(main())
