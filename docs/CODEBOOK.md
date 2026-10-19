# Codebook: MCR-GeoChem v1.0

*Plain-language note: this page explains every column in every table. If you open a file and wonder what a column means, look it up here. Units are always stated.*

## Files

| File | One row is | Use it for |
|---|---|---|
| `mcr_geochem_samples.csv` | one sample (whole rock) or one mineral analysis spot | where, what rock, rift membership, QA flags |
| `mcr_geochem_analyses_long.csv` / `.parquet` | one measurement of one analyte in one sample by one method | full detail: every determination, method, detection limit, flags |
| `mcr_geochem_wide.csv` | one sample, with best values as columns | quick plotting and spreadsheets |
| `method_crosswalk.csv` | one source method code | translating method codes (deliverable 2) |
| `detection_limits.csv` | one source x method x analyte | detection limits observed and documented (deliverable 2) |
| `excluded_samples.csv` | one sample read but not kept | auditing the rift filter |
| `spot_checks.csv` | one value chosen for hand checking | verification |
| `qa_report.txt`, `stats.json` | the QA report and every number quoted in the docs | review |

## Conventions

- **Units.** Major oxides, LOI, volatiles, S and C: weight percent (`wt%`). Au, Pt, Pd, Rh, Ru, Ir, Os, Re: parts per billion (`ppb`). All other elements: parts per million (`ppm`).
- **Element to oxide.** Sources that report majors as elements (USGS: Si, Al, Fe, Mg, Ca, Na, K, Ti, Mn, P in %) are converted with standard factors: SiO2 2.1393, TiO2 1.6681, Al2O3 1.8895, Fe2O3T 1.4297, MnO 1.2912, MgO 1.6583, CaO 1.3992, Na2O 1.3480, K2O 1.2046, P2O5 2.2914. FeOT to Fe2O3T: 1.1113. The original value and unit are kept in `value_source` and `unit_source`.
- **Total iron.** `Fe2O3T` is total iron as Fe2O3. GEOROC files that report only `FE2O3` (no FeO or FeOT) are labeled Fe2O3T, because in practice that column holds total iron; the rule is recorded in `harmonize_rule`. Where only Fe2O3 + FeO exist, Fe2O3T is calculated (`derived = True`).
- **Below detection.** In the long table: `value` empty, `censor = "<"`, `detection_limit` = the limit. In the wide table: a **negative number** means "below detection, limit = absolute value" (USGS convention), e.g. `-5` = less than 5.
- **Above upper limit.** `censor = ">"`, `detection_limit` holds the upper limit. USGS sources encode this as a value ending in `.11111` (e.g. `10.11111` = greater than 10); the pipeline decodes it.
- **Best value.** For each sample and analyte exactly one row has `is_best_value = True`: the source's own best value where it provides one (USGS NGDB and Duluth), otherwise the most complete method (total > near-total > partial > semi-quantitative), detected before censored, lowest limit first.

## `mcr_geochem_samples.csv`

| Column | Meaning |
|---|---|
| `mcr_uid` | Permanent MCR-GeoChem ID: `MCRG-<source>-<source sample id>` |
| `source_id` | S1 NGDB, S2 USGS Duluth, S4 GEOROC rock, S5 GEOROC mineral, S6 EarthChem, S7 Woodruff (S3 Earth MRI contributes none in v1.0) |
| `source_sample_id` | The ID used by the source (USGS lab ID, GEOROC UNIQUE_ID, field number) |
| `lab_id`, `field_id`, `igsn` | Laboratory number, collector's field number, International Geo Sample Number, where given |
| `latitude`, `longitude` | Decimal degrees (NAD83/WGS84 as given by the source). GEOROC ranges are replaced by their centroid |
| `coord_quality` | `reported`, `approximate` (one decimal place), `range_centroid` (GEOROC min/max box), `state_mismatch`, `missing` |
| `state` | MI, MN, or WI, from the coordinates (Census TIGER 2023) |
| `sample_type` | `whole_rock`, `mineral_grain` (in-situ spot analysis), `mineral_separate` |
| `mineral` | Mineral name for mineral analyses |
| `rock_class` | `igneous_intrusive`, `igneous_volcanic`, `sedimentary`, `metamorphic`, `vein_or_ore`, `unspecified` (from source fields, then rock name, then map unit) |
| `rock_name` | Rock name as given by the source |
| `stratigraphy` | Unit or locality hierarchy as given by the source |
| `geologic_age_source` | Age label as given by the source |
| `sample_source`, `collection_method` | Outcrop, drill core, mine...; grab, composite, channel... |
| `drill_hole`, `depth_from_m`, `depth_to_m`, `depth_source` | Drill hole; depth in metres only where the source states the unit; the original depth text |
| `collection_year`, `project`, `deposit_or_locality` | As given |
| `alteration_source` | Alteration as described by the source (GEOROC codes expanded: fresh, slightly, moderately, extensively altered) |
| `reference` | Publication or submitter for the sample |
| `source_doi`, `license` | DOI and license of the source dataset |
| `sgmc_label`, `sgmc_unit_name` | USGS State Geologic Map Compilation unit at the sample point (Mesoproterozoic units only) |
| `mcr_class` | `rift_igneous`, `rift_sedimentary`, `post_rift_sedimentary` |
| `mcr_match` | How rift membership was decided: `text+map`, `text` (source names a rift unit), `map` (on a rift map unit, no conflicting information), `map+context`, `context`. `map` and `context` are lower confidence |
| `mcr_reason` | Plain reason for inclusion |
| `major_oxide_total` | Sum of the 10 major oxides + LOI (or H2O + CO2), wt%, only when SiO2, Al2O3, Fe2O3T, MgO, CaO, Na2O, K2O are all measured |
| `n_major_oxides` | Number of the 10 major oxides with a best value |
| `loi_wt` | Loss on ignition (or H2O + CO2), wt% |
| `cia` | Chemical Index of Alteration, molar Al2O3/(Al2O3+CaO*+Na2O+K2O)x100, CaO* = CaO - 10/3 P2O5 - CO2 |
| `ai_ishikawa` | Ishikawa alteration index, 100(MgO+K2O)/(MgO+K2O+Na2O+CaO), wt% basis |
| `altered_criteria` | Which alteration tests fired, with values |
| `altered_likely` | True if any ALTERED_* flag is set |
| `duplicate_group` | Same ID for samples from different sources that are probably the same physical sample |
| `qa_flags` | Sample-level flags, semicolon-separated (see `docs/QA_RULES.md`) |
| `dataset_version` | Release version |

