"""Test a mass-flow acceptance rule against native transverse momentum data."""
import csv
import json
from math import isclose, isfinite
from pathlib import Path

HEIGHT = 0.016
DX = 0.002
TIME_STEP = 1e-7
VISCOSITY = 0.001
SHEAR = 2000.0
EXPECTED_MASS_FLOW = 1.0 * 700.0 * HEIGHT
OMISSION_RATE = -VISCOSITY * SHEAR / (DX / 2)
RATE_TOLERANCE = abs(OMISSION_RATE) * 0.01
CASES = ("pressure", "supersonic", "uniform")


def replay(path):
    with path.open(encoding="ascii", newline="") as handle:
        points = {case: [] for case in CASES}
        for row in csv.DictReader(handle):
            values = tuple(float(row[name]) for name in ("y_m", "rho_u", "rho_v_initial", "rho_v_final"))
            if not all(isfinite(value) for value in values):
                raise ValueError("nonfinite native data")
            points[row["case"]].append(values)
    results = {}
    for case, rows in points.items():
        if len(rows) != 17 or any(not isclose(row[0], index * HEIGHT / 16, abs_tol=1e-14)
                                  for index, row in enumerate(rows)):
            raise ValueError(f"{case}: wrong outlet sample coordinates")
        mass_flow = HEIGHT / 16 * sum((a[1] + b[1]) / 2 for a, b in zip(rows, rows[1:]))
        rates = [(row[3] - row[2]) / TIME_STEP for row in rows[4:13]]
        maximum = max(map(abs, rates))
        mass_passes = isclose(mass_flow, EXPECTED_MASS_FLOW, rel_tol=1e-6)
        momentum_passes = maximum <= RATE_TOLERANCE
        results[case] = {
            "mass_flow_kg_s_per_m_span": mass_flow,
            "mass_only_accepts": mass_passes,
            "central_nodes": len(rates),
            "min_transverse_rate_kg_m2_s2": min(rates),
            "max_transverse_rate_kg_m2_s2": max(rates),
            "mass_and_local_balance_accept": mass_passes and momentum_passes,
        }
    return {
        "case": "SU2 8.6.0 manufactured planar shear",
        "expected_mass_flow_kg_s_per_m_span": EXPECTED_MASS_FLOW,
        "analytic_missing_traction_rate_kg_m2_s2": OMISSION_RATE,
        "local_rate_tolerance_kg_m2_s2": RATE_TOLERANCE,
        "results": results,
    }


if __name__ == "__main__":
    record = replay(Path(__file__).with_name("outlet-traction.csv"))
    cases = record["results"]
    print(json.dumps(record, indent=2))
    omitted = cases["pressure"]
    matches_omission = all(abs(omitted[key] - OMISSION_RATE) <= RATE_TOLERANCE for key in (
        "min_transverse_rate_kg_m2_s2", "max_transverse_rate_kg_m2_s2"))
    if not (all(case["mass_only_accepts"] for case in cases.values())
            and not omitted["mass_and_local_balance_accept"] and matches_omission
            and all(cases[case]["mass_and_local_balance_accept"] for case in ("supersonic", "uniform"))):
        raise SystemExit("Expected one mass-only false acceptance and two corrected passes")
