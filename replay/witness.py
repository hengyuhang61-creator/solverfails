"""Replay the two scoped claims, evaluate controls, and export auditable decisions (stdlib)."""
import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "skills/survey-denominator/scripts"))
from survey_bounds import identified_range

OBS = json.loads((HERE / "observations.json").read_text(encoding="utf8"))
PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"

def verdict(value):
    return PASS if value else FAIL

def finite_model(q):
    """Ratio of differences on three geometrically refined levels, coarse first."""
    d1, d2 = q[0] - q[1], q[1] - q[2]
    if not d2 or d1 / d2 <= 1 or math.isclose(d1 / d2, 1, rel_tol=1e-12):
        return None
    return d1 / d2

def grid_case(q, h, candidate, limit, tol, name, origin, split, reported_order=None):
    ratio = finite_model(q)
    order = reported_order
    if order is None and ratio is not None:
        order = math.log(ratio) / math.log(h[0]/h[1])
    old = verdict(order is not None and 1.5 < order < 2.5)
    witness = None
    equal = all(math.isclose(a/b, h[0]/h[1]) for a,b in zip(h,h[1:]))
    if len(q)==4 and len(h)==4 and equal and ratio is not None:
        last, prev = q[2]-q[3], q[1]-q[2]
        if 0 < last / prev < 1:
            witness = q[3] + (q[3]-q[2]) / (ratio-1)
    new = UNKNOWN if witness is None else verdict(abs(candidate-witness) <= tol)
    truth = UNKNOWN if limit is None else verdict(abs(candidate-limit) <= tol)
    return dict(case="grid",name=name,origin=origin,split=split,baseline=old,revised=new,truth=truth,
                h=h,q=q,order=order,candidate=candidate,witness_limit=witness,analytic_limit=limit,tolerance=tol)

def grid_rows(tol):
    real = OBS["recorded"]
    q = [real[k] for k in ("f1","f2","f3")] + [OBS["fourth_L2"]]
    h = OBS["profile_dy"]
    fine = q[2]+(q[2]-q[1])/(finite_model(q)-1)
    for label, value in (("released",real["extrapolated_value"]),("fine-pair repair",fine)):
        yield grid_case(q,h,value,0,tol,label,"upstream fixture","observed",real["order_p"])
    for family, p in [("single",1),("single",2),("single",1.5),("single",2.5),("mixed",2)]:
        split = "development" if family=="single" and p in (1,2) else "holdout"
        for limit, amp, factor, start in product((0,1),(-1,1,1e-5),(2,3),(1,0.1)):
            h=[start / factor**i for i in range(4)]
            q=[limit + amp*(x**p + (x**(p+1) if family=="mixed" else 0)) for x in h]
            ratio=finite_model(q)
            for impl, value in (("coarse",q[0]+(q[0]-q[1])/(ratio-1)),
                                ("fine",q[2]+(q[2]-q[1])/(ratio-1))):
                name=f"{family}/p={p}/limit={limit}/a={amp}/r={factor}/h={start}/{impl}"
                yield grid_case(q,h,value,limit,tol,name,"manufactured",split)
    # Exactly representable geometric differences give a zero independent estimate.
    h=[1,0.5,0.25,0.125]
    q=[x*x for x in h]
    for name,value in (("inclusive tolerance",tol),("outside tolerance",math.nextafter(tol,math.inf))):
        yield grid_case(q,h,value,0,tol,name,"manufactured","boundary")
    yield grid_case(q[:3],h[:3],0,0,tol,"missing fourth level","manufactured","boundary")
    yield grid_case([1]*4,h,1,1,tol,"constant field","manufactured","boundary")
    # A different algorithm, added after the main matrix. Preserve its failures.
    for amplitude in (0, 1):
        values = []
        panels = [4, 8, 16, 32]
        for count in panels:
            samples = [math.exp(j/count) + amplitude*math.cos(64*math.pi*j/count)
                       for j in range(count+1)]
            values.append((sum(samples[1:-1]) + (samples[0]+samples[-1])/2)/count)
        ratio = finite_model(values)
        for first, second, label in [(0, 1, "coarse"), (2, 1, "fine")]:
            candidate = values[first] + (values[first]-values[second])/(ratio-1)
            yield grid_case(values,[1/n for n in panels],candidate,math.expm1(1),tol,
                            f"trapezoid/cosine={amplitude}/{label}","quadrature","post hoc")

def survey_rule(cited, target, fraction, claim, n=None, total=None):
    if not cited:
        return FAIL
    if target not in ("respondents","population") or claim is None:
        return UNKNOWN
    lo, hi = identified_range(target, fraction, n, total)
    return verdict(claim[0] <= lo and hi <= claim[1])

