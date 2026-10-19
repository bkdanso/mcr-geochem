#!/usr/bin/env python3
"""02_build.py - read every raw source, harmonize it, keep Midcontinent Rift samples, write the tables.

Plain-language note: this is the main script. It turns six differently formatted sources into
one set of tables with the same column names, units, and "below detection" convention, and
keeps only samples from Midcontinent Rift rocks in Michigan, Minnesota, and Wisconsin. It
writes data/processed/ and a list of every excluded sample with the reason. Run it with
`python code/02_build.py`. You do not need to open it.
"""
import json
import math
import os
import re
import sys
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harmonize as H  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")
VERSION = "1.0.0"
STUDY_STATES = {"MI": "26", "MN": "27", "WI": "55"}

SOURCES = {
    "S1": dict(name="USGS National Geochemical Database (NGDB), 1962-2023 release", doi="10.5066/P1FXE9GK",
               license="Public domain (USGS)"),
    "S2": dict(name="USGS Duluth Complex drill core and hand samples (Parks et al., 2025)", doi="10.5066/P13UFQYF",
               license="Public domain (USGS)"),
    "S3": dict(name="USGS Earth MRI geochemistry v12.0", doi="10.5066/P9WHRLXH", license="Public domain (USGS)"),
    "S4": dict(name="GEOROC Continental Flood Basalts: Midcontinent Rift System-Keweenawan", doi="10.25625/WSTPOX",
               license="CC BY-SA 4.0"),
    "S5": dict(name="GEOROC Minerals (region-filtered)", doi="10.25625/SGFTFN", license="CC BY-SA 4.0"),
    "S6": dict(name="EarthChem Library 1501: Portage Lake Volcanics (Davis et al., 2022)", doi="10.26022/IEDA/111501",
               license="CC BY-SA 4.0"),
    "S7": dict(name="USGS Duluth Complex basal contact watersheds, bedrock (Woodruff, 2019)", doi="10.5066/P9VO251H",
               license="Public domain (USGS)"),
}

SAMPLE_COLS = ["mcr_uid", "source_id", "source_sample_id", "lab_id", "field_id", "igsn", "latitude", "longitude",
               "coord_quality", "state", "sample_type", "mineral", "rock_class", "rock_name", "stratigraphy",
               "geologic_age_source", "sample_source", "collection_method", "drill_hole", "depth_from_m",
               "depth_to_m", "depth_source", "collection_year", "project", "deposit_or_locality", "alteration_source",
               "reference", "source_doi", "license", "sgmc_label", "sgmc_unit_name", "mcr_class", "mcr_match",
               "mcr_reason"]
LONG_COLS = ["mcr_uid", "analyte", "value", "unit", "censor", "detection_limit", "method_code_source",
             "is_best_value", "derived", "analyte_source", "unit_source", "value_source", "harmonize_rule"]


def clean(x):
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    s = str(x).strip()
    return "" if s.upper() in {"ND", "NAN", "NONE", "NULL"} else s


def join_text(*xs):
    return " | ".join(clean(x) for x in xs if clean(x))


class Collector:
    """Accumulates sample rows and analysis rows for one source."""

    def __init__(self, source_id):
        self.sid = source_id
        self.samples, self.rows = [], []

    def sample(self, **kw):
        kw.setdefault("source_id", self.sid)
        kw.setdefault("source_doi", SOURCES[self.sid]["doi"])
        kw.setdefault("license", SOURCES[self.sid]["license"])
        self.samples.append(kw)

    def analysis(self, uid, analyte_src, unit_src, value, censor, limit, method, best, value_src=None):
        h_val = value if value is not None else (limit if limit is not None else 1.0)
        h = H.harmonize(analyte_src, unit_src, h_val)
        if h is None:
            return
        a, u, v, rule = h
        out_v = v if value is not None else None
        out_dl = (v if limit is not None and value is None else None)
        if censor == "<" and limit is None:
            out_dl = None
        self.rows.append(dict(mcr_uid=uid, analyte=a, value=out_v, unit=u, censor=censor,
                              detection_limit=out_dl, method_code_source=method or "not reported",
                              is_best_value=bool(best), derived=False, analyte_source=analyte_src,
                              unit_source=unit_src, value_source=value_src if value_src is not None else
                              (value if value is not None else f"{censor}{limit}" if limit is not None else censor),
                              harmonize_rule=rule))


def uid(sid, raw):
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", str(raw)).strip("_")
    return f"MCRG-{sid}-{s}"


# ------------------------------------------------------------------ S1 NGDB
NGDB_EL = re.compile(r"^([A-Za-z0-9]+)_(ppm|pct|ppb)$")


