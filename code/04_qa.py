#!/usr/bin/env python3
"""04_qa.py - run the QA checker on the compiled tables and write the release files.

Plain-language note: this script runs the open QA checker (the mcrqa package in this
repository) over every sample and measurement, then writes the final tables, the QA
report (data/processed/qa_report.txt), and stats.json (every number quoted in the
documents). Run it with `python code/04_qa.py`. You do not need to open it.
"""
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from mcrqa import FLAG_DOC, flag_analyses, flag_samples, load_rules  # noqa: E402
from mcrqa import __version__ as QA_VERSION  # noqa: E402

OUT = os.path.join(ROOT, "data", "processed")
VERSION = "1.0.1"
WIDE_ANALYTES = ["SiO2", "TiO2", "Al2O3", "Fe2O3T", "Fe2O3", "FeO", "MnO", "MgO", "CaO", "Na2O", "K2O", "P2O5",
                 "LOI", "H2O", "CO2", "S", "C", "Ni", "Cu", "Co", "Cr", "V", "Sc", "Zn", "Pb", "Ag", "As", "Mo",
                 "Au", "Pt", "Pd", "Rh", "Ru", "Ir", "Os", "Re", "Rb", "Sr", "Ba", "Cs", "Y", "Zr", "Hf", "Nb", "Ta",
                 "Th", "U", "La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu",
                 "Li", "Be", "B", "Ga", "Ge", "Sn", "Sb", "W", "Bi", "Te", "Se", "Cd", "In", "Tl", "Hg", "F", "Cl"]
UNIT_SUFFIX = {"wt%": "wt", "ppm": "ppm", "ppb": "ppb"}
NGDB_FS = "https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer"


def wide_table(samples, long):
    b = long[long["is_best_value"]].copy()
    # negative number = below detection limit of |value| (USGS convention), documented in the codebook
    b["wide_value"] = np.where(b["censor"] == "<", -b["detection_limit"].fillna(np.nan), b["value"])
    b.loc[(b["censor"] == "<") & b["detection_limit"].isna(), "wide_value"] = np.nan
    unit = b.groupby("analyte")["unit"].first()
    piv = b.pivot_table(index="mcr_uid", columns="analyte", values="wide_value", aggfunc="first")
    cols = [a for a in WIDE_ANALYTES if a in piv.columns]
    piv = piv[cols]
    piv.columns = [f"{a}_{UNIT_SUFFIX[unit[a]]}" for a in cols]
    meta = ["mcr_uid", "source_id", "source_sample_id", "latitude", "longitude", "coord_quality", "state",
            "sample_type", "mineral", "rock_class", "rock_name", "stratigraphy", "mcr_class", "mcr_match",
            "sgmc_label", "major_oxide_total", "loi_wt", "cia", "ai_ishikawa", "altered_likely", "duplicate_group",
            "qa_flags", "license", "dataset_version"]
    return samples[meta].merge(piv, left_on="mcr_uid", right_index=True, how="left")


