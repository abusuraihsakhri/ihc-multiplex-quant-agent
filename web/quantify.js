/* Pure numerical functions shared by the local browser console and Node tests. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.IHCQuant = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  function checkCount(value, name) {
    if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0) {
      throw new RangeError(name + " must be a non-negative whole number.");
    }
    return value;
  }
  function calculate(values) {
    if (!values || typeof values !== "object") throw new TypeError("Quantification inputs are required.");
    const tumorCells = checkCount(values.tumorCells, "Viable tumor cells");
    const positiveTumorCells = checkCount(values.positiveTumorCells, "PD-L1-positive tumor cells");
    const positiveImmuneCells = checkCount(values.positiveImmuneCells, "PD-L1-positive immune cells");
    const cd8Cells = checkCount(values.cd8Cells, "CD8-positive cells");
    const foxp3Cells = checkCount(values.foxp3Cells, "FoxP3-positive cells");
    const areaMm2 = values.areaMm2;
    if (typeof areaMm2 !== "number" || !Number.isFinite(areaMm2) || areaMm2 <= 0) {
      throw new RangeError("Analyzed area must be a positive finite number in mm².");
    }
    if (positiveTumorCells > tumorCells) {
      throw new RangeError("PD-L1-positive tumor cells cannot exceed viable tumor cells.");
    }
    if (tumorCells < 100) {
      throw new RangeError("At least 100 viable tumor cells are required for this illustrative CPS/TPS analysis.");
    }
    const round = value => Math.round((value + Number.EPSILON) * 100) / 100;
    return {
      viableTumorCells: tumorCells,
      pdl1PositiveTumorCells: positiveTumorCells,
      pdl1PositiveImmuneCells: positiveImmuneCells,
      cd8Cells,
      foxp3Cells,
      areaMm2,
      cps: round(Math.min(100, 100 * (positiveTumorCells + positiveImmuneCells) / tumorCells)),
      tpsPercent: round(100 * positiveTumorCells / tumorCells),
      cd8DensityPerMm2: round(cd8Cells / areaMm2),
      foxp3DensityPerMm2: round(foxp3Cells / areaMm2),
      cd8ToFoxp3Ratio: foxp3Cells === 0 ? null : round(cd8Cells / foxp3Cells),
    };
  }
  return Object.freeze({ calculate });
});