def load_ngdb():
    c = Collector("S1")
    for layer, stype in [("rock", "whole_rock"), ("mineral", "mineral_separate"),
                         ("geologic_material", "whole_rock")]:
        p = os.path.join(RAW, "ngdb", f"ngdb_{layer}_MI_MN_WI.json")
        feats = json.load(open(p, encoding="utf-8"))["features"]
        if not feats:
            continue
        df = pd.DataFrame([f["attributes"] for f in feats])
        elcols = [col for col in df.columns if NGDB_EL.match(col)]
        for _, r in df.iterrows():
            u = uid("S1", r["lab_id"])
            sec = clean(r.get("secondary_class")).lower()
            form = clean(r.get("igneous_form")).lower()
            rc = {"sedimentary": "sedimentary", "metamorphic": "metamorphic"}.get(sec, "")
            if sec == "igneous":
                rc = ("igneous_volcanic" if any(k in form for k in ("volcan", "extrusive", "flow", "lava"))
                      else "igneous_intrusive" if any(k in form for k in ("intrus", "plut", "dike", "sill", "plug"))
                      else "igneous")
            c.sample(mcr_uid=u, source_sample_id=r["lab_id"], lab_id=r["lab_id"], field_id=clean(r.get("field_id")),
                     latitude=r.get("latitude"), longitude=r.get("longitude"), state=clean(r.get("state")),
                     sample_type=stype, mineral=clean(r.get("specific_name")) if stype != "whole_rock" else "",
                     rock_class=rc or "unspecified", rock_name=clean(r.get("specific_name")),
                     stratigraphy=clean(r.get("stratigraphy")), geologic_age_source=clean(r.get("geologic_age")),
                     sample_source=clean(r.get("sample_source")), collection_method=clean(r.get("method_collected")),
                     depth_text=clean(r.get("depth")), collection_year=clean(r.get("date_collect"))[:4],
                     project=clean(r.get("project_name")),
                     deposit_or_locality=join_text(r.get("deposit_name"), r.get("mine_name"), r.get("district_name"),
                                                   r.get("locate_desc")),
                     alteration_source=clean(r.get("alteration")),
                     reference=join_text(r.get("submitter"), "job " + clean(r.get("job_id"))),
                     _primary=join_text(r.get("stratigraphy"), r.get("addl_attr"), r.get("igneous_form")),
                     _secondary=join_text(r.get("deposit_name"), r.get("district_name"), r.get("mine_name"),
                                          r.get("project_name"), r.get("locate_desc"), r.get("sample_comment")))
            for col in elcols:
                el, unit = NGDB_EL.match(col).groups()
                best_v, method = r.get(col), clean(r.get(f"{el}_AM"))
                allv = clean(r.get(f"{col}_ALL"))
                if allv:
                    best_done = False
                    for part in allv.split(";"):
                        bits = [b.strip() for b in part.split(",")]
                        if len(bits) < 2:
                            continue
                        try:
                            raw = float(bits[0])
                        except ValueError:
                            continue
                        m = bits[-1]
                        v, cen, lim = H.parse_usgs_qualified(raw)
                        is_best = (not best_done) and m == method and best_v is not None and abs(raw - float(best_v)) < 1e-9
                        best_done = best_done or is_best
                        c.analysis(u, el, unit, v, cen, lim, m, is_best, value_src=raw)
                elif best_v is not None and not (isinstance(best_v, float) and math.isnan(best_v)):
                    v, cen, lim = H.parse_usgs_qualified(best_v)
                    c.analysis(u, el, unit, v, cen, lim, method, True, value_src=best_v)
    return c


# ------------------------------------------------------------------ S2 USGS Duluth
DUL_EL = re.compile(r"^([A-Za-z0-9_]+?)_(ppm|pct|ppb)$")
DUL_MAP = {"CRBNT_C": "C_carb", "Organic_C": "C_org", "H2O_Minus": "H2O-", "H2O_Plus": "H2O+", "Total_H2O": "H2O"}


