# Publish guide: MCR-GeoChem v1.0

*Plain-language note: step-by-step instructions to put the project on GitHub and get three DOIs from Zenodo. Verification is done and the final build is in this folder. Total time: about 45 minutes. If you would rather Claude do the uploads, see "Fast path" at the end.*

## What gets published where

| Deliverable | Where | Zenodo upload type | License | File |
|---|---|---|---|---|
| MCR-GeoChem v1.0 dataset (with codebook and provenance log) | Zenodo | Dataset | CC BY-SA 4.0 | `release/MCR-GeoChem_v1.0.0_dataset.zip` + `release/MCR-GeoChem_v1.0.0_raw_inputs_snapshot.zip` |
| Method and detection-limit crosswalk | Zenodo | Dataset | CC BY-SA 4.0 | `release/MCR-GeoChem_v1.0.0_method_detection_limit_crosswalk.zip` |
| QA checker script (mcrqa) | GitHub + Zenodo | Software | MIT | the GitHub release (Zenodo archives it automatically) |

The title, description, and keywords for each Zenodo record are ready to copy from `release/zenodo_dataset.json`, `release/zenodo_crosswalk.json`, and `release/zenodo_software.json`.

## Step 1. GitHub (15 min)

1. Go to https://github.com/new. Repository name: `mcr-geochem`. Description: `Harmonized, QA-flagged geochemistry of the Midcontinent Rift (MI, MN, WI) and the mcrqa checker`. Public. Do **not** add a README (the project has one). Click **Create repository**.
2. The screen shows an empty repository with a web address like `https://github.com/YOURNAME/mcr-geochem.git`.
3. Unzip `MCR-GeoChem_v1.0.0_project.zip`. The `mcr-geochem` folder is already a git repository with the release committed (you do not need to run `git init` or `git commit`).
4. In a terminal inside the `mcr-geochem` folder, paste these two lines:
   ```
   git remote add origin https://github.com/bkdanso/mcr-geochem.git
   git push -u origin main
   ```
   GitHub asks you to sign in in the browser the first time. Refresh the repository page: you should see the README with the sample map and both authors listed.

## Step 2. Connect Zenodo to GitHub (5 min)

1. Log in at https://zenodo.org with ORCID (so your ORCID attaches automatically).
2. Click your name (top right), then **GitHub**. Find `mcr-geochem` in the list and flip the switch **On**.

## Step 3. GitHub release = software DOI (5 min)

1. On the GitHub repository page, click **Releases**, then **Draft a new release**.
2. Tag: `v1.0.0`. Title: `MCR-GeoChem v1.0.0 and mcrqa 1.0.0`. Description: paste the text of `CHANGELOG.md`.
3. Click **Publish release**. Within a few minutes Zenodo shows a new record under **Upload** with a DOI (looks like `10.5281/zenodo.1234567`). Open it, click **Edit**, check both authors are listed (the `CITATION.cff` file supplies them), paste the title and description from `release/zenodo_software.json`, set license MIT, and click **Publish**.
4. Write this DOI down: it is the **QA checker DOI**.

## Step 4. Dataset DOI (10 min)

1. On Zenodo click **New upload**.
2. Drag in `MCR-GeoChem_v1.0.0_dataset.zip` and `MCR-GeoChem_v1.0.0_raw_inputs_snapshot.zip`.
3. Resource type: **Dataset**. Title, description, keywords: copy from `release/zenodo_dataset.json`. Creators, in this order (as in `AUTHORS.json`): **Danso, Bezali Kwame** (ORCID 0009-0006-1201-4129; Independent Researcher, East Lansing, Michigan, USA) and **Abdullah, Saadatu** (Independent Researcher, Athens, Georgia, US). Add Saadatu's ORCID if she has one. Version: `1.0.0`. License: **Creative Commons Attribution Share Alike 4.0 International**.
4. Related works: add the GitHub repository URL ("Is supplemented by") and the QA checker DOI ("Is supplemented by").
5. Click **Publish**. Write down the **dataset DOI**.

## Step 5. Crosswalk DOI (10 min)

Same as Step 4 with `MCR-GeoChem_v1.0.0_method_detection_limit_crosswalk.zip` and the text from `release/zenodo_crosswalk.json`. Under related works add the dataset DOI ("Is supplement to"). **Publish**. Write down the **crosswalk DOI**.

## Step 6. Record it the same day (5 min)

1. Send the three DOIs to Claude. Claude runs `python code/07_docs.py --final --doi <dataset DOI> --github-user bkdanso`, which puts the DOI into the README and CITATION.cff, and gives you the updated files (or pushes them, if you supplied a token).
2. Fill in the three rows of `docs/EVIDENCE_LOG.csv` (date, artifact, Zenodo, DOI, live). Save a PDF of each Zenodo record page. Records that are not logged on the day they go live are the ones that go missing later.

## v1.1 in August 2027

On each Zenodo record, use **New version** (not New upload), so the record keeps one "concept" DOI for all versions and each version gets its own DOI.

## Fast path: let Claude upload

If you prefer, create two tokens and paste them into the chat when Claude asks (a token is a temporary password you can cancel at any time):

- GitHub: https://github.com/settings/tokens, **Generate new token (classic)**, tick **repo**, expiry 7 days.
- Zenodo: https://zenodo.org/account/settings/applications/tokens/new/, tick **deposit:write** and **deposit:actions**.

Claude will first upload to the Zenodo **sandbox** (a practice site with fake DOIs) so you can see the records, then publish for real after you say yes. Revoke both tokens afterward on the same pages.
