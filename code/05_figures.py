#!/usr/bin/env python3
"""05_figures.py - draw the release figures from the processed tables.

Plain-language note: makes three PNG charts in paper/figures/: a map of where the samples
are, a chart of how many critical-metal results are measurable versus below detection, and
a chart of how many samples carry each QA flag. Figures carry a draft stamp until you approve them;
then run `python code/05_figures.py --final`.
"""
import argparse
import json
import os

import geopandas as gpd
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "paper", "figures")
# reference palette (dataviz skill), light mode; first three slots validate all-pairs
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
SURF, INK, INK2, GRID, MAPFILL = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#e9e7e1"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})


def stamp(fig, final):
    if not final:
        fig.text(0.99, 0.99, "DRAFT - not verified", ha="right", va="top", fontsize=9, color="#b0302f",
                 weight="bold")


def caption(fig, text):
    fig.text(0.01, 0.01, text, ha="left", va="bottom", fontsize=7.5, color=INK2)


def fig_map(s, st, final):
    states = gpd.read_file("zip://" + os.path.join(ROOT, "data", "raw", "census", "tl_2023_us_state.zip"))
    states = states[states.STUSPS.isin(["MI", "MN", "WI"])].to_crs(4326)
    units = gpd.read_file(os.path.join(ROOT, "data", "raw", "sgmc", "sgmc_mesoproterozoic_MI_MN_WI.geojson"))
    mem = pd.read_csv(os.path.join(ROOT, "docs", "mcr_units.csv"))
    units = units.merge(mem[["state", "sgmc_label", "mcr_class"]], left_on=["STATE", "SGMC_LABEL"],
                        right_on=["state", "sgmc_label"])
    units = units[units.mcr_class != "excluded"]
    fig, ax = plt.subplots(figsize=(8, 5.6))
    states.plot(ax=ax, color=SURF, edgecolor="#cfcdc6", linewidth=0.6)
    units.plot(ax=ax, color=MAPFILL, edgecolor="#d6d4cd", linewidth=0.2)
    groups = [("USGS (NGDB, Duluth, Woodruff)", s.source_id.isin(["S1", "S2", "S7"]), S1),
              ("GEOROC (rocks + minerals)", s.source_id.isin(["S4", "S5"]), S2),
              ("EarthChem (Portage Lake)", s.source_id.eq("S6"), S3)]
    for name, m, c in groups:
        d = s[m]
        ax.scatter(d.longitude, d.latitude, s=12, color=c, edgecolor=SURF, linewidth=0.5,
                   label=f"{name}  n={m.sum():,}", zorder=3)
    ax.set_xlim(-96.0, -83.5)
    ax.set_ylim(44.0, 49.3)
    ax.set_aspect(1 / 0.69)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(loc="lower left", frameon=False, fontsize=8.5, labelcolor=INK)
    ax.set_title(f"MCR-GeoChem v{st['version']}: {st['n_samples']:,} Midcontinent Rift samples",
                 loc="left", color=INK, fontsize=12, pad=18)
    ax.text(0.0, 1.0, "Shaded: USGS State Geologic Map Compilation rift units used for membership",
            transform=ax.transAxes, fontsize=8, color=INK2, va="bottom")
    caption(fig, "Sources: USGS NGDB 1962-2023 (doi:10.5066/P1FXE9GK); GEOROC (doi:10.25625/WSTPOX, 10.25625/SGFTFN); "
                 "EarthChem (doi:10.26022/IEDA/111501); SGMC (doi:10.3133/ds1052).")
    stamp(fig, final)
    fig.savefig(os.path.join(FIG, "fig1_sample_map.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_censoring(st, final):
    cm = st["critical_metals"]
    order = ["Ni", "Cu", "Co", "Pt", "Pd", "Au"]
    det = [cm[a]["n_detected"] for a in order]
    bdl = [cm[a]["n_bdl"] - cm[a]["n_bdl_uninformative"] for a in order]
    unin = [cm[a]["n_bdl_uninformative"] for a in order]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    y = range(len(order))[::-1]
    gap = 0  # segments separated by white edges (2px surface gap)
    ax.barh(y, det, color=S1, height=0.6, edgecolor=SURF, linewidth=1.5, label="Measured")
    ax.barh(y, bdl, left=det, color=S2, height=0.6, edgecolor=SURF, linewidth=1.5,
            label="Below detection, useful limit")
    ax.barh(y, unin, left=[a + b for a, b in zip(det, bdl)], color=S3, height=0.6, edgecolor=SURF,
            linewidth=1.5, label="Below detection, limit too high to be useful")
    for yi, a, d in zip(y, order, det):
        tot = cm[a]["n"]
        ax.text(tot + 30, yi, f"{100 * d / tot:.0f}% measured", va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{a} ({cm[a]['unit']})" for a in order], color=INK)
    ax.set_xlabel("Samples with a best value")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.set_xlim(0, max(cm[a]["n"] for a in order) * 1.18)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=3, frameon=False, fontsize=8.2)
    ax.set_title("Critical-metal results: measured vs. below detection", loc="left", color=INK, fontsize=12)
    caption(fig, "'Limit too high': detection limit above the mcrqa threshold (e.g. >10 ppb for Pt, Pd, Au), "
                 "mostly legacy emission spectrography.")
    fig.subplots_adjust(bottom=0.32)
    stamp(fig, final)
    fig.savefig(os.path.join(FIG, "fig2_critical_metals_censoring.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_flags(st, final):
    f = pd.Series(st["sample_flags"]).sort_values()
    labels = {"COORD_APPROXIMATE": "Approximate coordinates", "ALTERED_AI": "Altered: Ishikawa index",
              "MAJOR_TOTAL_LOW": "Oxide total low", "POSSIBLE_DUPLICATE": "Possible duplicate",
              "ALTERED_LOI": "Altered: high LOI", "MAJOR_TOTAL_HIGH": "Oxide total high",
              "ALTERED_SOURCE": "Altered: per source", "ALTERED_CIA": "Altered: CIA",
              "SI_ELEMENT_SUSPECT": "Si/SiO2 unit suspect", "COORD_MISSING": "Missing coordinates",
              "COORD_STATE_MISMATCH": "State mismatch"}
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.barh([labels.get(k, k) for k in f.index], f.values, color=S1, height=0.6)
    for i, v in enumerate(f.values):
        ax.text(v + 8, i, f"{v:,}", va="center", fontsize=8.5, color=INK2)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel(f"Samples flagged (of {st['n_samples']:,})")
    ax.set_title("Sample-level QA flags from the mcrqa checker", loc="left", color=INK, fontsize=12)
    stamp(fig, final)
    fig.savefig(os.path.join(FIG, "fig3_sample_qa_flags.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true", help="remove the DRAFT stamp (after verification)")
    a = ap.parse_args()
    os.makedirs(FIG, exist_ok=True)
    st = json.load(open(os.path.join(P, "stats.json")))
    s = pd.read_csv(os.path.join(P, "mcr_geochem_samples.csv"), low_memory=False)
    fig_map(s, st, a.final)
    fig_censoring(st, a.final)
    fig_flags(st, a.final)
    print("figures written to paper/figures/")


if __name__ == "__main__":
    main()