def load_usgs_duluth():
    c = Collector("S2")
    df = pd.read_csv(os.path.join(RAW, "usgs_duluth", "MCR_USGS_geochem_BV.csv"), low_memory=False)
    elcols = [col for col in df.columns if DUL_EL.match(col) and f"{col}_all" in df.columns]
    for i, r in df.iterrows():
        sid = clean(r["Field_ID"]) or f"row{i}"
        u = uid("S2", sid)
        strat = join_text(r.get("Strat_00"), r.get("Strat_01"), r.get("Strat_02"), r.get("Strat_03"), r.get("Strat_04"))
        ft = lambda x: round(float(x) * 0.3048, 3) if clean(x) else None  # noqa: E731
        c.sample(mcr_uid=u, source_sample_id=sid, lab_id=clean(r.get("Lab_ID")), field_id=sid,
                 latitude=r.get("Latitude_NAD83"), longitude=r.get("Longitude_NAD83"), state="MN",
                 sample_type="whole_rock", rock_class="", rock_name=clean(r.get("Rock_type")), stratigraphy=strat,
                 geologic_age_source=clean(r.get("Geologic_age")), sample_source=clean(r.get("Sample_source")),
                 collection_method=clean(r.get("Method_collected")), drill_hole=clean(r.get("Drill_hole_ID")),
                 depth_from_m=ft(r.get("From_ft")), depth_to_m=ft(r.get("To_ft")),
                 depth_text=f"{clean(r.get('From_ft'))}-{clean(r.get('To_ft'))} ft" if clean(r.get("From_ft")) else "",
                 collection_year=clean(r.get("Year_collected")), project="USGS Midcontinent Rift (Duluth Complex)",
                 deposit_or_locality=clean(r.get("Deposit_area")),
                 alteration_source="", reference="Parks et al. (2025), doi:10.5066/P13UFQYF; job " + clean(r.get("Job_ID")),
                 _primary=strat, _secondary=join_text(r.get("Deposit_area"), r.get("Sample_description")))
        for col in elcols:
            el, unit = DUL_EL.match(col).groups()
            el = DUL_MAP.get(el, el)
            allv = clean(r.get(f"{col}_all"))
            best_m = clean(r.get(f"{col}_method"))
            best_txt = clean(r.get(col))
            done = False
            for part in allv.split(";"):
                if not part.strip():
                    continue
                txt, _, m = part.rpartition(",")
                v, cen, lim = H.parse_text_value(txt.strip())
                if v is None and not cen:
                    continue
                is_best = (not done) and m.strip() == best_m and txt.strip() == best_txt
                done = done or is_best
                c.analysis(u, el, unit, v, cen, lim, m.strip(), is_best, value_src=txt.strip())
    return c


# ------------------------------------------------------------------ S3 Earth MRI
def load_emri():
    c = Collector("S3")
    df = pd.read_csv(os.path.join(RAW, "emri", "EMRI_Data.csv"), low_memory=False, encoding="latin1")
    df = df[df["State"].isin(STUDY_STATES)]
    df = df[df["QAQC_Sample"].fillna("") != "Duplicate"]  # field duplicates kept out; originals kept
    dd = pd.read_csv(os.path.join(RAW, "emri", "EMRI_DataDictionary.csv"), encoding="latin1")
    # map column suffix -> method code using the data dictionary text where possible
    colpat = re.compile(r"^([A-Z][a-z]?\d*[A-Za-z0-9]*?)_(pct|ppm|ppb)_([A-Za-z0-9]+)$")
    descr = {}
    for _, d in dd.iterrows():
        vals = [clean(v) for v in d.values]
        if vals and colpat.match(vals[0] or ""):
            descr[vals[0]] = " ".join(vals[1:])
    elcols = [col for col in df.columns if colpat.match(col)]
    for _, r in df.iterrows():
        u = uid("S3", r["Lab_ID"])
        rt = clean(r.get("Rock_Type")).lower()
        form = clean(r.get("Igneous_Form")).lower()
        rc = {"sedimentary": "sedimentary", "metamorphic": "metamorphic", "ore": "vein_or_ore"}.get(rt, "")
        if rt == "igneous":
            rc = "igneous_volcanic" if "volcan" in form or "extrus" in form else (
                "igneous_intrusive" if form else "igneous")
        c.sample(mcr_uid=u, source_sample_id=r["Lab_ID"], lab_id=r["Lab_ID"], field_id=clean(r.get("Field_ID")),
                 igsn=clean(r.get("IGSN")), latitude=r.get("Lat_WGS84"), longitude=r.get("Long_WGS84"),
                 state=clean(r.get("State")), sample_type="whole_rock", rock_class=rc or "unspecified",
                 rock_name=clean(r.get("Rock_Name")), stratigraphy=clean(r.get("Stratigraphy")),
                 geologic_age_source=clean(r.get("Geologic_Age")), sample_source=clean(r.get("Sample_Source")),
                 collection_method=clean(r.get("Method_Collected")), depth_text=clean(r.get("Sample_Depth")),
                 collection_year=clean(r.get("Date_Collected"))[-4:], project=clean(r.get("Proj_Name")),
                 deposit_or_locality=clean(r.get("Location_Desc")), alteration_source=clean(r.get("Alteration")),
                 reference="USGS Earth MRI geochemistry v12, job " + clean(r.get("Job_ID")),
                 _primary=join_text(r.get("Stratigraphy"), r.get("Sample_Desc")),
                 _secondary=join_text(r.get("Proj_Name"), r.get("Location_Desc"), r.get("Mineralization")))
        for col in elcols:
            v0 = r.get(col)
            if v0 is None or (isinstance(v0, float) and math.isnan(v0)):
                continue
            el, unit, mtag = colpat.match(col).groups()
            v, cen, lim = H.parse_usgs_qualified(v0) if isinstance(v0, (int, float)) else H.parse_text_value(v0)
            c.analysis(u, el, unit, v, cen, lim, mtag, False, value_src=v0)
    _mark_best_by_order(c)
    return c


