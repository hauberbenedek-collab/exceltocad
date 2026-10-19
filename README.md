# exceltocad
Excel táblázatból (méretek, tűrések) automatikusan legenerálja egy alkatrész (pl. fogaskerék) 3D-s modelljét.
cd ~/Documents/GitHub/egyetem/exceltocad
cat > README.md << 'EOF'
# Excel-ből fogaskerék 3D modell generátor

Python script FreeCAD-hez, amely egy Excel táblázatból (méretek, tűrések) automatikusan legenerálja egyenes fogazatú, evolvens fogprofilú fogaskerekek 3D modelljét. A kimenet FreeCAD (`.FCStd`) és STEP (`.step`) fájl, amelyet bármilyen CAD program megnyit.

Egyetemi projektfeladat, Széchenyi István Egyetem, mechatronikai mérnöki BSc. Készítette: Hauber Benedek.

## Képek



## Hogyan működik

```
Excel (adat/fogaskerekek.xlsx)
        |  forras/excel_olvaso.py: beolvasás, ellenőrzés, számítások
        v
JSON (kimenet/fogaskerekek.json)
        |  forras/fogaskerek_generator.py (FreeCAD): fogprofil, kihúzás, furat
        v
3D modell (kimenet/<nev>.FCStd és kimenet/<nev>.step)
```

A projekt két részre van bontva, mert a FreeCAD saját Pythonja nem tartalmazza az `openpyxl` csomagot. Az Excel beolvasása ezért a rendes Pythonnal fut, és JSON fájlban adja át az adatokat a FreeCAD scriptnek.

## Követelmények

- FreeCAD (tesztelve: 1.1.4)
- Python 3
- `openpyxl` (a `requirements.txt` tartalmazza)
- Tesztelt rendszer: macOS

## Telepítés

```
git clone https://github.com/FELHASZNALONEV/exceltocad.git
cd exceltocad
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Használat

1. **Az Excel kitöltése.** A bemeneti fájl az `adat/fogaskerekek.xlsx`. Egy sor egy fogaskerék. Minta fájlt a `python3 minta_excel_keszito.py` paranccsal lehet készíteni.
2. **Az Excel beolvasása és ellenőrzése** (a projekt gyökeréből, aktív `.venv`-vel):
```
   python3 forras/excel_olvaso.py adat/fogaskerekek.xlsx
```
   Ez kiírja a fogaskerekek főbb adatait, és létrehozza a `kimenet/fogaskerekek.json` fájlt. Hibás adat esetén megmondja, melyik sorban mi a hiba.
3. **A 3D modellek generálása FreeCAD-del:**
```
   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd forras/fogaskerek_generator.py
```
   Más rendszeren a `freecadcmd` elérési útja eltér (azt nem teszteltem).
4. **Az eredmény** a `kimenet` mappában van: minden kerékhez egy `.FCStd` és egy `.step` fájl. A `.FCStd` a FreeCAD-ben megnyitható (File > Open).

## Az Excel oszlopai

| Oszlop | Jelentés | Egység | Megkötés |
|---|---|---|---|
| `nev` | a fogaskerék neve, ez lesz a fájlnév | | kötelező, egyedi |
| `modul` | fogaskerék modul | mm | pozitív |
| `fogszam` | fogak száma | db | egész, legalább 8 |
| `nyomaszog` | kapcsolószög | fok | 10 és 30 között |
| `szelesseg` | a kerék szélessége (vastagsága) | mm | pozitív |
| `furat_nevleges` | furat névleges átmérője | mm | pozitív, kisebb a lábkör átmérőjénél |
| `furat_felso` | furat felső határeltérése | mm | nem kisebb az alsónál |
| `furat_also` | furat alsó határeltérése | mm | |
| `turesmod` | melyik méretre modellezzen | | `nevleges`, `kozep`, `min` vagy `max` |

A tizedesvessző és a tizedespont is elfogadott.

## Tűrésmódok

A furat átmérőjét a `turesmod` oszlop határozza meg. Példa: névleges 8 mm, felső eltérés +0,015, alsó eltérés 0:

| `turesmod` | Modellezett furatátmérő |
|---|---|
| `nevleges` | 8,000 mm |
| `min` | 8,000 mm (névleges + alsó eltérés) |
| `max` | 8,015 mm (névleges + felső eltérés) |
| `kozep` | 8,0075 mm (a tűrésmező közepe) |

## Számítások

| Méret | Képlet |
|---|---|
| osztókör átmérő | d = m · z |
| fejkör átmérő | da = d + 2m |
| lábkör átmérő | df = d - 2,5m |
| alapkör átmérő | db = d · cos(α) |

A fogoldal evolvens görbe, amelyet az alapkörből számol a program az evolvens függvénnyel: inv(α) = tan(α) - α. A fog vastagsága az osztókörön π·m/2. A fogoldalt oldalanként 15 pont írja le, a profil ezek összekötéséből áll.

## Mappaszerkezet

```
exceltocad/
├── README.md
├── requirements.txt
├── minta_excel_keszito.py     minta Excel generálása
├── adat/                      bemeneti Excel fájl
├── forras/
│   ├── excel_olvaso.py        Excel beolvasás, ellenőrzés, JSON export
│   ├── evolvens.py            evolvens fogprofil számítása (tiszta Python)
│   └── fogaskerek_generator.py  FreeCAD script a 3D testhez
├── tesztek/                   egységtesztek
├── kimenet/                   generált JSON, FCStd és STEP fájlok
└── dokumentacio/              képek és leírások
```

## Tesztek

```
python3 -m unittest discover -s tesztek -p "teszt*.py" -v
```

A tesztek az Excel beolvasót (érvényes és hibás adatok, tűrésmódok) és a fogprofilt (sugárhatárok, forgásszimmetria, fogvastagság az osztókörön) ellenőrzik.

## Ismert korlátok

- Csak egyenes fogazatú fogaskereket készít.
- A fogprofil szakaszos vonalakkal közelített, nem sima görbe.
- A tűrés jelenleg a furat átmérőjére hat.
- A fogszám legalább 8 lehet.
- Csak macOS-en tesztelt.
EOF
open README.md