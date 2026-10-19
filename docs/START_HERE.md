# Start Here: MCR-GeoChem

*Read this first. It explains your project in plain language. Words in bold are explained in [GLOSSARY.md](GLOSSARY.md).*

## What you are building

One free, carefully checked table of rock and mineral chemistry for the 1.1-billion-year-old **Midcontinent Rift** rocks of Michigan, Minnesota, and Wisconsin, plus a small program that flags questionable values.

## Why it matters

Companies and government scientists are looking for nickel, copper, cobalt, and **platinum-group elements** around Lake Superior. All of these are on the 2025 U.S. critical minerals list. The chemistry they need already exists, but it is scattered across several databases that use different units, different lab methods, and different ways of writing "too small to measure." Today, anyone who wants one clean table has to rebuild it by hand.

Your project does that work once, documents every step, and publishes the result so anyone can download it, cite it, and trust where each number came from.

Think of it like merging three family address books that each write phone numbers differently: you end up with one book, every entry in the same format, and a note saying which book each entry came from.

## Where the information comes from

All sources are free and public.

| Source | In plain terms | What one row looks like | License |
|---|---|---|---|
| USGS **National Geochemical Database**, 1962 to 2023 release (doi:10.5066/P1FXE9GK, published January 2026) | The federal government's archive of rock analyses since 1962 | One rock sample: location, rock type, and up to ~80 element values, each with its lab method | U.S. public domain |
| USGS Duluth Complex drill core release (doi:10.5066/P13UFQYF, 2025) | Recent USGS analyses of Duluth Complex drill core, from the Midcontinent Rift critical minerals project | One drill core interval with its chemistry | U.S. public domain |
| USGS Earth MRI geochemistry (doi:10.5066/P9WHRLXH, version 12, December 2025) | Chemistry from the federal critical minerals mapping program, filtered to the three states | One sample with its chemistry and detection limits | U.S. public domain |
| **GEOROC** "Midcontinent Rift System - Keweenawan" file (Continental Flood Basalts compilation, generated 2026-09-01) plus GEOROC mineral files | A German university's database of published rock and mineral analyses | One sample or one mineral grain, with the paper it came from | CC BY-SA 4.0 (share-alike) |
| EarthChem Library: Portage Lake Volcanics (doi:10.26022/IEDA/111501) | A published set of Keweenaw lava analyses | One lava sample | CC BY-SA 4.0 |
| State survey releases (Minnesota DNR / Minnesota Geological Survey, Wisconsin and Michigan surveys), **planned for v1.1** | State reports with rock analyses | Varies; most are tables inside PDF reports | Varies, logged per file |

## What you will have at the end

- [ ] **MCR-GeoChem v1.0 dataset**: one table, consistent units, every value labeled with its source, method, and detection limit, on Zenodo with a **DOI**
- [ ] **Method and detection-limit crosswalk**: a lookup table translating every lab method code into one vocabulary, with its own DOI
- [ ] **QA checker script**: a free program that flags below-detection values, unit errors, and altered samples, on GitHub and Zenodo with a DOI
- [ ] **Codebook and provenance log**: what every column means, and where every file came from (URL, date, row count, license)
- [ ] A plan for v1.1 (adds state survey tables once the provenance log is complete)

## How it connects to your work

It gives the USGS Midcontinent Rift and Earth MRI efforts, state surveys, universities, and explorers a shared, open, quality-flagged starting point for critical mineral studies in the Lake Superior region. That table does not exist today.

## What you need to do

| Your task | When | Time |
|---|---|---|
| Create accounts (ORCID, GitHub, Zenodo) | Now | 15 min |
| Answer four setup questions | Done | |
| Check the results using the checklist | When the draft is ready | 1.5 to 2 hours |
| Approve publishing | After checking | 5 min |
| Click "Publish" on Zenodo, using the guide (if I cannot push for you) | After checking | 20 min |

Everything else is built for you.

## The steps ahead

1. **Data collected.** Download each source and record exactly where it came from.
2. **Data combined.** Convert everything to the same units and column names in one table.
3. **Crosswalk built.** Translate every lab method and detection limit into one vocabulary.
4. **Quality checks.** Run the QA checker; count and flag anything questionable.
5. **First figures.** Maps and charts of what is in the table.
6. **Ready for your check.** You verify; then we publish.

*You are here: verified; ready to publish (see docs/PUBLISH_GUIDE.md).*
