"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {calculate} = require("./quantify.js");
const baseline = {tumorCells: 200, positiveTumorCells: 40, positiveImmuneCells: 15, cd8Cells: 80, foxp3Cells: 20, areaMm2: 1.6};
test("CPS, TPS, densities and ratios are computed from counts", () => {
  const r = calculate(baseline);
  assert.equal(r.cps, 27.5);
  assert.equal(r.tpsPercent, 20);
  assert.equal(r.cd8DensityPerMm2, 50);
  assert.equal(r.foxp3DensityPerMm2, 12.5);
  assert.equal(r.cd8ToFoxp3Ratio, 4);
});
test("CPS is capped at 100 even with many positive immune cells", () => {
  assert.equal(calculate({...baseline, positiveImmuneCells: 250}).cps, 100);
});
test("zero FoxP3 counts result in an undefined rather than infinite ratio", () => {
  assert.equal(calculate({...baseline, foxp3Cells: 0}).cd8ToFoxp3Ratio, null);
});
test("invalid tumor counts, positive subsets and areas fail", () => {
  for (const values of [
    {tumorCells: 99}, {positiveTumorCells: 201}, {cd8Cells: -1},
    {positiveImmuneCells: 1.5}, {areaMm2: 0}, {areaMm2: Infinity},
    {tumorCells: NaN}, {foxp3Cells: 2.5}
  ]) assert.throws(() => calculate({...baseline, ...values}), RangeError);
});
