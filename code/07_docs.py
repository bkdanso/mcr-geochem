#!/usr/bin/env python3
"""07_docs.py - fill every number in the documents from stats.json, and write the release metadata.

Plain-language note: no number in the README, limitations, talk track, or checklist is typed by
hand. This script reads data/processed/stats.json and writes those documents, plus CITATION.cff
and the Zenodo metadata files, using the author details in AUTHORS.json. Run it after any rebuild
with `python code/07_docs.py` (add --final after verification to drop the draft status).
"""
import argparse
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
T = os.path.join(ROOT, "docs", "templates")
GH = "https://github.com/{user}/mcr-geochem"


def flat_stats(st, authors, final, doi, gh_user):
    a = authors["authors"][0]
    k = {r["source_id"]: r for r in st["counts_by_source"]}
    cm = st["critical_metals"]
    df = st["determination_flags"]
    sf = st["sample_flags"]
    S = dict(
        version=st["version"], build_date=st["build_date"], n_samples=st["n_samples"],
        n_det=st["n_determinations"], n_best=st["n_best_values"], n_analytes=st["n_analytes"],
        n_methods=st["n_method_codes"], n_excluded=st["n_excluded"],
        n_mi=st["samples_by_state"].get("MI", 0), n_mn=st["samples_by_state"].get("MN", 0),
        n_wi=st["samples_by_state"].get("WI", 0), n_min=st["samples_by_type"].get("mineral_grain", 0),
        n_wr=st["samples_by_type"].get("whole_rock", 0),
        n_ig=st["samples_by_mcr_class"].get("rift_igneous", 0), n_rsed=st["samples_by_mcr_class"].get("rift_sedimentary", 0),
        n_post=st["samples_by_mcr_class"].get("post_rift_sedimentary", 0),
        n_semi=df.get("SEMI_QUANTITATIVE", 0), pct_semi=round(100 * df.get("SEMI_QUANTITATIVE", 0) / st["n_determinations"]),
        n_nomethod=df.get("METHOD_NOT_REPORTED", 0), n_zero=df.get("ZERO_VALUE", 0), n_unit_err=df.get("POSSIBLE_UNIT_ERROR", 0),
        n_bdl=df.get("BDL", 0), n_bdl_unin=df.get("BDL_UNINFORMATIVE", 0),
        n_coord_approx=sf.get("COORD_APPROXIMATE", 0), n_map_only=st["samples_by_mcr_match"].get("map", 0),
        n_dup_samples=st["n_samples_in_duplicate_groups"], n_dup_groups=st["n_duplicate_groups"],
        n_ig_wr=st["n_igneous_wholerock"], n_ig_alt=st["n_igneous_altered_likely"],
        pct_ig_alt=round(100 * st["n_igneous_altered_likely"] / max(st["n_igneous_wholerock"], 1)),
        pct_cens=st["pct_censored_best"],
        pt_n=cm["Pt"]["n"], pt_det=cm["Pt"]["n_detected"], pt_unin=cm["Pt"]["n_bdl_uninformative"],
        pd_n=cm["Pd"]["n"], pd_det=cm["Pd"]["n_detected"],
        author_name=a["name"], author_orcid_md=f" ([ORCID](https://orcid.org/{a['orcid']}))" if a.get("orcid") else "",
        author_list="; ".join(x["name"] + (f" ([ORCID](https://orcid.org/{x['orcid']}))" if x.get("orcid") else "") +
                              f", {x['affiliation']}" for x in authors["authors"]),
        status_line=((f"Released v{st['version']} ({st['build_date']})" if doi else
                      f"v{st['version']}, verified by the authors {st['build_date']}; Zenodo DOI pending") if final else
                     f"DRAFT v{st['version']} (unverified, built {st['build_date']})"),
        doi_line=doi or "pending first Zenodo release",
        fig1="paper/figures/fig1_sample_map.png", gh=GH.format(user=gh_user or "GITHUB-USERNAME"),
    )
    for sid in ("S1", "S2", "S3", "S4", "S5", "S6", "S7"):
        S[f"k_{sid}"] = k.get(sid, {}).get("samples_kept_mcr", 0)
    return S


def render(name, out, S):
    with open(os.path.join(T, name), encoding="utf-8") as f:
        txt = f.read().format(**S)
    with open(out, "w", encoding="utf-8") as f:
        f.write(txt)
    print("wrote", os.path.relpath(out, ROOT))