def pick_spot_checks(samples, long):
    """Deterministic, varied spot checks: easy, hard, extreme, every source."""
    b = long[long["is_best_value"]]
    v = lambda uid, a: b[(b.mcr_uid == uid) & (b.analyte == a)]  # noqa: E731
    picks = []
    s1 = samples[samples.source_id == "S1"]

    def add(uid, analytes, why):
        if uid is None or uid in [p["mcr_uid"] for p in picks]:
            return
        r = samples.set_index("mcr_uid").loc[uid]
        for a in analytes:
            x = v(uid, a)
            if len(x):
                x = x.iloc[0]
                picks.append(dict(mcr_uid=uid, source_id=r.source_id, source_sample_id=r.source_sample_id,
                                  analyte=a, value=x.value, unit=x.unit, censor=x.censor,
                                  detection_limit=x.detection_limit, value_source=x.value_source,
                                  unit_source=x.unit_source, method=x.method_code_source, why=why))

    pt = b[(b.analyte == "Pt") & (b.censor == "") & b.mcr_uid.isin(s1.mcr_uid)].sort_values("value")
    add(pt.mcr_uid.iloc[-1] if len(pt) else None, ["Pt", "Pd", "Cu", "Ni"], "highest detected Pt in the USGS NGDB set (extreme)")
    plv = s1[s1.stratigraphy.fillna("").str.contains("Portage Lake", case=False)]
    sio = b[(b.analyte == "SiO2") & b.mcr_uid.isin(plv.mcr_uid) & (b.method_code_source == "WDX_Fuse")]
    add(sio.mcr_uid.sort_values().iloc[0] if len(sio) else None, ["SiO2", "MgO", "Fe2O3T"], "Portage Lake basalt majors (Si as element converted to SiO2)")
    nsh = s1[s1.stratigraphy.fillna("").str.contains("Nonesuch", case=False)]
    cu = b[(b.analyte == "Cu") & b.mcr_uid.isin(nsh.mcr_uid) & (b.censor == "")].sort_values("value")
    add(cu.mcr_uid.iloc[-1] if len(cu) else None, ["Cu", "Ag"], "Nonesuch Shale copper (rift sediment, White Pine host)")
    es = b[(b.analyte == "Pt") & (b.censor == "<") & (b.method_code_source == "ES_SQ") & b.mcr_uid.isin(s1.mcr_uid)]
    add(es.mcr_uid.sort_values().iloc[0] if len(es) else None, ["Pt", "Au"], "legacy below-detection Pt with a very high limit (hard case)")
    s2 = b[(b.analyte == "Pd") & b.mcr_uid.str.startswith("MCRG-S2-") & (b.censor == "")].sort_values("value")
    if len(s2):
        top = s2.mcr_uid.iloc[-1]
        pdv = s2.value.iloc[-1]
        ptv = b[(b.mcr_uid == top) & (b.analyte == "Pt")].value
        ratio = f"; Pd/Pt = {pdv / ptv.iloc[0]:.0f}, unusually high: confirm the source has no typo" if len(ptv) and ptv.iloc[0] else ""
        add(top, ["Pd", "Pt", "Cu"], "USGS Duluth drill core, highest Pd" + ratio)
    nsv = samples[(samples.source_id == "S4") & samples.stratigraphy.fillna("").str.contains("NORTH SHORE")]
    add(nsv.mcr_uid.sort_values().iloc[0] if len(nsv) else None, ["SiO2", "TiO2", "Zr"], "GEOROC North Shore Volcanic Group")
    add("MCRG-S6-9550" if (samples.mcr_uid == "MCRG-S6-9550").any() else None, ["SiO2", "Fe2O3T", "Ni"], "EarthChem Portage Lake sample 9550")
    add("MCRG-S7-C-392223" if (samples.mcr_uid == "MCRG-S7-C-392223").any() else None, ["Cu", "Ni", "Al2O3"], "Woodruff (2019) troctolite FR-3")
    s5 = samples[(samples.source_id == "S5") & samples.mineral.fillna("").str.upper().str.contains("OLIVINE")]
    add(s5.mcr_uid.sort_values().iloc[0] if len(s5) else None, ["MgO", "SiO2"], "GEOROC olivine grain (mineral chemistry)")
    return pd.DataFrame(picks)


def source_link(row, samples):
    s = samples.set_index("mcr_uid").loc[row.mcr_uid]
    if row.source_id == "S1":
        layer = 3 if s.sample_type == "mineral_separate" else 1
        return f"{NGDB_FS}/{layer}/query?where=lab_id%3D%27{s.source_sample_id}%27&outFields=*&f=html"
    return {"S2": "https://doi.org/10.5066/P13UFQYF (file MCR_USGS_geochem_BV.csv, column Field_ID)",
            "S4": "https://doi.org/10.25625/WSTPOX (file ...MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN.csv, column UNIQUE_ID)",
            "S5": "https://doi.org/10.25625/SGFTFN (mineral file named in 'project'; data/raw/georoc/georoc_minerals_mcr_region.csv)",
            "S6": "https://ecl.earthchem.org/view.php?id=1501 (sheet '3 Data')",
            "S7": "https://doi.org/10.5066/P9VO251H (file Bedrock.csv, column Lab No.)"}.get(row.source_id, "")


