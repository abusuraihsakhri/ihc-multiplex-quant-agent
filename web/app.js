/* Local-only results view. No remote requests, browser storage, or patient identifiers. */
"use strict";
const form = document.querySelector("#quant-form");
const error = document.querySelector("#error");
const results = document.querySelector("#results");
const output = document.querySelector("#metrics");
const exportJson = document.querySelector("#download-json");
const exportCsv = document.querySelector("#download-csv");
const sample = document.querySelector("#sample");
const inputs = ["tumorCells", "positiveTumorCells", "positiveImmuneCells", "cd8Cells", "foxp3Cells", "areaMm2"];
let latest = null;
const labels = {
  cps: "PD-L1 CPS",
  tpsPercent: "PD-L1 TPS",
  cd8DensityPerMm2: "CD8 cells/mm²",
  foxp3DensityPerMm2: "FoxP3 cells/mm²",
  cd8ToFoxp3Ratio: "CD8/FoxP3 ratio"
};
function clearResults() {
  latest = null;
  results.hidden = true;
  exportJson.disabled = true;
  exportCsv.disabled = true;
  output.replaceChildren();
}
function render(result) {
  const fragment = document.createDocumentFragment();
  for (const [field, label] of Object.entries(labels)) {
    const article = document.createElement("div");
    article.className = "measure";
    const title = document.createElement("span");
    title.textContent = label;
    const value = document.createElement("strong");
    value.textContent = result[field] === null ? "N/A" : result[field].toLocaleString(undefined, {maximumFractionDigits: 2});
    article.append(title, value);
    fragment.append(article);
  }
  output.replaceChildren(fragment);
  latest = result;
  results.hidden = false;
  exportJson.disabled = false;
  exportCsv.disabled = false;
}
form.addEventListener("submit", event => {
  event.preventDefault();
  clearResults();
  error.textContent = "";
  try {
    const raw = {};
    for (const id of inputs) {
      const value = document.getElementById(id).value.trim();
      if (value === "") throw new RangeError("All fields must be completed.");
      raw[id] = Number(value);
    }
    render(IHCQuant.calculate(raw));
  } catch (problem) {
    error.textContent = problem.message;
  }
});
form.addEventListener("input", () => {
  clearResults();
  error.textContent = "";
});
sample.addEventListener("click", () => {
  const values = [200, 40, 15, 80, 20, 1.6];
  inputs.forEach((id, index) => { document.getElementById(id).value = values[index]; });
  clearResults();
  error.textContent = "";
});
function download(name, type, content) {
  const objectUrl = URL.createObjectURL(new Blob([content], {type}));
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = name;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
}
exportJson.addEventListener("click", () => {
  if (latest) download("ihc-quantification.json", "application/json", JSON.stringify(latest, null, 2) + "\n");
});
exportCsv.addEventListener("click", () => {
  if (!latest) return;
  const keys = Object.keys(latest);
  const csv = keys.join(",") + "\n" + keys.map(key => latest[key] === null ? "" : String(latest[key])).join(",") + "\n";
  download("ihc-quantification.csv", "text/csv;charset=utf-8", csv);
});
