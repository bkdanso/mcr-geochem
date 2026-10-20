# Provenance log: MCR-GeoChem v1.0.1

*Plain-language note: this page records exactly where every input file came from, when it was downloaded, and its license. The machine-readable version is `data/raw/provenance_log.csv`. A checksum (SHA-256) is a fingerprint: if a re-downloaded file has the same checksum, it is byte-for-byte identical.*

Build date: 2026-10-20. Pipeline: `code/01_fetch.py` to `code/06_provenance.py`.

## Row counts by source

| Source | Samples read | In MI/MN/WI | Kept (rift) | Measurements kept |
|---|---:|---:|---:|---:|
| S1 USGS NGDB 1962-2023 | 6,496 | 6,496 | 2,237 | 125,952 |
| S2 USGS Duluth Complex (Parks et al. 2025) | 390 | 390 | 331 | 27,267 |
| S3 USGS Earth MRI v12 | 777 | 777 | 0 | 0 |
| S4 GEOROC CFB: MCR-Keweenawan | 1,357 | 718 | 661 | 10,310 |
| S5 GEOROC Minerals (region) | 4,450 | 974 | 204 | 1,091 |
| S6 EarthChem 1501 Portage Lake | 55 | 55 | 55 | 2,255 |
| S7 USGS Woodruff (2019) bedrock | 42 | 42 | 36 | 1,614 |

S3 contributes no samples to v1.0: all of its MI/MN/WI rocks are Archean, Paleoproterozoic, or Paleozoic. It stays in the pipeline so later Earth MRI versions are picked up automatically.

## Files

### G1

**Citation:** Horton, J.D., San Juan, C.A., and Stoeser, D.B., 2017, The State Geologic Map Compilation (SGMC) geodatabase of the conterminous United States: U.S. Geological Survey Data Series 1052, https://doi.org/10.3133/ds1052

**License:** Public domain (USGS)

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| sgmc/sgmc_mesoproterozoic_MI_MN_WI.geojson | 716 | 7,077,125 | 2026-10-19 | `7b45742f768c7ccd` | https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/SB_5888bf4fe4b05ccb964bab9d_USGS_SGMC_feature/FeatureServer/3/query?whe... | 716 features via ArcGIS REST query |

### G2

**Citation:** U.S. Census Bureau, 2023 TIGER/Line Shapefiles: States, https://www2.census.gov/geo/tiger/TIGER2023/STATE/

**License:** Public domain (U.S. Census)

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| census/tl_2023_us_state.zip |  | 9,947,818 | 2026-10-19 | `8ded0ef036e205e2` | https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip |  |

### R1

**Citation:** Granitto, M., Labay, K.A., and Wang, B., 2024, Alaska Geochemical Database Version 4.0 (AGDB4) including best value data compilations for rock, sediment, soil, mineral, and concentrate sample media: U.S. Geological Survey data release, https://doi.org/10.5066/P14THGQH

**License:** Public domain (USGS)

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| agdb4/AnalyticMethod.txt | 119 | 18,460 | 2026-10-19 | `7dbe775e3ff5f248` | https://www.sciencebase.gov/catalog/file/get/6500b2bed34ed30c2057f99b?f=__disk__1b%2F2b%2F78%2F1b2b78f88db90a823b173e0708511be7c8373504 | extracted from AGDB4_text.zip (AnalyticMethod.txt) |
| agdb4/AnalyticMethod_Biblio.txt | 510 | 243,337 | 2026-10-19 | `503ff89a35f064e6` | https://www.sciencebase.gov/catalog/file/get/6500b2bed34ed30c2057f99b?f=__disk__1b%2F2b%2F78%2F1b2b78f88db90a823b173e0708511be7c8373504 | extracted from AGDB4_text.zip (AnalyticMethod_Biblio.txt) |
| agdb4/DataDictionary.txt | 481 | 80,378 | 2026-10-19 | `10e7e89559de6e3d` | https://www.sciencebase.gov/catalog/file/get/6500b2bed34ed30c2057f99b?f=__disk__1b%2F2b%2F78%2F1b2b78f88db90a823b173e0708511be7c8373504 | extracted from AGDB4_text.zip (DataDictionary.txt) |
| agdb4/Parameter.txt | 1,415 | 204,792 | 2026-10-19 | `5de9cf02f08fa66f` | https://www.sciencebase.gov/catalog/file/get/6500b2bed34ed30c2057f99b?f=__disk__1b%2F2b%2F78%2F1b2b78f88db90a823b173e0708511be7c8373504 | extracted from AGDB4_text.zip (Parameter.txt) |
| agdb4/Parameter_Rank.txt | 1,415 | 109,653 | 2026-10-19 | `27a8d56df2624cb4` | https://www.sciencebase.gov/catalog/file/get/6500b2bed34ed30c2057f99b?f=__disk__1b%2F2b%2F78%2F1b2b78f88db90a823b173e0708511be7c8373504 | extracted from AGDB4_text.zip (Parameter_Rank.txt) |

