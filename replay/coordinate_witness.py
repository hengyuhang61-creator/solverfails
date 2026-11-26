"""Reproduce a coordinate-identity failure in a pinned cfd-vv-suite checkout.

Requires numpy and the dependencies of cfd-vv-suite. Run:
    python replay/coordinate_witness.py /path/to/cfd-vv-suite
"""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

PINNED = "d428d076fad18b486947deb341bcf51773ecc24f"


def guarded(compare, reference, computed, axes, calculated_axes, *, limit=None):
    """Conservative scope: exact 2-D correspondence or one named line."""
    if axes != calculated_axes:
        return {"status": "UNKNOWN", "reason": "coordinate projection needs an explicit specification"}
    ref_points = {row[:-1] for row in reference}
    res_points = {row[:-1] for row in computed}
    if len(ref_points) != len(reference) or len(res_points) != len(computed):
        return {"status": "FAIL", "reason": "duplicate input coordinates"}
    if len(axes) > 1:
        for index, axis in enumerate(axes):
            a = {row[index] for row in reference}
            b = {row[index] for row in computed}
            if len(a) == len(b) == 1 and a != b:
                return {"status": "FAIL", "reason": f"disjoint station on {axis}"}
    if len(axes) == 1:
        lower = min(row[0] for row in computed)
        upper = max(row[0] for row in computed)
        if any(not lower <= row[0] <= upper for row in reference):
            return {"status": "FAIL", "reason": "computed profile has incomplete support"}
    elif ref_points != res_points:
        return {"status": "UNKNOWN", "reason": "nonidentical clouds need a declared spatial matching rule"}
    result = compare()
    status = "UNKNOWN" if limit is None else ("PASS" if result["norm_value"] <= limit else "FAIL")
    return {"status": status, "score": result["norm_value"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", type=Path)
    args = parser.parse_args()
    suite = args.suite.resolve()
    head = subprocess.check_output(["git", "-C", str(suite), "rev-parse", "HEAD"], text=True).strip()
    diff = subprocess.check_output(["git", "-C", str(suite), "status", "--porcelain", "--untracked-files=no"],
                                   text=True)
    if head != PINNED or diff:
        parser.error(f"expected clean checkout at {PINNED}, found {head}")
    sys.path.insert(0, str(suite / "tools"))
    import numpy as np
    from cfdvv.compare import _match_by_coordinates, compare_field

    reference = [(0, 0, 0), (0, 0.5, 1), (0, 1, 2)]
    cloud = [(0, 0, 1), (0, 1, 2), (1, 0, 3), (1, 1, 4)]
    cases = [
        ("same_station", ("x", "y"), reference, ("x", "y"), reference, "PASS"),
        ("different_station", ("x", "y"), reference, ("x", "y"),
         [(1, y, u) for _, y, u in reference], "FAIL"),
        ("missing_station", ("x", "y"), reference, ("y",),
         [(y, u) for _, y, u in reference], "UNKNOWN"),
        ("different_axes_without_transform", ("x", "y"), reference, ("z", "y"),
         [(1, y, u) for _, y, u in reference], "UNKNOWN"),
        ("outside_support", ("y",), [(0, 1), (0.5, 1), (1, 1)], ("y",),
         [(0.25, 1), (0.75, 1)], "FAIL"),
        ("nearest_many_to_one", ("x", "y"), cloud, ("x", "y"),
         [(0.1, 0.1, 1), (0.2, 0.2, 1)], "UNKNOWN"),
    ]
    outcomes = {}
    with TemporaryDirectory() as directory:
        for name, axes, ref, res_axes, res, expected in cases:
            path = Path(directory) / "result.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                csv.writer(stream).writerows([(*res_axes, "u"), *res])

            def upstream():
                return compare_field(str(path), np.asarray(ref, dtype=float), [*axes, "u"], "u")

            baseline = upstream()
            corrected = guarded(upstream, ref, res, axes, res_axes, limit=0.0)
            assert baseline["norm_value"] == 0.0, name
            assert corrected["status"] == expected, name
            outcomes[name] = {
                "upstream_l2": baseline["norm_value"],
                "reported_pairs": baseline["n_points"],
                "reference_points": len(ref), "guarded": corrected,
            }
    # Direct helper only. compare_field intersects named axes before invoking it.
    m, r = _match_by_coordinates(np.array([[0, 9], [1, 9]]), np.array([[0], [1]]),
                                 np.array([4, 5]), np.array([4, 5]))
    assert np.array_equal(m, r)
    outcomes["internal_positional_truncation_only"] = {"equal_after_truncation": True}
    outcomes["nearest_many_to_one"]["unique_reference_support"] = 1
    print(json.dumps({"suite_commit": head, "cases": outcomes}, indent=2))


if __name__ == "__main__":
    main()
