"""Canonical point names.

Every BAS names points differently. One site calls supply air temp
"AHU1-SA-T", another calls it "SAT_1". The rules never see raw names.
They only see these canonical keys, and a mapping dict translates a
specific CSV into them.

Today the mapping is hand written. Later this is where an LLM can
*suggest* a mapping that a human confirms.
"""

# canonical key -> human description
POINTS = {
    "sat": "Supply air temperature (F)",
    "sat_sp": "Supply air temperature setpoint (F)",
    "oat": "Outdoor air temperature (F)",
    "mat": "Mixed air temperature (F)",
    "rat": "Return air temperature (F)",
    "sf_status": "Supply fan status (0 off, 1 on)",
    "oa_dmpr_cmd": "Outdoor air damper command (0 to 1)",
    "clg_vlv_cmd": "Cooling valve command (0 to 1)",
    "occupied": "Occupied mode (0 or 1)",
}

# Mapping for the LBNL single-duct AHU dataset (column names from the
# dataset's PDF inventory, Table 2).
#
# Notice what is NOT mapped: CHWC_VLV (valve position) and OA_DMPR
# (damper position). Most real buildings only trend the *command*, not
# a position feedback. If the rules lean on position columns, they work
# great on this simulation and fall over on Caleb's real data.
LBNL_SDAHU = {
    "sat": "SA_TEMP",
    "sat_sp": "SA_TEMPSPT",
    "oat": "OA_TEMP",
    "mat": "MA_TEMP",
    "rat": "RA_TEMP",
    "sf_status": "SF_SPD_DM",
    "oa_dmpr_cmd": "OA_DMPR_DM",
    "clg_vlv_cmd": "CHWC_VLV_DM",
    "occupied": "SYS_CTL",
}
