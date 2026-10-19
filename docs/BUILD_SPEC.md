# Build spec: MCR-GeoChem v1.0

*Plain-language note: this is the one-page plan the whole build follows. You do not need to edit it. If the project changes shape, this file changes first.*

```
PROJECT:     MCR-GeoChem. Archetypes: (1) open dataset + (2) tool (QA checker) + crosswalk table.
QUESTION:    What is the documented, quality-flagged whole-rock and mineral chemistry of
             Midcontinent Rift (~1.1 Ga, Keweenawan) rocks in Michigan, Minnesota, and Wisconsin?
SOURCES:
  S1 USGS NGDB "Geochemical data for rock, sediment, soil, and mineral samples, United States
     and territories, 1962 to 2023" (Granitto et al., 2026), doi:10.5066/P1FXE9GK. Pulled from the
     USGS public ArcGIS feature service of that release (Geochem_features, layers Rock and Mineral),
     because the ScienceBase bulk files now require a login. Public domain.
  S2 USGS "Geochemistry of drill core and hand samples from the Duluth Complex, Minnesota"
     (Parks et al., 2025), doi:10.5066/P13UFQYF. Public domain.
  S3 USGS Earth MRI geochemistry ver. 12.0 (Dec 2025), doi:10.5066/P9WHRLXH. Public domain.
  S4 GEOROC Compilation: Continental Flood Basalts, file MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN
     (DIGIS, generated 2026-09-01), doi:10.25625/WSTPOX. CC BY-SA 4.0.
  S5 GEOROC Compilation: Minerals (2024-12), doi:10.25625/SGFTFN, filtered to the study area. CC BY-SA 4.0.
  S6 EarthChem Library, Davis, Collins & Rooney, Portage Lake Volcanics, doi:10.26022/IEDA/111501. CC BY-SA 4.0.
  Support: USGS SGMC State Geologic Map Compilation (Horton et al., 2017), public feature service
     (rift map-unit footprint); U.S. Census TIGER state boundaries (study-area clip). Public domain.
  Deferred to v1.1: state survey tables (MN DNR / MGS, WGNHS, Michigan GS), listed in docs/STATE_SOURCES.md.
UNIT:        One analysis = one sample x one analyte x one determination (long table).
             Also one row per sample (samples table) and one row per sample with best values (wide table).
MEASURES:
  - Major elements as oxide wt% (SiO2, TiO2, Al2O3, Fe2O3T, FeO, MnO, MgO, CaO, Na2O, K2O, P2O5, LOI);
    element-wt% values converted with standard oxide factors; original value kept.
  - Trace elements ppm; Au and platinum-group elements ppb; original value and unit kept.
  - Censoring: below-detection values stored as value=NULL, censored="<", detection_limit=|value|.
  - Method: source code kept, plus harmonized method family (crosswalk).
  - MCR membership: point-in-polygon against SGMC Mesoproterozoic rift units (membership table
    docs/mcr_units.csv), else rift text match in source metadata; how matched is recorded.
  - QA flags per analysis and per sample (see QA checker spec in docs/QA_RULES.md).
OUTPUTS:     data/processed/mcr_geochem_samples.csv, mcr_geochem_analyses_long.csv(.parquet),
             mcr_geochem_wide.csv, method_crosswalk.csv, detection_limits.csv, qa_report.txt,
             stats.json; code/mcrqa/ (QA checker); docs/CODEBOOK.md, docs/PROVENANCE.md; figures.
VENUES:      GitHub repo (code + docs); Zenodo DOI x3 (dataset v1.0 with codebook + provenance;
             crosswalk; QA checker software). Optional later: data descriptor paper.
VERIFY POINTS (author rules):
  V1 Which SGMC units count as rift (Wolf River/Wausau ~1.47 Ga excluded; Jacobsville/Bayfield included as post-rift sediment)
  V2 Altered-sample thresholds (default LOI > 3 wt%, CIA > 60 for igneous, Na2O+K2O outside igneous range)
  V3 Possible cross-source duplicates: keep both, flagged (default) or drop
  V4 Spot checks of 8 named samples against the source pages
LICENSE:     Data CC BY-SA 4.0 (required by GEOROC/EarthChem share-alike). Code MIT. Docs CC BY 4.0.
ASSUMPTIONS: Brief dates (Feb/Aug 2027) are targets, not waits; build now. Mineral chemistry in v1.0
             comes from GEOROC Minerals and NGDB mineral samples only.
```

## What this means for you, line by line

- **Project:** one table, one lookup table (the crosswalk), and one checking program.
- **Sources:** six free public sources. Three are U.S. government (no restrictions), three are share-alike.
- **Unit:** every row in the main table is one measurement of one element in one sample. A second table has one row per sample.
- **Measures:** all major elements in the same unit (oxide weight percent), all trace elements in ppm, precious metals in ppb. "Too small to measure" is always written the same way.
- **Rift membership:** a sample counts if it sits on a rift rock unit on the USGS state geologic map, or its source labels it as rift rock. You confirm the list of units.
- **Outputs:** CSV files anyone can open in Excel, plus the checker program and documentation.
- **License:** anyone can reuse the data if they credit you and share alike; the code is free to reuse.
- **Your decisions:** four items, all with defaults, listed in your checklist.
