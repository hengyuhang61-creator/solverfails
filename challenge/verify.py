import cmath,csv,json,math,subprocess
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1]
raw=subprocess.check_output(["node","challenge/sweep.mjs","--rows"],cwd=root)
rows=list(csv.DictReader(raw.decode().splitlines()))
counts=Counter()
seen=set()
for row in rows:
    k,t,a=map(float,(row["k"],row["phase"],row["amplitude"]))
    method=row["method"];s={"interleaved":.5,"staggered":(3-math.sqrt(5))/2}[method]
    # Sum complex roots of unity without calling either sampling loop.
    advance=cmath.exp(2j*math.pi*k/32)
    if k%32==0: mult=1
    elif k.is_integer():mult=0
    else:mult=(1-cmath.exp(2j*math.pi*k))/(32*(1-advance))
    def average(shift):
        return 1+a*(cmath.exp(2j*math.pi*(t+k*shift/32))*mult).real
    exact=1 if k.is_integer() else 1+a*(cmath.exp(2j*math.pi*t)*(cmath.exp(2j*math.pi*k)-1)/(2j*math.pi*k)).real
    primary,probe=average(0),average(s)
    assert max(abs(primary-float(row["estimate"])),abs(probe-float(row["witness"])),abs(exact-float(row["exact"])))<1e-11
    accept,accurate=abs(primary-probe)<=.02,abs(primary-exact)<=.02
    assert (int(accept),int(accurate))==(int(row["accept"]),int(row["accurate"]))
    key=(k,t,a,method);assert key not in seen;seen.add(key)
    counts[row["group"],method,"accurate" if accurate else "inaccurate"]+=1
    counts[row["group"],method,"falseAccept"]+=int(accept and not accurate)
    counts[row["group"],method,"falseReject"]+=int(not accept and accurate)
summary=json.loads(subprocess.check_output(["node","challenge/sweep.mjs"],cwd=root))
assert len(rows)==2*summary["inputs"]==14080
for g,methods in summary["groups"].items():
    for m,values in methods.items():
        assert all(counts[g,m,k]==v for k,v in values.items())
assert summary==json.loads((root/"site/sampling-summary.json").read_text(encoding="utf8"))
print("Verified 14,080 decisions by finite geometric sums.")
