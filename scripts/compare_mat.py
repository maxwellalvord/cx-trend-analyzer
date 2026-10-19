from cx.loader import load_trend
from cx.points import LBNL_SDAHU

for name in ["AHU_annual", "oa_bias_4_annual"]:
    df = load_trend(f"data/{name}.csv", LBNL_SDAHU)
    running = df[df["sf_status"] > 0.5]
    print(f"\n{name}  (MAT while fan on, by month)")
    print(running["mat"].groupby(running.index.month).agg(["min", "median", "max"]).round(1))