import { describe, expect, it } from "vitest";
import { fromCents, toCents } from "./money";

describe("toCents", () => {
  it("converts typed amounts to whole cents", () => {
    expect(toCents("2.50")).toBe(250);
    expect(toCents("8.2")).toBe(820);
    expect(toCents("10")).toBe(1000);
    expect(toCents("0")).toBe(0);
    expect(toCents("0.05")).toBe(5);
  });

  it("avoids floating-point rounding errors", () => {
    // 0.1 + 0.2 is not exact in floating point; cents must be exact.
    expect(toCents("0.10") + toCents("0.20")).toBe(30);
    expect(toCents("6.75")).toBe(675);
  });

  it("rejects text that is not a non-negative amount", () => {
    expect(toCents("")).toBeNull();
    expect(toCents("abc")).toBeNull();
    expect(toCents("-1")).toBeNull();
    expect(toCents("1.234")).toBeNull();
    expect(toCents("1,50")).toBeNull();
    expect(toCents(undefined)).toBeNull();
  });
});

describe("fromCents", () => {
  it("formats cents with two decimals", () => {
    expect(fromCents(250)).toBe("2.50");
    expect(fromCents(5)).toBe("0.05");
  });
});
