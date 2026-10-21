#!/bin/bash
# Double-click this file to set up and use MCR-GeoChem on a Mac (or run: bash START_MAC.command on Linux).
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then echo "Python is not installed. Install it from https://www.python.org/downloads/"; read -p "Press Enter to close"; exit 1; fi
if [ ! -d .venv ]; then
  echo "First-time setup: installing what the project needs. This takes a few minutes..."
  "$PY" -m venv .venv && source .venv/bin/activate
  pip install --quiet --upgrade pip && pip install --quiet -r requirements.txt && pip install --quiet -e .
else
  source .venv/bin/activate
fi
while true; do
  echo; echo "===== MCR-GeoChem ====="
  echo "1. Check my own spreadsheet with the QA checker"
  echo "2. Rebuild the whole dataset from the public sources (15-30 min)"
  echo "3. Run the self-test"
  echo "4. Quit"
  read -p "Type 1, 2, 3 or 4 and press Enter: " c
  case "$c" in
    1) read -p "Drag your CSV or Excel file into this window, then press Enter: " f
       f=$(echo "$f" | sed "s/^'//; s/'$//; s/\\\\ / /g")
       read -p "Name of the sample ID column (or press Enter to skip): " idc
       if [ -z "$idc" ]; then mcrqa wide "$f" --out qa_results; else mcrqa wide "$f" --id-col "$idc" --out qa_results; fi
       echo "Results are in the qa_results folder."; open qa_results 2>/dev/null ;;
    2) for s in 01_fetch.py 02a_mcr_units.py 02_build.py 03_crosswalk.py 04_qa.py; do python code/$s || break; done
       python code/05_figures.py --final --paper && python code/06_provenance.py && python code/07_docs.py --final --github-user bkdanso
       echo "Done. See data/processed/qa_report.txt"; open data/processed 2>/dev/null ;;
    3) python -m pytest -q tests ;;
    *) exit 0 ;;
  esac
done
