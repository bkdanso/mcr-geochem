"""Core checks for whole-rock and mineral geochemistry tables.

Input schema (long table, one row per determination):
    mcr_uid, analyte, value, unit, censor ('', '<', '>'), detection_limit, is_best_value,
    extent (total / near-total / partial / semi-quantitative / unknown)
Samples table: mcr_uid, sample_type, rock_class, latitude, longitude, coord_quality,
    alteration_source, field_id, source_id
Any table in this schema can be checked, not only MCR-GeoChem.
"""
import json
import math

import numpy as np
import pandas as pd

from .rules import DEFAULT_RULES

MAJORS = ["SiO2", "TiO2", "Al2O3", "Fe2O3T", "MnO", "MgO", "CaO", "Na2O", "K2O", "P2O5"]
MW = {"SiO2": 60.08, "TiO2": 79.87, "Al2O3": 101.96, "Fe2O3T": 159.69, "MnO": 70.94, "MgO": 40.30,
      "CaO": 56.08, "Na2O": 61.98, "K2O": 94.20, "P2O5": 141.94}

FLAG_DOC = {
    "BDL": "Below detection limit: value unknown, less than the detection limit.",
    "BDL_UNINFORMATIVE": "Below detection, but the detection limit is so high the result says little about the rock.",
    "ABOVE_UPPER_LIMIT": "Above the method's upper limit: true value is higher than reported.",
    "SEMI_QUANTITATIVE": "Semi-quantitative method (e.g., DC-arc emission spectrography); use for screening only.",
    "PARTIAL_DIGESTION": "Partial digestion (e.g., aqua regia): may under-report elements in resistant minerals.",
    "METHOD_NOT_REPORTED": "The source file does not give the analytical method.",
    "IMPLAUSIBLE_VALUE": "Physically impossible after unit harmonization (negative, >100 wt%, >1,000,000 ppm).",
    "SOURCE_VALUE_SUSPECT": "Published value kept as reported but judged suspect by the dataset authors pending confirmation from the source (see docs/corrections.csv and author_note).",
    "AUTHOR_CORRECTED": "Value corrected by the dataset authors; the original is kept in value_source (see docs/corrections.csv).",
    "ZERO_VALUE": "Reported as exactly zero; in compilations this usually means 'not detected' with no limit given.",
    "POSSIBLE_UNIT_ERROR": "Far above what unmineralized rock contains; check units (ppm vs ppb, element vs oxide).",
    "MAJOR_TOTAL_LOW": "Sum of major oxides + LOI below the accepted range.",
    "MAJOR_TOTAL_HIGH": "Sum of major oxides + LOI above the accepted range.",
    "SI_ELEMENT_SUSPECT": "SiO2 in an igneous rock is in the range expected if Si (element) was reported as SiO2.",
    "ALTERED_LOI": "Loss on ignition above threshold: likely hydrated or carbonated.",
    "ALTERED_CIA": "Chemical Index of Alteration above threshold: feldspar likely weathered to clay.",
    "ALTERED_AI": "Ishikawa alteration index outside the least-altered range.",
    "ALTERED_SOURCE": "The source describes the sample as altered.",
    "COORD_MISSING": "No coordinates.",
    "COORD_APPROXIMATE": "Coordinates are approximate (one decimal place, or a locality range centroid).",
    "COORD_STATE_MISMATCH": "State given in the source differs from the state at the coordinates.",
    "POSSIBLE_DUPLICATE": "Same place and near-identical SiO2 and MgO (or same name) as a sample in another source.",
}


def load_rules(path=None):
    r = json.loads(json.dumps(DEFAULT_RULES))
    if path:
        with open(path, encoding="utf-8") as f:
            r.update(json.load(f))
    return r


def _join(flags):
    return ";".join(sorted(set(f for f in flags if f)))


