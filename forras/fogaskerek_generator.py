"""FreeCAD script: fogaskerekek 3D modelljének generálása a JSON bemenetből.

Futtatás a projekt gyökeréből:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd forras/fogaskerek_generator.py

Bemenet:  kimenet/fogaskerekek.json (az excel_olvaso.py készíti)
Kimenet:  kimenet/<nev>.FCStd és kimenet/<nev>.step
"""

import json
import sys
from pathlib import Path

import FreeCAD
import Part

try:
    FORRAS_MAPPA = Path(__file__).resolve().parent
except NameError:
    FORRAS_MAPPA = Path.cwd() / "forras"
GYOKER_MAPPA = FORRAS_MAPPA.parent
sys.path.insert(0, str(FORRAS_MAPPA))

from evolvens import fogprofil_pontok  # noqa: E402

KIMENET_MAPPA = GYOKER_MAPPA / "kimenet"
BEMENET = KIMENET_MAPPA / "fogaskerekek.json"


def fogaskerek_alak(adat):
    """Felépíti a fogaskerék 3D testét: körvonal, kihúzás, furat kivágása."""
    pontok = [FreeCAD.Vector(x, y, 0) for x, y in fogprofil_pontok(adat)]
    pontok.append(pontok[0])
    huzal = Part.makePolygon(pontok)
    lap = Part.Face(huzal)
    test = lap.extrude(FreeCAD.Vector(0, 0, adat["szelesseg"]))
    furat = Part.makeCylinder(
        adat["furat_atmero"] / 2,
        adat["szelesseg"],
        FreeCAD.Vector(0, 0, 0),
        FreeCAD.Vector(0, 0, 1),
    )
    return test.cut(furat)


def mentes(adat, alak):
    """Elmenti a testet FreeCAD (.FCStd) és STEP formátumban."""
    nev = adat["nev"]
    KIMENET_MAPPA.mkdir(exist_ok=True)
    dokumentum = FreeCAD.newDocument(nev)
    objektum = dokumentum.addObject("Part::Feature", nev)
    objektum.Shape = alak
    dokumentum.recompute()
    dokumentum.saveAs(str(KIMENET_MAPPA / f"{nev}.FCStd"))
    alak.exportStep(str(KIMENET_MAPPA / f"{nev}.step"))
    FreeCAD.closeDocument(dokumentum.Name)


def fo():
    if not BEMENET.exists():
        print(f"Hiba: nem található a bemeneti fájl: {BEMENET}")
        print("Előbb futtasd: python3 forras/excel_olvaso.py adat/fogaskerekek.xlsx")
        return

    with BEMENET.open(encoding="utf-8") as fajl:
        kerekek = json.load(fajl)

    kesz = 0
    for adat in kerekek:
        try:
            alak = fogaskerek_alak(adat)
            mentes(adat, alak)
        except Exception as hiba:
            print(f"{adat['nev']}: HIBA: {hiba}")
            continue
        kesz += 1
        print(
            f"{adat['nev']}: kész, térfogat = {alak.Volume:.1f} mm3, "
            f"érvényes test: {alak.isValid()}"
        )
    print(f"{kesz} / {len(kerekek)} fogaskerék elkészült, mappa: {KIMENET_MAPPA}")


fo()
