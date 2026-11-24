export const reference = Array.from({ length: 21 }, (_, x) => Math.min(x / 12, 1));

function rmse(errors) {
  return Math.sqrt(errors.reduce((sum, error) => sum + error ** 2, 0) / errors.length);
}

export function coverage(samples) {
  if (!Number.isInteger(samples) || samples < 2 || samples > reference.length) {
    throw new RangeError("Choose an integer sample count from 2 to 21.");
  }
  const computed = reference.slice(0, samples);
  const errors = reference.map((value, i) => computed[Math.min(i, computed.length - 1)] - value);
  return {
    samples, naiveRmse: rmse(errors), overlapRmse: rmse(errors.slice(0, samples)),
    verdict: samples === reference.length ? "COMPLETE_SUPPORT" : "FAIL_INCOMPLETE_SUPPORT",
  };
}

export function conservation(record) {
  const fluxes = Object.values(record.inwardBoundaryFluxKgPerSecondPerMetre);
  if (!fluxes.every(Number.isFinite) || !Number.isFinite(record.massTolerancePercent)
      || record.massTolerancePercent <= 0) {
    throw new RangeError("Finite boundary fluxes and a positive tolerance are required.");
  }
  const incoming = fluxes.filter((value) => value > 0).reduce((a, b) => a + b, 0);
  if (incoming === 0) throw new RangeError("A positive total inflow is required.");
  const net = fluxes.reduce((a, b) => a + b, 0);
  const imbalancePercent = 100 * Math.abs(net) / incoming;
  return { incoming, net, imbalancePercent, verdict: imbalancePercent <= record.massTolerancePercent
    ? "MASS_BALANCE_MET" : "FAIL_MASS_BALANCE" };
}

export function delivery(installedBuild) {
  if (!["stale", "promoted"].includes(installedBuild)) throw new RangeError("Choose stale or promoted.");
  const candidateBuild = "example-2";
  const probedBuild = installedBuild === "promoted" ? "example-2" : "example-1";
  return { candidateTests: "PASS", candidateBuild, probedBuild,
    verdict: candidateBuild === probedBuild ? "VERSION_MATCH" : "NOT_DEPLOYED" };
}

export function mach5Drift(record) {
  const { earlier, later, massThresholdPercent, edgeThresholdMm } = record;
  if (earlier.iterations >= later.iterations ||
      !/^[a-f\d]{64}$/.test(earlier.restartSha256) ||
      earlier.restartSha256 !== later.restartInputSha256 ||
      ![massThresholdPercent, edgeThresholdMm].every((value) => Number.isFinite(value) && value > 0)) {
    throw new RangeError("Two ordered, hash-linked checkpoints and positive tolerances are required.");
  }
  const massErrorPercent = [earlier, later].map(({ inlet, outlet, sepMm, reattachMm }) => {
    if (![inlet, outlet, sepMm, reattachMm].every(Number.isFinite) ||
        inlet <= 0 || outlet >= 0 || sepMm >= reattachMm) {
      throw new RangeError("Invalid checkpoint fluxes or wall crossings.");
    }
    return Math.abs(inlet + outlet) / inlet * 100;
  });
  const driftMm = Math.max(Math.abs(later.sepMm - earlier.sepMm),
    Math.abs(later.reattachMm - earlier.reattachMm));
  const massPass = massErrorPercent.every((error) => error <= massThresholdPercent);
  return { massErrorPercent, massPass, driftMm, verdict: !massPass ? "FAIL_MASS_BALANCE" :
    driftMm <= edgeThresholdMm ? "CHECKS_MET" : "HOLD_WALL_DRIFT" };
}
