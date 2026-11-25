"""Refresh compact observations from clean pinned checkouts. Use Python with NumPy and Node 24."""
import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFD = "d428d076fad18b486947deb341bcf51773ecc24f"
COUNCIL = "6eb6dc4d645a772aaacdbbaf197e1b09c4be8be6"

def head(repo, pin):
    sha = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
    if sha != pin or subprocess.check_output(["git", "-C", repo, "diff", "HEAD", "--name-only"]):
        raise ValueError(f"Expected clean tracked files at {pin} in {repo}")
    return sha

def extract(cfd, council):
    cfd_sha, council_sha = head(cfd, CFD), head(council, COUNCIL)
    sys.path.insert(0, str(cfd / "tools"))
    import numpy as np
    from cfdvv.compare import compare_case
    from cfdvv.gci import compute_gci
    case = cfd / "tools/cfdvv/cases/verification/incompressible/poiseuille-2d"
    files = [cfd / f"tools/tests/integration_data/gci-{level}.csv" for level in ("coarse","medium","fine")]
    q = compute_gci(str(case), list(map(str, files)), [0.05, 0.025, 0.0125])["quantity_results"][0]
    # Confirm the independent refinement continues the same sampled analytical curve.
    spacings = []
    for file in files:
        y, u, v = np.loadtxt(file, delimiter=",", skiprows=1).T
        np.testing.assert_allclose(u, y * (1 - y) / 2, rtol=0, atol=1e-14)
        np.testing.assert_allclose(np.diff(y), y[1]-y[0], rtol=0, atol=1e-14)
        np.testing.assert_allclose([y[0],y[-1]], [0,1])
        np.testing.assert_array_equal(v, 0)
        spacings.append(float(y[1] - y[0]))
    np.testing.assert_allclose(spacings, [0.2,0.1,0.05])
    with tempfile.TemporaryDirectory() as tmp:
        y = np.linspace(0, 1, 41)
        path = Path(tmp) / "extra-fine.csv"
        np.savetxt(path, np.column_stack((y, y*(1-y)/2, y*0)), delimiter=",", header="y,u,v", comments="")
        field = next(f for f in compare_case(str(case), str(path))["field_results"] if f["field"] == "u")
        # Load a temporary sibling module so it calls the original comparison pipeline.
        source = (cfd / "tools/cfdvv/gci.py").read_text(encoding="utf8")
        old = "f_extrap = f1 + (f1 - f2) / (r21**p - 1)"
        if source.count(old) != 1:
            raise ValueError("Pinned extrapolation expression differs")
        patched = Path(tmp) / "repaired_gci.py"
        patched.write_text(source.replace(old, "f_extrap = f3 + (f3 - f2) / (r32**p - 1)"), encoding="utf8")
        spec = importlib.util.spec_from_file_location("cfdvv.repaired_gci", patched)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        repaired = module.compute_gci(str(case), list(map(str, files)), [0.05, 0.025, 0.0125])
    hearings = json.loads(subprocess.check_output(["node", HERE/"verify-hearings.mjs", council], encoding="utf8"))
    return {"cfd_commit":cfd_sha, "council_commit":council_sha, "profile_dy":spacings+[0.025],
            "mesh_labels":[0.05,0.025,0.0125], "recorded":q, "fourth_L2":field["norm_value"],
            "reference_points":field["n_points"], "repair_limit":repaired["quantity_results"][0]["extrapolated_value"],
            "hearings":hearings}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cfd",type=Path)
    parser.add_argument("council",type=Path)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    data=extract(args.cfd.resolve(),args.council.resolve())
    if args.out:
        args.out.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    else:
        frozen=json.loads((HERE/"observations.json").read_text(encoding="utf8"))
        import math
        for name in ("f1","f2","f3","order_p","extrapolated_value","gci21"):
            if not math.isclose(data["recorded"][name],frozen["recorded"][name],rel_tol=1e-12,abs_tol=1e-15):
                raise ValueError(name)
        if not math.isclose(data["fourth_L2"],frozen["fourth_L2"],rel_tol=1e-12):
            raise ValueError("fourth level differs")
        if not math.isclose(data["repair_limit"],frozen["repair_limit"],rel_tol=1e-10,abs_tol=1e-14):
            raise ValueError("one-line repair differs")
        for key in data.keys() - {"recorded","fourth_L2","repair_limit"}:
            if data[key]!=frozen[key]: raise ValueError(key)
        print("Pinned observations and both recorded hearings verified.")
