# Your verification checklist: MCR-GeoChem v1.0.1

*Plain-language version: before anything goes public under your name, you check it. Tick each box and add the date. Total time: about 1.5 to 2 hours. The publish gate checks the mechanical items automatically; these are yours.*

## Part 1: Make sure the results can be rebuilt (15 to 30 min)

Pick one:
- [ ] **Option A, run it yourself.** In a terminal in the project folder, paste: `pip install -r requirements.txt` then `./run_all.sh`. At the end you should see `14 passed`, and `data/processed/qa_report.txt` should say `Total kept: 3,524 samples, 168,748 determinations`.
- [ ] **Option B, ask Claude.** In a new chat with Opus 5.5 or Fable 5, upload the project zip and say: "Re-run this pipeline from scratch with run_all.sh and give me the headline numbers." Compare: 3,524 samples; 168,748 determinations; 1,695 MN / 1,057 MI / 772 WI. They should match, unless a source has published a newer version (then note it).
- [ ] Every number in README.md, LIMITATIONS.md, and TALK_TRACK.md matches `data/processed/stats.json` (they are generated from it; spot-check two).

## Part 2: Check the sources (15 min)

- [ ] Each link in the README Sources table opens and is free to access.
- [ ] USGS NGDB: https://doi.org/10.5066/P1FXE9GK shows publication date January 2026. Licenses: S1, S2, S3, S7, SGMC, AGDB4 public domain; S4, S5, S6 CC BY-SA 4.0 (so the dataset is CC BY-SA 4.0, as you chose).
- [ ] GEOROC: https://doi.org/10.25625/WSTPOX lists the file `2026-09-WSTPOX_MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN.csv`. If a newer file exists, tell Claude; v1.0 can be rebuilt on it.

## Part 3: Check values by hand (30 to 45 min)

For each line: find the value in our file, then open the source and confirm the source number. Our value may be converted (for example Si 22.3% becomes SiO2 47.71 wt%, ppm becomes ppb x 1,000); the line tells you what the source shows.

**Named spot checks** (easy cases, hard cases, and extremes; one or more per source). Our file: `data/processed/mcr_geochem_analyses_long.csv`, filter `mcr_uid` and `analyte`, take the row with `is_best_value = True`.