def flag_analyses(long, samples=None, rules=None):
    """Return a copy of the long table with a 'qa_flags' column (semicolon-separated)."""
    rules = rules or load_rules()
    d = long.copy()
    flags = [[] for _ in range(len(d))]
    cen = d["censor"].fillna("").astype(str).values
    val = pd.to_numeric(d["value"], errors="coerce").values
    dl = pd.to_numeric(d["detection_limit"], errors="coerce").values
    an = d["analyte"].astype(str).values
    unit = d["unit"].astype(str).values
    ext = d["extent"].fillna("unknown").astype(str).values if "extent" in d else np.array(["unknown"] * len(d))
    unin = rules["uninformative_dl"]
    ceil = rules["ceiling_wholerock"]
    stype = rtype = sulf = None
    if samples is not None:
        sm = samples.set_index("mcr_uid")
        stype = d["mcr_uid"].map(sm["sample_type"]).fillna("").values
        best = d[d.get("is_best_value", True) == True]  # noqa: E712
        s_wt = best[best["analyte"] == "S"].set_index("mcr_uid")["value"]
        sulf = d["mcr_uid"].map(s_wt).astype(float).values
    for i in range(len(d)):
        f = flags[i]
        if cen[i] == "<":
            f.append("BDL")
            if an[i] in unin and not math.isnan(dl[i]) and dl[i] > unin[an[i]]:
                f.append("BDL_UNINFORMATIVE")
        elif cen[i] == ">":
            f.append("ABOVE_UPPER_LIMIT")
        if ext[i] == "semi-quantitative":
            f.append("SEMI_QUANTITATIVE")
        elif ext[i] == "partial":
            f.append("PARTIAL_DIGESTION")
        elif ext[i] == "unknown":
            f.append("METHOD_NOT_REPORTED")
        v = val[i]
        if not math.isnan(v):
            if v == 0:
                f.append("ZERO_VALUE")
            if an[i] == "LOI" and -5 <= v < 0:
                pass  # negative LOI is real (oxidation of FeO during ignition)
            elif v < 0 or (unit[i] == "wt%" and v > 100.5) or (unit[i] == "ppm" and v > 1e6) or (unit[i] == "ppb" and v > 1e9):
                f.append("IMPLAUSIBLE_VALUE")
            elif an[i] in ceil and v > ceil[an[i]]:
                mineralized = sulf is not None and not math.isnan(sulf[i]) and sulf[i] >= rules["mineralized_S_wt"]
                whole = stype is None or stype[i] in ("whole_rock", "")
                if whole and not mineralized:
                    f.append("POSSIBLE_UNIT_ERROR")
    d["qa_flags"] = [_join(f) for f in flags]
    return d


def _best_wide(long):
    b = long[(long["is_best_value"] == True) & long["value"].notna()]  # noqa: E712
    return b.pivot_table(index="mcr_uid", columns="analyte", values="value", aggfunc="first")


def alteration_indices(w):
    """CIA (Nesbitt & Young 1982) and Ishikawa AI (Ishikawa et al. 1976) from a wide table of oxide wt%."""
    g = lambda c: w[c] if c in w else pd.Series(np.nan, index=w.index)  # noqa: E731
    al, ca, na, k, p, mg = (g("Al2O3") / MW["Al2O3"], g("CaO") / MW["CaO"], g("Na2O") / MW["Na2O"],
                            g("K2O") / MW["K2O"], g("P2O5").fillna(0) / MW["P2O5"], g("MgO"))
    co2 = g("CO2").fillna(0) / 44.01
    # CaO in silicates: remove apatite (10/3 P2O5) and calcite (CO2) when reported. For igneous rocks
    # (the only class flagged) this is the usual convention; the McLennan (1993) cap is for sediments.
    ca_star = (ca - (10.0 / 3.0) * p - co2).clip(lower=0)
    cia = 100 * al / (al + ca_star + na + k)
    ai = 100 * (g("MgO") + g("K2O")) / (g("MgO") + g("K2O") + g("Na2O") + g("CaO"))
    return cia, ai


