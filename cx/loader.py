"""Load a trend CSV into a time-indexed DataFrame with canonical columns."""

from __future__ import annotations

import pandas as pd

TIME_HINTS = ("time", "date")


def _find_time_column(columns: list[str]) -> str:
    """Pick the timestamp column.

    I have NOT seen the real LBNL CSV header yet (the zip is behind a
    download form). So this guesses: first column whose name contains
    "time" or "date", otherwise the first column. Check this the first
    time you load a real file.
    """
    for col in columns:
        if any(hint in col.lower() for hint in TIME_HINTS):
            return col
    return columns[0]


def load_trend(source, mapping: dict[str, str], resample: str | None = None) -> pd.DataFrame:
    """Read a CSV and return only the mapped points, renamed to canonical keys.

    source:   path or file-like object
    mapping:  canonical key -> column name in this CSV
    resample: optional pandas offset like "5min". The LBNL files are
              1-minute data for a full year (~525k rows each), which is
              more than a chart needs.
    """
    header = pd.read_csv(source, nrows=0).columns.tolist()
    if hasattr(source, "seek"):
        source.seek(0)

    time_col = _find_time_column(header)

    missing = [col for col in mapping.values() if col not in header]
    if missing:
        raise KeyError(f"Mapped columns not in CSV: {missing}")

    # usecols keeps memory sane: we skip ~20 columns we never look at.
    df = pd.read_csv(source, usecols=[time_col, *mapping.values()])
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.set_index(time_col).sort_index()
    df.index.name = "timestamp"

    df = df.rename(columns={raw: key for key, raw in mapping.items()})

    if resample:
        df = df.resample(resample).mean()

    return df
