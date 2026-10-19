"""Check any 'wide' geochemistry spreadsheet (one row per sample, one column per element).

Recognized column styles:
    USGS:    Cu_ppm, Si_pct, Au_ppb, Cu_ppm_ICP60      (negative = below detection; x.11111 = above limit)
    GEOROC:  SIO2(WT%), NI(PPM), PT(PPB)
    Simple:  SiO2_wt%, SiO2 (wt%), Ni ppm, Ni [ppm]
Values may be numbers or text such as '<0.5' or '>10000'.
The table is converted to the long schema, then the standard checks are run.
"""
import re

import pandas as pd

from .units import harmonize, parse_text_value, parse_usgs_qualified

PATTERNS = [
    re.compile(r"^(?P<a>[A-Za-z][A-Za-z0-9]*?)_(?P<u>ppm|ppb|pct|wt%|ppt)(?:_(?P<m>[A-Za-z0-9-]+))?$", re.I),
    re.compile(r"^(?P<a>[A-Za-z][A-Za-z0-9]*)\s*[\(\[](?P<u>ppm|ppb|pct|wt%|wt\.%|%|ppt)[\)\]]$", re.I),
    re.compile(r"^(?P<a>[A-Za-z][A-Za-z0-9]*)\s+(?P<u>ppm|ppb|pct|wt%|wt\.%|ppt)$", re.I),
]


def parse_column(col):
    for p in PATTERNS:
        m = p.match(col.strip())
        if m:
            u = m.group("u").lower().replace("wt.%", "wt%").replace("%", "wt%") if m.group("u") != "%" else "wt%"
            u = "wt%" if u in ("wt%", "wtwt%", "pct") else u
            return m.group("a"), u, (m.groupdict().get("m") or "")
    return None


def wide_to_long(df, id_col=None, usgs_negative=True):
    """Return (long_df, samples_df, mapping_df). usgs_negative: treat negative numbers as '<|x|'."""
    ids = df[id_col].astype(str) if id_col else pd.Series([f"row{i + 2}" for i in range(len(df))], index=df.index)
    rows, mapping = [], []
    for col in df.columns:
        p = parse_column(str(col))
        if not p:
            continue
        a, u, m = p
        test = harmonize(a, u, 1.0)
        mapping.append(dict(column=col, analyte_source=a, unit_source=u, method_tag=m,
                            analyte=test[0] if test else "", unit=test[1] if test else "",
                            recognized=bool(test)))
        if not test:
            continue
        for uid, raw in zip(ids, df[col]):
            if isinstance(raw, (int, float)) and usgs_negative:
                v, cen, lim = parse_usgs_qualified(raw)
            else:
                v, cen, lim = parse_text_value(raw)
            if v is None and not cen:
                continue
            base = v if v is not None else (lim if lim is not None else 1.0)
            h = harmonize(a, u, base)
            rows.append(dict(mcr_uid=uid, analyte=h[0], value=h[2] if v is not None else None, unit=h[1],
                             censor=cen, detection_limit=h[2] if (v is None and lim is not None) else None,
                             is_best_value=True, extent="unknown" if not m else "total",
                             method_code_source=m, source_column=col, value_source=raw))
    long = pd.DataFrame(rows)
    if len(long):
        long = long.sort_values(["mcr_uid", "analyte"])
        long["is_best_value"] = ~long.duplicated(["mcr_uid", "analyte"])
    samples = pd.DataFrame({"mcr_uid": ids.values, "sample_type": "whole_rock", "rock_class": "",
                            "coord_quality": "", "alteration_source": "", "field_id": ids.values,
                            "source_id": "input", "latitude": None, "longitude": None})
    for c in ("rock_class", "rock_type", "ROCK TYPE", "lithology"):
        if c in df.columns:
            rc = df[c].astype(str).str.lower()
            samples["rock_class"] = rc.where(~rc.str.contains("basalt|gabbro|granite|rhyol|andes|dior|troct|igneous|volc|plut"),
                                             "igneous").values
            break
    for la, lo in (("latitude", "longitude"), ("Latitude", "Longitude"), ("LATITUDE", "LONGITUDE"),
                   ("lat", "lon"), ("Lat_WGS84", "Long_WGS84")):
        if la in df.columns and lo in df.columns:
            samples["latitude"], samples["longitude"] = df[la].values, df[lo].values
            break
    return long, samples, pd.DataFrame(mapping)
