"""Evolvens fogprofil számítása. Tiszta Python, FreeCAD nélkül is futtatható."""

import math

OLDALANKENTI_PONTOK = 15
FEJ_KOZBENSO_PONTOK = 2
LAB_KOZBENSO_PONTOK = 3


def evolvens(szog):
    """Az evolvens függvény: inv(a) = tan(a) - a."""
    return math.tan(szog) - szog


def fel_fogszog(adat, sugar):
    """A fog félszöge (radiánban) a megadott sugáron.

    A fogközépvonaltól az egyik fogoldalig mért szög. Az alapkör alatt
    az értéket az alapkörön számoljuk (ott a fogoldal sugárirányú).
    """
    fogszam = adat["fogszam"]
    alfa = math.radians(adat["nyomaszog"])
    alapkor_sugar = adat["alapkor_atmero"] / 2
    sugar = max(sugar, alapkor_sugar)
    return (
        math.pi / (2 * fogszam)
        + evolvens(alfa)
        - evolvens(math.acos(alapkor_sugar / sugar))
    )


def _polar(sugar, szog):
    return (sugar * math.cos(szog), sugar * math.sin(szog))


def fogprofil_pontok(adat):
    """A teljes fogaskerék körvonala (x, y) pontok listájaként, óramutatóval ellentétesen."""
    fogszam = int(adat["fogszam"])
    alapkor_sugar = adat["alapkor_atmero"] / 2
    fejkor_sugar = adat["fejkor_atmero"] / 2
    labkor_sugar = adat["labkor_atmero"] / 2
    kezdo_sugar = max(alapkor_sugar, labkor_sugar)

    fej_felszog = fel_fogszog(adat, fejkor_sugar)
    if fej_felszog <= 0:
        raise ValueError("a fog hegyes lenne, növeld a fogszámot")

    kezdo_felszog = fel_fogszog(adat, kezdo_sugar)
    if 2 * math.pi / fogszam - 2 * kezdo_felszog <= 0:
        raise ValueError("a fogak összeérnek a lábkörnél")

    sugarak = [
        kezdo_sugar + (fejkor_sugar - kezdo_sugar) * i / (OLDALANKENTI_PONTOK - 1)
        for i in range(OLDALANKENTI_PONTOK)
    ]
    lab_ala_esik = labkor_sugar < alapkor_sugar

    pontok = []
    for k in range(fogszam):
        kozep = 2 * math.pi * k / fogszam
        kovetkezo = 2 * math.pi * (k + 1) / fogszam

        # jobb fogoldal, alulról felfelé
        if lab_ala_esik:
            pontok.append(_polar(labkor_sugar, kozep - kezdo_felszog))
        for sugar in sugarak:
            pontok.append(_polar(sugar, kozep - fel_fogszog(adat, sugar)))

        # fogfej a fejkörön
        for i in range(1, FEJ_KOZBENSO_PONTOK + 1):
            szog = kozep - fej_felszog + 2 * fej_felszog * i / (FEJ_KOZBENSO_PONTOK + 1)
            pontok.append(_polar(fejkor_sugar, szog))

        # bal fogoldal, felülről lefelé
        for sugar in reversed(sugarak):
            pontok.append(_polar(sugar, kozep + fel_fogszog(adat, sugar)))
        if lab_ala_esik:
            pontok.append(_polar(labkor_sugar, kozep + kezdo_felszog))

        # fogárok alja a lábkörön a következő fogig
        lab_kezdet = kozep + kezdo_felszog
        lab_veg = kovetkezo - kezdo_felszog
        for i in range(1, LAB_KOZBENSO_PONTOK + 1):
            szog = lab_kezdet + (lab_veg - lab_kezdet) * i / (LAB_KOZBENSO_PONTOK + 1)
            pontok.append(_polar(labkor_sugar, szog))

    return pontok
