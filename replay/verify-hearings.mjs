// Reapply the released validator to each recorded model stage, without inference.
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {resolve, join} from "node:path";
import {pathToFileURL} from "node:url";

const repo = resolve(process.argv[2]);
const {deliberate} = await import(pathToFileURL(join(repo, "council.mjs")));
const excerpts = [];
for (const file of ["results.json", "results-4b.json"]) {
  const rows = JSON.parse(await readFile(join(repo, "eval", file), "utf8"));
  const item = rows.find(row => row.id === "clinic");
  const {perspectives, exchanges, unknowns, conclusion} = item.output;
  const stages = [{perspectives}, {
    exchanges: exchanges.map(({from, to, ...rest}) => ({route: from + " > " + to, ...rest})), unknowns
  }, conclusion];
  const replay = await deliberate(item.input, async () => structuredClone(stages.shift()));
  assert.deepEqual(replay, item.output);
  assert.equal(stages.length, 0);
  const evidence = replay.docket.records.find(({id}) => id === "E2");
  assert.ok(conclusion.refs.includes(evidence.id));
  excerpts.push({file: "eval/" + file, model: item.model, evidence, text: conclusion.rationale,
    refs: conclusion.refs, validator: "PASS"});
}
console.log(JSON.stringify(excerpts));
