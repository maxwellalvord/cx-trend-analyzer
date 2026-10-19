import pandas as pd

from cx.rules import cooling_valve_leak, find_episodes, mat_out_of_range


def make_df(minutes: int, **overrides) -> pd.DataFrame:
    """A healthy AHU: fan on, MAT between OAT and RAT, coil off, SAT a hair above MAT."""
    idx = pd.date_range("2024-07-01 08:00", periods=minutes, freq="1min")
    base = {
        "oat": 80.0,
        "rat": 74.0,
        "mat": 76.0,
        "sat": 77.0,  # fan heat: SAT runs slightly ABOVE MAT with the coil off
        "sf_status": 1.0,
        "clg_vlv_cmd": 0.0,
    }
    base.update(overrides)
    return pd.DataFrame(base, index=idx)


# --- find_episodes ----------------------------------------------------------

def test_episode_shorter_than_min_is_ignored():
    idx = pd.date_range("2024-01-01", periods=10, freq="1min")
    cond = pd.Series([False, True, True, True, False, False, False, False, False, False], index=idx)
    assert find_episodes(cond, min_minutes=5) == []


def test_two_separate_episodes_are_counted_separately():
    idx = pd.date_range("2024-01-01", periods=20, freq="1min")
    cond = pd.Series([True] * 8 + [False] * 4 + [True] * 8, index=idx)
    assert len(find_episodes(cond, min_minutes=5)) == 2


# --- MAT out of range (worked example) --------------------------------------

def test_mat_healthy_unit_has_no_findings():
    assert mat_out_of_range(make_df(120)) == []


def test_mat_colder_than_both_oat_and_rat_is_flagged():
    assert len(mat_out_of_range(make_df(120, mat=65.0))) == 1


def test_mat_fault_ignored_when_fan_off():
    assert mat_out_of_range(make_df(120, mat=65.0, sf_status=0.0)) == []


# --- Cooling valve leak (Max writes the rule to make these pass) ------------

def test_leak_healthy_unit_has_no_findings():
    assert cooling_valve_leak(make_df(180)) == []


def test_leak_flagged_when_sat_well_below_mat_with_valve_closed():
    assert len(cooling_valve_leak(make_df(180, sat=70.0))) == 1


def test_leak_not_flagged_when_valve_is_actually_open():
    # Coil is supposed to be cooling here. Cold SAT is correct behavior.
    assert cooling_valve_leak(make_df(180, sat=55.0, clg_vlv_cmd=0.6)) == []


def test_leak_ignored_when_fan_off():
    assert cooling_valve_leak(make_df(180, sat=70.0, sf_status=0.0)) == []
