import { describe, expect, it } from "vitest";
import { defaultWindow, splitSlowMovers } from "./dashboard";

describe("splitSlowMovers", () => {
  it("puts items with sales in bars, slowest first, and counts the rest", () => {
    const rows = [
      { sku: "A", days_of_stock: 15 },
      { sku: "B", days_of_stock: null },
      { sku: "C", days_of_stock: 60 },
    ];
    const { bars, noSales } = splitSlowMovers(rows);
    expect(bars.map((r) => r.sku)).toEqual(["C", "A"]);
    expect(noSales.map((r) => r.sku)).toEqual(["B"]);
  });
});

describe("defaultWindow", () => {
  it("returns the 30 days ending on the given UTC date", () => {
    const now = new Date("2026-10-24T12:00:00Z");
    expect(defaultWindow(30, now)).toEqual({ start: "2026-09-25", end: "2026-10-24" });
  });

  it("a one-day window starts and ends on the same date", () => {
    const now = new Date("2026-10-24T12:00:00Z");
    expect(defaultWindow(1, now)).toEqual({ start: "2026-10-24", end: "2026-10-24" });
  });
});
