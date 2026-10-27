import { describe, expect, it } from "vitest";
import { buildSearchParams, STATUS_OPTIONS } from "./search";

describe("buildSearchParams", () => {
  it("leaves out empty filters", () => {
    expect(buildSearchParams({ q: "", category_id: "", location_id: "", status: "" })).toBe("");
  });

  it("trims the text and includes the chosen filters", () => {
    const qs = buildSearchParams({
      q: "  glass ", category_id: "2", location_id: "1", status: "negative",
    });
    expect(qs).toBe("q=glass&category_id=2&location_id=1&status=negative");
  });

  it("ignores text that is only spaces", () => {
    expect(buildSearchParams({ q: "   " })).toBe("");
  });
});

describe("STATUS_OPTIONS", () => {
  it("offers every status the backend accepts", () => {
    const values = STATUS_OPTIONS.map((o) => o.value).filter(Boolean);
    expect(values.sort()).toEqual(["in_stock", "low", "negative", "out"]);
  });
});
