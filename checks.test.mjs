import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const cli = fileURLToPath(new URL("./checks.mjs", import.meta.url));
function run(expected, ...args) {
  const result = spawnSync(process.execPath, [cli, ...args], { encoding: "utf8" });
  assert.equal(result.status, expected, result.stderr || result.error?.message);
  return expected === 2 ? result.stderr : JSON.parse(result.stdout);
}

test("endpoint clamp hides a rejected 13/21 comparison", () => {
  assert.deepEqual(run(1, "coverage", "13"),
    { samples: 13, naiveRmse: 0, overlapRmse: 0, verdict: "FAIL_INCOMPLETE_SUPPORT" });
  assert.equal(run(0, "coverage", "21").verdict, "COMPLETE_SUPPORT");
  assert.match(run(2, "coverage", "0"), /sample count/);
});

test("recorded CFD boundary sums fail the mass budget", () => {
  const result = run(1, "conservation");
  assert.equal(result.verdict, "FAIL_MASS_BALANCE");
  assert.equal(result.imbalancePercent.toFixed(4), "1.0408");
});

test("candidate tests can pass while the probed build is stale", () => {
  assert.equal(run(1, "deployment", "stale").verdict, "NOT_DEPLOYED");
  assert.equal(run(0, "deployment", "promoted").verdict, "VERSION_MATCH");
});

test("two hash-linked Mach 5 outputs pass the mass gate and fail local stationarity", () => {
  const result = run(1, "mach5-drift");
  assert.equal(result.massPass, true);
  assert.equal(result.driftMm.toFixed(2), "7.20");
  assert.equal(result.verdict, "HOLD_WALL_DRIFT");
});

test("sampling challenge retains positive, false-reject and shared-failure controls", async () => {
  const {cases,evaluate,regression}=await import("./site/sampling.mjs");
  const first=evaluate(cases[0],"interleaved");
  assert.equal(first.accept,true);
  assert.equal(first.accurate,false);
  assert.equal(evaluate(cases[0],"staggered").accept,false);
  assert.equal(evaluate(cases[1],"interleaved").accurate,true);
  assert.equal(evaluate(cases[2],"staggered").accurate,true);
  assert.equal(evaluate(cases[2],"staggered").accept,false);
  assert.equal(evaluate(cases[3],"staggered").accept,true);
  assert.equal(evaluate(cases[3],"staggered").accurate,false);
  assert.match(regression(cases[0],"interleaved"),/def accepts/);
});