def main():
    rules = load_rules()
    samples = pd.read_csv(os.path.join(OUT, "_stage_samples.csv"), low_memory=False)
    long = pd.read_parquet(os.path.join(OUT, "_stage_long2.parquet"))
    counts = pd.read_csv(os.path.join(OUT, "_stage_counts.csv"))
    excluded = pd.read_csv(os.path.join(OUT, "excluded_samples.csv"), low_memory=False)
    print("flagging determinations ...")
    long = flag_analyses(long, samples, rules)
    ac = long["author_corrected"].fillna(False).astype(bool)
    long.loc[ac, "qa_flags"] = [";".join(sorted(set(filter(None, f.split(";"))) | {"AUTHOR_CORRECTED"})) for f in long.loc[ac, "qa_flags"]]
    sus = long["author_note"].fillna("").str.startswith("flag") & ~ac
    long.loc[sus, "qa_flags"] = [";".join(sorted(set(filter(None, f.split(";"))) | {"SOURCE_VALUE_SUSPECT"})) for f in long.loc[sus, "qa_flags"]]
    print("flagging samples ...")
    samples = flag_samples(samples, long, rules)
    samples["dataset_version"] = VERSION

    long.to_parquet(os.path.join(OUT, "mcr_geochem_analyses_long.parquet"), index=False)
    long.to_csv(os.path.join(OUT, "mcr_geochem_analyses_long.csv"), index=False)
    samples.to_csv(os.path.join(OUT, "mcr_geochem_samples.csv"), index=False)
    wide = wide_table(samples, long)
    wide.to_csv(os.path.join(OUT, "mcr_geochem_wide.csv"), index=False)

    # ---------------- stats
    best = long[long.is_best_value]
    st = {"version": VERSION, "build_date": dt.date.today().isoformat(), "qa_checker_version": QA_VERSION}
    st["n_samples"] = int(len(samples))
    st["n_determinations"] = int(len(long))
    st["n_best_values"] = int(len(best))
    st["n_analytes"] = int(long.analyte.nunique())
    st["n_method_codes"] = int(pd.read_csv(os.path.join(OUT, "method_crosswalk.csv")).shape[0])
    st["n_excluded"] = int(len(excluded))
    st["samples_by_source"] = samples.groupby("source_id").size().to_dict()
    st["samples_by_state"] = samples.groupby("state").size().to_dict()
    st["samples_by_type"] = samples.groupby("sample_type").size().to_dict()
    st["samples_by_mcr_class"] = samples.groupby("mcr_class").size().to_dict()
    st["samples_by_rock_class"] = samples.groupby("rock_class").size().to_dict()
    st["samples_by_mcr_match"] = samples.groupby("mcr_match").size().to_dict()
    st["pct_censored_best"] = round(100 * (best.censor == "<").mean(), 1)
    fa = long.qa_flags.str.split(";").explode()
    st["determination_flags"] = fa[fa != ""].value_counts().to_dict()
    fs = samples.qa_flags.str.split(";").explode()
    st["sample_flags"] = fs[fs != ""].value_counts().to_dict()
    st["n_altered_likely"] = int(samples.altered_likely.sum())
    ig = samples[samples.rock_class.str.startswith("igneous") & (samples.sample_type == "whole_rock")]
    st["n_igneous_wholerock"] = int(len(ig))
    st["n_igneous_altered_likely"] = int(ig.altered_likely.sum())
    st["n_duplicate_groups"] = int(samples.duplicate_group.replace("", np.nan).nunique())
    st["n_samples_in_duplicate_groups"] = int((samples.duplicate_group != "").sum())
    cm = {}
    for a in ["Ni", "Cu", "Co", "Pt", "Pd", "Au"]:
        x = best[best.analyte == a]
        cm[a] = dict(n=int(len(x)), n_detected=int((x.censor == "").sum()),
                     n_bdl=int((x.censor == "<").sum()),
                     n_bdl_uninformative=int(x.qa_flags.str.contains("BDL_UNINFORMATIVE").sum()),
                     median_detected=None if (x.censor == "").sum() == 0 else float(round(x[x.censor == ""].value.median(), 2)),
                     unit=x.unit.iloc[0] if len(x) else "")
    st["critical_metals"] = cm
    tot = samples.major_oxide_total.dropna()
    st["major_totals"] = dict(n=int(len(tot)), within_range=int(tot.between(rules["total_min"], rules["total_max"]).sum()),
                              median=float(round(tot.median(), 2)))
    st["counts_by_source"] = counts.to_dict(orient="records")
    with open(os.path.join(OUT, "stats.json"), "w") as f:
        json.dump(st, f, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))

    spots = pick_spot_checks(samples, long)
    spots["where_to_check"] = [source_link(r, samples) for r in spots.itertuples()]
    spots.to_csv(os.path.join(OUT, "spot_checks.csv"), index=False)

    # ---------------- report
    L = []
    w = L.append
    w(f"MCR-GeoChem v{VERSION} QA report   (built {st['build_date']}, mcrqa {QA_VERSION})")
    w("Plain-language note: this file lists every check the pipeline ran. Read the 'Spot checks'")
    w("section during verification; the rest is reference.")
    w("")
    w("1. ROW COUNTS BY STAGE")
    w(counts.to_string(index=False))
    w("")
    w(f"Total kept: {st['n_samples']:,} samples, {st['n_determinations']:,} determinations "
      f"({st['n_best_values']:,} best values, {st['n_analytes']} analytes).")
    w(f"Excluded: {st['n_excluded']:,} samples (data/processed/excluded_samples.csv, one reason each).")
    w("")
    w("2. RIFT MEMBERSHIP: HOW EACH KEPT SAMPLE WAS MATCHED")
    w(pd.Series(st["samples_by_mcr_match"]).to_string())
    w("  text = source names a rift unit; map = sample sits on an SGMC rift map unit (docs/mcr_units.csv);")
    w("  context = rift named only in locality or project. 'map' and 'context' are lower confidence.")
    w("")
    w("3. COMPOSITION OF THE DATASET")
    for k in ("samples_by_state", "samples_by_type", "samples_by_mcr_class", "samples_by_rock_class"):
        w(f"  {k}: {st[k]}")
    w("")
    w("4. FLAGS")
    w("  Determinations:")
    for k, v in st["determination_flags"].items():
        w(f"    {k:<22}{v:>9,}  {FLAG_DOC.get(k, '')}")
    w("  Samples:")
    for k, v in st["sample_flags"].items():
        w(f"    {k:<22}{v:>9,}  {FLAG_DOC.get(k, '')}")
    w(f"  Igneous whole-rock samples: {st['n_igneous_wholerock']:,}; flagged likely altered: {st['n_igneous_altered_likely']:,}")
    w(f"  Possible cross-source duplicate groups: {st['n_duplicate_groups']} ({st['n_samples_in_duplicate_groups']} samples). Kept and flagged, not deleted.")
    w("")
    w("5. CRITICAL METALS (best values)")
    for a, d in cm.items():
        w(f"  {a}: n={d['n']:,} detected={d['n_detected']:,} below-detection={d['n_bdl']:,} "
          f"(uninformative limit {d['n_bdl_uninformative']:,}); median detected {d['median_detected']} {d['unit']}")
    w("")
    w("6. RANGE CHECKS")
    w(f"  Major-oxide totals (8+ oxides): n={st['major_totals']['n']:,}, within {rules['total_min']}-{rules['total_max']} wt%: "
      f"{st['major_totals']['within_range']:,}, median {st['major_totals']['median']}")
    rng = best[best.value.notna()].groupby(["analyte", "unit"]).value.agg(["count", "min", "median", "max"]).reset_index()
    rng = rng[rng.analyte.isin(["SiO2", "MgO", "Fe2O3T", "Na2O", "K2O", "LOI", "Ni", "Cu", "Co", "Cr", "Pt", "Pd", "Au", "S"])]
    w(rng.to_string(index=False))
    w("")
    w("7. SPOT CHECKS (verify each against the source; links in spot_checks.csv)")
    for r in spots.itertuples():
        shown = f"{r.censor}{r.detection_limit:g}" if r.censor == "<" else f"{r.value:g}"
        w(f"  {r.mcr_uid:<34} {r.analyte:<7} {shown:>10} {r.unit:<4} | source shows: {r.value_source} {r.unit_source} (method {r.method}) | {r.why}")
    with open(os.path.join(OUT, "qa_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L[:60]))


if __name__ == "__main__":
    main()
