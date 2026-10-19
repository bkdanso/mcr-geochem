#!/usr/bin/env bash
# Rebuild MCR-GeoChem from scratch. Takes about 15-30 minutes (most of it the GEOROC mineral scan).
set -euo pipefail
cd "$(dirname "$0")"
python code/01_fetch.py
python code/02a_mcr_units.py
python code/02_build.py
python code/03_crosswalk.py
python code/04_qa.py
python code/05_figures.py "$@"
python code/06_provenance.py
python code/07_docs.py
python -m pytest -q tests
python code/08_package.py
