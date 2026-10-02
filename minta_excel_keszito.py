"""Minta bemeneti Excel fájl készítése a fogaskerék generátorhoz."""
from pathlib import Path

from openpyxl import Workbook

munkafuzet = Workbook()
lap = munkafuzet.active
lap.title = "fogaskerekek"
lap.append(["nev", "modul", "fogszam", "nyomaszog", "szelesseg",
            "furat_nevleges", "furat_felso", "furat_also", "turesmod"])
lap.append(["kerek_20", 2.0, 20, 20, 10, 8, 0.015, 0, "nevleges"])
lap.append(["kerek_30", 2.0, 30, 20, 12, 10, 0.015, 0, "kozep"])
lap.append(["kerek_16", 1.5, 16, 20, 8, 6, 0.012, 0, "max"])

Path("adat").mkdir(exist_ok=True)
munkafuzet.save("adat/fogaskerekek.xlsx")
print("Létrehozva: adat/fogaskerekek.xlsx")
