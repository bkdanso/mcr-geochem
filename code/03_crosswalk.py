#!/usr/bin/env python3
"""03_crosswalk.py - translate every lab method code into one vocabulary and tabulate detection limits.

Plain-language note: the sources use about 90 different codes for lab methods ("AES_HF",
"C_WDXRF-MAJORS", "NI_FINA" ...). This script writes data/processed/method_crosswalk.csv, which
gives each code a plain technique name, how the sample was dissolved (digestion), and whether the
result is total, partial, or only semi-quantitative. It also writes detection_limits.csv (the
smallest amount each method could measure, per element) and finishes the main long table.
You do not need to open it.
"""
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harmonize as H  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")

# ---- USGS (NGDB/AGDB) code grammar: <TECHNIQUE>_<DIGESTION>[_P]
USGS_TECH = [
    (r"^AA_CV", "AAS, cold vapor (CVAAS)"), (r"^AA_GF", "AAS, graphite furnace (GFAAS)"),
    (r"^AA_HG", "AAS, hydride generation (HGAAS)"), (r"^AA_FE", "AAS, flame emission"),
    (r"^AA_TR", "AAS, trace (solvent extraction)"), (r"^AA_F", "AAS, flame (FAAS)"),
    (r"^AES", "ICP-AES/OES"), (r"^MS", "ICP-MS"), (r"^CB_IRC", "Combustion, infrared (C, S)"),
    (r"^CB_TC", "Combustion, thermal conductivity"), (r"^CB_TT", "Combustion, titration"),
    (r"^CM", "Colorimetry/spectrophotometry"), (r"^CP$", "Coulometry"), (r"^DN$", "Delayed neutron counting"),
    (r"^EDX", "XRF, energy dispersive (EDXRF)"), (r"^WDX", "XRF, wavelength dispersive (WDXRF)"),
    (r"^ES_SQ", "Emission spectrography, semi-quantitative (DC-arc)"), (r"^ES_Q", "Emission spectrography, quantitative"),
    (r"^FA_AA", "Fire assay, AAS finish"), (r"^FA_ES", "Fire assay, emission spectrography finish"),
    (r"^FA_MS", "Fire assay, ICP-MS finish"), (r"^FA_AES", "Fire assay, ICP-AES finish"),
    (r"^FL", "Fluorimetry"), (r"^GV", "Gravimetry"), (r"^ISE", "Ion-selective electrode"),
    (r"^NA_", "Neutron activation (INAA)"), (r"^TT", "Titration"), (r"^VOL", "Volumetric (gasometric)"),
]
USGS_DIG = [
    (r"_AZ|_AR", "aqua regia", "partial"), (r"_HBr", "HBr-Br2 leach", "partial"),
    (r"_HNO3", "nitric acid", "partial"), (r"_HCl_OE", "HCl extraction", "partial"),
    (r"_HFST|_HF", "multi-acid incl. HF (4-acid)", "near-total"), (r"_HSF", "HF-H2SO4", "near-total"),
    (r"_Fuse|_Flux", "fusion", "total"), (r"_ST", "sodium peroxide sinter", "total"),
    (r"_IE", "fusion + ion exchange", "total"), (r"_HCl", "HCl dissolution", "partial"),
    (r"_Acid", "acid digestion", "partial"), (r"_WO", "without digestion", "total"),
]

