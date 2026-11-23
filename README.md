# SolverFails

**Everything passed. The result was still wrong.**

Three case files about the difference between a passing signal and the outcome it was meant to establish.

[Open the interactive casebook](https://hengyuhang61-creator.github.io/solverfails/) · [Release](https://github.com/hengyuhang61-creator/solverfails/releases/latest) · [Report an issue](https://github.com/hengyuhang61-creator/solverfails/issues/new) · [中文](README.zh-CN.md)

![The casebook and its interactive coverage demo](media/cover.png)

| Case | Evidence |
| --- | --- |
| [A perfect score with eight points missing](https://hengyuhang61-creator.github.io/solverfails/coverage.html) | A synthetic regression verified against the released audit code |
| [The solver ran. The mass budget failed](https://hengyuhang61-creator.github.io/solverfails/conservation.html) | Selected scalar outputs from a Fluent checkpoint |
| [The tests passed. The installed app stayed old](https://hengyuhang61-creator.github.io/solverfails/deployment.html) | A redacted historical handover and a synthetic version probe |

## Replay locally

Use Node.js 24 or compatible. No npm installation is required.

```sh
node checks.mjs coverage 13
node checks.mjs coverage 21
node checks.mjs conservation
node checks.mjs deployment stale
node --test checks.test.mjs
```

Exit 0 means the criterion was met, exit 1 means the claim was rejected, and exit 2 means invalid input. The 13-point coverage, conservation and stale deployment fixtures deliberately return 1. To use the browser interface locally, run `python -m http.server 8000 --directory site` and open http://localhost:8000.

[Watch the UI demo](media/demo.gif) · [Sources and rights](THIRD_PARTY_NOTICES.md) · [English and Chinese launch copy](PROMOTION.md) · [MIT license](LICENSE)
