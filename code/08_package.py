#!/usr/bin/env python3
"""08_package.py - build the release archives for Zenodo.

Plain-language note: makes the zip files you (or the upload script) put on Zenodo:
one for the dataset, one for the method crosswalk, one for the QA checker software, and a
snapshot of the raw inputs. They land in release/. Run with `python code/08_package.py`.
"""
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = os.path.join(ROOT, "release")
V = json.load(open(os.path.join(ROOT, "data", "processed", "stats.json")))["version"]


def z(name, files, base=ROOT):
    path = os.path.join(REL, name)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            full = os.path.join(base, f)
            if os.path.isdir(full):
                for dp, _, fns in os.walk(full):
                    if "__pycache__" in dp or ".pytest_cache" in dp:
                        continue
                    for fn in fns:
                        p = os.path.join(dp, fn)
                        zf.write(p, os.path.join(f"MCR-GeoChem_v{V}", os.path.relpath(p, base)))
            elif os.path.exists(full):
                zf.write(full, os.path.join(f"MCR-GeoChem_v{V}", f))
            else:
                raise SystemExit(f"missing {f}")
    print(f"{name}: {os.path.getsize(path) / 1e6:.1f} MB")


def main():
    os.makedirs(REL, exist_ok=True)
    proc = ["mcr_geochem_samples.csv", "mcr_geochem_analyses_long.csv", "mcr_geochem_analyses_long.parquet",
            "mcr_geochem_wide.csv", "method_crosswalk.csv", "detection_limits.csv", "excluded_samples.csv",
            "spot_checks.csv", "qa_report.txt", "stats.json"]
    docs = ["README.md", "CITATION.cff", "LICENSE-DATA.md", "AUTHORS.json", "CHANGELOG.md", "data/raw/provenance_log.csv",
            "docs/START_HERE.md", "docs/GLOSSARY.md", "docs/CODEBOOK.md", "docs/PROVENANCE.md", "docs/LIMITATIONS.md",
            "docs/QA_RULES.md", "docs/STATE_SOURCES.md", "docs/NEXT_STEPS.md", "docs/BUILD_SPEC.md", "docs/DECISIONS.md", "docs/mcr_units.csv",
            "paper/figures"]
    z(f"MCR-GeoChem_v{V}_dataset.zip", [f"data/processed/{p}" for p in proc] + docs)
    z(f"MCR-GeoChem_v{V}_method_detection_limit_crosswalk.zip",
      ["data/processed/method_crosswalk.csv", "data/processed/detection_limits.csv", "docs/CODEBOOK.md",
       "README.md", "CITATION.cff", "LICENSE-DATA.md", "data/raw/agdb4"])
    z(f"mcrqa_v{V}_software.zip", ["mcrqa", "tests", "pyproject.toml", "LICENSE", "README.md", "CITATION.cff", "code",
                                   "requirements.txt", "run_all.sh", "docs/QA_RULES.md"])
    z(f"MCR-GeoChem_v{V}_raw_inputs_snapshot.zip", ["data/raw", "LICENSE-DATA.md", "docs/PROVENANCE.md"])


if __name__ == "__main__":
    main()
