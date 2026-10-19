"""Command-line interface.

    mcrqa check  --samples S.csv --analyses A.csv|.parquet --out DIR [--rules rules.json]
    mcrqa wide   TABLE.csv [--id-col SAMPLE] --out DIR [--rules rules.json] [--no-usgs-negative]
    mcrqa flags                     # list every flag and what it means
"""
import argparse
import os
import sys

import pandas as pd

from . import __version__
from .checker import FLAG_DOC, flag_analyses, flag_samples, load_rules
from .wide import wide_to_long


def _read(path):
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    if path.endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    return pd.read_csv(path, low_memory=False)


def summarize(samples, long):
    lines = [f"mcrqa {__version__} summary", f"samples: {len(samples):,}   determinations: {len(long):,}", ""]
    fa = long["qa_flags"].str.split(";").explode()
    fa = fa[fa.fillna("") != ""].value_counts()
    fs = samples["qa_flags"].str.split(";").explode()
    fs = fs[fs.fillna("") != ""].value_counts()
    lines.append("Determination flags (count):")
    lines += [f"  {k:<22} {v:>9,}  {FLAG_DOC.get(k, '')}" for k, v in fa.items()]
    lines.append("")
    lines.append("Sample flags (count):")
    lines += [f"  {k:<22} {v:>9,}  {FLAG_DOC.get(k, '')}" for k, v in fs.items()]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mcrqa", description="Open geochemistry QA checker (MCR-GeoChem).")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="check a long-format table plus a samples table")
    c.add_argument("--samples", required=True)
    c.add_argument("--analyses", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--rules")
    w = sub.add_parser("wide", help="check a wide spreadsheet (one row per sample)")
    w.add_argument("table")
    w.add_argument("--id-col")
    w.add_argument("--out", required=True)
    w.add_argument("--rules")
    w.add_argument("--no-usgs-negative", action="store_true",
                   help="do NOT treat negative numbers as below-detection")
    sub.add_parser("flags", help="list flags")
    a = ap.parse_args(argv)
    if a.cmd == "flags":
        for k, v in FLAG_DOC.items():
            print(f"{k:<22} {v}")
        return 0
    rules = load_rules(a.rules)
    os.makedirs(a.out, exist_ok=True)
    if a.cmd == "check":
        samples, long = _read(a.samples), _read(a.analyses)
    else:
        long, samples, mapping = wide_to_long(_read(a.table), a.id_col, not a.no_usgs_negative)
        mapping.to_csv(os.path.join(a.out, "column_mapping.csv"), index=False)
        if long.empty:
            print("No geochemistry columns recognized. See column_mapping.csv.", file=sys.stderr)
            return 2
    long = flag_analyses(long, samples, rules)
    samples = flag_samples(samples, long, rules)
    long.to_csv(os.path.join(a.out, "qa_analyses.csv"), index=False)
    samples.to_csv(os.path.join(a.out, "qa_samples.csv"), index=False)
    txt = summarize(samples, long)
    with open(os.path.join(a.out, "qa_summary.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
