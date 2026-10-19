"""Generate a small fake trend CSV with LBNL-style column names.

Use this to run the app before you download the real 593 MB dataset.
It is fake. Never present results from it as real.

Usage: python scripts/make_sample.py data/sample.csv
"""

import sys

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
idx = pd.date_range("2024-07-01", periods=3 * 24 * 60, freq="1min")  # 3 days
hour = idx.hour + idx.minute / 60

occupied = ((hour >= 6) & (hour < 22)).astype(float)
oat = 70 + 12 * np.sin((hour - 9) / 24 * 2 * np.pi) + rng.normal(0, 0.3, len(idx))
rat = 74 + rng.normal(0, 0.3, len(idx))
oa_frac = 0.1
mat = oa_frac * oat + (1 - oa_frac) * rat
clg = np.where(occupied > 0, 0.5, 0.0)
sat = np.where(clg > 0, 55.0, mat + 1.0) + rng.normal(0, 0.2, len(idx))

df = pd.DataFrame(
    {
        "Datetime": idx,
        "SA_TEMP": sat,
        "SA_TEMPSPT": 55.0,
        "OA_TEMP": oat,
        "MA_TEMP": mat,
        "RA_TEMP": rat,
        "SF_SPD_DM": occupied,
        "OA_DMPR_DM": np.where(occupied > 0, oa_frac, 0.0),
        "CHWC_VLV_DM": clg,
        "SYS_CTL": occupied,
    }
)

# Plant one fault: MAT sensor reads 10F low for 2 hours on day 2.
bad = (idx >= "2024-07-02 13:00") & (idx < "2024-07-02 15:00")
df.loc[bad, "MA_TEMP"] -= 10

out = sys.argv[1] if len(sys.argv) > 1 else "data/sample.csv"
df.to_csv(out, index=False)
print(f"wrote {len(df)} rows to {out} (planted MAT fault 2024-07-02 13:00-15:00)")
