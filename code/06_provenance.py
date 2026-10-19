#!/usr/bin/env python3
"""06_provenance.py - write the human-readable provenance log (docs/PROVENANCE.md).

Plain-language note: turns data/raw/provenance_log.csv into a readable page listing every
source file: where it came from (URL), when it was downloaded, its size and checksum,
how many rows it has, how many rows made it into the dataset, and its license. This page
ships with every release. Run it with `python code/06_provenance.py`.
"""
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
P = os.path.join(ROOT, "data", "processed")


def rows_in(path):
    full = os.path.join(RAW, path)
    try:
        if path.endswith(".json") or path.endswith(".geojson"):
            return len(json.load(open(full, encoding="utf-8"))["features"])
        if path.endswith(".csv"):
            if "KEWEENAWAN" in path:
                d = pd.read_csv(full, encoding="latin1", low_memory=False, usecols=["TECTONIC SETTING"])
                return int(d["TECTONIC SETTING"].notna().sum())
            return sum(1 for _ in open(full, encoding="latin1")) - 1
        if path.endswith(".txt") and "agdb4" in path:
            return sum(1 for _ in open(full, encoding="latin1")) - 1
        if path.endswith(".xlsx"):
            return 55 if "Portage" in path else None
    except Exception:
        return None
    return None


def main():
    log = pd.read_csv(os.path.join(RAW, "provenance_log.csv"))
    st = json.load(open(os.path.join(P, "stats.json")))
    counts = {r["source_id"]: r for r in st["counts_by_source"]}
    log["rows"] = [rows_in(f) for f in log.file]
    L = ["# Provenance log: MCR-GeoChem v" + st["version"], "",
         "*Plain-language note: this page records exactly where every input file came from, when it was "
         "downloaded, and its license. The machine-readable version is `data/raw/provenance_log.csv`. "
         "A checksum (SHA-256) is a fingerprint: if a re-downloaded file has the same checksum, it is byte-for-byte identical.*",
         "", f"Build date: {st['build_date']}. Pipeline: `code/01_fetch.py` to `code/06_provenance.py`.", "",
         "## Row counts by source", "",
         "| Source | Samples read | In MI/MN/WI | Kept (rift) | Measurements kept |", "|---|---:|---:|---:|---:|"]
    names = {"S1": "USGS NGDB 1962-2023", "S2": "USGS Duluth Complex (Parks et al. 2025)",
             "S3": "USGS Earth MRI v12", "S4": "GEOROC CFB: MCR-Keweenawan", "S5": "GEOROC Minerals (region)",
             "S6": "EarthChem 1501 Portage Lake", "S7": "USGS Woodruff (2019) bedrock"}
    for sid, n in names.items():
        c = counts.get(sid, {})
        L.append(f"| {sid} {n} | {c.get('samples_read', 0):,} | {c.get('samples_in_study_states', 0):,} | "
                 f"{c.get('samples_kept_mcr', 0):,} | {c.get('determinations_kept', 0):,} |")
    L += ["", "S3 contributes no samples to v1.0: all of its MI/MN/WI rocks are Archean, Paleoproterozoic, or Paleozoic. "
          "It stays in the pipeline so later Earth MRI versions are picked up automatically.", "",
          "## Files", ""]
    for sid, g in log.groupby("source_id"):
        r0 = g.iloc[0]
        L += [f"### {sid}", "", f"**Citation:** {r0.citation}", "", f"**License:** {r0.license}", "",
              "| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |", "|---|---:|---:|---|---|---|---|"]
        for r in g.itertuples():
            url = r.url if len(str(r.url)) < 140 else str(r.url)[:137] + "..."
            note = "" if pd.isna(r.note) else str(r.note).replace("|", "/")
            rows = "" if r.rows is None or pd.isna(r.rows) else f"{int(r.rows):,}"
            L.append(f"| {r.file} | {rows} | {int(r.bytes):,} | {r.access_date} | `{r.sha256[:16]}` | {url} | {note} |")
        L.append("")
    L += ["## Access notes", "",
          "- **USGS NGDB 1962-2023.** Since the November 2025 file update, the ScienceBase bulk files (geodatabase, GeoPackage, "
          "Parquet) require a ScienceBase login. The same release is served by the public USGS ArcGIS feature service "
          "`Geochem_features` (layers Rock, Mineral, Geologic_material), linked from the USGS Geochemical Data Portal. "
          "v1.0 queries that service for `state IN ('MI','MN','WI')`. To re-check against the bulk files, log in at "
          "https://www.sciencebase.gov/catalog/item/63a107a0d34e0de3a1f2795f and download the Parquet archive.",
          "- **GEOROC Minerals.** The 19 global mineral files (about 2.4 million rows) are downloaded one at a time, "
          "filtered to the study region, and deleted. Per-file counts are in `data/raw/georoc/georoc_minerals_scan_manifest.csv`.",
          "- **AGDB4 method dictionary.** Only the method and parameter tables are kept from the 212 MB archive; "
          "they define the same USGS method codes used in the NGDB.",
          "- **State survey releases.** Not in v1.0; see `docs/STATE_SOURCES.md` for the candidate list for v1.1.", ""]
    with open(os.path.join(ROOT, "docs", "PROVENANCE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("wrote docs/PROVENANCE.md")


if __name__ == "__main__":
    main()
