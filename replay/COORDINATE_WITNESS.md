# Zero discrepancy across different stations

A numerical comparison needs both the value and its location. The original cfd-vv-suite `compare_field` at d428d076 returns L2=0 on two identical value arrays at x=0 and x=1. Both files contain x and y. The varying coordinate is y, so the interpolation path ignores the different constant x values. The independent domain statement fixes x as the station. Under that interpretation the score compares two different physical lines.

| Inference case | Upstream L2 | Guarded disposition |
| --- | ---: | --- |
| Same declared station, exact same input | 0 | PASS |
| Known disjoint stations | 0 | FAIL |
| One file omits station | 0 | UNKNOWN |
| Axis sets differ and mapping is absent | 0 | UNKNOWN |
| Reference points outside computed support | 0 | FAIL |
| 2-D near points in one reference neighborhood | 0 | UNKNOWN |

The last row reports two pairs, from four reference points. The two near points both map to the same reference point. The original routine can be used for a declared partial comparison. A full-reference claim needs reference coverage, and a meaningful physical match needs an agreed length metric and tolerance. The direct positional-dimension probe exercises the internal helper. The public entry point first intersects named coordinate columns. The guard in this example permits exact 2-D matches and a small 1-D domain check. Real projections, unit conversion, nonidentical multidimensional grids and appropriate error budgets need explicit policies. The endpoint probe replays an existing mechanism. The other probes share the pinned upstream source.

Run from the repository root, with Python dependencies for the upstream package installed in an isolated environment.

```sh
git clone https://github.com/vvp-cfd/cfd-vv-suite
git -C cfd-vv-suite checkout d428d076fad18b486947deb341bcf51773ecc24f
python replay/coordinate_witness.py cfd-vv-suite
```

[Observed JSON](../site/coordinate-results.json) · [Pinned source](https://github.com/vvp-cfd/cfd-vv-suite/blob/d428d076fad18b486947deb341bcf51773ecc24f/tools/cfdvv/compare.py) · [CFD Profile Audit](https://github.com/hengyuhang61-creator/cfd-profile-audit)