## `mcr_geochem_analyses_long`

| Column | Meaning |
|---|---|
| `mcr_uid`, `source_id` | Links to the samples table |
| `analyte` | Harmonized analyte name (SiO2, Fe2O3T, Ni, Pt ...) |
| `value` | Harmonized value; empty when censored |
| `unit` | `wt%`, `ppm`, or `ppb` |
| `censor` | empty (measured), `<` (below detection), `>` (above upper limit) |
| `detection_limit` | Limit in harmonized units for censored values |
| `is_best_value` | One True per sample x analyte |
| `best_value_basis` | `source best value`, `crosswalk rank`, or `derived` |
| `method_id` | `<source>:<method code>`, the key into `method_crosswalk.csv` |
| `method_code_source` | Method code as the source wrote it |
| `technique`, `digestion`, `extent` | From the crosswalk; `extent` is total, near-total, partial, semi-quantitative, or unknown |
| `derived` | True for calculated values (Fe2O3T from Fe2O3 + FeO) |
| `analyte_source`, `unit_source`, `value_source` | Exactly what the source file says |
| `harmonize_rule` | The conversion applied |
| `qa_flags` | Determination-level flags |

## `mcr_geochem_wide.csv`

Sample metadata plus one column per analyte named `<analyte>_<unit>` (`SiO2_wt`, `Ni_ppm`, `Pt_ppb` ...), holding best values. Negative = below detection (see Conventions). Determination flags are not in this table; use the long table when censoring or methods matter.

## `method_crosswalk.csv`

| Column | Meaning |
|---|---|
| `method_id` | `<source>:<code>` |
| `technique` | Plain technique (e.g. "XRF, wavelength dispersive (WDXRF)", "Fire assay (NiS), INAA finish") |
| `digestion` | How the sample was dissolved or prepared (USGS AGDB4 dictionary where available) |
| `extent` | total, near-total, partial, semi-quantitative, unknown |
| `quantitative` | quantitative / semi-quantitative / unknown |
| `n_determinations`, `n_samples`, `analytes` | Use of the code in v1.0 |
| `description`, `reference` | Method description and the publication that defines it |

## `detection_limits.csv`

| Column | Meaning |
|---|---|
| `source_id`, `method_code_source`, `analyte`, `unit` | Key |
| `n_determinations`, `n_censored`, `pct_censored`, `n_above_upper` | Counts in v1.0 |
| `dl_min_observed`, `dl_max_observed`, `n_distinct_dl` | Detection limits actually reported with censored values, harmonized units |
| `documented_lld_source_units` | Documented lower limit of determination range, source units (USGS AGDB4 or Woodruff 2019) |
| `usgs_bestvalue_rank` | USGS best-value rank of the method for that species (lower is preferred; A/P = total/partial) |
| `technique`, `extent` | From the crosswalk |

## `excluded_samples.csv`

Every sample read from a source but not kept, with `exclusion_reason` (outside the three states, non-rift unit or age named in the source, not on a rift map unit, or no chemistry values).
