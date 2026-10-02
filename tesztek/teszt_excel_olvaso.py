import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "forras"))

from excel_olvaso import (  # noqa: E402
    KOTELEZO_OSZLOPOK,
    EllenorzesiHiba,
    fogaskerekek_beolvasasa,
)

JO_SOR = ["kerek_20", 2.0, 20, 20, 10, 8, 0.015, 0, "nevleges"]


class ExcelOlvasoTeszt(unittest.TestCase):
    def setUp(self):
        self.ideiglenes = tempfile.TemporaryDirectory()
        self.addCleanup(self.ideiglenes.cleanup)

    def excel_keszit(self, sorok, fejlec=KOTELEZO_OSZLOPOK):
        munkafuzet = Workbook()
        lap = munkafuzet.active
        lap.append(list(fejlec))
        for sor in sorok:
            lap.append(sor)
        utvonal = Path(self.ideiglenes.name) / "teszt.xlsx"
        munkafuzet.save(utvonal)
        return utvonal

    def test_jo_fajl(self):
        kerekek = fogaskerekek_beolvasasa(self.excel_keszit([JO_SOR]))
        self.assertEqual(len(kerekek), 1)
        self.assertEqual(kerekek[0].fogszam, 20)
        self.assertAlmostEqual(kerekek[0].osztokor_atmero, 40.0)

    def test_turesmodok(self):
        sorok = []
        for mod in ("nevleges", "min", "max", "kozep"):
            sor = list(JO_SOR)
            sor[0] = f"kerek_{mod}"
            sor[8] = mod
            sorok.append(sor)
        kerekek = {
            k.turesmod: k for k in fogaskerekek_beolvasasa(self.excel_keszit(sorok))
        }
        self.assertAlmostEqual(kerekek["nevleges"].furat_atmero, 8.0)
        self.assertAlmostEqual(kerekek["min"].furat_atmero, 8.0)
        self.assertAlmostEqual(kerekek["max"].furat_atmero, 8.015)
        self.assertAlmostEqual(kerekek["kozep"].furat_atmero, 8.0075)

    def test_tizedesvesszo(self):
        sor = list(JO_SOR)
        sor[1] = "2,0"
        kerekek = fogaskerekek_beolvasasa(self.excel_keszit([sor]))
        self.assertAlmostEqual(kerekek[0].modul, 2.0)

    def test_hianyzo_oszlop(self):
        fejlec = [c for c in KOTELEZO_OSZLOPOK if c != "fogszam"]
        sor = [v for c, v in zip(KOTELEZO_OSZLOPOK, JO_SOR) if c != "fogszam"]
        with self.assertRaises(EllenorzesiHiba):
            fogaskerekek_beolvasasa(self.excel_keszit([sor], fejlec=fejlec))

    def test_keves_fog(self):
        sor = list(JO_SOR)
        sor[2] = 3
        with self.assertRaises(EllenorzesiHiba):
            fogaskerekek_beolvasasa(self.excel_keszit([sor]))

    def test_ismetlodo_nev(self):
        with self.assertRaises(EllenorzesiHiba):
            fogaskerekek_beolvasasa(self.excel_keszit([JO_SOR, JO_SOR]))


if __name__ == "__main__":
    unittest.main()
