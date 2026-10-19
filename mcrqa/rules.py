"""Default thresholds for the MCR-GeoChem QA checker.

Every number here is a documented, adjustable default. Pass a JSON file with --rules to override
any of them. Each rule names its basis so users can judge whether it suits their rocks.
"""

DEFAULT_RULES = {
    # ---- detection limits
    # A below-detection result is "uninformative" when its detection limit exceeds this value
    # (harmonized units). Basis: typical crustal or mafic-rock abundance; a "<" above it tells you
    # almost nothing about the rock. Mostly catches legacy emission-spectrography limits.
    "uninformative_dl": {
        "Au": 10.0, "Pt": 10.0, "Pd": 10.0, "Rh": 5.0, "Ru": 5.0, "Ir": 5.0, "Os": 5.0, "Re": 5.0,  # ppb
        "Ni": 50.0, "Cu": 50.0, "Co": 20.0, "Cr": 50.0, "Zn": 100.0, "Pb": 20.0, "Ag": 1.0, "As": 10.0,
        "Mo": 5.0, "Sb": 2.0, "Bi": 2.0, "Cd": 2.0, "Sn": 10.0, "W": 10.0, "U": 5.0, "Th": 10.0,
        "Nb": 20.0, "Ta": 5.0, "La": 20.0, "Ce": 50.0, "Nd": 20.0, "Y": 10.0, "Yb": 5.0, "Eu": 2.0,
        "Be": 5.0, "B": 20.0, "Li": 20.0, "Sc": 10.0, "V": 20.0, "Ba": 50.0, "Sr": 50.0, "Zr": 50.0,
        "Te": 1.0, "Se": 1.0, "Hg": 0.1, "In": 1.0, "Tl": 2.0, "Ga": 10.0, "Ge": 5.0,
    },
    # ---- plausibility ceilings for whole-rock data (harmonized units); above = possible unit error
    # unless the sample is mineralized (S > mineralized_S_wt). Basis: maxima of unmineralized
    # crustal and mantle rocks, generous by an order of magnitude.
    "ceiling_wholerock": {
        "Au": 1000.0, "Pt": 2000.0, "Pd": 3000.0, "Rh": 300.0, "Ru": 300.0, "Ir": 300.0, "Os": 300.0,
        "Ni": 5000.0, "Cu": 5000.0, "Co": 500.0, "Cr": 20000.0, "Zn": 5000.0, "Pb": 2000.0, "Ag": 50.0,
        "SiO2": 100.0, "TiO2": 15.0, "Al2O3": 40.0, "Fe2O3T": 60.0, "MnO": 5.0, "MgO": 52.0, "CaO": 60.0,
        "Na2O": 15.0, "K2O": 15.0, "P2O5": 15.0,
    },
    "mineralized_S_wt": 1.0,
    # ---- oxide totals (whole rock; SiO2, Al2O3, Fe2O3T, MgO, CaO, Na2O, K2O measured and 8+ of 10 majors)
    "total_min": 96.0, "total_max": 102.5,
    # SiO2 in an igneous whole rock between these bounds may be Si-element mislabeled as SiO2
    "si_element_suspect": [15.0, 32.0],
    # ---- alteration (igneous whole rock)
    "loi_max": 3.0,                # wt%; above suggests hydration or carbonation
    "cia_max": 60.0,               # Chemical Index of Alteration (Nesbitt & Young 1982)
    "ai_range": [20.0, 65.0],      # Ishikawa alteration index box for least-altered rocks (Large et al. 2001)
    "alteration_words": ["altered", "alteration", "moderat", "extensive", "strong", "weather", "propylit",
                         "chlorit", "sericit", "serpentin", "epidot", "carbonat", "silicif", "potassic",
                         "argillic", "zeolit"],
    "fresh_words": ["fresh", "unaltered", "none", "slight", "least altered", "no alteration"],
    # ---- duplicates across sources
    "dup_distance_deg": 0.005,     # ~500 m
    "dup_rel_tol": 0.01,           # 1% relative on SiO2 and MgO
}
