"""Streamlit UI. Run with: streamlit run app.py

Streamlit reruns this whole file top to bottom every time you touch a
widget. That's the entire mental model. No routes, no state management,
no frontend. @st.cache_data stops it from re-reading a 130 MB CSV on
every click.
"""

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from cx.loader import load_trend
from cx.points import LBNL_SDAHU
from cx.rules import run_all

DATA_DIR = Path("data")

st.set_page_config(page_title="AHU Trend Check", layout="wide")
st.title("AHU Trend Check")
st.caption("Rule-based fault detection on BAS trend exports. Prototype.")


@st.cache_data
def load(path: str, resample: str):
    return load_trend(path, LBNL_SDAHU, resample=resample or None)


files = sorted(DATA_DIR.glob("*.csv"))
if not files:
    st.warning("No CSVs in ./data. Run `python scripts/make_sample.py data/sample.csv` or add LBNL files.")
    st.stop()

col_a, col_b = st.columns([3, 1])
choice = col_a.selectbox("Trend file", files, format_func=lambda p: p.name)
resample = col_b.selectbox("Resample", ["15min", "5min", ""], format_func=lambda r: r or "raw (1 min)")

df = load(str(choice), resample)
findings = run_all(df)

st.subheader(f"Findings ({len(findings)})")
if findings.empty:
    st.success("No faults flagged by the active rules.")
else:
    st.dataframe(findings, use_container_width=True, hide_index=True)

st.subheader("Trend")
window = df
if not findings.empty:
    pick = st.selectbox(
        "Zoom to finding",
        findings.index,
        format_func=lambda i: f"{findings.loc[i, 'rule']}  {findings.loc[i, 'start']}",
    )
    pad = (findings.loc[pick, "end"] - findings.loc[pick, "start"]) * 2
    window = df.loc[findings.loc[pick, "start"] - pad : findings.loc[pick, "end"] + pad]

fig = go.Figure()
for key, label in [("oat", "OAT"), ("rat", "RAT"), ("mat", "MAT"), ("sat", "SAT")]:
    fig.add_trace(go.Scatter(x=window.index, y=window[key], name=label, mode="lines"))
for _, f in findings.iterrows():
    fig.add_vrect(x0=f["start"], x1=f["end"], fillcolor="red", opacity=0.12, line_width=0)
fig.update_layout(yaxis_title="Temperature (F)", height=450, margin=dict(t=10))
st.plotly_chart(fig, use_container_width=True)
