"""Tests for the mcrqa checker. Run: python -m pytest tests/"""
import math
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcrqa import flag_analyses, flag_samples, load_rules, wide_to_long  # noqa: E402
from mcrqa.units import harmonize, parse_text_value, parse_usgs_qualified  # noqa: E402


# ---------------------------------------------------------------- unit conversion and censoring
def test_element_to_oxide():
    a, u, v, _ = harmonize("Si", "pct", 22.0)
    assert (a, u) == ("SiO2", "wt%") and math.isclose(v, 47.0646, rel_tol=1e-6)


def test_feot_to_fe2o3t():
    a, u, v, _ = harmonize("FEOT", "WT%", 10.0)
    assert a == "Fe2O3T" and math.isclose(v, 11.113, rel_tol=1e-6)


def test_pge_to_ppb():
    assert harmonize("PT", "PPM", 0.05)[:3] == ("Pt", "ppb", 50.0)
    assert harmonize("Au", "ppb", 7)[:3] == ("Au", "ppb", 7.0)


def test_trace_pct_to_ppm():
    assert harmonize("Cu", "pct", 1.5)[:3] == ("Cu", "ppm", 15000.0)


def test_non_chemistry_skipped():
    assert harmonize("DensB", "gcc", 2.9) is None


def test_usgs_qualified():
    assert parse_usgs_qualified(-0.5) == (None, "<", 0.5)
    assert parse_usgs_qualified(10.11111) == (None, ">", 10)
    assert parse_usgs_qualified(111.0) == (111.0, "", None)


@pytest.mark.parametrize("txt,exp", [("<0.5", (None, "<", 0.5)), (">10000", (None, ">", 10000.0)),
                                     ("12.3", (12.3, "", None)), ("bdl", (None, "<", None)),
                                     ("ND", (None, "", None))])
def test_text_values(txt, exp):
    assert parse_text_value(txt) == exp


# ---------------------------------------------------------------- fixture tables
@pytest.fixture
def tables():
    samples = pd.DataFrame([
        # fresh basalt
        dict(mcr_uid="A", sample_type="whole_rock", rock_class="igneous_volcanic", latitude=47.0, longitude=-88.5,
             coord_quality="reported", alteration_source="fresh", field_id="KW-1", source_id="S1"),
        # altered basalt (high LOI, high CIA)
        dict(mcr_uid="B", sample_type="whole_rock", rock_class="igneous_volcanic", latitude=47.1, longitude=-88.4,
             coord_quality="approximate", alteration_source="extensively altered", field_id="KW-2", source_id="S1"),
        # same physical sample as A in another source
        dict(mcr_uid="C", sample_type="whole_rock", rock_class="igneous_volcanic", latitude=47.001, longitude=-88.501,
             coord_quality="reported", alteration_source="", field_id="kw1", source_id="S4"),
        # Si element reported as SiO2 (unit error)
        dict(mcr_uid="D", sample_type="whole_rock", rock_class="igneous_intrusive", latitude=None, longitude=None,
             coord_quality="missing", alteration_source="", field_id="X", source_id="S2"),
    ])
    fresh = dict(SiO2=48.5, TiO2=1.5, Al2O3=15.8, Fe2O3T=12.5, MnO=0.18, MgO=7.5, CaO=10.5, Na2O=2.4, K2O=0.4,
                 P2O5=0.15, LOI=0.6)
    altered = dict(SiO2=44.0, TiO2=1.4, Al2O3=19.0, Fe2O3T=12.0, MnO=0.2, MgO=9.0, CaO=1.5, Na2O=0.3, K2O=3.5,
                   P2O5=0.1, LOI=8.5)
    rows = []
    for uid, comp in [("A", fresh), ("B", altered), ("C", fresh)]:
        for k, v in comp.items():
            rows.append(dict(mcr_uid=uid, analyte=k, value=v, unit="wt%", censor="", detection_limit=None,
                             is_best_value=True, extent="total"))
    rows.append(dict(mcr_uid="D", analyte="SiO2", value=22.5, unit="wt%", censor="", detection_limit=None,
                     is_best_value=True, extent="total"))
    rows += [
        dict(mcr_uid="A", analyte="Pt", value=None, unit="ppb", censor="<", detection_limit=50000.0,
             is_best_value=True, extent="semi-quantitative"),
        dict(mcr_uid="A", analyte="Pd", value=None, unit="ppb", censor="<", detection_limit=2.0,
             is_best_value=True, extent="total"),
        dict(mcr_uid="A", analyte="Cu", value=None, unit="ppm", censor=">", detection_limit=None,
             is_best_value=True, extent="partial"),
        dict(mcr_uid="A", analyte="Ni", value=90000.0, unit="ppm", censor="", detection_limit=None,
             is_best_value=True, extent="total"),
        dict(mcr_uid="A", analyte="MgO", value=130.0, unit="wt%", censor="", detection_limit=None,
             is_best_value=False, extent="total"),
        dict(mcr_uid="C", analyte="Zr", value=120.0, unit="ppm", censor="", detection_limit=None,
             is_best_value=True, extent="unknown"),
    ]
    return samples, pd.DataFrame(rows)