def _mark_best_by_order(c):
    """For sources with several methods per element and no best-value field: first determination wins.
    (Refined later by the crosswalk rank in 03_crosswalk.py.)"""
    seen = set()
    for row in c.rows:
        k = (row["mcr_uid"], row["analyte"])
        if k not in seen and row["value"] is not None:
            row["is_best_value"] = True
            seen.add(k)
    for row in c.rows:
        k = (row["mcr_uid"], row["analyte"])
        if k not in seen:
            row["is_best_value"] = True
            seen.add(k)


# ------------------------------------------------------------------ S4 / S5 GEOROC
GEOROC_COL = re.compile(r"^([A-Z0-9_]+)\((WT%|PPM|PPB|PPT)\)$")


def georoc_refs(df):
    """Reference rows at the end of GEOROC files: '[1234] AUTHOR: TITLE'."""
    refs = {}
    for t in df.iloc[:, 0].dropna().astype(str):
        m = re.match(r"^\s*\[(\d+)\]\s*(.+)$", t)
        if m:
            refs[m.group(1)] = re.sub(r"\s+", " ", m.group(2)).strip()
    return refs


def _georoc_coords(r, latmin, latmax, lonmin, lonmax):
    la = pd.to_numeric(pd.Series([r.get(latmin), r.get(latmax)]), errors="coerce")
    lo = pd.to_numeric(pd.Series([r.get(lonmin), r.get(lonmax)]), errors="coerce")
    lat, lon = la.mean(), lo.mean()
    span = max((la.max() - la.min()) if la.notna().all() else 0, (lo.max() - lo.min()) if lo.notna().all() else 0)
    dec = min(len(str(r.get(latmin)).split(".")[-1]) if "." in str(r.get(latmin)) else 0,
              len(str(r.get(lonmin)).split(".")[-1]) if "." in str(r.get(lonmin)) else 0)
    q = "range_centroid" if span > 0.01 else ("approximate" if dec <= 1 else "reported")
    return lat, lon, q


def load_georoc_cfb():
    c = Collector("S4")
    p = os.path.join(RAW, "georoc", "2026-09-WSTPOX_MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN.csv")
    df = pd.read_csv(p, encoding="latin1", low_memory=False, dtype=str)
    refs = georoc_refs(df)
    df = df[df["TECTONIC SETTING"].notna()]
    elcols = [col for col in df.columns if GEOROC_COL.match(col)]
    for _, r in df.iterrows():
        u = uid("S4", r["UNIQUE_ID"])
        lat, lon, q = _georoc_coords(r, "LATITUDE MIN", "LATITUDE MAX", "LONGITUDE MIN", "LONGITUDE MAX")
        rt = clean(r.get("ROCK TYPE"))
        rc = {"VOL": "igneous_volcanic", "PLU": "igneous_intrusive", "SED": "sedimentary", "MET": "metamorphic",
              "VEIN": "vein_or_ore", "ORE": "vein_or_ore"}.get(rt, "unspecified")
        cites = re.findall(r"\[(\d+)\]", clean(r.get("CITATIONS")) + " " + clean(r.get("MATERIAL")))
        ref = "; ".join(dict.fromkeys(refs.get(k, f"GEOROC ref {k}") for k in cites))
        loc = clean(r.get("LOCATION"))
        c.sample(mcr_uid=u, source_sample_id=r["UNIQUE_ID"],
                 field_id=re.sub(r"^s_|\s*\[\d+\]$", "", clean(r.get("SAMPLE NAME"))),
                 latitude=lat, longitude=lon, coord_quality=q, state="", sample_type="whole_rock",
                 rock_class=rc, rock_name=re.sub(r"\s*\[\d+\]$", "", clean(r.get("ROCK NAME"))),
                 stratigraphy=loc.replace("MIDCONTINENT RIFT SYSTEM-KEWEENAWAN / ", ""),
                 geologic_age_source=clean(r.get("GEOL.")) or clean(r.get("AGE")),
                 sample_source="drill core" if clean(r.get("DRILL DEPTH MIN")) else "",
                 deposit_or_locality=clean(r.get("LOCATION COMMENT")),
                 alteration_source={"F": "fresh", "S": "slightly altered", "M": "moderately altered",
                                    "E": "extensively altered"}.get(clean(r.get("ALTERATION")), clean(r.get("ALTERATION"))),
                 reference=ref, _primary=loc, _secondary=clean(r.get("LOCATION COMMENT")))
        has = {GEOROC_COL.match(col).group(1) for col in elcols if clean(r.get(col))}
        for col in elcols:
            t = clean(r.get(col))
            if not t:
                continue
            el, unit = GEOROC_COL.match(col).groups()
            v, cen, lim = H.parse_text_value(t)
            if v is None and not cen:
                continue
            # Fe2O3 alone (no FeO, no FeOT) is reported total iron in practice -> label Fe2O3T, flagged in rule
            if el == "FE2O3" and "FEO" not in has and "FEOT" not in has:
                el = "FE2O3T"
            c.analysis(u, el, unit.lower(), v, cen, lim, "not reported (GEOROC precompiled file)", True, value_src=t)
    return c


