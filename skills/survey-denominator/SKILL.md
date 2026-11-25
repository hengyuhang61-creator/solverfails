---
name: survey-denominator
description: Audit whether a percentage reported for survey respondents supports a numeric claim about the entire eligible population. Compute exact finite-population bounds when response counts are known.
---

Quote the evidence wording and the claim separately. Identify the measured attribute, time period, eligible population, number responding and number reporting the attribute. The calculation assumes unique respondents drawn from that same finite population and accurate binary responses. If an outcome changes from “reported an access barrier” to “will be excluded”, flag the outcome change separately.

When exact counts are supplied, run the bundled script from this skill directory with Python 3.9 or later. The command below uses illustrative counts.

```sh
python scripts/survey_bounds.py --affected 18 --respondents 100 --population 200 --claim-percent 18 18
```

The two percentage arguments define an inclusive interval. Report its status and both extreme completions. An exact respondent rate and an exact population rate are distinct claims. If the denominator or exact counts are unavailable, preserve the reported scope and mark the actual population rate unknown. A rounded percentage does not establish an exact count. Weighted surveys, probabilistic forecasts, sampling-design inference, differential measurement and causal claims need other evidence.

In the [recorded clinic case](https://hengyuhang61-creator.github.io/solverfails/witnesses.html#survey), E2 says 18% of respondents report a barrier. The text supplies no counts. A hypothetical 100 further patients demonstrates why multiple population rates fit. Identify such counts as illustrative. For a census with complete responses, the respondent and population rates coincide.

Source and license: SolverFails, copyright 2026 Heng Yuhang, MIT.