def flag_samples(samples, long, rules=None):
    """Return a copy of samples with QA columns and a 'qa_flags' column."""
    rules = rules or load_rules()
    s = samples.copy().set_index("mcr_uid")
    w = _best_wide(long).reindex(s.index)
    present = w.reindex(columns=MAJORS).notna().sum(axis=1)
    key = ["SiO2", "Al2O3", "Fe2O3T", "MgO", "CaO", "Na2O", "K2O"]
    has_key = w.reindex(columns=key).notna().all(axis=1)
    vol = w["LOI"] if "LOI" in w else pd.Series(np.nan, index=w.index)
    if "H2O" in w or "CO2" in w:
        alt = w.get("H2O", pd.Series(np.nan, index=w.index)).fillna(0) + w.get("CO2", pd.Series(np.nan, index=w.index)).fillna(0)
        vol = vol.fillna(alt.where(alt > 0))
    total = w.reindex(columns=MAJORS).sum(axis=1, min_count=8) + vol.fillna(0)
    total = total.where((present >= 8) & has_key)  # SiO2 etc. must be measured (HF digestions lose Si)
    cia, ai = alteration_indices(w)
    s["major_oxide_total"] = total.round(2)
    s["n_major_oxides"] = present
    s["loi_wt"] = vol.round(2)
    s["cia"] = cia.round(1)
    s["ai_ishikawa"] = ai.round(1)
    igneous = s["rock_class"].fillna("").str.startswith("igneous") & (s["sample_type"] == "whole_rock")
    whole = s["sample_type"] == "whole_rock"
    sulfur = w["S"] if "S" in w else pd.Series(np.nan, index=w.index)
    out_flags, crit = [], []
    aw, fw = rules["alteration_words"], rules["fresh_words"]
    lo, hi = rules["ai_range"]
    for uid in s.index:
        f, c = [], []
        r = s.loc[uid]
        t = total.get(uid)
        if whole.get(uid) and t == t and t is not None:
            mineral_s = sulfur.get(uid)
            if t < rules["total_min"] and not (mineral_s == mineral_s and mineral_s is not None and mineral_s >= rules["mineralized_S_wt"]):
                f.append("MAJOR_TOTAL_LOW")
            if t > rules["total_max"]:
                f.append("MAJOR_TOTAL_HIGH")
        si = w["SiO2"].get(uid) if "SiO2" in w else np.nan
        a, b = rules["si_element_suspect"]
        if igneous.get(uid) and si == si and si is not None and a <= si <= b and not (sulfur.get(uid, np.nan) >= 5):
            f.append("SI_ELEMENT_SUSPECT")
        if igneous.get(uid):
            if vol.get(uid) == vol.get(uid) and vol.get(uid) is not None and vol.get(uid) > rules["loi_max"]:
                f.append("ALTERED_LOI"); c.append(f"LOI {vol.get(uid):.1f}")
            if cia.get(uid) == cia.get(uid) and cia.get(uid) is not None and cia.get(uid) > rules["cia_max"]:
                f.append("ALTERED_CIA"); c.append(f"CIA {cia.get(uid):.0f}")
            if ai.get(uid) == ai.get(uid) and ai.get(uid) is not None and not (lo <= ai.get(uid) <= hi):
                f.append("ALTERED_AI"); c.append(f"AI {ai.get(uid):.0f}")
        alt_txt = str(r.get("alteration_source") or "").lower()
        if alt_txt and any(x in alt_txt for x in aw) and not any(x in alt_txt for x in fw[:3]):
            f.append("ALTERED_SOURCE"); c.append("source: " + alt_txt[:40])
        cq = str(r.get("coord_quality") or "")
        if cq == "missing":
            f.append("COORD_MISSING")
        elif cq in ("approximate", "range_centroid"):
            f.append("COORD_APPROXIMATE")
        elif cq == "state_mismatch":
            f.append("COORD_STATE_MISMATCH")
        out_flags.append(f)
        crit.append("; ".join(c))
    s["altered_criteria"] = crit
    s["altered_likely"] = [any(x.startswith("ALTERED") for x in f) for f in out_flags]
    # duplicates across sources
    grp = find_duplicates(s.reset_index(), w, rules)
    s["duplicate_group"] = s.index.map(grp).fillna("")
    for i, uid in enumerate(s.index):
        if s.at[uid, "duplicate_group"]:
            out_flags[i].append("POSSIBLE_DUPLICATE")
    s["qa_flags"] = [_join(f) for f in out_flags]
    return s.reset_index()


def find_duplicates(s, w, rules):
    """Group samples from different sources that are probably the same physical sample."""
    tol, rel = rules["dup_distance_deg"], rules["dup_rel_tol"]
    d = s[["mcr_uid", "source_id", "latitude", "longitude", "field_id"]].copy()
    d["lab"] = (s["lab_id"] if "lab_id" in s else pd.Series("", index=s.index)).fillna("").astype(str).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    d["lat"] = pd.to_numeric(d["latitude"], errors="coerce")
    d["lon"] = pd.to_numeric(d["longitude"], errors="coerce")
    d["si"] = d["mcr_uid"].map(w["SiO2"]) if "SiO2" in w else np.nan
    d["mg"] = d["mcr_uid"].map(w["MgO"]) if "MgO" in w else np.nan
    d["name"] = d["field_id"].fillna("").astype(str).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    d = d.dropna(subset=["lat", "lon"])
    d["cell"] = list(zip((d.lat / tol).round().astype(int), (d.lon / tol).round().astype(int)))
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    by_cell = {}
    for r in d.itertuples(index=False):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                by_cell.setdefault((r.cell[0] + dx, r.cell[1] + dy), []).append(r)
    seen = set()
    for r in d.itertuples(index=False):
        for o in by_cell.get(r.cell, []):
            if o.mcr_uid == r.mcr_uid or o.source_id == r.source_id or (o.mcr_uid, r.mcr_uid) in seen:
                continue
            seen.add((r.mcr_uid, o.mcr_uid))
            if abs(o.lat - r.lat) > tol or abs(o.lon - r.lon) > tol:
                continue
            same_name = (r.name and len(r.name) >= 3 and r.name == o.name) or (r.lab and len(r.lab) >= 4 and r.lab == o.lab)
            chem = all(x == x for x in (r.si, o.si, r.mg, o.mg)) and \
                abs(r.si - o.si) <= rel * max(r.si, o.si) and abs(r.mg - o.mg) <= max(rel * max(r.mg, o.mg), 0.05)
            if same_name or chem:
                union(r.mcr_uid, o.mcr_uid)
    groups = {}
    for u in list(parent):
        groups.setdefault(find(u), []).append(u)
    out = {}
    for k, (root, members) in enumerate(sorted(groups.items())):
        allm = sorted(set(members + [root]))
        if len(allm) > 1:
            for m in allm:
                out[m] = f"DUP{k + 1:04d}"
    return out