def checklist(S, final):
    spots = pd.read_csv(os.path.join(P, "spot_checks.csv"))
    long = pd.read_parquet(os.path.join(P, "mcr_geochem_analyses_long.parquet"))
    samples = pd.read_csv(os.path.join(P, "mcr_geochem_samples.csv"), low_memory=False)
    pool = long[long.is_best_value & (long.censor == "") & long.source_id.isin(["S1", "S2", "S6", "S7"]) &
                long.analyte.isin(["SiO2", "MgO", "Ni", "Cu", "Co", "Cr", "Pt", "Pd", "Zr", "Sr"])]
    rnd = pool.sample(5, random_state=2027)
    link = {"S2": "USGS Duluth file MCR_USGS_geochem_BV.csv (data/raw/usgs_duluth/), row with Field_ID = ",
            "S6": "EarthChem file (data/raw/earthchem/), sheet '3 Data', SAMPLE NAME = ",
            "S7": "USGS Woodruff Bedrock.csv (data/raw/usgs_woodruff2019/), Lab No. = "}
    ngdb = "https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Geochem_features/FeatureServer/1/query?where=lab_id%3D%27{}%27&outFields=*&f=html"
    sm = samples.set_index("mcr_uid")

    def where(uid, sid):
        sid_raw = sm.loc[uid, "source_sample_id"]
        return ngdb.format(sid_raw) if sid == "S1" else link.get(sid, "") + str(sid_raw)

    def shown(r):
        return f"<{r.detection_limit:.4g}" if r.censor == "<" else f"{r.value:.4g}"

    L = [f"# Your verification checklist: MCR-GeoChem v{S['version']}", "",
         "*Plain-language version: before anything goes public under your name, you check it. Tick each box and add the date. "
         "Total time: about 1.5 to 2 hours. The publish gate checks the mechanical items automatically; these are yours.*", "",
         "## Part 1: Make sure the results can be rebuilt (15 to 30 min)", "", "Pick one:",
         "- [ ] **Option A, run it yourself.** In a terminal in the project folder, paste: `pip install -r requirements.txt` then `./run_all.sh`. "
         f"At the end you should see `14 passed`, and `data/processed/qa_report.txt` should say `Total kept: {S['n_samples']:,} samples, {S['n_det']:,} determinations`.",
         "- [ ] **Option B, ask Claude.** In a new chat with Opus 5.5 or Fable 5, upload the project zip and say: \"Re-run this pipeline from scratch "
         f"with run_all.sh and give me the headline numbers.\" Compare: {S['n_samples']:,} samples; {S['n_det']:,} determinations; "
         f"{S['n_mn']:,} MN / {S['n_mi']:,} MI / {S['n_wi']:,} WI. They should match, unless a source has published a newer version (then note it).",
         "- [ ] Every number in README.md, LIMITATIONS.md, and TALK_TRACK.md matches `data/processed/stats.json` (they are generated from it; spot-check two).", "",
         "## Part 2: Check the sources (15 min)", "",
         "- [ ] Each link in the README Sources table opens and is free to access.",
         "- [ ] USGS NGDB: https://doi.org/10.5066/P1FXE9GK shows publication date January 2026. Licenses: S1, S2, S3, S7, SGMC, AGDB4 public domain; S4, S5, S6 CC BY-SA 4.0 (so the dataset is CC BY-SA 4.0, as you chose).",
         "- [ ] GEOROC: https://doi.org/10.25625/WSTPOX lists the file `2026-09-WSTPOX_MIDCONTINENT_RIFT_SYSTEM-KEWEENAWAN.csv`. If a newer file exists, tell Claude; v1.0 can be rebuilt on it.", "",
         "## Part 3: Check values by hand (30 to 45 min)", "",
         "For each line: find the value in our file, then open the source and confirm the source number. Our value may be converted "
         "(for example Si 22.3% becomes SiO2 47.71 wt%, ppm becomes ppb x 1,000); the line tells you what the source shows.", "",
         "**Named spot checks** (easy cases, hard cases, and extremes; one or more per source). Our file: `data/processed/mcr_geochem_analyses_long.csv`, filter `mcr_uid` and `analyte`, take the row with `is_best_value = True`.", ""]
    for r in spots.itertuples():
        L.append(f"- [ ] `{r.mcr_uid}` {r.analyte} = {shown(r)} {r.unit}. Source shows **{r.value_source} {r.unit_source}** (method {r.method}). "
                 f"Check at: {r.where_to_check}  _({r.why})_ ___")
    L += ["", "**Five random values** (chosen by computer, seed 2027):", ""]
    for r in rnd.itertuples():
        L.append(f"- [ ] `{r.mcr_uid}` {r.analyte} = {shown(r)} {r.unit}. Source shows **{r.value_source} {r.unit_source}**. "
                 f"Check at: {where(r.mcr_uid, r.source_id)} ___")
    L += ["", "**Excluded samples** (5 min):",
          "- [ ] Open `data/processed/excluded_samples.csv`, filter `source_id = S1`, scan 20 rows. Each reason should make sense "
          "(for example \"non-rift unit named in source: michigamme\"). Note any rift rock wrongly excluded. ___", "",
          "## Part 4: Your decisions (10 min)", "",
          "The build made these choices provisionally. Agree or change each one.", "",
          "- [ ] **V1. Which map units count as rift rock?** See `docs/mcr_units.csv` (77 units). Excluded: Wolf River batholith, Wausau and Stettin plutons (about 1.47 to 1.56 billion years, older than the rift), and the Minnesota unit \"mafic intrusions of unknown age\". "
          "Jacobsville Sandstone and Bayfield Group are kept, labeled post_rift_sedimentary. Option A (recommended): keep as is. Option B: drop post-rift sediments "
          f"(removes {S['n_post']:,} samples). Your choice: ___",
          f"- [ ] **V2. Should samples matched only by the map be kept?** {S['n_map_only']:,} samples sit on a rift map unit with no unit name in the source. "
          "Option A (recommended): keep them, labeled mcr_match = map so users can drop them. Option B: drop them from v1.0. Your choice: ___",
          f"- [ ] **V3. Alteration thresholds.** LOI above 3 wt%, CIA above 60, Ishikawa index outside 20 to 65. Result: {S['n_ig_alt']:,} of {S['n_ig_wr']:,} igneous samples flagged. "
          "Option A (recommended): keep. Option B: stricter LOI 2 wt% (more flagged). Option C: looser LOI 4 wt% (fewer flagged). Your choice: ___",
          f"- [ ] **V4. Cross-source duplicates.** {S['n_dup_samples']:,} samples in {S['n_dup_groups']:,} groups. Option A (recommended): keep all, flagged with duplicate_group. "
          "Option B: keep only the newest source in each group. Your choice: ___", "",
          "## Part 5: Before it goes public (15 to 30 min)", "",
          "- [ ] The README \"In plain terms\" paragraph and the Zenodo description are rewritten in your own words. Claude can do this with you line by line.",
          "- [ ] Your name, ORCID, affiliation, and email are correct in `AUTHORS.json` (ORCID is still blank: send it to Claude).",
          "- [ ] You have read `docs/LIMITATIONS.md` and agree with it.",
          "- [ ] Claude has re-run with `--final` (draft stamps removed) and the publish gate passes: `python tools/publish_gate.py . --allow-draft-in tools/ data/raw/ code/05_figures.py code/07_docs.py` (those two scripts contain the stamp text itself).",
          "- [ ] Evidence-log row written on release day.", "",
          "**When every box is ticked, tell Claude in your own words that you have checked the package and approve publishing.**", ""]
    with open(os.path.join(ROOT, "docs", "VERIFY_CHECKLIST.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("wrote docs/VERIFY_CHECKLIST.md")


def citation(S, authors, doi, gh, final):
    a = authors["authors"][0]
    lines = ["cff-version: 1.2.0", 'message: "If you use this dataset or software, please cite it as below, and cite the original sources listed in docs/PROVENANCE.md."',
             "type: dataset", 'title: "MCR-GeoChem: harmonized whole-rock and mineral geochemistry of the Midcontinent Rift (Michigan, Minnesota, Wisconsin)"',
             f'version: "{S["version"]}"', f'date-released: "{S["build_date"]}"', "authors:"]
    for a in authors["authors"]:
        lines += [f'  - family-names: "{a["family"]}"', f'    given-names: "{a["given"]}"', f'    affiliation: "{a["affiliation"]}"']
        if a.get("email"):
            lines.append(f'    email: "{a["email"]}"')
        if a.get("orcid"):
            lines.append(f'    orcid: "https://orcid.org/{a["orcid"]}"')
    lines += ["license: CC-BY-SA-4.0", f'repository-code: "{gh}"']
    if doi:
        lines.append(f'doi: "{doi}"')
    lines += ["keywords:", '  - "geochemistry"', '  - "Midcontinent Rift"', '  - "Keweenawan"', '  - "Duluth Complex"',
              '  - "critical minerals"', '  - "platinum-group elements"', '  - "nickel"', '  - "copper"', '  - "data harmonization"',
              '  - "quality assurance"']
    with open(os.path.join(ROOT, "CITATION.cff"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote CITATION.cff")


def zenodo_meta(S, authors, gh):
    creators = []
    for a in authors["authors"]:
        c = {"name": f'{a["family"]}, {a["given"]}', "affiliation": a["affiliation"]}
        if a.get("orcid"):
            c["orcid"] = a["orcid"]
        creators.append(c)
    common = dict(creators=creators, version=S["version"], access_right="open", language="eng",
                  related_identifiers=[{"identifier": gh, "relation": "isSupplementTo", "scheme": "url"}])
    os.makedirs(os.path.join(ROOT, "release"), exist_ok=True)
    srcs = ("Sources: USGS NGDB 1962-2023 (doi:10.5066/P1FXE9GK); USGS Duluth Complex (doi:10.5066/P13UFQYF); "
            "USGS Earth MRI v12 (doi:10.5066/P9WHRLXH); GEOROC CFB and Minerals (doi:10.25625/WSTPOX, doi:10.25625/SGFTFN); "
            "EarthChem Library 1501 (doi:10.26022/IEDA/111501); USGS Woodruff 2019 (doi:10.5066/P9VO251H).")
    metas = {
        "zenodo_dataset.json": dict(upload_type="dataset", license="cc-by-sa-4.0",
            title=f"MCR-GeoChem v{S['version']}: harmonized whole-rock and mineral geochemistry of the Midcontinent Rift (Michigan, Minnesota, Wisconsin)",
            description=(f"<p>An open, versioned, quality-flagged compilation of {S['n_samples']:,} samples and {S['n_det']:,} geochemical determinations "
                         f"from 1.1-billion-year-old Midcontinent Rift (Keweenawan) intrusions, lavas, and rift sediments in Michigan ({S['n_mi']:,}), "
                         f"Minnesota ({S['n_mn']:,}), and Wisconsin ({S['n_wi']:,}). Units, censored values, methods, and sample-type labels are harmonized; "
                         "each value keeps its original form. Includes the codebook, provenance log (sources, URLs, access dates, checksums, row counts, licenses), "
                         "QA report, and figures.</p><p>" + srcs + "</p><p>Limitations: docs/LIMITATIONS.md. State survey releases are planned for v1.1.</p>"),
            keywords=["geochemistry", "Midcontinent Rift", "Keweenawan", "Duluth Complex", "critical minerals", "platinum-group elements",
                      "nickel", "copper", "cobalt", "Lake Superior"]),
        "zenodo_crosswalk.json": dict(upload_type="dataset", license="cc-by-sa-4.0",
            title=f"Legacy analytical-method and detection-limit crosswalk for MCR-GeoChem v{S['version']}",
            description=(f"<p>Crosswalk of {S['n_methods']} laboratory method codes used in USGS, GEOROC, and EarthChem geochemistry of the Midcontinent Rift "
                         "to a common vocabulary (technique, digestion, total/near-total/partial/semi-quantitative extent), with method descriptions and "
                         "references, plus a method-by-analyte detection-limit table (observed and documented limits, censoring rates, USGS best-value ranks).</p>"
                         "<p>Companion to the MCR-GeoChem dataset.</p>"),
            keywords=["analytical methods", "detection limits", "geochemistry", "crosswalk", "USGS NGDB", "data harmonization"]),
        "zenodo_software.json": dict(upload_type="software", license="mit",
            title="mcrqa: open geochemistry QA checker (below-detection values, unit errors, altered samples, duplicates)",
            description=("<p>Python package and command-line tool that flags below-detection and uninformative detection limits, above-limit values, "
                         "semi-quantitative and partial-digestion methods, unit errors, oxide-total problems, likely altered igneous samples (LOI, CIA, "
                         "Ishikawa index, source descriptions), coordinate problems, and probable cross-source duplicates, for long-format or wide "
                         "geochemistry tables. Built for MCR-GeoChem; works on any table.</p>"),
            keywords=["geochemistry", "quality assurance", "detection limit", "Python", "data validation"]),
    }
    for fn, m in metas.items():
        m.update(common)
        with open(os.path.join(ROOT, "release", fn), "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2, ensure_ascii=False)
    print("wrote release/zenodo_*.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--doi", default="")
    ap.add_argument("--github-user", default="")
    a = ap.parse_args()
    st = json.load(open(os.path.join(P, "stats.json")))
    authors = json.load(open(os.path.join(ROOT, "AUTHORS.json")))
    S = flat_stats(st, authors, a.final, a.doi, a.github_user)
    render("README.md.tmpl", os.path.join(ROOT, "README.md"), S)
    render("LIMITATIONS.md.tmpl", os.path.join(ROOT, "docs", "LIMITATIONS.md"), S)
    render("TALK_TRACK.md.tmpl", os.path.join(ROOT, "docs", "TALK_TRACK.md"), S)
    checklist(S, a.final)
    citation(S, authors, a.doi, S["gh"], a.final)
    zenodo_meta(S, authors, S["gh"])


if __name__ == "__main__":
    main()