def load_georoc_minerals():
    c = Collector("S5")
    p = os.path.join(RAW, "georoc", "georoc_minerals_mcr_region.csv")
    if not os.path.exists(p):
        print("  (GEOROC mineral file not present; skipped)")
        return c
    df = pd.read_csv(p, low_memory=False, dtype=str)
    df = df[df["TECTONIC SETTING"].notna() | df["LOCATION"].notna()]
    elcols = [col for col in df.columns if GEOROC_COL.match(col)]
    idcol = "UNIQUE_ID" if "UNIQUE_ID" in df.columns else None
    for i, r in df.iterrows():
        mfile = re.sub(r"^\d{4}-\d{2}-SGFTFN_|\.csv$", "", clean(r.get("GEOROC_FILE")))
        rid = clean(r.get(idcol)) if idcol else ""
        rid = rid or f"{mfile}-{i}"
        spot = clean(r.get("SPOT")) or clean(r.get("CRYSTAL"))
        u = uid("S5", rid)
        lat, lon, q = _georoc_coords(r, "LATITUDE (MIN.)", "LATITUDE (MAX.)", "LONGITUDE (MIN.)", "LONGITUDE (MAX.)")
        loc = clean(r.get("LOCATION"))
        cites = re.findall(r"\[(\d+)\]", clean(r.get("CITATION")))
        mineral = clean(r.get("MINERAL"))
        c.sample(mcr_uid=u, source_sample_id=f"{clean(r.get('GEOROC_FILE'))} row {i + 2} of region file",
                 field_id=re.sub(r"\s*\[\d+\]$", "", clean(r.get("SAMPLE NAME"))) + (f" spot {spot}" if spot else ""),
                 latitude=lat, longitude=lon, coord_quality=q, state="", sample_type="mineral_grain",
                 mineral=mineral, rock_class="", rock_name=re.sub(r"\s*\[\d+\]$", "", clean(r.get("ROCK NAME"))),
                 stratigraphy=loc, geologic_age_source="", deposit_or_locality=clean(r.get("LOCATION COMMENT")),
                 alteration_source=clean(r.get("ALTERATION")),
                 reference=clean(r.get("CITATION")) or ("GEOROC refs " + ",".join(cites)),
                 project=clean(r.get("GEOROC_FILE")), _primary=loc, _secondary=clean(r.get("LOCATION COMMENT")),
                 _extra=join_text(clean(r.get("RIM/CORE (MINERAL GRAINS)")), clean(r.get("PRIMARY/SECONDARY"))))
        for col in elcols:
            t = clean(r.get(col))
            if not t:
                continue
            el, unit = GEOROC_COL.match(col).groups()
            v, cen, lim = H.parse_text_value(t)
            if v is None and not cen:
                continue
            c.analysis(u, el, unit.lower(), v, cen, lim, "not reported (GEOROC precompiled file)", True, value_src=t)
    return c


