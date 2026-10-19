# State survey sources: candidates for v1.1

*Plain-language note: the brief calls for state geological survey data. In October 2026 none of the three states had a computer-readable chemistry table for rift rocks. This page lists what was found, so v1.1 can add each source after its tables are extracted and checked by hand. Each one gets a row in the provenance log when it is added.*

| State | Source | What it holds | Format | Status for v1.1 |
|---|---|---|---|---|
| MN | Minnesota DNR, Report 241 (1985-86), Economic Mineralization in the Duluth Complex. https://www.dnr.state.mn.us/lands_minerals/mpes_projects/report241.html | Drill core assays, Duluth Complex Cu-Ni-PGE zones | PDF report and tables | Extract tables; check 10 rows by hand |
| MN | Minnesota DNR mineral potential project reports (index). https://www.dnr.state.mn.us/lands_minerals/mpes_projects/index.html | Many drill core and outcrop analyses; most are Archean, some rift | PDF, some data files | Screen each report for rift samples |
| MN | MGS / DNR Drill Core Library hand-sample inventory (2016). https://files.dnr.state.mn.us/lands_minerals/drilling_data/mgs_hand_samples.zip | 43,545 samples; flags whether whole-rock analysis (WRA) exists. **No chemistry values** | xlsx, shapefile | Use to find samples with WRA = Y and trace their source reports |
| MN | Minnesota Minerals Coordinating Committee GIS data list. https://mcc.mn.gov/gis-data.html | Index of state drilling, assay, and geochemistry files | Links | Index for the above |
| MN | Minnesota Geological Survey publications, University Digital Conservancy. https://conservancy.umn.edu | Reports of Investigation and theses with rift analyses (e.g. RI-58, Duluth Complex geology) | PDF | Extract appendix tables |
| MN | Natural Resources Research Institute (UMN Duluth) technical reports | Duluth Complex stratigraphy and chemistry (e.g. Severson 1994, cited by the USGS 2025 release) | PDF | Check license and extract |
| WI | Wisconsin Geological and Natural History Survey | Mellen Complex, Chengwatana, Powder Mill rocks | Open-file reports (PDF) | Search catalog; confirm terms of use |
| MI | Michigan Geological Survey (Western Michigan University) | Keweenaw, Porcupine Mountains, Copperwood and White Pine areas | Reports, core library records | Search catalog; confirm terms of use |
| all | GEOROC 2.0 API (methods and detection limits for GEOROC values) | Per-value analytical methods | JSON API | Pull methods for the GEOROC values marked "method not reported" in v1.0 |

Rule for v1.1: a state value enters the dataset only after (1) its license or terms are recorded, (2) its table is extracted by script where possible, and (3) ten rows per report are checked by hand against the PDF, with the check logged.
