# Reproduce the two evidence checks

From the repository root run `python replay/witness.py` for the observed cases, `python replay/witness.py summary` for the controls and `python replay/witness.py json` for the complete decisions. The default replay uses two small recorded inputs and recomputes the decisions offline. Open [the local case page](../site/witnesses.html) directly. To regenerate the page and downloadable JSON, run `python replay/build_page.py`.

## Recover the observations from source

With Git, Python 3.9+ with NumPy, and Node.js 24 available, start from the SolverFails root. The two cloned directories in this example are siblings of the SolverFails checkout.

```sh
git clone https://github.com/vvp-cfd/cfd-vv-suite.git ../cfd-vv-suite
git -C ../cfd-vv-suite checkout d428d076fad18b486947deb341bcf51773ecc24f
git clone https://github.com/hengyuhang61-creator/thinkcouncil.git ../thinkcouncil
git -C ../thinkcouncil checkout 6eb6dc4d645a772aaacdbbaf197e1b09c4be8be6
python replay/extract.py ../cfd-vv-suite ../thinkcouncil
python replay/test_witness.py
```

The extractor calls the original comparison and GCI package on the original CSVs. It checks their values and physical sample spacings, generates a fourth CSV on 41 points and measures its L2 error against 101 reference coordinates. It changes one expression in a temporary copy of the module and reruns the same package entry point. It also passes the three recorded stages of each separate hearing through the released `deliberate` function and requires deep equality with the entire archived hearing. This is a validator replay; it consumes no model or inference service. [Grid source and integration test](https://github.com/vvp-cfd/cfd-vv-suite/tree/d428d076fad18b486947deb341bcf51773ecc24f/tools) · [ThinkCouncil source and model outputs](https://github.com/hengyuhang61-creator/thinkcouncil/tree/6eb6dc4d645a772aaacdbbaf197e1b09c4be8be6).

## Scope of the grid verdict

The upstream test genuinely checks the observed order. Treating that PASS as assurance about the *returned limit* would exceed what the test verifies. The upstream project supplied the package, test and three fixture CSVs. Earlier local work had already demonstrated the formula error on a manufactured polynomial. This replay adds an end-to-end test of the actual package and its shipped fixture, a fresh independently sampled level, a controlled repair, and an evaluation of the new check. We have no evidence of a downstream deployment incident.

The profile is the exact parabola sampled on increasingly fine grids. Linear interpolation of that curve converges uniformly as the maximum spacing decreases, so its limiting L2 error is zero. This oracle needs neither the p estimate nor the candidate extrapolate. The input mesh labels are 0.05, 0.025 and 0.0125; the CSV coordinate spacings are 0.20, 0.10 and 0.05. Both sequences have common ratio two. L2 here is the project's root-mean-square difference in velocity values. The numerical threshold 1e−6 is the benchmark accuracy budget for the returned limit, using the scale of the case L2 tolerance. It does not certify a solver.

Write R=(q1−q2)/(q2−q3), indexing samples from coarse to fine. The correction reports q3+(q3−q2)/(R−1). The witness uses q4+(q4−q3)/(R−1). These share a fitted ratio and an interpolation routine. The separate observation checks local consistency, while the analytic oracle judges its mistakes. The near-zero corrected value is slightly negative. An application requiring a nonnegative estimate would need a separate decision about that constraint. Synthetic order-gate false rejections include accurate estimates of orders other than two; that is a mismatch with the broader continuum-accuracy target, not a failure of the original order requirement.

## Scope of the survey verdict

Both original validators checked the full hearing structure, method routes and allowed citation IDs. An analyst annotated a single question per hearing: “Does E2 supply a patient-wide 18% rate?” The 4B rationale directly states such a rate. The 8B model uses it in a warning about possible exclusion. Its warning and the actual probability of exclusion are distinct questions; only the numerical attribution is scored. The repaired claim reports respondents. The test checks a structured claim and does not parse arbitrary free text.

The two outputs share one authored scenario and one E2 record. No patient observations were collected. Assuming 18 affected respondents out of 100 and 100 unobserved patients is one *possible* completion, not a recovered sample size. Adding either zero or 100 affected patients yields patient-wide rates of 9% or 59%. Both are compatible with the reported 18%. The target is evidence entailment, not population prevalence. For the finite synthetic controls, the independent oracle constructs every binary assignment to nonrespondents. The revised rule checks only extremal attainable rates; the two implementations share inputs but no verdicts. Ambiguous claims remain UNKNOWN.

## What the controls establish

The [frozen design](DESIGN.md) separates source fixtures, authored faults and reserved parameter families. The [row-level output](../site/witness-results.json) contains 483 candidate decisions at the main threshold, including 4 post hoc transfer probes. There are two primary case mechanisms. The two outputs of the same clinic scenario, the two implementations on the upstream fixture and hundreds of correlated controls are not independent case counts. Sensitivity runs reuse the grid rows. A native MachAtlas record appears separately with unknown truth and zero weight in the scores.

* At 1e−6, the full 144-decision grid holdout has 51 false acceptances and 33 false rejections with the order proxy, and zero of either with the fourth-grid check. In the four boundary controls the new check abstains twice, including a truly constant field. At 1e−7 the revised holdout check falsely accepts two candidates. Raw floating-point comparisons near the strict 1.5 and 2.5 cutoffs may affect synthetic baseline counts on other math libraries.
* Among 168 held-out survey variants the citation-presence proxy falsely accepts 74 and rejects no supported claim. The scope check has no errors or abstentions on those bounded, pre-annotated inputs. It abstains on the separate ambiguous-target control. Raw output records both unknown truth and abstention, which may apply to the same row.
* After the main matrix, we locked the rules and evaluated composite trapezoid integration of exp(x), then exp(x)+cos(64πx) on [0,1] at 4, 8, 16 and 32 panels. Each function has the same analytical integral, e−1. In the second experiment the cosine aliases to one across all four grids. Both gates accept the fine-pair estimate 2.7182812462, almost exactly one too high. The same process gives a correct acceptance on the smooth control. A useful next experiment would vary the sampling phase independently, keep the present negative control, and measure the extra false rejections. [Post hoc results and tolerances](../site/witness-results.json).

For the MachAtlas 23.56 / 23.14 / 21.17 mm separation sequence, the physical continuum answer remains UNKNOWN. Changes in solver version or a source term can establish a numerical cause within a run matrix. The extrapolation replay supplies no experimental validation of that Mach 5 flow. [MachAtlas scientific record](https://github.com/hengyuhang61-creator/machatlas/blob/804c447820/research/DISCREPANCY.md).

Defects4J and BugsInPy provide buggy/fixed revisions and triggering tests. Tests4Py adds system-test oracles and passing inputs. CheckList supplies behavioral test types for language systems. SolverFails reuses those distinctions and records the original green signal, the exact claim someone might carry forward, a separately checkable contradiction, and failures of the proposed replacement. Richardson extrapolation, finite-population bounds, fault injection and behavioral testing have established prior art. The contribution here is the measured evidence and replay. [Defects4J](https://github.com/rjust/defects4j/tree/8c16da8230843cdc918eaf4ddb449637f02b83c6) · [BugsInPy](https://github.com/soarsmu/BugsInPy/tree/11c5f1eea954a42132cfd06bf257766a7963e0fd) · [Tests4Py](https://github.com/smythi93/Tests4Py/tree/3e2328f95ff3934f9d4cc48d3053ac89cc3e1797) · [CheckList](https://github.com/marcotcr/checklist/blob/4e6e5e33a26f30c20ed602b2050f6c73e123cc23/checklist/test_types.py).
