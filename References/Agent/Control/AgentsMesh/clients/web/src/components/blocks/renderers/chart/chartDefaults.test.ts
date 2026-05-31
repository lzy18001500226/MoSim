import { describe, expect, it } from "vitest";

import { chartInitialData, chartLabel, CHART_SUB_TYPES } from "./chartDefaults";

// Guards the invariant that every slash-menu seed for a chart sub-type
// satisfies the backend's RequiredDataKey: ["type", "series"]. A mistake here
// means "+ Add block → Chart / X" produces a block the server rejects.
describe("chartDefaults", () => {
  it("lists all six supported sub-types", () => {
    expect([...CHART_SUB_TYPES].sort()).toEqual(
      ["area", "bar", "line", "pie", "radar", "scatter"].sort(),
    );
  });

  it.each(CHART_SUB_TYPES)("chartInitialData(%s) satisfies backend RequiredDataKey", (sub) => {
    const data = chartInitialData(sub);
    expect(data.type).toBe(sub);
    expect(Array.isArray(data.series)).toBe(true);
    expect((data.series as unknown[]).length).toBeGreaterThan(0);
  });

  it.each(CHART_SUB_TYPES)("chartLabel(%s) prefixes 'Chart /'", (sub) => {
    expect(chartLabel(sub).startsWith("Chart /")).toBe(true);
  });

  it("seed data uses pie-specific {name,value} shape", () => {
    const pie = chartInitialData("pie");
    const firstSeries = (pie.series as Array<{ data: Array<{ name?: unknown; value?: unknown }> }>)[0];
    expect(firstSeries.data.every((d) => typeof d.name === "string" && typeof d.value === "number")).toBe(true);
  });

  it("seed data uses scatter-specific {x,y} shape", () => {
    const scatter = chartInitialData("scatter");
    const firstSeries = (scatter.series as Array<{ data: Array<{ x?: unknown; y?: unknown }> }>)[0];
    expect(firstSeries.data.every((d) => typeof d.x === "number" && typeof d.y === "number")).toBe(true);
  });
});