# ------------------------------------------------------------------ S6 EarthChem
def load_earthchem():
    c = Collector("S6")
    p = os.path.join(RAW, "earthchem", "1501-1_ECL_Davis_et_al_Portage_Lake_volcanics.xlsx")
    smp = pd.read_excel(p, "2 Samples", header=None)
    hdr = [clean(x) for x in smp.iloc[4]]
    smp = smp.iloc[7:].copy()
    smp.columns = [h or f"c{i}" for i, h in enumerate(hdr)]
    smp = smp[smp["SAMPLE NAME"].notna()]
    dat = pd.read_excel(p, "3 Data", header=None)
    params = [clean(x) for x in dat.iloc[1]]
    mcodes = [clean(x) for x in dat.iloc[2]]
    units = [clean(x) for x in dat.iloc[3]]
    meta = pd.read_excel(p, "4 Primary Analytical Metadata", header=None).iloc[6:, [0, 1, 3, 5]]
    meta.columns = ["code", "param", "technique", "lab"]
    tech = {(clean(a), clean(b)): clean(t) for a, b, t in zip(meta.code, meta.param, meta.technique)}
    dl_sheet = pd.read_excel(p, "5 Method-specific Metadata", header=None).iloc[6:, [0, 1, 3, 4]]
    dl_sheet.columns = ["code", "param", "dl", "unit"]
    dls = {(clean(a), clean(b)): (pd.to_numeric(d, errors="coerce"), clean(un)) for a, b, d, un in
           zip(dl_sheet.code, dl_sheet.param, dl_sheet.dl, dl_sheet.unit)}
    rows = dat.iloc[6:]
    rows = rows[rows[0].notna()]
    info = smp.set_index("SAMPLE NAME")
    for _, r in rows.iterrows():
        name = clean(r[0])
        s = info.loc[r[0]] if r[0] in info.index else pd.Series(dtype=object)
        u = uid("S6", name)
        c.sample(mcr_uid=u, source_sample_id=name, field_id=name, igsn=clean(r[1]),
                 latitude=pd.to_numeric(s.get("LATITUDE"), errors="coerce"),
                 longitude=pd.to_numeric(s.get("LONGITUDE"), errors="coerce"), state="",
                 sample_type="whole_rock", rock_class="igneous_volcanic", rock_name=clean(s.get("LITHOLOGY")),
                 stratigraphy="Portage Lake Volcanics", geologic_age_source=clean(s.get("age")),
                 deposit_or_locality=clean(s.get("LOCATION KEYWORDS")),
                 reference="Davis, Collins & Rooney (2022), doi:10.26022/IEDA/111501",
                 _primary="Portage Lake Volcanics", _secondary=clean(s.get("LOCATION KEYWORDS")))
        for j in range(8, len(params)):
            if not params[j]:
                continue
            v, cen, lim = H.parse_text_value(r[j])
            if v is None and not cen:
                continue
            code = mcodes[j].split(".")[0] if mcodes[j] else ""
            method = f"ECL1501-{code}:{tech.get((code, params[j]), '')}"
            if cen == "<" and lim is None:
                d = dls.get((code, params[j]))
                lim = d[0] if d and d[0] == d[0] else None
            c.analysis(u, params[j], units[j] or "ppm", v, cen, lim, method, True, value_src=r[j])
    return c


# ------------------------------------------------------------------ S7 Woodruff 2019
def load_woodruff():
    c = Collector("S7")
    df = pd.read_csv(os.path.join(RAW, "usgs_woodruff2019", "Bedrock.csv"), encoding="utf-8-sig")
    df.columns = [x.strip() for x in df.columns]
    df = df[df["Lab No."].notna()]
    pat = re.compile(r"^(\S+)\s+(?:Crbnt\s+)?([A-Z][a-z]?)\s+(wt\.%|ppm|ppb)$")
    for _, r in df.iterrows():
        u = uid("S7", r["Lab No."])
        desc = clean(r.get("Bedrock Description"))
        c.sample(mcr_uid=u, source_sample_id=r["Lab No."], lab_id=r["Lab No."], field_id=clean(r.get("Field No.")),
                 latitude=r.get("Latitude"), longitude=r.get("Longitude"), state="MN", sample_type="whole_rock",
                 rock_class="", rock_name=clean(r.get("Rock Type")), stratigraphy=desc,
                 sample_source="natural exposure/outcrop", deposit_or_locality=clean(r.get("Watershed")),
                 reference="Woodruff (2019), doi:10.5066/P9VO251H",
                 _primary=join_text(desc, r.get("Rock Type")), _secondary=clean(r.get("Watershed")))
        for col in df.columns:
            m = pat.match(col)
            if not m:
                continue
            meth, el, unit = m.groups()
            if col.startswith("Coulometric"):
                el, meth = "C_carb", "Coulometric_Crbnt_C"
            v, cen, lim = H.parse_text_value(r[col])
            if v is None and not cen:
                continue
            c.analysis(u, el, unit.replace("wt.%", "wt%"), v, cen, lim, meth, True, value_src=r[col])
    return c


