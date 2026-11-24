import { reference, coverage, conservation, delivery, mach5Drift } from "./model.mjs";

function result(element, title, detail) {
  const line = document.createElement("small");
  line.textContent = detail;
  element.replaceChildren(title, document.createElement("br"), line);
}

const slider = document.querySelector("#extent");
if (slider) {
  let strict = true;
  const naiveButton = document.querySelector("#naive");
  const strictButton = document.querySelector("#strict");
  const plot = document.querySelector("#plot");
  const height = (value) => (5 + value * 87) + "%";
  const points = reference.map((value) => {
    const column = document.createElement("span");
    const dot = document.createElement("i");
    dot.style.bottom = height(value);
    column.append(dot, document.createElement("b"));
    return column;
  });
  plot.replaceChildren(...points);

  function render() {
    const audit = coverage(Number(slider.value));
    document.querySelector("#count").textContent = audit.samples;
    naiveButton.setAttribute("aria-pressed", String(!strict));
    strictButton.setAttribute("aria-pressed", String(strict));
    points.forEach((column, index) => {
      column.className = index < audit.samples ? "supported" : strict ? "missing" : "missing clamped";
      column.lastElementChild.style.bottom = height(reference[audit.samples - 1]);
    });
    const supported = audit.samples + " / " + reference.length + " supported";
    const output = document.querySelector("#result");
    if (strict) {
      result(output, audit.verdict === "COMPLETE_SUPPORT" ? "Full coverage confirmed" : "Full-domain verdict withheld",
        supported + " · Overlap RMSE " + audit.overlapRmse.toFixed(3));
    } else {
      result(output, "Clamped RMSE " + audit.naiveRmse.toFixed(3),
        supported + (audit.samples < reference.length ? " · Endpoint value fills the missing samples" : " · No missing samples"));
    }
  }

  slider.addEventListener("input", render);
  naiveButton.addEventListener("click", () => { strict = false; render(); });
  strictButton.addEventListener("click", () => { strict = true; render(); });
  render();
}

document.querySelector("#budget")?.addEventListener("click", async () => {
  const output = document.querySelector("#budget-result");
  try {
    const response = await fetch(new URL("./case003b.json", import.meta.url));
    if (!response.ok) throw new Error("HTTP " + response.status);
    const audit = conservation(await response.json());
    result(output, audit.verdict, audit.imbalancePercent.toFixed(4) + "% of total inward mass flux");
  } catch {
    result(output, "Evidence could not be loaded", "Serve the site over HTTP and try again.");
  }
});

for (const [button, build] of [["#old-build", "stale"], ["#new-build", "promoted"]]) {
  document.querySelector(button)?.addEventListener("click", () => {
    const audit = delivery(build);
    result(document.querySelector("#delivery-result"), audit.verdict,
      "Candidate " + audit.candidateBuild + " · Installed " + audit.probedBuild);
  });
}

for (const button of ["#drift-mass", "#drift-both"]) {
  document.querySelector(button)?.addEventListener("click", async () => {
    const output = document.querySelector("#drift-output");
    try {
      const response = await fetch(new URL("./mach5-drift.json", import.meta.url));
      if (!response.ok) throw new Error("HTTP " + response.status);
      const audit = mach5Drift(await response.json());
      const mass = "Mass error across saves " + audit.massErrorPercent.map((x) => x.toFixed(5) + "%").join(" / ");
      if (button === "#drift-mass") {
        result(output, audit.massPass ? "MASS_BALANCE_MET" : "FAIL_MASS_BALANCE", mass);
      } else {
        result(output, audit.verdict, mass + " · Maximum crossing drift " + audit.driftMm.toFixed(2) + " mm");
      }
    } catch {
      result(output, "Evidence could not be loaded", "Serve the site over HTTP and try again.");
    }
  });
}
