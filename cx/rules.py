"""Fault rules.

Every rule follows the same shape:
  1. Build a boolean Series: "is the fault condition true at this sample?"
  2. Pass it to find_episodes() so one noisy sample doesn't count.
  3. Return Findings a commissioning engineer can read.

Step 2 is the part people skip. A sensor that blips outside range for
one minute is noise. Outside range for 30 straight minutes is an issue
for the issues log. Persistence is what separates the two.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Finding:
    rule: str
    start: pd.Timestamp
    end: pd.Timestamp
    minutes: float
    message: str


def find_episodes(condition: pd.Series, min_minutes: float) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Return (start, end) for every unbroken run of True lasting >= min_minutes.

    The trick: (condition != condition.shift()).cumsum() gives every
    run of identical values its own group id. Then we keep only the
    groups that are True and long enough.
    """
    condition = condition.fillna(False).astype(bool)
    if condition.empty:
        return []

    run_id = (condition != condition.shift()).cumsum()
    episodes = []
    for _, run in condition.groupby(run_id):
        if not run.iloc[0]:
            continue
        start, end = run.index[0], run.index[-1]
        if (end - start) / pd.Timedelta(minutes=1) >= min_minutes:
            episodes.append((start, end))
    return episodes


def _to_findings(rule: str, episodes, message: str) -> list[Finding]:
    return [
        Finding(rule, s, e, (e - s) / pd.Timedelta(minutes=1), message)
        for s, e in episodes
    ]


# ---------------------------------------------------------------------------
# Rule 1: Mixed air temperature out of range  (worked example)
# ---------------------------------------------------------------------------
# Mixed air is literally outdoor air and return air mixed together. Its
# temperature has to land somewhere between the two. If MAT reads colder
# than both or hotter than both, one of the three sensors is lying.
#
# This is a simplified version of a Guideline 36 AHU fault condition.
# Read the real one before showing this to an engineer.

def mat_out_of_range(df: pd.DataFrame, tolerance_f: float = 2.0, min_minutes: float = 30) -> list[Finding]:
    low = df[["oat", "rat"]].min(axis=1) - tolerance_f
    high = df[["oat", "rat"]].max(axis=1) + tolerance_f

    fan_on = df["sf_status"] > 0.5
    out_of_range = (df["mat"] < low) | (df["mat"] > high)

    episodes = find_episodes(fan_on & out_of_range, min_minutes)
    return _to_findings(
        "MAT out of range",
        episodes,
        f"Mixed air temp outside the OAT/RAT band by more than {tolerance_f}F. "
        "Check MAT, OAT and RAT sensors.",
    )


# ---------------------------------------------------------------------------
# Rule 2: Cooling coil valve leaking  (YOURS TO WRITE)
# ---------------------------------------------------------------------------
# Spec:
#   Flag when the fan is on, the cooling valve is commanded closed, and
#   the supply air is still noticeably colder than the mixed air.
#
# Questions to answer BEFORE you write code:
#   - With the coil off, should SAT equal MAT exactly? (Hint: air goes
#     through a fan that's dumping motor heat into it. Which way does
#     that push SAT?)
#   - What counts as "commanded closed"? Is 0.01 closed?
#   - The LBNL data has a CHWC_VLV *position* column that would make
#     this trivial. Why is using it cheating? (Read the comment in
#     points.py.)
#
# Use mat_out_of_range as your template. tests/test_rules.py has the
# tests this has to pass. Run: pytest

def cooling_valve_leak(df: pd.DataFrame, delta_f: float = 2.0, min_minutes: float = 60) -> list[Finding]:
    """Return Findings when the cooling valve is leaking.

    A leak is defined as:
      - Fan is on
      - Cooling valve is commanded closed (0.0)
      - Supply air is colder than mixed air by delta_f or more
    """
    fan_on = df["sf_status"] > 0.5
    valve_closed = df["clg_vlv_cmd"] < 0.01
    sat_colder_than_mat = df["mat"] - df["sat"] >= delta_f

    episodes = find_episodes(fan_on & valve_closed & sat_colder_than_mat, min_minutes)
    return _to_findings(
        "Cooling valve leak",
        episodes,
        f"Cooling valve commanded closed but SAT colder than MAT by {delta_f}F or more. "
        "Check cooling coil and SAT sensor.",
    )


RULES = [mat_out_of_range, cooling_valve_leak]


def run_all(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rule in RULES:
        try:
            rows.extend(vars(f) for f in rule(df))
        except NotImplementedError:
            continue
    return pd.DataFrame(rows, columns=["rule", "start", "end", "minutes", "message"])