# ------------------------------------------------------------------ spatial and rift assignment
def spatial(samples):
    sdf = samples.copy()
    sdf["latitude"] = pd.to_numeric(sdf["latitude"], errors="coerce")
    sdf["longitude"] = pd.to_numeric(sdf["longitude"], errors="coerce")
    ok = sdf.latitude.between(-90, 90) & sdf.longitude.between(-180, 180) & sdf.latitude.notna()
    g = gpd.GeoDataFrame(sdf, geometry=[Point(xy) if k else None for xy, k in
                                        zip(zip(sdf.longitude, sdf.latitude), ok)], crs="EPSG:4326")
    with zipfile.ZipFile(os.path.join(RAW, "census", "tl_2023_us_state.zip")) as z:
        pass
    states = gpd.read_file("zip://" + os.path.join(RAW, "census", "tl_2023_us_state.zip"))[["STUSPS", "geometry"]]
    states = states.to_crs(4326)
    j = gpd.sjoin(g[ok], states, how="left", predicate="within")
    j = j[~j.index.duplicated()]
    g["state_from_coords"] = j["STUSPS"].reindex(g.index)
    units = gpd.read_file(os.path.join(RAW, "sgmc", "sgmc_mesoproterozoic_MI_MN_WI.geojson"))[
        ["STATE", "SGMC_LABEL", "UNIT_NAME", "geometry"]]
    mem = pd.read_csv(os.path.join(ROOT, "docs", "mcr_units.csv"))
    units = units.merge(mem[["state", "sgmc_label", "mcr_class"]], left_on=["STATE", "SGMC_LABEL"],
                        right_on=["state", "sgmc_label"], how="left")
    units = units.drop(columns=["state", "sgmc_label"])
    units["geometry"] = units.geometry.buffer(0)
    j2 = gpd.sjoin(g[ok][["geometry"]], units, how="left", predicate="within")
    j2 = j2[~j2.index.duplicated()]
    g["sgmc_label"] = j2["SGMC_LABEL"].reindex(g.index)
    g["sgmc_unit_name"] = j2["UNIT_NAME"].reindex(g.index)
    g["sgmc_class"] = j2["mcr_class"].reindex(g.index)
    return pd.DataFrame(g.drop(columns="geometry"))


def finalize(samples):
    s = spatial(samples)
    s["state_source"] = s["state"].fillna("")
    s["state"] = s["state_from_coords"].fillna("")
    s.loc[(s["state"] == "") & s["state_source"].isin(STUDY_STATES), "state"] = s["state_source"]
    s["coord_quality"] = s["coord_quality"].fillna("")
    s.loc[s["coord_quality"] == "", "coord_quality"] = "reported"
    s.loc[s.latitude.isna() | s.longitude.isna(), "coord_quality"] = "missing"
    s.loc[(s["state_source"].isin(STUDY_STATES)) & (s["state_from_coords"].fillna("") != "") &
          (s["state_source"] != s["state_from_coords"].fillna("")), "coord_quality"] = "state_mismatch"
    keep, how, reason, cls = [], [], [], []
    for _, r in s.iterrows():
        map_member = r["sgmc_class"] if isinstance(r["sgmc_class"], str) and r["sgmc_class"] != "excluded" else ""
        if r["state"] not in STUDY_STATES:
            keep.append(False); how.append(""); cls.append("")
            reason.append("outside study states (coordinates fall in " +
                          (r['state_from_coords'] if isinstance(r['state_from_coords'], str) else
                           "no U.S. state; mostly Ontario, Canada") + ")")
            continue
        ok, h, why = H.rift_decision(r.get("_primary"), r.get("_secondary"), r.get("geologic_age_source"), map_member)
        keep.append(ok); how.append(h); reason.append(why)
        cls.append(map_member if ok else "")
    s["in_mcr"], s["mcr_match"], s["mcr_reason"], s["mcr_class"] = keep, how, reason, cls
    # rock class fallback from map + class
    m = (s["rock_class"].fillna("").isin(["", "unspecified", "igneous"])) & s["in_mcr"]
    lith = s["sgmc_unit_name"].fillna("").str.lower()
    s.loc[m & (s["mcr_class"].str.contains("sediment")), "rock_class"] = "sedimentary"
    s.loc[m & (s["rock_class"].fillna("").isin(["", "unspecified", "igneous"])) &
          lith.str.contains("volcan|basalt|rhyolite|lava|flows"), "rock_class"] = "igneous_volcanic"
    s.loc[m & (s["rock_class"].fillna("").isin(["", "unspecified", "igneous"])) &
          lith.str.contains("gabbro|troctol|intrus|granophyre|diabase|granite|anorth|cumulat|cyclic|ferromonzo|logan"),
          "rock_class"] = "igneous_intrusive"
    rn = s["rock_name"].fillna("").str.lower()
    m = s["rock_class"].fillna("").isin(["", "unspecified", "igneous"])
    s.loc[m & rn.str.contains("basalt|rhyolite|andesite|lava|flow|icelandite|amygdal"), "rock_class"] = "igneous_volcanic"
    m = s["rock_class"].fillna("").isin(["", "unspecified", "igneous"])
    s.loc[m & rn.str.contains("gabbro|troctol|norite|diorite|granophyre|diabase|granite|anorth|dunite|peridot|pyroxenite|dolerite|monzo"),
          "rock_class"] = "igneous_intrusive"
    m = s["rock_class"].fillna("").isin(["", "unspecified"])
    s.loc[m & rn.str.contains("sandstone|shale|siltstone|conglomerate|argillite|mudstone|arkose"), "rock_class"] = "sedimentary"
    s.loc[m & rn.str.contains("hornfels|schist|gneiss|quartzite|slate"), "rock_class"] = "metamorphic"
    s.loc[s["rock_class"].fillna("") == "", "rock_class"] = "unspecified"
    s.loc[s["in_mcr"], "mcr_class"] = [H.member_class(join_text(r.get("_primary"), r.get("stratigraphy")),
                                                      r["mcr_class"], r["rock_class"])
                                       for _, r in s[s["in_mcr"]].iterrows()]
    s.loc[s["sample_type"] == "mineral_grain", "rock_class"] = s.loc[s["sample_type"] == "mineral_grain", "rock_class"].replace("unspecified", "")
    return s


