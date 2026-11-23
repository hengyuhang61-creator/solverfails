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