def _flags(df, uid, analyte=None):
    d = df[df.mcr_uid == uid]
    if analyte:
        d = d[d.analyte == analyte]
    return set(";".join(d.qa_flags).split(";")) - {""}


def test_analysis_flags(tables):
    s, l = tables
    out = flag_analyses(l, s, load_rules())
    assert {"BDL", "BDL_UNINFORMATIVE", "SEMI_QUANTITATIVE"} <= _flags(out, "A", "Pt")
    assert _flags(out, "A", "Pd") == {"BDL"}
    assert {"ABOVE_UPPER_LIMIT", "PARTIAL_DIGESTION"} <= _flags(out, "A", "Cu")
    assert "POSSIBLE_UNIT_ERROR" in _flags(out, "A", "Ni")
    assert "IMPLAUSIBLE_VALUE" in _flags(out, "A", "MgO")
    assert "METHOD_NOT_REPORTED" in _flags(out, "C", "Zr")


def test_sample_flags(tables):
    s, l = tables
    la = flag_analyses(l, s)
    out = flag_samples(s, la).set_index("mcr_uid")
    fa = set(out.at["A", "qa_flags"].split(";")) - {""}
    assert not any(f.startswith("ALTERED") for f in fa)
    assert 98 <= out.at["A", "major_oxide_total"] <= 101
    fb = set(out.at["B", "qa_flags"].split(";"))
    assert {"ALTERED_LOI", "ALTERED_CIA", "ALTERED_AI", "ALTERED_SOURCE", "COORD_APPROXIMATE"} <= fb
    assert out.at["B", "altered_likely"]
    assert "POSSIBLE_DUPLICATE" in out.at["A", "qa_flags"] and out.at["A", "duplicate_group"] == out.at["C", "duplicate_group"]
    fd = set(out.at["D", "qa_flags"].split(";"))
    assert {"SI_ELEMENT_SUSPECT", "COORD_MISSING"} <= fd


def test_wide_mode():
    df = pd.DataFrame({"Sample": ["s1", "s2"], "Si_pct": [23.0, 22.0], "Cu_ppm": [-5, 120.11111],
                       "NI(PPM)": ["<10", "85"], "Pt ppb": [3, None], "Notes": ["a", "b"]})
    long, samples, mapping = wide_to_long(df, "Sample")
    assert set(mapping[mapping.recognized].analyte) == {"SiO2", "Cu", "Ni", "Pt"}
    cu = long[(long.mcr_uid == "s1") & (long.analyte == "Cu")].iloc[0]
    assert cu.censor == "<" and cu.detection_limit == 5
    assert long[(long.mcr_uid == "s2") & (long.analyte == "Cu")].iloc[0].censor == ">"
    out = flag_analyses(long, samples)
    assert "BDL" in _flags(out, "s1", "Ni")
