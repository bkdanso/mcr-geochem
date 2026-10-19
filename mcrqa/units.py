"""Analyte names, unit harmonization, and censored-value parsing.

Targets: major oxides and volatiles in wt%; Au, platinum-group elements and Re in ppb;
all other elements in ppm. Element-basis majors (e.g. Si in %) are converted to oxides
with standard gravimetric factors. Below/above-limit conventions handled:
USGS negative values (<), USGS fractional .11111 (>), and text '<x', '>x', 'bdl'.
"""
import math
import re

# ---------------------------------------------------------------- analytes and units
# Element reported as element-% -> oxide wt% (standard gravimetric factors)
ELEMENT_TO_OXIDE = {
    "Si": ("SiO2", 2.1393), "Ti": ("TiO2", 1.6681), "Al": ("Al2O3", 1.8895),
    "Fe": ("Fe2O3T", 1.4297), "Mn": ("MnO", 1.2912), "Mg": ("MgO", 1.6583),
    "Ca": ("CaO", 1.3992), "Na": ("Na2O", 1.3480), "K": ("K2O", 1.2046), "P": ("P2O5", 2.2914),
}
FEO_TO_FE2O3 = 1.1113

MAJOR_OXIDES = ["SiO2", "TiO2", "Al2O3", "Fe2O3T", "MnO", "MgO", "CaO", "Na2O", "K2O", "P2O5"]
OTHER_WT_PCT = ["Fe2O3", "FeO", "LOI", "H2O", "H2O+", "H2O-", "CO2", "S", "C", "C_org", "C_carb",
                "SO3", "Cr2O3", "NiO", "BaO", "SrO", "ZrO2", "V2O3", "ZnO", "CoO", "CuO", "Ce2O3", "V2O5"]
PPB_ANALYTES = {"Au", "Pt", "Pd", "Rh", "Ru", "Ir", "Os", "Re"}
SYMBOLS = ("H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se "
           "Br Kr Rb Sr Y Zr Nb Mo Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Sm Eu Gd Tb Dy Ho "
           "Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Th U").split()
SYMBOL_BY_UPPER = {s.upper(): s for s in SYMBOLS}
OXIDE_BY_UPPER = {o.upper(): o for o in MAJOR_OXIDES + OTHER_WT_PCT}
OXIDE_BY_UPPER.update({"FE2O3T": "Fe2O3T", "FEOT": "FeOT", "FE2O3": "Fe2O3", "FEO": "FeO",
                       "H2OP": "H2O+", "H2OM": "H2O-", "H2OT": "H2O", "H2O_PLUS": "H2O+",
                       "H2O_MINUS": "H2O-", "TOTAL_H2O": "H2O", "H2OB": "H2O+", "H2OM_": "H2O-",
                       "CORG": "C_org", "ORGANIC_C": "C_org", "CCO3": "C_carb", "CRBNT_C": "C_carb",
                       "CINORG": "C_carb"})
WT_PCT_SET = set(MAJOR_OXIDES) | set(OTHER_WT_PCT) | {"FeOT"}
NON_CHEMISTRY = {"DENSB", "DENSP", "PH", "SPLWTAU", "SPLWTFA", "ASH", "ACIDINSOL", "SULFIDE", "SPYR",
                 "SORG", "SO4", "VOLATILES", "OTHERS", "O", "OH", "CH4", "CO1", "CL2", "SO2", "B2O3"}

UNIT_ALIASES = {"pct": "wt%", "wt%": "wt%", "wt.%": "wt%", "%": "wt%", "percent": "wt%",
                "ppm": "ppm", "ppb": "ppb", "ppt": "ppt", "g/t": "ppm", "mg/kg": "ppm", "ug/kg": "ppb"}


def canon_analyte(name):
    """Return the canonical analyte name for a source label (case-insensitive), or None."""
    if name is None:
        return None
    n = str(name).strip().replace(" ", "")
    u = n.upper()
    if u in NON_CHEMISTRY:
        return None
    if u in OXIDE_BY_UPPER:
        return OXIDE_BY_UPPER[u]
    if u == "LOI":
        return "LOI"
    if u in SYMBOL_BY_UPPER:
        return SYMBOL_BY_UPPER[u]
    return None


def harmonize(analyte, unit, value):
    """Convert one (analyte, unit, value) to the target scheme.

    Returns (analyte_h, unit_h, value_h, rule) or None if not chemistry.
    Targets: major oxides and volatiles wt%; Au, PGE, Re ppb; all other elements ppm.
    """
    a = canon_analyte(analyte)
    if a is None or value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    u = UNIT_ALIASES.get(str(unit).strip().lower())
    if u is None:
        return None
    to_wt = {"wt%": 1.0, "ppm": 1e-4, "ppb": 1e-7, "ppt": 1e-10}
    to_ppm = {"wt%": 1e4, "ppm": 1.0, "ppb": 1e-3, "ppt": 1e-6}
    if a in ELEMENT_TO_OXIDE:
        ox, f = ELEMENT_TO_OXIDE[a]
        return ox, "wt%", value * to_wt[u] * f, f"{a} {u} -> {ox} wt% (x{f})"
    if a == "FeOT":
        return "Fe2O3T", "wt%", value * to_wt[u] * FEO_TO_FE2O3, f"FeOT {u} -> Fe2O3T wt% (x{FEO_TO_FE2O3})"
    if a in WT_PCT_SET:
        return a, "wt%", value * to_wt[u], f"{a} {u} -> wt%"
    if a in PPB_ANALYTES:
        return a, "ppb", value * to_ppm[u] * 1e3, f"{a} {u} -> ppb"
    return a, "ppm", value * to_ppm[u], f"{a} {u} -> ppm"


# ---------------------------------------------------------------- censoring
def parse_usgs_qualified(v):
    """USGS NGDB 'qualified value': negative = less than |v|; fractional part .11111 = greater than.

    Returns (value, censor, limit). Detected: (v, '', None).
    """
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None, "", None
    v = float(v)
    if v < 0:
        return None, "<", -v
    frac = round(v - math.floor(v), 5)
    if abs(frac - 0.11111) < 1e-6:
        return None, ">", math.floor(v)
    return v, "", None


_NUM = re.compile(r"^\s*([<>]?)\s*(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*$")


def parse_text_value(s):
    """Parse '12.3', '<0.5', '>10000', 'bdl', 'n.d.'. Returns (value, censor, limit) or (None,'',None)."""
    if s is None:
        return None, "", None
    if isinstance(s, (int, float)):
        if isinstance(s, float) and math.isnan(s):
            return None, "", None
        return float(s), "", None
    t = str(s).strip()
    if t == "" or t.upper() in {"ND", "NA", "N/A", "NAN", "-", "--", "NS", "INS"}:
        return None, "", None
    if t.lower() in {"bdl", "b.d.l.", "bd", "b.d.", "n.d.", "<dl", "<lod"}:
        return None, "<", None
    m = _NUM.match(t.replace(",", ""))
    if not m:
        return None, "", None
    q, num = m.group(1), float(m.group(2))
    if q == "<":
        return None, "<", num
    if q == ">":
        return None, ">", num
    return num, "", None


