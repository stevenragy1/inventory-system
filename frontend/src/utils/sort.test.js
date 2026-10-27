import { describe, expect, it } from "vitest";
import { sortRows } from "./sort";

const rows = [
  { sku: "B", days: 10 },
  { sku: "A", days: null },
  { sku: "C", days: 3 },
];

describe("sortRows", () => {
  it("sorts numbers ascending", () => {
    expect(sortRows(rows, "days", "asc").map((r) => r.sku)).toEqual(["C", "B", "A"]);
  });

  it("sorts numbers descending but keeps nulls last", () => {
    expect(sortRows(rows, "days", "desc").map((r) => r.sku)).toEqual(["B", "C", "A"]);
  });

  it("sorts text alphabetically", () => {
    expect(sortRows(rows, "sku", "asc").map((r) => r.sku)).toEqual(["A", "B", "C"]);
  });

  it("does not change the input array", () => {
    const copy = [...rows];
    sortRows(rows, "days", "desc");
    expect(rows).toEqual(copy);
  });
});
