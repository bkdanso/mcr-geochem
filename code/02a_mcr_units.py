#!/usr/bin/env python3
"""02a_mcr_units.py - list every Mesoproterozoic map unit in MI, MN, WI and label its rift membership.

Plain-language note: the USGS state geologic map has 77 map units of the right broad age in
the three states. Not all are rift rocks (the Wolf River batholith is ~1.47 billion years
old, older than the rift). This script writes docs/mcr_units.csv: one row per unit with a
label (rift_igneous, rift_sedimentary, post_rift_sedimentary, or excluded) and the reason.
You confirm this list in your checklist (decision V1).
"""
import json
import os
import re

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "raw", "sgmc", "sgmc_mesoproterozoic_MI_MN_WI.geojson")
OUT = os.path.join(ROOT, "docs", "mcr_units.csv")

EXCLUDE = [
    (r"wolf river|wausau|stettin|hager", "Wolf River batholith / Wausau / Stettin plutons (~1.47-1.56 Ga): older than the rift"),
    (r"unknown age", "Age unknown (Mesoproterozoic or Paleoproterozoic); included only if the source names a rift unit"),
]
POST = r"jacobsville|bayfield|chequamegon|orienta|devil"
RIFT_SED = r"copper harbor conglomerate$|oronto|freda|nonesuch|puckwunge|nopeming|interflow|sandstone, siltstone, and local conglomerate"


def main():
    g = json.load(open(SRC, encoding="utf-8"))
    rows = {}
    for f in g["features"]:
        p = f["properties"]
        key = (p["STATE"], p["SGMC_LABEL"])
        r = rows.setdefault(key, dict(state=p["STATE"], sgmc_label=p["SGMC_LABEL"], unit_name=p["UNIT_NAME"].strip(),
                                      generalized_lith=p["GENERALIZED_LITH"], age_min=p["AGE_MIN"], age_max=p["AGE_MAX"],
                                      n_polygons=0, reference=p.get("REFERENCE")))
        r["n_polygons"] += 1
    out = []
    for r in rows.values():
        name = r["unit_name"].lower()
        cls, why = None, ""
        for pat, reason in EXCLUDE:
            if re.search(pat, name):
                cls, why = "excluded", reason
                break
        if cls is None and re.search(POST, name):
            cls, why = "post_rift_sedimentary", "Bayfield Group / Jacobsville Sandstone: late- to post-rift basin fill"
        if cls is None and (re.search(RIFT_SED, name) or (r["generalized_lith"] or "").startswith("Sedimentary")):
            cls, why = "rift_sedimentary", "Keweenawan rift-basin sedimentary unit"
        if cls is None:
            cls, why = "rift_igneous", "Keweenawan (Midcontinent Rift) igneous unit"
        if r["state"] == "MN" and r["sgmc_label"].startswith("Y3") and cls == "excluded":
            why += " (check: MN Y3 units are Keweenawan)"
        r.update(mcr_class=cls, reason=why)
        out.append(r)
    df = pd.DataFrame(out).sort_values(["mcr_class", "state", "sgmc_label"])
    df.to_csv(OUT, index=False)
    print(df.groupby("mcr_class").size().to_string())
    print(f"wrote {os.path.relpath(OUT, ROOT)} ({len(df)} units)")


if __name__ == "__main__":
    main()
