# Decisions and verification record: MCR-GeoChem v1.0.0

*Plain-language note: the judgment calls behind v1.0, who made them, and when the package was checked.*

## Setup decisions (2026-10-19, Bezali Kwame Danso)

| Question | Decision |
|---|---|
| Which rocks go in? | All rift rocks, labeled: intrusions, lavas, and rift sediments (rift_igneous / rift_sedimentary / post_rift_sedimentary) |
| Dataset license | Whole table CC BY-SA 4.0 (required by GEOROC and EarthChem share-alike); code MIT; docs CC BY 4.0 |
| State survey data | v1.0 = USGS + GEOROC + EarthChem; state survey tables in v1.1 (docs/STATE_SOURCES.md) |
| Author block | Bezali Kwame Danso (ORCID 0009-0006-1201-4129), Independent Researcher, East Lansing, Michigan, USA; co-author Saadatu Abdullah, Independent Researcher, Athens, Georgia, US |

## Verification decisions (2026-10-19, recommended options accepted by the author)

| ID | Question | Decision |
|---|---|---|
| V1 | Which SGMC map units count as rift | As listed in docs/mcr_units.csv: Wolf River, Wausau, Stettin plutons and MN "unknown age" mafic intrusions excluded; Jacobsville and Bayfield kept as post_rift_sedimentary |
| V2 | Keep samples matched only by the map | Keep, labeled `mcr_match = map` |
| V3 | Alteration thresholds | LOI > 3 wt%, CIA > 60, Ishikawa AI outside 20-65 |
| V4 | Cross-source duplicates | Keep all, flagged with `duplicate_group` |

## Author correction (2026-10-19, Bezali Kwame Danso)

- USGS Duluth sample `MCRG-S2-1002826`: the source file reports Pd = 123,000 ppb with Pt = 123 ppb (Pd/Pt about 1,000). The author judged this a transcription error and normalized Pd to **123 ppb**. The original source value (123000) stays in `value_source`, the row carries the flag `AUTHOR_CORRECTED`, and the correction is listed in `docs/corrections.csv`. The USGS data contact (Heather L. Parks, doi:10.5066/P13UFQYF) should be asked to confirm: four other NorthMet west-pit samples in the same release also have Pd far above Pt (e.g. 1002841: Pd 10,200 ppb, Pt <5 ppb), so the published value may be genuine. Revert by deleting the row in docs/corrections.csv and rebuilding.

## Verification

On 2026-10-19 the author reviewed the draft package and approved release. The pipeline reproduced identical headline numbers and identical samples, wide, and crosswalk tables from a fresh download in a clean folder on the same day.
