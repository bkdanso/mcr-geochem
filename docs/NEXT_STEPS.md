# Next steps

*Plain-language note: what comes after v1.0, so v1.0 is read as a first release, not the last word.*

## v1.1 (target August 2027; depends on the provenance log being complete for the new sources)

1. **State survey tables** from `docs/STATE_SOURCES.md`, each with a license note, a scripted extraction, and ten hand-checked rows per report.
2. **GEOROC methods.** Pull per-value methods from the GEOROC 2.0 API, so most "method not reported" values gain a technique.
3. **USGS bulk files.** With a ScienceBase login, compare the feature-service extract with the Parquet release (lab names, analysis dates, per-determination limits). Record any differences.
4. **Mineral chemistry.** Add microprobe data from theses and reports (olivine, plagioclase, pyroxene, sulfides).
5. **Rift unit list review.** Re-check samples matched only by the map; consider 1:24,000-scale maps where they exist.

## Also planned

- Zenodo versioning: each release gets its own DOI under one concept DOI, so citations stay stable.
- The `mcrqa` checker can go to PyPI, and possibly to the Journal of Open Source Software once it has outside users and more tests.
- A short data-descriptor paper (methods, validation, usage notes) once v1.0 has been checked and released.