- [ ] `MCRG-S1-W210634` Pt = 4600 ppb. Source shows **4.6 ppm** (method ES_SQ). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27W210634%27&outFields=*&f=html  _(highest detected Pt in the USGS NGDB set (extreme))_ ___
- [ ] `MCRG-S1-W210634` Pd = <1000 ppb. Source shows **-1.0 ppm** (method ES_SQ). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27W210634%27&outFields=*&f=html  _(highest detected Pt in the USGS NGDB set (extreme))_ ___
- [ ] `MCRG-S1-W210634` Cu = 24 ppm. Source shows **24.0 ppm** (method EDX). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27W210634%27&outFields=*&f=html  _(highest detected Pt in the USGS NGDB set (extreme))_ ___
- [ ] `MCRG-S1-W210634` Ni = 30 ppm. Source shows **30.0 ppm** (method AA_F_HF). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27W210634%27&outFields=*&f=html  _(highest detected Pt in the USGS NGDB set (extreme))_ ___
- [ ] `MCRG-S1-C100666` SiO2 = 47.71 wt%. Source shows **22.3 pct** (method WDX_Fuse). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27C100666%27&outFields=*&f=html  _(Portage Lake basalt majors (Si as element converted to SiO2))_ ___
- [ ] `MCRG-S1-C100666` MgO = 7.346 wt%. Source shows **4.43 pct** (method WDX_Fuse). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27C100666%27&outFields=*&f=html  _(Portage Lake basalt majors (Si as element converted to SiO2))_ ___
- [ ] `MCRG-S1-C100666` Fe2O3T = 11.8 wt%. Source shows **8.25 pct** (method WDX_Fuse). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27C100666%27&outFields=*&f=html  _(Portage Lake basalt majors (Si as element converted to SiO2))_ ___
- [ ] `MCRG-S1-W175024` Cu = 1.25e+05 ppm. Source shows **125000.0 ppm** (method AA_F_HF). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27W175024%27&outFields=*&f=html  _(Nonesuch Shale copper (rift sediment, White Pine host))_ ___
- [ ] `MCRG-S1-AHK811` Pt = <3e+04 ppb. Source shows **-30.0 ppm** (method ES_SQ). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27AHK811%27&outFields=*&f=html  _(legacy below-detection Pt with a very high limit (hard case))_ ___
- [ ] `MCRG-S1-AHK811` Au = <20 ppb. Source shows **-0.02 ppm** (method AA_F_HBr). Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27AHK811%27&outFields=*&f=html  _(legacy below-detection Pt with a very high limit (hard case))_ ___
- [ ] `MCRG-S2-1002826` Pd = 1.23e+05 ppb. Source shows **123000.0 ppb** (method C_FA_TRACE_AU-PD-PT). Check at: https://doi.org/10.5066/P13UFQYF (file MCR_USGS_geochem_BV.csv, column Field_ID)  _(USGS Duluth drill core, highest Pd; Pd/Pt = 1000, unusually high: confirm the source has no typo)_ ___
- [ ] `MCRG-S2-1002826` Pt = 123 ppb. Source shows **123.0 ppb** (method C_FA_TRACE_AU-PD-PT). Check at: https://doi.org/10.5066/P13UFQYF (file MCR_USGS_geochem_BV.csv, column Field_ID)  _(USGS Duluth drill core, highest Pd; Pd/Pt = 1000, unusually high: confirm the source has no typo)_ ___
- [ ] `MCRG-S2-1002826` Cu = 5.54e+04 ppm. Source shows **55400.0 ppm** (method C_ICPOES_MS-60). Check at: https://doi.org/10.5066/P13UFQYF (file MCR_USGS_geochem_BV.csv, column Field_ID)  _(USGS Duluth drill core, highest Pd; Pd/Pt = 1000, unusually high: confirm the source has no typo)_ ___
- [ ] `MCRG-S4-104473` SiO2 = 67.5 wt%. Source shows **67.5 wt%** (method not reported (GEOROC precompiled file)). Check at: https://doi.org/10.25625/WSTPOX (file ...MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN.csv, column UNIQUE_ID)  _(GEOROC North Shore Volcanic Group)_ ___
- [ ] `MCRG-S4-104473` TiO2 = 0.95 wt%. Source shows **0.95 wt%** (method not reported (GEOROC precompiled file)). Check at: https://doi.org/10.25625/WSTPOX (file ...MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN.csv, column UNIQUE_ID)  _(GEOROC North Shore Volcanic Group)_ ___
- [ ] `MCRG-S4-104473` Zr = 600 ppm. Source shows **600.0 ppm** (method not reported (GEOROC precompiled file)). Check at: https://doi.org/10.25625/WSTPOX (file ...MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN.csv, column UNIQUE_ID)  _(GEOROC North Shore Volcanic Group)_ ___
- [ ] `MCRG-S6-9550` SiO2 = 46.21 wt%. Source shows **46.21 WT%** (method ECL1501-1:XRF). Check at: https://ecl.earthchem.org/view.php?id=1501 (sheet '3 Data')  _(EarthChem Portage Lake sample 9550)_ ___
- [ ] `MCRG-S6-9550` Fe2O3T = 12.81 wt%. Source shows **12.81 WT%** (method ECL1501-1:XRF). Check at: https://ecl.earthchem.org/view.php?id=1501 (sheet '3 Data')  _(EarthChem Portage Lake sample 9550)_ ___
- [ ] `MCRG-S6-9550` Ni = 235.1 ppm. Source shows **235.1 PPM** (method ECL1501-1:ICP:MS-LA). Check at: https://ecl.earthchem.org/view.php?id=1501 (sheet '3 Data')  _(EarthChem Portage Lake sample 9550)_ ___
- [ ] `MCRG-S7-C-392223` Cu = 141 ppm. Source shows **141.0 ppm** (method ICPAES_MS). Check at: https://doi.org/10.5066/P9VO251H (file Bedrock.csv, column Lab No.)  _(Woodruff (2019) troctolite FR-3)_ ___
- [ ] `MCRG-S7-C-392223` Ni = 296 ppm. Source shows **296.0 ppm** (method ICPAES_MS). Check at: https://doi.org/10.5066/P9VO251H (file Bedrock.csv, column Lab No.)  _(Woodruff (2019) troctolite FR-3)_ ___
- [ ] `MCRG-S7-C-392223` Al2O3 = 17.04 wt%. Source shows **9.02 wt%** (method ICPAES_MS). Check at: https://doi.org/10.5066/P9VO251H (file Bedrock.csv, column Lab No.)  _(Woodruff (2019) troctolite FR-3)_ ___
- [ ] `MCRG-S5-OLIVINES-2150` MgO = 30.4 wt%. Source shows **30.4 wt%** (method not reported (GEOROC precompiled file)). Check at: https://doi.org/10.25625/SGFTFN (mineral file named in 'project'; data/raw/georoc/georoc_minerals_mcr_region.csv)  _(GEOROC olivine grain (mineral chemistry))_ ___
- [ ] `MCRG-S5-OLIVINES-2150` SiO2 = 36.83 wt%. Source shows **36.83 wt%** (method not reported (GEOROC precompiled file)). Check at: https://doi.org/10.25625/SGFTFN (mineral file named in 'project'; data/raw/georoc/georoc_minerals_mcr_region.csv)  _(GEOROC olivine grain (mineral chemistry))_ ___