EXPLICIT = {
    # USGS Duluth release (Parks et al., 2025) and Woodruff (2019), from their method tables
    ("S2", "C_CO2-CARB"): ("Combustion, infrared (carbonate C)", "perchloric acid evolution", "total"),
    ("S2", "C_CVAAS-HG"): ("AAS, cold vapor (CVAAS)", "H2SO4-HNO3-KMnO4", "near-total"),
    ("S2", "C_FA_AU-PD-PT"): ("Fire assay (Pb), ICP-OES/MS finish", "lead fire assay", "total"),
    ("S2", "C_FA_TRACE_AU-PD-PT"): ("Fire assay (Pb), ICP-MS finish", "lead fire assay", "total"),
    ("S2", "C_HGAAS-AS"): ("AAS, hydride generation (HGAAS)", "sodium peroxide fusion", "total"),
    ("S2", "C_HGAAS-SE"): ("AAS, hydride generation (HGAAS)", "multi-acid incl. HF (4-acid)", "near-total"),
    ("S2", "C_Se Hyd"): ("AAS, hydride generation (HGAAS)", "multi-acid incl. HF (4-acid)", "near-total"),
    ("S2", "C_ICPAES_MS_55"): ("ICP-AES + ICP-MS", "sodium peroxide sinter", "total"),
    ("S2", "C_ICPOES_MS-49"): ("ICP-OES + ICP-MS", "multi-acid incl. HF (4-acid)", "near-total"),
    ("S2", "C_ICPOES_MS-60"): ("ICP-OES + ICP-MS", "sodium peroxide fusion", "total"),
    ("S2", "C_ISE-CL"): ("Ion-selective electrode", "KOH fusion", "total"),
    ("S2", "C_ISE-F"): ("Ion-selective electrode", "NaOH fusion", "total"),
    ("S2", "C_NIS-FA_ICPMS-PGE"): ("Fire assay (NiS), INAA/ICP-MS finish", "nickel sulfide fire assay", "total"),
    ("S2", "C_ORGANIC-C"): ("Calculated (total C - carbonate C)", "none", "total"),
    ("S2", "C_TITR-FEO"): ("Titration (dichromate)", "H2SO4-HF-HCl", "total"),
    ("S2", "C_TOTAL-C"): ("Combustion, infrared (C, S)", "none (solid sample)", "total"),
    ("S2", "C_TOTAL-S"): ("Combustion, infrared (C, S)", "none (solid sample)", "total"),
    ("S2", "C_TOTAL-H2O"): ("Gravimetry (Penfield-type H2O)", "none (solid sample)", "total"),
    ("S2", "C_WDXRF-MAJORS"): ("XRF, wavelength dispersive (WDXRF)", "lithium borate fusion", "total"),
    ("S2", "FUS_ICP"): ("ICP-OES", "lithium borate fusion", "total"),
    ("S2", "FUS_MS"): ("ICP-MS", "lithium borate fusion", "total"),
    ("S2", "INAA"): ("Neutron activation (INAA)", "none (solid sample)", "total"),
    ("S2", "MULT INAA _ TD_ICP"): ("INAA or ICP-OES (lab did not specify)", "none or 4-acid", "near-total"),
    ("S2", "NI_FINA"): ("Fire assay (NiS), INAA finish", "nickel sulfide fire assay", "total"),
    ("S2", "TD_ICP"): ("ICP-OES", "multi-acid incl. HF (4-acid)", "near-total"),
    ("S7", "ICPAES_MS"): ("ICP-AES + ICP-MS", "multi-acid incl. HF (4-acid)", "near-total"),
    ("S7", "As_Hyd"): ("AAS, hydride generation (HGAAS)", "multi-acid incl. HF (4-acid)", "near-total"),
    ("S7", "Se_Hyd"): ("AAS, hydride generation (HGAAS)", "multi-acid incl. HF (4-acid)", "near-total"),
    ("S7", "CV_AA"): ("AAS, cold vapor (CVAAS)", "acid digestion", "near-total"),
    ("S7", "Coulometric_Crbnt_C"): ("Coulometry (carbonate C)", "acid evolution", "total"),
    ("S6", "ECL1501-1:XRF"): ("XRF (method details per source)", "not reported", "total"),
    ("S6", "ECL1501-1:ICP:MS-LA"): ("LA-ICP-MS", "not reported", "total"),
    ("S6", "ECL1501-2:"): ("Gravimetry (LOI)", "none (solid sample)", "total"),
}
NOT_REPORTED = ("Not reported in source file", "not reported", "unknown")


