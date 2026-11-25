# Can you trust 64 samples?

This independent experiment was specified before its sweep. It tests a numerical integration claim on [0,1] with absolute tolerance 0.02. Both checkers spend 64 function evaluations. Each reports the mean of the same 32 samples at j/32, j=0…31. Each buys 32 additional samples at (j+s)/32 and accepts when the two means differ by at most 0.02. The interleaved grid uses s=1/2; the staggered grid uses s=(3−√5)/2. Neither checker sees the generating function or oracle. A checker decision is wrong if it disagrees with whether the reported mean is within 0.02 of the analytical integral.

Inputs are 1 + A cos(2π(kx+t)). The integral is 1 + A[sin(2π(k+t))−sin(2πt)]/(2πk); at positive integer k it is exactly 1. Sweep both amplitudes 0.1 and 1 and all 16 phases t=j/16. Keep strata separate:

* Low integer frequencies 1…128, including both resonant and well-sampled cases.
* Selected resonances k=32m, m=5…64. Deliberate stress inputs, disjoint from the first stratum.
* Half-integer frequencies 0.5…31.5 in unit increments. The nonperiodic endpoint need not match.

There are 7,040 constructed inputs and two judgments per input. The false-accept denominator is inaccurate estimates and the false-reject denominator is accurate estimates. Report both, without optimizing the shift on these rows. A frozen shared-failure probe has k=1088, phase 0 and amplitude 1. The first public challenge uses k=64. Grid phase and input frequency are visible after making a decision. The probe and challenge are members of the sweep, not independent cases. This finite family supplies no general CFD or AI error rate. The earlier 8,192-input prototype is a separate reported experiment; these inputs and counts come from this implementation.

Run `node challenge/sweep.mjs` for the aggregate, or `node challenge/sweep.mjs --rows` for the full CSV. The browser and runner share the sampled checker. An external Python recomputation using a finite geometric series verified the exported decisions for this release.