**Five random values** (chosen by computer, seed 2027):

- [ ] `MCRG-S1-C119007` MgO = 0.4975 wt%. Source shows **0.3 pct**. Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27C119007%27&outFields=*&f=html ___
- [ ] `MCRG-S1-EBN170` Zr = 100 ppm. Source shows **100.0 ppm**. Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27EBN170%27&outFields=*&f=html ___
- [ ] `MCRG-S1-EBT735` Cr = 50 ppm. Source shows **50.0 ppm**. Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27EBT735%27&outFields=*&f=html ___
- [ ] `MCRG-S1-W180652` Ni = 100 ppm. Source shows **100.0 ppm**. Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27W180652%27&outFields=*&f=html ___
- [ ] `MCRG-S1-D207450` Zr = 440 ppm. Source shows **440.0 ppm**. Check at: https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27D207450%27&outFields=*&f=html ___

**Excluded samples** (5 min):
- [ ] Open `data/processed/excluded_samples.csv`, filter `source_id = S1`, scan 20 rows. Each reason should make sense (for example "non-rift unit named in source: michigamme"). Note any rift rock wrongly excluded. ___

## Part 4: Your decisions (10 min)

The build made these choices provisionally. Agree or change each one.

- [ ] **V1. Which map units count as rift rock?** See `docs/mcr_units.csv` (77 units). Excluded: Wolf River batholith, Wausau and Stettin plutons (about 1.47 to 1.56 billion years, older than the rift), and the Minnesota unit "mafic intrusions of unknown age". Jacobsville Sandstone and Bayfield Group are kept, labeled post_rift_sedimentary. Option A (recommended): keep as is. Option B: drop post-rift sediments (removes 34 samples). Your choice: ___
- [ ] **V2. Should samples matched only by the map be kept?** 443 samples sit on a rift map unit with no unit name in the source. Option A (recommended): keep them, labeled mcr_match = map so users can drop them. Option B: drop them from v1.0. Your choice: ___
- [ ] **V3. Alteration thresholds.** LOI above 3 wt%, CIA above 60, Ishikawa index outside 20 to 65. Result: 488 of 2,821 igneous samples flagged. Option A (recommended): keep. Option B: stricter LOI 2 wt% (more flagged). Option C: looser LOI 4 wt% (fewer flagged). Your choice: ___
- [ ] **V4. Cross-source duplicates.** 239 samples in 110 groups. Option A (recommended): keep all, flagged with duplicate_group. Option B: keep only the newest source in each group. Your choice: ___

## Part 5: Before it goes public (15 to 30 min)

- [ ] The README "In plain terms" paragraph and the Zenodo description are rewritten in your own words. Claude can do this with you line by line.
- [ ] Your name, ORCID, affiliation, and email are correct in `AUTHORS.json` (ORCID is still blank: send it to Claude).
- [ ] You have read `docs/LIMITATIONS.md` and agree with it.
- [ ] Claude has re-run with `--final` (draft stamps removed) and the publish gate passes: `python tools/publish_gate.py . --allow-draft-in tools/ data/raw/ code/05_figures.py code/07_docs.py` (those two scripts contain the stamp text itself).
- [ ] Evidence-log row written on release day.

**When every box is ticked, tell Claude in your own words that you have checked the package and approve publishing.**