### S1

**Citation:** Granitto, M., Goldman, M.A., Labay, K.A., San Juan, C.A., Azain, J.S., and Rozinek, T.R., 2026, Geochemical data for rock, sediment, soil, and mineral samples, United States and territories, 1962 to 2023: U.S. Geological Survey data release, https://doi.org/10.5066/P1FXE9GK

**License:** Public domain (USGS)

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| ngdb/geochem_metadata.xml |  | 146,919 | 2026-10-19 | `f219bfe4dd164237` | https://www.sciencebase.gov/catalog/file/get/63a107a0d34e0de3a1f2795f?f=__disk__07%2F80%2F07%2F0780071539c805206db060e6b944eb8614741ec7 | FGDC metadata of the release |
| ngdb/ngdb_geologic_material_MI_MN_WI.json | 0 | 228 | 2026-10-19 | `71434e3e5534899b` | https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/4/query?where=state IN ('MI','MN','WI') | Layer 4 Geochem_geologic_material; same release as doi:10.5066/P1FXE9GK. ScienceBase bulk files require login, so the public USGS feature service (found via https://alaska.usgs.gov/science/geology/geochem_portal/) was used. |
| ngdb/ngdb_mineral_MI_MN_WI.json | 12 | 77,737 | 2026-10-19 | `0d2a8e805a07ed05` | https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/3/query?where=state IN ('MI','MN','WI') | Layer 3 Geochem_mineral; same release as doi:10.5066/P1FXE9GK. ScienceBase bulk files require login, so the public USGS feature service (found via https://alaska.usgs.gov/science/geology/geochem_portal/) was used. |
| ngdb/ngdb_rock_MI_MN_WI.json | 6,484 | 41,634,152 | 2026-10-19 | `c610c4eff6299408` | https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=state IN ('MI','MN','WI') | Layer 1 Geochem_rock; same release as doi:10.5066/P1FXE9GK. ScienceBase bulk files require login, so the public USGS feature service (found via https://alaska.usgs.gov/science/geology/geochem_portal/) was used. |

### S2

**Citation:** Parks, H.L., Zientek, M.L., Peterson, D.M., Hoffmann, N., Larson, P., and Mauk, J.L., 2025, Geochemistry of drill core and hand samples from the Duluth Complex, Minnesota: U.S. Geological Survey data release, https://doi.org/10.5066/P13UFQYF

**License:** Public domain (USGS)

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| usgs_duluth/MCR_USGS_geochem_BV.csv | 390 | 1,561,943 | 2026-10-19 | `1b58c014c80221e4` | https://www.sciencebase.gov/catalog/file/get/675b332fd34e08c81ed96c4c?f=__disk__d8%2Fd8%2F31%2Fd8d831a1eb287570f4d7421d8555adf270a28641 |  |
| usgs_duluth/MCR_USGS_geochem_data_dictionary.csv | 540 | 101,125 | 2026-10-19 | `b494111754c5141c` | https://www.sciencebase.gov/catalog/file/get/675b332fd34e08c81ed96c4c?f=__disk__ff%2F62%2Fd2%2Fff62d2a648a80e2ca805caf88cb8d1bf37aafab9 |  |
| usgs_duluth/MCR_USGS_geochem_locations.zip |  | 8,689 | 2026-10-19 | `39489a8212b3649c` | https://www.sciencebase.gov/catalog/file/get/675b332fd34e08c81ed96c4c?f=__disk__4c%2F99%2F71%2F4c9971f747d51b6894c8c515b28cba8138be69ce |  |
| usgs_duluth/MCR_USGS_geochem_metadata.xml |  | 13,501 | 2026-10-19 | `7a9d60dcf3841745` | https://www.sciencebase.gov/catalog/file/get/675b332fd34e08c81ed96c4c?f=__disk__cb%2F17%2Ff1%2Fcb17f1bd7b4f77b4fde8462669e8ca37256421a6 |  |
| usgs_duluth/MCR_USGS_geochem_methods.csv | 25 | 12,706 | 2026-10-19 | `520b9fe88ccb7c7c` | https://www.sciencebase.gov/catalog/file/get/675b332fd34e08c81ed96c4c?f=__disk__fa%2Faa%2F96%2Ffaaa962ee77a32dce5f4c830c981377be70633e4 |  |
| usgs_duluth/MCR_USGS_geochem_references.csv | 7 | 2,685 | 2026-10-19 | `38ed4a0d09528ad1` | https://www.sciencebase.gov/catalog/file/get/675b332fd34e08c81ed96c4c?f=__disk__8a%2F2e%2Fd3%2F8a2ed3a4d9d42e6533cb742d977c68dd18ede70e |  |

### S3

**Citation:** U.S. Geological Survey, 2021, Geochemical data generated by projects funded by the USGS Earth Mapping Resources Initiative (ver. 12.0, December 2025): U.S. Geological Survey data release, https://doi.org/10.5066/P9WHRLXH

**License:** Public domain (USGS)

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| emri/EMRI_Data.csv | 24,937 | 35,207,279 | 2026-10-19 | `f93d1576870ed51c` | https://www.sciencebase.gov/catalog/file/get/601963c6d34edf5c66f0d0e5?f=__disk__18%2Fc3%2Fe5%2F18c3e59007dbdf02c2acb961e1126bffcc280018 |  |
| emri/EMRI_DataDictionary.csv | 1,120 | 492,088 | 2026-10-19 | `a80f10d916c75ec5` | https://www.sciencebase.gov/catalog/file/get/601963c6d34edf5c66f0d0e5?f=__disk__34%2Fe9%2F0a%2F34e90a79011b4d8703ac6cfb199417f99a66f2aa |  |
| emri/EMRI_Geochem_Metadata_v12.html |  | 294,018 | 2026-10-19 | `34d806c70d859f07` | https://www.sciencebase.gov/catalog/file/get/601963c6d34edf5c66f0d0e5?f=__disk__8e%2F2e%2F73%2F8e2e739d4abc66056a77ea898aa494fa1966cc63 |  |
| emri/EMRI_Geochem_Metadata_v12.xml |  | 956,660 | 2026-10-19 | `beab921b09277a32` | https://www.sciencebase.gov/catalog/file/get/601963c6d34edf5c66f0d0e5?f=__disk__a3%2F51%2F64%2Fa35164e816681f496c5765e79469189546cea5fd |  |
| emri/Limits_AnalyticalMethods.csv | 633 | 27,334 | 2026-10-19 | `384469c762e504ed` | https://www.sciencebase.gov/catalog/file/get/601963c6d34edf5c66f0d0e5?f=__disk__d5%2Fa4%2Fcd%2Fd5a4cd6cc41dccb2a538d8fbd8f37aae082c388e |  |
| emri/QAQC_Values.csv | 112 | 130,867 | 2026-10-19 | `da60382e0427ec2d` | https://www.sciencebase.gov/catalog/file/get/601963c6d34edf5c66f0d0e5?f=__disk__86%2Fa4%2F39%2F86a439251b8e9c46081125b035f99298d84a6c36 |  |
| emri/USGS_Earth MRI Geochemistry Data Revision History.txt |  | 14,752 | 2026-10-19 | `f4151e297a8d0ef2` | https://www.sciencebase.gov/catalog/file/get/601963c6d34edf5c66f0d0e5?f=__disk__50%2F31%2F0f%2F50310f20889d845e29cca0d8dd234538b4bcefbe |  |

### S4

**Citation:** DIGIS Team, 2026, GEOROC Compilation: Continental Flood Basalts, GRO.data, https://doi.org/10.25625/WSTPOX (files generated 2026-09-01)

**License:** CC BY-SA 4.0

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| georoc/2026-09-WSTPOX_MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN.csv | 1,357 | 1,175,190 | 2026-10-19 | `2400ddfecbfa5471` | https://data.goettingen-research-online.de/api/access/datafile/218710 | GRO.data datafile id 218710 |

### S5

**Citation:** DIGIS Team, 2024, GEOROC Compilation: Minerals, GRO.data, https://doi.org/10.25625/SGFTFN

**License:** CC BY-SA 4.0

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| georoc/georoc_minerals_mcr_region.csv | 4,450 | 5,540,621 | 2026-10-19 | `ac20d8ac37466037` | https://doi.org/10.25625/SGFTFN | Region filter of 19 mineral files: lat 41.5-49.5, lon -97.5--82.0, or LOCATION mentions Midcontinent Rift/Keweenaw/Duluth; 4450 rows kept; per-file counts in georoc_minerals_scan_manifest.csv |

### S6

**Citation:** Davis, W.R., Collins, M.A., and Rooney, T.O., 2022, Major and trace element analysis of the Portage Lake volcanics from the Keweenaw Continental Flood Basalt Province, EarthChem Library, https://doi.org/10.26022/IEDA/111501

**License:** CC BY-SA 4.0

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| earthchem/1501-1_ECL_Davis_et_al_Portage_Lake_volcanics.xlsx | 55 | 89,498 | 2026-10-19 | `245ef9692dffa721` | https://ecl.earthchem.org/dl_multi.php | POST id=1501 from landing page https://ecl.earthchem.org/view.php?id=1501 |

### S7

**Citation:** Woodruff, L.G., 2019, Geochemical characterization of solid media from three watersheds that transect the basal contact of the Duluth Complex, northeastern Minnesota: U.S. Geological Survey data release, https://doi.org/10.5066/P9VO251H

**License:** Public domain (USGS)

| File | Rows | Bytes | Accessed | SHA-256 (first 16) | URL | Note |
|---|---:|---:|---|---|---|---|
| usgs_woodruff2019/Analytical_methods_LLD.csv | 66 | 3,097 | 2026-10-19 | `cd05ac2bc637f7a1` | https://www.sciencebase.gov/catalog/file/get/5d2f40f3e4b038fabe24db02?f=__disk__d5%2F94%2F05%2Fd5940504bbda5dbd4fbc331c211a1034fccd350e |  |
| usgs_woodruff2019/Bedrock.csv | 44 | 14,298 | 2026-10-19 | `249299314cb09355` | https://www.sciencebase.gov/catalog/file/get/5d2f40f3e4b038fabe24db02?f=__disk__93%2F76%2F66%2F937666905f68b42aadaa819c84eb28db507c966a |  |
| usgs_woodruff2019/Geochemical_characterization_of_solid_media_from_three_watersheds_that_transect_the_basal_contact_of_the_Duluth_Complex_northeastern_Minnesota_v2.xml |  | 134,057 | 2026-10-19 | `83d0ecac63de78dc` | https://www.sciencebase.gov/catalog/file/get/5d2f40f3e4b038fabe24db02?f=__disk__3b%2F1d%2Fa9%2F3b1da920031d9cd6543fad53eeb80151481ce3e9 |  |

## Access notes

- **USGS NGDB 1962-2023.** Since the November 2025 file update, the ScienceBase bulk files (geodatabase, GeoPackage, Parquet) require a ScienceBase login. The same release is served by the public USGS ArcGIS feature service `Geochem_features` (layers Rock, Mineral, Geologic_material), linked from the USGS Geochemical Data Portal. v1.0 queries that service for `state IN ('MI','MN','WI')`. To re-check against the bulk files, log in at https://www.sciencebase.gov/catalog/item/63a107a0d34e0de3a1f2795f and download the Parquet archive.
- **GEOROC Minerals.** The 19 global mineral files (about 2.4 million rows) are downloaded one at a time, filtered to the study region, and deleted. Per-file counts are in `data/raw/georoc/georoc_minerals_scan_manifest.csv`.
- **AGDB4 method dictionary.** Only the method and parameter tables are kept from the 212 MB archive; they define the same USGS method codes used in the NGDB.
- **State survey releases.** Not in v1.0; see `docs/STATE_SOURCES.md` for the candidate list for v1.1.
