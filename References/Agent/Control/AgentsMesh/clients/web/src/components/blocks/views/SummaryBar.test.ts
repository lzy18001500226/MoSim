import { describe, expect, it } from "vitest";

import type { Block, SummaryColumn } from "@/lib/viewModels/blockstore";

import { computeAggregate } from "./SummaryBar";

function block(id: string, data: Record<string, unknown>): Block {
  return {
    id, workspace_id: "w", type: "task", data,
    meta: {}, created_by: 1, created_at: "", updated_at: "",
  } as Block;
}

describe("computeAggregate", () => {
  const rows = [
    block("a", { progress: 0.3, status: "todo" }),
    block("b", { progress: 0.7, status: "done" }),
    block("c", { progress: 1.0, status: "done" }),
    block("d", { status: "in_progress" }),
  ];

  const sc = (aggregate: SummaryColumn["aggregate"], key = "progress"): SummaryColumn =>
    ({ key, aggregate });

  it("count returns row count regardless of key", () => {
    expect(computeAggregate(rows, sc("count"))).toBe(4);
  });

  it("count_distinct counts unique values", () => {
    expect(computeAggregate(rows, sc("count_distinct", "status"))).toBe(3);
  });

  it("sum ignores missing / non-numeric values", () => {
    expect(computeAggregate(rows, sc("sum"))).toBeCloseTo(2.0);
  });

  it("avg averages only numeric values", () => {
    expect(computeAggregate(rows, sc("avg"))).toBeCloseTo(2.0 / 3);
  });

  it("min / max find extremes", () => {
    expect(computeAggregate(rows, sc("min"))).toBeCloseTo(0.3);
    expect(computeAggregate(rows, sc("max"))).toBeCloseTo(1.0);
  });

  it("returns NaN when no numeric samples", () => {
    const empty = [block("x", {}), block("y", {})];
    expect(Number.isNaN(computeAggregate(empty, sc("avg")))).toBe(true);
    expect(Number.isNaN(computeAggregate(empty, sc("min")))).toBe(true);
  });
});
