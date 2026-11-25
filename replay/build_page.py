"""Rebuild the directly openable case page and downloadable row-level evidence."""
import json
from html import escape
from pathlib import Path
from witness import OBS, report

SITE=Path(__file__).resolve().parents[1]/"site"

def render(data):
    grid=[r for r in data["rows"] if r["case"]=="grid" and r["split"]=="observed"]
    original,repair=grid
    assert abs(repair["candidate"]-OBS["repair_limit"]) < 1e-14
    counts=[r for r in data["summary"] if r["split"]=="holdout"]
    table="".join(f"<tr><th>{r['case'].title()} · {r['gate']}</th><td>{r['n']}</td><td>{r['false_accept']}</td><td>{r['false_reject']}</td><td>{r['abstain']}</td></tr>" for r in counts)
    excerpts="".join(f"<details><summary>{escape(h['model'].split(' Q4')[0])} · read recorded rationale</summary><blockquote>{escape(h['text'])}</blockquote></details>" for h in OBS["hearings"])
    neg=next(r for r in data["rows"] if r["name"]=="trapezoid/cosine=1/fine")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>When the check passes | SolverFails</title><link rel="stylesheet" href="style.css">
<style>details{{border-top:1px solid var(--line);padding:.8em 0}}summary{{cursor:pointer;color:var(--a);font-weight:650}}details p,blockquote{{margin:.7em 0}}blockquote{{padding-left:1em;border-left:3px solid var(--line)}}table{{border-collapse:collapse;font-size:.92em}}td,th{{padding:.4em .65em;border-bottom:1px solid var(--line);text-align:left}}.scroll{{overflow:auto}}.case section{{margin:2.5em 0}}.rate{{color:var(--hi)}}.case a{{overflow-wrap:anywhere}}</style>
</head><body><a class="skip" href="#main">Skip to content</a><header class="bar"><a class="brand" href="index.html"><b>↳</b> SolverFails</a><nav><a href="#grid">Grid</a><a href="#survey">Survey</a><a href="#controls">Controls</a></nav></header>
<main id="main" class="case"><h1>What did the passing test establish?</h1>
<p class="lede">Inspect a numerical estimate and a cited percentage. In each case the original check ran successfully. Open the independent check to see which claim the evidence supports.</p>
<section id="grid"><p class="kind">Numerical verification</p><h2>A second-order slope and an inaccurate limit</h2>
<p>The released Poiseuille integration test estimates order <strong>{original['order']:.6f}</strong>, inside its required range of 1.5 to 2.5. Its three sampled velocity profiles follow the same analytical parabola. Their interpolation error approaches zero as spacing shrinks.</p>
<p>Reported continuum L2 error <b class="rate">{original['candidate']:.8f}</b> · original check <b>PASS</b></p>
<details><summary>Check the estimate against a fourth profile</summary><p>With 41 profile points, the measured L2 error is {OBS['fourth_L2']:.8g}. The fine and fourth observations predict a limit of {original['witness_limit']:.4g}. The released estimate fails the 10⁻⁶ agreement test.</p>
<p>Using the fine pair in the original three-level extrapolation gives <strong>{repair['candidate']:.5g}</strong>. It passes the fourth-level test and lies within 10⁻⁶ of the analytical zero. The small negative estimate is a signed extrapolation artifact.</p></details>
<a href="https://github.com/vvp-cfd/cfd-vv-suite/blob/{OBS['cfd_commit']}/tools/tests/test_integration.py">Upstream test and fixture paths ↗</a></section>
<section id="survey"><p class="kind">Evidence attribution</p><h2>The percentage survived. The denominator changed.</h2><blockquote>{escape(OBS['hearings'][0]['evidence']['text'])}</blockquote>
<p>Two archived models passed ThinkCouncil’s schema and citation checks on this authored clinic scenario. Both rationales attached 18% to patients. The audit asks only whether E2 supplies that patient-wide figure.</p>{excerpts}
<details><summary>Construct two populations consistent with E2</summary><p>Suppose 18 of 100 respondents reported a barrier, and another 100 patients did not respond. If none of the latter have the barrier, the patient-wide rate is <strong>9%</strong>. If all do, it is <strong>59%</strong>. These illustrative populations refute the inference from E2 alone. The clinic’s actual prevalence is unknown.</p><p>A supported wording is “18% of survey respondents reported no smartphone or unreliable data.” This check uses a human annotation of the target population and leaves decisions about rollout and exclusion risk open.</p></details>
<a href="https://github.com/hengyuhang61-creator/thinkcouncil/tree/{OBS['council_commit']}/eval">Original docket and both hearings ↗</a></section>
<section id="controls"><h2>Held-out controls</h2><p>Counts are candidate decisions from related constructed inputs. The grid oracle evaluates the generating function at zero. The survey oracle enumerates possible individual nonresponses.</p><div class="scroll"><table><thead><tr><th>Case and check</th><th>Decisions</th><th>False accepts</th><th>False rejects</th><th>Abstentions</th></tr></thead><tbody>{table}</tbody></table></div>
<details><summary>See a false acceptance by the revised checker</summary><p>On a separate stress test, the 4-, 8-, 16- and 32-panel trapezoid grids all sample cos(64πx) at the same phase. The fourth grid agrees with a proposed integral of <strong>{neg['candidate']:.6f}</strong>. The analytical integral of exp(x) + cos(64πx) on [0, 1] is <strong>{neg['analytic_limit']:.6f}</strong>. Both checks pass an error near one. At a tighter 10⁻⁷ threshold the revised checker also makes errors within the reserved grid set.</p></details>
<p>Recompute with <code>python replay/witness.py summary</code>. The full results include boundary cases, abstentions, separate sensitivity runs and an unscored native CFD question.</p><a href="witness-results.json" download>Download the decisions and inputs (JSON)</a>
</section></main><footer><a href="index.html#cases">All cases</a><a href="https://github.com/hengyuhang61-creator/solverfails/issues/new">Contribute a public counterexample ↗</a></footer></body></html>
"""

if __name__=="__main__":
    data=report()
    (SITE/"witnesses.html").write_text(render(data),encoding="utf8")
    (SITE/"witness-results.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n",encoding="utf8")
