# mcrqa: open QA checker for geochemistry tables

*Plain-language note: a small free program that reads a table of rock chemistry and marks values that need care: results below the detection limit, numbers that look like unit mistakes, rocks that were probably altered after they formed, and the same sample appearing twice. It does not change any value; it only adds flags.*

Part of **MCR-GeoChem** (Midcontinent Rift geochemistry compilation). Works on any table in the MCR-GeoChem long schema, or on an ordinary wide spreadsheet (one row per sample).

## Install

```
pip install .            # from the repository root
# or, with no install:  python -m mcrqa ...
```
Requires Python 3.9+, pandas, numpy (pyarrow for .parquet, openpyxl for .xlsx).

## Use

Wide spreadsheet (USGS `Cu_ppm`, GEOROC `NI(PPM)`, or `SiO2 (wt%)` style columns; values may be numbers or text like `<0.5`):
```
mcrqa wide my_samples.csv --id-col Sample --out qa_out/
```
Negative numbers are read as below-detection (USGS convention). Turn that off with `--no-usgs-negative`.

Long table plus samples table (MCR-GeoChem schema):
```
mcrqa check --samples mcr_geochem_samples.csv --analyses mcr_geochem_analyses_long.parquet --out qa_out/
```
Outputs: `qa_analyses.csv`, `qa_samples.csv`, `qa_summary.txt` (and `column_mapping.csv` in wide mode).

List the flags: `mcrqa flags`. Change any threshold with `--rules my_rules.json` (keys as in `mcrqa/rules.py`).

## Flags

| Flag | Level | Rule (default) |
|---|---|---|
| BDL | value | censor `<` |
| BDL_UNINFORMATIVE | value | below detection with limit above an analyte threshold (e.g. Pt, Pd, Au > 10 ppb; Ni, Cu > 50 ppm) |
| ABOVE_UPPER_LIMIT | value | censor `>` (USGS `.11111` code decoded) |
| SEMI_QUANTITATIVE / PARTIAL_DIGESTION / METHOD_NOT_REPORTED | value | from the method crosswalk `extent` |
| IMPLAUSIBLE_VALUE | value | negative (LOI allowed down to -5), > 100 wt%, > 10^6 ppm |
| POSSIBLE_UNIT_ERROR | value | above a generous ceiling for unmineralized whole rock (e.g. Ni, Cu > 5,000 ppm; Pt > 2,000 ppb) unless S >= 1 wt% |
| ZERO_VALUE | value | exactly 0 |
| MAJOR_TOTAL_LOW / HIGH | sample | oxides + LOI outside 96-102.5 wt% (needs SiO2, Al2O3, Fe2O3T, MgO, CaO, Na2O, K2O measured; low totals ignored when S >= 1 wt%) |
| SI_ELEMENT_SUSPECT | sample | igneous SiO2 between 15 and 32 wt% (looks like Si reported as SiO2) |
| ALTERED_LOI / ALTERED_CIA / ALTERED_AI / ALTERED_SOURCE | sample | igneous: LOI > 3 wt%; CIA > 60 (Nesbitt & Young 1982); Ishikawa AI outside 20-65 (Large et al. 2001); source describes alteration |
| COORD_MISSING / COORD_APPROXIMATE / COORD_STATE_MISMATCH | sample | from coordinate quality |
| POSSIBLE_DUPLICATE | sample | different sources, within ~500 m, and same normalized field or lab ID, or SiO2 and MgO within 1% |

Every threshold is a screening default, documented with its basis in `rules.py`. Flags are advice, not deletions.

## Test

```
python -m pytest tests/
```

## Cite

See `CITATION.cff` in the repository. License: MIT.

## References

- Ishikawa, Y., Sawaguchi, T., Iwaya, S., and Horiuchi, M., 1976, Delineation of prospecting targets for Kuroko deposits based on modes of volcanism of underlying dacite and alteration halos: Mining Geology, v. 26, p. 105-117.
- Large, R.R., Gemmell, J.B., Paulick, H., and Huston, D.L., 2001, The alteration box plot: Economic Geology, v. 96, p. 957-971.
- Nesbitt, H.W., and Young, G.M., 1982, Early Proterozoic climates and plate motions inferred from major element chemistry of lutites: Nature, v. 299, p. 715-717.
