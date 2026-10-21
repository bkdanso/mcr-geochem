@echo off
setlocal EnableDelayedExpansion
REM Double-click this file to set up and use MCR-GeoChem on Windows.
cd /d "%~dp0"
where python >nul 2>nul || (echo Python is not installed. Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH". & pause & exit /b)
if not exist .venv (
  echo First-time setup: installing what the project needs. This takes a few minutes...
  python -m venv .venv
  call .venv\Scripts\activate
  python -m pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
  pip install --quiet -e .
) else (
  call .venv\Scripts\activate
)
:menu
echo.
echo ===== MCR-GeoChem =====
echo 1. Check my own spreadsheet with the QA checker
echo 2. Rebuild the whole dataset from the public sources (15-30 min)
echo 3. Run the self-test
echo 4. Quit
set /p choice=Type 1, 2, 3 or 4 and press Enter: 
if "%choice%"=="1" (
  set /p file=Drag your CSV or Excel file into this window, then press Enter: 
  set /p idcol=Name of the sample ID column (or press Enter to skip): 
  if "!idcol!"=="" (mcrqa wide !file! --out qa_results) else (mcrqa wide !file! --id-col "!idcol!" --out qa_results)
  echo Results are in the qa_results folder.
  start "" qa_results
  goto menu
)
if "%choice%"=="2" (
  for %%s in (01_fetch.py 02a_mcr_units.py 02_build.py 03_crosswalk.py 04_qa.py) do python code\%%s
  python code\05_figures.py --final --paper
  python code\06_provenance.py
  python code\07_docs.py --final --github-user bkdanso
  echo Done. See data\processed\qa_report.txt
  start "" data\processed
  goto menu
)
if "%choice%"=="3" ( python -m pytest -q tests & goto menu )
exit /b