def survey_row(name, origin, split, target, fraction, claim, truth, cited=True, n=None, total=None):
    return dict(case="survey",name=name,origin=origin,split=split,target=target,rate=str(fraction),
                claim=[str(x) for x in claim] if claim else None,n=n,total=total,baseline=verdict(cited),
                revised=survey_rule(cited,target,fraction,claim,n,total),truth=truth)

def survey_rows():
    rate=Fraction(18,100)
    for rec in OBS["hearings"]:
        # Audit only whether E2 supplies the stated 18% patient denominator.
        # A possible clinic with 100 respondents and 100 additional patients has
        # prevalence 9% if none of the latter are affected, or 59% if all are.
        examples=[Fraction(18,200),Fraction(118,200)]
        row=survey_row(rec["file"],"recorded generation","observed","population",rate,(rate,rate),
                       verdict(all(x==rate for x in examples)),rec["evidence"]["id"] in rec["refs"])
        row.update(baseline=rec["validator"],source=rec["evidence"]["text"],excerpt=rec["text"],
                   compatible_rates=[str(x) for x in examples])
        yield row
    yield survey_row("scope-preserving repair","editorial control","development","respondents",
                     rate,(rate,rate),PASS)
    yield survey_row("target left implicit","synthetic survey","boundary","unspecified",rate,(rate,rate),UNKNOWN)
    yield survey_row("unknown citation","synthetic survey","boundary","respondents",rate,(rate,rate),FAIL,False)
    for n in (4,5,7):
        split = "development" if n==4 else "holdout"
        for k, missing in product(range(n+1),(0,1,3)):
            total=n+missing
            rate=Fraction(k,n)
            # Oracle constructs every assignment to individual nonrespondents.
            possible=[Fraction(k+sum(bits),total) for bits in product((0,1),repeat=missing)]
            claims={"exact":(rate,rate),"lower-half":(0,Fraction(1,2)),
                    "upper-half":(Fraction(1,2),1),"inclusive-range":(Fraction(k,total),Fraction(k+missing,total))}
            for kind,claim in claims.items():
                label=verdict(all(claim[0]<=v<=claim[1] for v in possible))
                yield survey_row(f"n={n}/k={k}/missing={missing}/{kind}","synthetic survey",split,
                                 "population",rate,claim,label,n=n,total=total)

def summarize(rows):
    counts=defaultdict(Counter)
    for row in rows:
        for gate in ("baseline","revised"):
            truth,decision=row["truth"],row[gate]
            key=(row["case"],row["origin"],row["split"],gate)
            c=counts[key]
            c["n"]+=1
            if truth==UNKNOWN: c["truth_unknown"]+=1
            if decision==UNKNOWN: c["abstain"]+=1
            if truth==UNKNOWN or decision==UNKNOWN: continue
            c[{(PASS,PASS):"true_accept",(PASS,FAIL):"false_reject",
               (FAIL,PASS):"false_accept",(FAIL,FAIL):"true_reject"}[truth,decision]]+=1
    return [dict(case=k[0],origin=k[1],split=k[2],gate=k[3],**{s:v[s] for s in
            ("n","true_accept","false_accept","false_reject","true_reject","abstain","truth_unknown")})
            for k,v in counts.items()]

def report():
    rows=[*grid_rows(1e-6),*survey_rows()]
    sensitivity={str(tol):summarize(list(grid_rows(tol))) for tol in (1e-7,1e-5)}
    return dict(grid_tolerance=1e-6,rows=rows,summary=summarize(rows),grid_sensitivity=sensitivity,
                unscored=[dict(source="https://github.com/hengyuhang61-creator/machatlas/blob/804c447820/research/DISCREPANCY.md",
                    claim="Mach 5 continuum separation length in mm",length_mm=[23.56,23.14,21.17],
                    cells=[37275,75639,145765],baseline=UNKNOWN,revised=UNKNOWN,truth=UNKNOWN,
                    reason="These three native grids lack an independent limit and fourth observation. "
                           "The published numerical checks do not assert a continuum limit.")])

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("view",choices=["examples","summary","json"],nargs="?",default="examples")
    args=parser.parse_args()
    data=report()
    if args.view=="json":
        print(json.dumps(data,ensure_ascii=True,indent=2,allow_nan=False))
    elif args.view=="summary":
        print("case    origin                split        gate       N   FA   FR  abstain  unknown_truth")
        for r in data["summary"]:
            print("{case:7} {origin:21} {split:11} {gate:8} {n:4} {false_accept:4} {false_reject:4} {abstain:8} {truth_unknown:14}".format(**r))
    else:
        for r in data["rows"]:
            if r["split"]=="observed" or r["origin"]=="editorial control":
                detail=f"estimate={r['candidate']:.10g}, witness={r['witness_limit']:.10g}, exact=0" if r["case"]=="grid" else f"{r['rate']} of {r['target']}"
                print(f"{r['name']}: {r['baseline']} -> {r['revised']} | reference={r['truth']} | {detail}")