def usgs_classify(code, agdb):
    tech = next((t for p, t in USGS_TECH if re.search(p, code)), "Other/unknown")
    dig, ext = "none (solid sample)", "total"
    for p, d, e in USGS_DIG:
        if re.search(p, code):
            dig, ext = d, e
            break
    if code.endswith("_P"):
        ext = "partial"
    if code.startswith("ES_SQ"):
        ext = "semi-quantitative"
    if code.startswith(("FA_", "AA_TR")):
        dig = "fire assay" if code.startswith("FA_") else dig
    if code in ("GV", "GV_Flux", "CP", "DN", "EDX", "WDX_PP") or code.startswith("NA_"):
        dig = "fusion (flux)" if code == "GV_Flux" else "none (solid sample)"
    a = agdb.get(code)
    if a is not None and isinstance(a.get("DIGESTION_METHOD"), str) and a["DIGESTION_METHOD"] not in ("", "unknown"):
        dig = a["DIGESTION_METHOD"]
    return tech, dig, ext


def main():
    longdf = pd.read_parquet(os.path.join(OUT, "_stage_long.parquet"))
    samples = pd.read_csv(os.path.join(OUT, "_stage_samples.csv"), low_memory=False)
    longdf = longdf.merge(samples[["mcr_uid", "source_id"]], on="mcr_uid", how="left")
    am = pd.read_csv(os.path.join(RAW, "agdb4", "AnalyticMethod.txt"), sep=None, engine="python", encoding="latin1")
    agdb = {r.ANALYTIC_METHOD: r._asdict() for r in am.itertuples(index=False)}
    bib = pd.read_csv(os.path.join(RAW, "agdb4", "AnalyticMethod_Biblio.txt"), sep=None, engine="python", encoding="latin1")
    bibmap = {r.ANALYTIC_METHOD_PUB_ID: r.PUB_CITATION for r in bib.itertuples(index=False)}
    dul = pd.read_csv(os.path.join(RAW, "usgs_duluth", "MCR_USGS_geochem_methods.csv"))
    duldesc = dict(zip(dul.Method_abbreviation, dul.Method_description))

    g = (longdf.groupby(["source_id", "method_code_source"])
         .agg(n_determinations=("analyte", "size"), n_samples=("mcr_uid", "nunique"),
              analytes=("analyte", lambda s: " ".join(sorted(set(s)))))
         .reset_index())
    rows = []
    for r in g.itertuples(index=False):
        sid, code = r.source_id, r.method_code_source
        desc, ref = "", ""
        if (sid, code) in EXPLICIT:
            tech, dig, ext = EXPLICIT[(sid, code)]
            desc = duldesc.get(code, "")
            ref = {"S2": "Parks et al. (2025) method table, doi:10.5066/P13UFQYF",
                   "S7": "Woodruff (2019), doi:10.5066/P9VO251H",
                   "S6": "Davis et al. (2022) metadata sheet, doi:10.26022/IEDA/111501"}[sid]
        elif sid in ("S1", "S3"):
            tech, dig, ext = usgs_classify(code, agdb)
            a = agdb.get(code)
            if a is not None:
                desc = a.get("ANALYTIC_METHOD_DESC", "")
                ref = bibmap.get(a.get("ANALYTIC_METHOD_PUB_ID"), "") or str(a.get("ANALYTIC_METHOD_PUB_ID", ""))
            else:
                desc = "Code not in the AGDB4 method dictionary; classified from the USGS code grammar"
        else:
            tech, dig, ext = NOT_REPORTED
            desc = "GEOROC precompiled files do not carry per-value methods; see the cited publication"
        quant = "semi-quantitative" if ext == "semi-quantitative" else "quantitative" if ext != "unknown" else "unknown"
        rows.append(dict(method_id=f"{sid}:{code}", source_id=sid, method_code_source=code, technique=tech,
                         digestion=dig, extent=ext, quantitative=quant, n_determinations=r.n_determinations,
                         n_samples=r.n_samples, analytes=r.analytes, description=str(desc)[:600],
                         reference=ref))
    cw = pd.DataFrame(rows).sort_values(["source_id", "method_code_source"])
    cw.to_csv(os.path.join(OUT, "method_crosswalk.csv"), index=False)
    print(f"method_crosswalk.csv: {len(cw)} method codes")

    # ---- author corrections (docs/corrections.csv): documented, value_source keeps the original
    corr_path = os.path.join(ROOT, "docs", "corrections.csv")
    longdf["author_corrected"] = False
    if os.path.exists(corr_path):
        corr = pd.read_csv(corr_path)
        for c in corr.itertuples(index=False):
            m = (longdf.mcr_uid == c.mcr_uid) & (longdf.analyte == c.analyte) & (longdf.unit == c.unit) & \
                np.isclose(longdf.value.astype(float), float(c.original_value))
            if m.sum() == 0:
                raise SystemExit(f"correction not applied (no match): {c.mcr_uid} {c.analyte} {c.original_value}")
            longdf.loc[m, "value"] = float(c.corrected_value)
            longdf.loc[m, "harmonize_rule"] = longdf.loc[m, "harmonize_rule"] + \
                f"; AUTHOR CORRECTION {c.date}: {c.original_value} -> {c.corrected_value} {c.unit} ({c.decided_by})"
            longdf.loc[m, "author_corrected"] = True
            print(f"applied correction: {c.mcr_uid} {c.analyte} {c.original_value} -> {c.corrected_value} {c.unit} ({m.sum()} row)")

    # ---- best value: one per sample x analyte
    longdf["method_id"] = longdf["source_id"] + ":" + longdf["method_code_source"]
    longdf = longdf.merge(cw[["method_id", "technique", "digestion", "extent"]], on="method_id", how="left")
    ext_rank = {"total": 0, "near-total": 1, "unknown": 2, "partial": 3, "semi-quantitative": 4}
    longdf["_rank"] = (longdf["extent"].map(ext_rank).fillna(5) * 10 + longdf["value"].isna().astype(int) * 100
                       - (~longdf["is_best_value"]).astype(int) * 0)
    longdf["_src_best"] = longdf["is_best_value"].astype(bool)
    longdf = longdf.sort_values(["mcr_uid", "analyte", "_src_best", "_rank", "detection_limit"],
                                ascending=[True, True, False, True, True])
    first = ~longdf.duplicated(["mcr_uid", "analyte"])
    longdf["is_best_value"] = first
    longdf["best_value_basis"] = np.where(first & longdf["_src_best"], "source best value",
                                          np.where(first, "crosswalk rank", ""))

    # ---- derived Fe2O3T where only Fe2O3 + FeO exist
    b = longdf[longdf["is_best_value"]]
    piv = b.pivot_table(index="mcr_uid", columns="analyte", values="value", aggfunc="first")
    rows_needed = piv.index[piv.get("Fe2O3T", pd.Series(index=piv.index, dtype=float)).isna()
                     & piv.get("Fe2O3", pd.Series(index=piv.index, dtype=float)).notna()
                     & piv.get("FeO", pd.Series(index=piv.index, dtype=float)).notna()]
    der = pd.DataFrame(dict(mcr_uid=rows_needed, analyte="Fe2O3T",
                            value=(piv.loc[rows_needed, "Fe2O3"] + H.FEO_TO_FE2O3 * piv.loc[rows_needed, "FeO"]).values,
                            unit="wt%", censor="", detection_limit=np.nan, method_code_source="calculated",
                            is_best_value=True, derived=True, analyte_source="Fe2O3 + FeO",
                            unit_source="wt%", value_source="", harmonize_rule="Fe2O3T = Fe2O3 + 1.1113*FeO",
                            technique="Calculated", digestion="", extent="total",
                            best_value_basis="derived (no measured Fe2O3T)", author_corrected=False))
    der["source_id"] = der["mcr_uid"].str.split("-").str[1]
    der["method_id"] = der["source_id"] + ":calculated"
    longdf = pd.concat([longdf, der], ignore_index=True)
    print(f"derived Fe2O3T for {len(der)} samples")

    # ---- detection limits
    cen = longdf[longdf["censor"] == "<"]
    dl_obs = (cen.groupby(["source_id", "method_code_source", "analyte", "unit"])
              .agg(dl_min_observed=("detection_limit", "min"), dl_max_observed=("detection_limit", "max"),
                   n_distinct_dl=("detection_limit", "nunique"), n_censored=("mcr_uid", "size")).reset_index())
    tot = (longdf.groupby(["source_id", "method_code_source", "analyte", "unit"])
           .agg(n_determinations=("mcr_uid", "size"), n_above_upper=("censor", lambda s: (s == ">").sum()))
           .reset_index())
    dl = tot.merge(dl_obs, how="left", on=["source_id", "method_code_source", "analyte", "unit"])
    dl["n_censored"] = dl["n_censored"].fillna(0).astype(int)
    dl["pct_censored"] = (100 * dl["n_censored"] / dl["n_determinations"]).round(1)
    # documented limits: AGDB4 Parameter_Rank (USGS), Woodruff LLD table
    pr = pd.read_csv(os.path.join(RAW, "agdb4", "Parameter_Rank.txt"), sep=None, engine="python", encoding="latin1")
    pr["unit_src"] = pr["PARAMETER"].str.extract(r"^[A-Za-z0-9]+_(ppm|pct|ppb|ppt)_")[0]
    doc = {}
    for r in pr.itertuples(index=False):
        h = H.harmonize(r.SPECIES, r.unit_src or "", 1.0)
        if h:
            doc[("S1", r.ANALYTIC_METHOD, h[0])] = (f"{r.LLD_RANGE} {r.unit_src} ({r.SPECIES})" if isinstance(r.LLD_RANGE, str) else "",
                                                     str(r.BESTVALUE_RANK))
    wl = pd.read_csv(os.path.join(RAW, "usgs_woodruff2019", "Analytical_methods_LLD.csv"), encoding="utf-8-sig")
    for r in wl.iloc[:, :3].itertuples(index=False):
        el = str(r[0]).split(",")[-1].strip()
        h = H.harmonize(el, "ppm", 1.0)
        if h:
            doc[("S7", str(r[1]).strip(), h[0])] = (str(r[2]).strip() + f" ({el})", "")
    dl["documented_lld_source_units"] = [doc.get((a, b, c), ("", ""))[0] for a, b, c in
                                         zip(dl.source_id, dl.method_code_source, dl.analyte)]
    dl["usgs_bestvalue_rank"] = [doc.get((a, b, c), ("", ""))[1] for a, b, c in
                                 zip(dl.source_id, dl.method_code_source, dl.analyte)]
    dl = dl.merge(cw[["source_id", "method_code_source", "technique", "extent"]], how="left")
    dl.to_csv(os.path.join(OUT, "detection_limits.csv"), index=False)
    print(f"detection_limits.csv: {len(dl)} method x analyte rows")

    cols = ["mcr_uid", "source_id", "analyte", "value", "unit", "censor", "detection_limit", "is_best_value",
            "best_value_basis", "author_corrected", "method_id", "method_code_source", "technique", "digestion", "extent", "derived",
            "analyte_source", "unit_source", "value_source", "harmonize_rule"]
    longdf = longdf[cols].sort_values(["mcr_uid", "analyte", "is_best_value"], ascending=[True, True, False])
    longdf.to_parquet(os.path.join(OUT, "_stage_long2.parquet"), index=False)
    print(f"long table: {len(longdf):,} rows")


if __name__ == "__main__":
    main()
