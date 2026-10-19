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


PAPER = {"on": False}


def title(ax, text, **kw):
    if not PAPER["on"]:
        ax.set_title(text, **kw)


def out(name):
    return os.path.join(FIG, ("paper_" if PAPER["on"] else "") + name)


def stamp(fig, final):
    if not final:
        fig.text(0.99, 0.99, "DRAFT - not verified", ha="right", va="top", fontsize=9, color="#b0302f",
                 weight="bold")


def caption(fig, text):
    if PAPER["on"]:
        return
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
    title(ax, f"MCR-GeoChem v{st['version']}: {st['n_samples']:,} Midcontinent Rift samples",
                 loc="left", color=INK, fontsize=12, pad=18)
    if not PAPER["on"]:
        ax.text(0.0, 1.0, "Shaded: USGS State Geologic Map Compilation rift units used for membership",
                transform=ax.transAxes, fontsize=8, color=INK2, va="bottom")
    caption(fig, "Sources: USGS NGDB 1962-2023 (doi:10.5066/P1FXE9GK); GEOROC (doi:10.25625/WSTPOX, 10.25625/SGFTFN); "
                 "EarthChem (doi:10.26022/IEDA/111501); SGMC (doi:10.3133/ds1052).")
    stamp(fig, final)
    fig.savefig(out("fig1_sample_map.png"), dpi=200, bbox_inches="tight")
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
    title(ax, "Critical-metal results: measured vs. below detection", loc="left", color=INK, fontsize=12)
    caption(fig, "'Limit too high': detection limit above the mcrqa threshold (e.g. >10 ppb for Pt, Pd, Au), "
                 "mostly legacy emission spectrography.")
    fig.subplots_adjust(bottom=0.32)
    stamp(fig, final)
    fig.savefig(out("fig2_critical_metals_censoring.png"), dpi=200, bbox_inches="tight")
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
    title(ax, "Sample-level QA flags from the mcrqa checker", loc="left", color=INK, fontsize=12)
    stamp(fig, final)
    fig.savefig(out("fig3_sample_qa_flags.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_methods(final):
    c = pd.read_csv(os.path.join(P, "method_crosswalk.csv"))
    c["family"] = c.technique.str.split(r"[,(]").str[0].str.strip().replace(
        {"Not reported in source file": "Not reported (GEOROC)", "Calculated": "Calculated"})
    g = c.groupby("family").n_determinations.sum().sort_values()
    g = g[g >= 500]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh(g.index, g.values, color=S1, height=0.6)
    for i, v in enumerate(g.values):
        ax.text(v + 400, i, f"{v:,}", va="center", fontsize=8.5, color=INK2)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel("Determinations in MCR-GeoChem v1.0")
    title(ax, "Analytical technique families after crosswalk harmonization", loc="left", color=INK, fontsize=12)
    fig.subplots_adjust(bottom=0.2)
    caption(fig, "Families with at least 500 determinations; full code-level mapping in method_crosswalk.csv.")
    stamp(fig, final)
    fig.savefig(out("fig4_technique_families.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_tas(s, final):
    l = pd.read_parquet(os.path.join(P, "mcr_geochem_analyses_long.parquet"))
    b = l[l.is_best_value & l.value.notna() & l.analyte.isin(["SiO2", "Na2O", "K2O"])]
    w = b.pivot_table(index="mcr_uid", columns="analyte", values="value", aggfunc="first").dropna()
    m = s.set_index("mcr_uid")
    w = w.join(m[["rock_class", "altered_likely", "sample_type"]], how="inner")
    w = w[(w.sample_type == "whole_rock") & w.rock_class.str.startswith("igneous_")]
    w["alk"] = w.Na2O + w.K2O
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    for rc, col, lab in [("igneous_volcanic", S1, "Volcanic"), ("igneous_intrusive", S2, "Intrusive")]:
        d = w[w.rock_class == rc]
        fresh, alt = d[~d.altered_likely.astype(bool)], d[d.altered_likely.astype(bool)]
        ax.scatter(fresh.SiO2, fresh.alk, s=10, color=col, edgecolor=SURF, linewidth=0.3,
                   label=f"{lab}, not flagged (n={len(fresh):,})", zorder=3)
        ax.scatter(alt.SiO2, alt.alk, s=12, facecolor="none", edgecolor=col, linewidth=0.7,
                   label=f"{lab}, flagged altered (n={len(alt):,})", zorder=2)
    ax.set_xlim(35, 80)
    ax.set_ylim(0, 14)
    ax.set_xlabel("SiO$_2$ (wt%)")
    ax.set_ylabel("Na$_2$O + K$_2$O (wt%)")
    ax.grid(color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    title(ax, "Total alkali vs. silica, rift igneous whole rocks (best values)", loc="left", color=INK, fontsize=11.5)
    caption(fig, "Open symbols: mcrqa ALTERED_* flag (LOI > 3 wt%, CIA > 60, or Ishikawa AI outside 20-65, or source description).")
    stamp(fig, final)
    fig.savefig(out("fig5_tas_alteration.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    return len(w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true", help="remove the DRAFT stamp (after verification)")
    ap.add_argument("--paper", action="store_true", help="also write untitled versions for the preprint")
    a = ap.parse_args()
    os.makedirs(FIG, exist_ok=True)
    st = json.load(open(os.path.join(P, "stats.json")))
    s = pd.read_csv(os.path.join(P, "mcr_geochem_samples.csv"), low_memory=False)
    fig_map(s, st, a.final)
    fig_censoring(st, a.final)
    fig_flags(st, a.final)
    fig_methods(a.final)
    fig_tas(s, a.final)
    if a.paper:
        PAPER["on"] = True
        fig_map(s, st, a.final); fig_censoring(st, a.final); fig_flags(st, a.final)
        fig_methods(a.final); fig_tas(s, a.final)
        PAPER["on"] = False
    print("figures written to paper/figures/")


if __name__ == "__main__":
    main()
