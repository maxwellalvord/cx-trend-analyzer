# AHU Trend Check

Rule-based fault detection on air handling unit trend data, the kind of
CSV a building automation system exports during commissioning.

## Status

What works:
- Loads a trend CSV and maps BAS point names to canonical points
- Episode detection (a fault has to persist, not just blip)
- Rule: mixed air temperature out of the OAT/RAT band
- Streamlit view: findings table plus a trend chart zoomed to each finding

Not done yet:
- Cooling valve leak rule (stub, tests written)
- Scoring against LBNL ground truth (detection rate, false positives)
- Point mapping for anything other than the LBNL single-duct AHU dataset

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
mkdir data
python scripts/make_sample.py data/sample.csv   # fake data, for smoke testing only
pytest
streamlit run app.py
```

## Real data

LBNL Fault Detection and Diagnostics Data Sets, single-duct AHU:
https://faultdetection.lbl.gov/dataset/simulated-sd-ahu/

Download the zip (593 MB, requires a short form), unzip, and copy a few
CSVs into `data/`. Start with `AHU_annual.csv` (fault free) and one
faulted file. Do not commit them; `data/` is gitignored.

Cite as: Lawrence Berkeley National Laboratory, LBNL FDD Data Sets.
DOI: https://dx.doi.org/10.25984/1881324
