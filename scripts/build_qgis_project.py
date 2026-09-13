"""Build qgis/snt.qgz from the GeoPackage and the QML styles.

Run it with the QGIS Python, not the system one:

    "C:\\Program Files\\QGIS 3.40.4\\bin\\python-qgis-ltr.bat" scripts/build_qgis_project.py

The project it writes is the starting point, not the finished map: two layers,
LGAs styled by intervention mix, states as white outlines over the top, paths
stored relative so the project moves with the repository. Open it in QGIS to
check the styling, switch adm2_lga to either single-axis style
(Layer Properties > Style > Load Style > qgis/adm2_net_type.qml or
adm2_chemoprevention.qml) and export the maps from there.
"""

from __future__ import annotations

import sys
from pathlib import Path

from qgis.core import (QgsApplication, QgsProject, QgsVectorLayer,
                       QgsSimpleLineSymbolLayer, QgsFillSymbol)
from qgis.PyQt.QtGui import QColor

ROOT = Path(__file__).resolve().parent.parent
GPKG = ROOT / "data" / "processed" / "nga_cod_admin.gpkg"
QGIS_DIR = ROOT / "qgis"
PROJECT = QGIS_DIR / "snt.qgz"


def main() -> int:
    app = QgsApplication([], False)
    app.initQgis()

    project = QgsProject.instance()
    # Relative paths, so qgis/snt.qgz still finds data/processed/ after a
    # clone to any folder.
    project.writeEntryBool("Paths", "/Absolute", False)

    lga = QgsVectorLayer(f"{GPKG}|layername=adm2_lga", "LGA intervention mix",
                         "ogr")
    state = QgsVectorLayer(f"{GPKG}|layername=adm1_state", "States", "ogr")
    for layer in (lga, state):
        if not layer.isValid():
            raise SystemExit(f"layer failed to load: {layer.name()}")

    lga.loadNamedStyle(str(QGIS_DIR / "adm2_intervention_mix.qml"))

    # States: no fill, white outline, drawn over the LGA fills.
    outline = QgsSimpleLineSymbolLayer(QColor("white"))
    outline.setWidth(0.46)
    symbol = QgsFillSymbol()
    symbol.changeSymbolLayer(0, outline)
    state.renderer().setSymbol(symbol)

    # Added LGAs first, then states, so states sit on top of the layer stack.
    project.addMapLayer(lga)
    project.addMapLayer(state)

    QGIS_DIR.mkdir(exist_ok=True)
    if not project.write(str(PROJECT)):
        raise SystemExit(f"could not write {PROJECT}")

    print(f"wrote {PROJECT.relative_to(ROOT)}")
    print(f"  {lga.name()}: {lga.featureCount()} features")
    print(f"  {state.name()}: {state.featureCount()} features")

    project.clear()
    app.exitQgis()
    return 0


if __name__ == "__main__":
    sys.exit(main())
