import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";

import { ChartPreview } from "./ChartPreview";
import { chartInitialData } from "./chartDefaults";
import { mergeSeries, normalize } from "./chartUtils";

// next-themes throws in jsdom without a provider; return a stable value so
// the palette selection below is deterministic.
vi.mock("next-themes", () => ({
  useTheme: () => ({ resolvedTheme: "light" }),
}));

// ResponsiveContainer swallows its child when given a 0-height container in
// jsdom, and recharts' child charts need an explicit parent size. Force
// render the child directly so normalize() and variant selection are
// exercised — the actual SVG output isn't meaningful in jsdom without
// layout.
vi.mock("recharts", async () => {
  const actual = await vi.importActual<typeof import("recharts")>("recharts");
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="chart-host">{children}</div>
    ),
  };
});

describe("ChartPreview", () => {
  it("renders a placeholder when data is empty", () => {
    render(<ChartPreview data={{}} />);
    expect(screen.getByText("No data")).toBeInTheDocument();
  });

  it("renders a placeholder when type is unknown", () => {
    render(<ChartPreview data={{ type: "weird", series: [{ data: [{ x: 1 }] }] }} />);
    expect(screen.getByText("No data")).toBeInTheDocument();
  });

  it("renders a placeholder when series is empty", () => {
    render(<ChartPreview data={{ type: "bar", series: [] }} />);
    expect(screen.getByText("No data")).toBeInTheDocument();
  });

  it.each(["bar", "line", "pie", "area", "scatter", "radar"] as const)(
    "picks a chart host for %s default seed (no placeholder)",
    (sub) => {
      render(<ChartPreview data={chartInitialData(sub)} />);
      expect(screen.queryByText("No data")).not.toBeInTheDocument();
      expect(screen.getByTestId("chart-host")).toBeInTheDocument();
    },
  );

  it("applies the height prop to the placeholder container", () => {
    render(<ChartPreview data={{}} height={120} />);
    const placeholder = screen.getByText("No data");
    expect(placeholder.style.height || placeholder.getAttribute("style") || "").toMatch(/120/);
  });
});

describe("normalize", () => {
  it("returns null for unknown type", () => {
    expect(normalize({ type: "bogus", series: [] })).toBeNull();
  });

  it("returns null when series is not an array", () => {
    expect(normalize({ type: "bar", series: {} })).toBeNull();
  });

  it("coerces non-array data to empty array", () => {
    const r = normalize({ type: "bar", series: [{ name: "s", data: null }] });
    expect(r?.series[0].data).toEqual([]);
  });
});

describe("mergeSeries", () => {
  it("pivots [{month:Jan,value:1},{month:Feb,value:2}] with two series", () => {
    const out = mergeSeries(
      [
        { name: "A", data: [{ month: "Jan", value: 1 }, { month: "Feb", value: 2 }] },
        { name: "B", data: [{ month: "Jan", value: 10 }, { month: "Feb", value: 20 }] },
      ],
      "month",
    );
    expect(out).toHaveLength(2);
    expect(out[0]).toEqual({ month: "Jan", A: 1, B: 10 });
    expect(out[1]).toEqual({ month: "Feb", A: 2, B: 20 });
  });

  it("falls back to series_i when name is missing", () => {
    const out = mergeSeries([{ data: [{ x: "one", value: 5 }] }], "x");
    expect(out[0]).toHaveProperty("series_0", 5);
  });
});
