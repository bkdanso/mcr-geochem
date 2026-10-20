# Changelog

## v1.0.1 (2026-10-20)
- Co-author review: the USGS Duluth Pd value of 123,000 ppb (sample MCRG-S2-1002826) is restored as published and flagged SOURCE_VALUE_SUSPECT instead of being normalized to 123 ppb. New column `author_note` in the long table; new flag SOURCE_VALUE_SUSPECT in mcrqa.
- Preprint revisions from co-author review (abstract, figure order, interpretation of alteration flags, author contributions).

## v1.0.0 (2026-10-19)
- First compilation: USGS NGDB 1962-2023, USGS Duluth Complex (2025), USGS Woodruff (2019), GEOROC CFB-Keweenawan and Minerals, EarthChem 1501. Earth MRI v12 screened (no rift samples in MI/MN/WI).
- Method crosswalk and detection-limit table (see stats.json for counts).
- mcrqa 1.0.0 QA checker with 14 tests.
