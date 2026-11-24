import { readFileSync } from "node:fs";
import { coverage, conservation, delivery, mach5Drift } from "./site/model.mjs";

try {
  const [example, value, ...extra] = process.argv.slice(2);
  let result;
  if (extra.length) throw new Error("Too many arguments.");
  switch (example) {
    case "coverage":
      result = coverage(value === undefined ? 13 : Number(value));
      break;
    case "conservation":
      if (value !== undefined) throw new Error("Conservation takes no second argument.");
      result = conservation(JSON.parse(readFileSync(new URL("./site/case003b.json", import.meta.url), "utf8")));
      break;
    case "deployment":
      result = delivery(value ?? "stale");
      break;
    case "mach5-drift":
      if (value !== undefined) throw new Error("Mach 5 drift takes no second argument.");
      result = mach5Drift(JSON.parse(readFileSync(new URL("./site/mach5-drift.json", import.meta.url), "utf8")));
      break;
    default:
      throw new Error("Use coverage [2–21], conservation, deployment [stale|promoted], or mach5-drift.");
  }
  console.log(JSON.stringify(result, null, 2));
  process.exitCode = ["COMPLETE_SUPPORT", "MASS_BALANCE_MET", "VERSION_MATCH", "CHECKS_MET"].includes(result.verdict) ? 0 : 1;
} catch (error) {
  console.error(error.message);
  process.exitCode = 2;
}