def depth_m(text):
    """Convert a depth text to metres only when the unit is stated; NGDB depths often lack units."""
    m = re.match(r"^\s*(\d+(?:\.\d+)?)(?:\s*-\s*\d+(?:\.\d+)?)?\s*(m|ft|feet|meters?|metres?)\b", text or "", re.I)
    if not m:
        return None
    v = float(m.group(1))
    return round(v * 0.3048, 3) if m.group(2).lower().startswith("f") else v


def main():
    os.makedirs(OUT, exist_ok=True)
    loaders = [load_ngdb, load_usgs_duluth, load_emri, load_georoc_cfb, load_georoc_minerals, load_earthchem,
               load_woodruff]
    all_s, all_l, counts = [], [], []
    for f in loaders:
        c = f()
        print(f"{c.sid}: {len(c.samples):,} samples read, {len(c.rows):,} determinations")
        all_s += c.samples
        all_l += c.rows
        counts.append(dict(source_id=c.sid, samples_read=len(c.samples), determinations_read=len(c.rows)))
    samples = pd.DataFrame(all_s)
    for col in SAMPLE_COLS + ["_primary", "_secondary", "depth_text"]:
        if col not in samples:
            samples[col] = None
    dup = samples["mcr_uid"].duplicated(keep=False)
    if dup.any():
        samples.loc[dup, "mcr_uid"] = samples.loc[dup, "mcr_uid"] + "_" + samples[dup].groupby("mcr_uid").cumcount().astype(str)
        raise SystemExit(f"duplicate uids: {samples.loc[dup, 'mcr_uid'].head().tolist()}")
    samples["depth_source"] = samples["depth_text"]
    fill = samples["depth_from_m"].isna() & samples["depth_text"].fillna("").ne("")
    samples.loc[fill, "depth_from_m"] = samples.loc[fill, "depth_text"].map(depth_m)
    s = finalize(samples)
    longdf = pd.DataFrame(all_l)

    excl = s[~s["in_mcr"]]
    kept = s[s["in_mcr"]].copy()
    longk = longdf[longdf["mcr_uid"].isin(kept["mcr_uid"])].copy()
    # drop samples with no chemistry at all
    has_chem = set(longk["mcr_uid"])
    nochem = kept[~kept["mcr_uid"].isin(has_chem)]
    kept = kept[kept["mcr_uid"].isin(has_chem)]

    excl_out = pd.concat([excl.assign(exclusion_reason=excl["mcr_reason"]),
                          nochem.assign(exclusion_reason="no chemistry values")])
    excl_out[["mcr_uid", "source_id", "source_sample_id", "latitude", "longitude", "state", "state_from_coords",
              "rock_name", "stratigraphy", "geologic_age_source", "sgmc_label", "sgmc_unit_name",
              "exclusion_reason"]].to_csv(os.path.join(OUT, "excluded_samples.csv"), index=False)
    kept["dataset_version"] = VERSION
    kept[SAMPLE_COLS + ["dataset_version"]].to_csv(os.path.join(OUT, "_stage_samples.csv"), index=False)
    longk["value_source"] = longk["value_source"].astype(str)
    longk[LONG_COLS].to_parquet(os.path.join(OUT, "_stage_long.parquet"), index=False)
    cdf = pd.DataFrame(counts)
    cdf["samples_in_study_states"] = cdf.source_id.map(s[s.state.isin(STUDY_STATES)].groupby("source_id").size()).fillna(0).astype(int)
    cdf["samples_kept_mcr"] = cdf.source_id.map(kept.groupby("source_id").size()).fillna(0).astype(int)
    cdf["determinations_kept"] = cdf.source_id.map(longk.merge(kept[["mcr_uid", "source_id"]]).groupby("source_id").size()).fillna(0).astype(int)
    cdf.to_csv(os.path.join(OUT, "_stage_counts.csv"), index=False)
    print(cdf.to_string(index=False))
    print(f"kept {len(kept):,} samples, {len(longk):,} determinations; excluded {len(excl_out):,}")


if __name__ == "__main__":
    main()
