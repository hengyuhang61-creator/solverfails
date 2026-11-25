export const tolerance = 0.02;
export const shifts = Object.freeze({interleaved: 0.5, staggered: (3 - Math.sqrt(5)) / 2});
export const cases = [
  {k:64, phase:0, amplitude:1}, {k:7, phase:3/16, amplitude:1},
  {k:32, phase:0.25, amplitude:1}, {k:1088, phase:0, amplitude:1},
  {k:0.5, phase:0, amplitude:1}
];

export function value(input,x) {
  return 1 + input.amplitude * Math.cos(2 * Math.PI * (input.k*x + input.phase));
}
export function integral({k,phase,amplitude}) {
  if (Number.isInteger(k)) return 1;
  const angle = 2*Math.PI;
  return 1 + amplitude*(Math.sin(angle*(k+phase))-Math.sin(angle*phase))/(angle*k);
}
export function sampleMean(input,shift) {
  let total=0;
  for (let j=0;j<32;j++) total+=value(input,(j+shift)/32);
  return total/32;
}
export function evaluate(input,method) {
  if (!Object.hasOwn(shifts,method)) throw new RangeError("Unknown sampling rule");
  const estimate=sampleMean(input,0);
  const witness=sampleMean(input,shifts[method]);
  const exact=integral(input);
  return {estimate,witness,exact,accept:Math.abs(estimate-witness)<=tolerance,
    accurate:Math.abs(estimate-exact)<=tolerance};
}

export function regression(input,method) {
  if (!cases.some(c=>c.k===input.k && c.phase===input.phase && c.amplitude===input.amplitude) ||
      !Object.hasOwn(shifts,method)) throw new RangeError("Unknown challenge");
  return `"""Standalone SolverFails regression. Python 3. Replace accepts() with your rule."""
import math
import sys

k, phase, amplitude = ${input.k}, ${input.phase}, ${input.amplitude}
shift = ${shifts[method]}
tolerance = 0.02

def mean(offset):
    return sum(1 + amplitude * math.cos(2 * math.pi * (k*(j+offset)/32 + phase))
               for j in range(32)) / 32

def accepts(estimate, witness):
    return abs(estimate - witness) <= tolerance

estimate, witness = mean(0), mean(shift)
exact = 1 if float(k).is_integer() else 1 + amplitude * (
    math.sin(2*math.pi*(k+phase)) - math.sin(2*math.pi*phase)) / (2*math.pi*k)
expected = abs(estimate - exact) <= tolerance
actual = accepts(estimate, witness)
print(f"estimate={estimate:.8f} witness={witness:.8f} exact={exact:.8f}")
print(f"checker_accepts={actual} oracle_accepts={expected}")
sys.exit(int(actual != expected))
`;
}
