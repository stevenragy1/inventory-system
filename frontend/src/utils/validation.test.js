import { describe, expect, it } from "vitest";
import { toItemPayload, validateItemForm } from "./validation";

const valid = {
  sku: "CUP-CER-004",
  name: "Espresso cup 90ml",
  category_id: "1",
  unit_cost: "2.50",
  reorder_level: "100",
};

describe("validateItemForm", () => {
  it("accepts a complete form", () => {
    expect(validateItemForm(valid)).toEqual({});
  });

  it("requires SKU, name, and category", () => {
    const errors = validateItemForm({ ...valid, sku: "  ", name: "", category_id: "" });
    expect(errors.sku).toBeDefined();
    expect(errors.name).toBeDefined();
    expect(errors.category_id).toBeDefined();
  });

  it("rejects a bad price", () => {
    expect(validateItemForm({ ...valid, unit_cost: "abc" }).unit_cost).toBeDefined();
    expect(validateItemForm({ ...valid, unit_cost: "-3" }).unit_cost).toBeDefined();
  });

  it("accepts zero reorder level but rejects decimals and negatives", () => {
    expect(validateItemForm({ ...valid, reorder_level: "0" })).toEqual({});
    expect(validateItemForm({ ...valid, reorder_level: "2.5" }).reorder_level).toBeDefined();
    expect(validateItemForm({ ...valid, reorder_level: "-1" }).reorder_level).toBeDefined();
    expect(validateItemForm({ ...valid, reorder_level: "" }).reorder_level).toBeDefined();
  });
});

describe("toItemPayload", () => {
  it("builds the API body with cents and trimmed text", () => {
    expect(toItemPayload({ ...valid, sku: " CUP-CER-004 ", name: " Espresso cup 90ml " })).toEqual({
      sku: "CUP-CER-004",
      name: "Espresso cup 90ml",
      category_id: 1,
      unit_cost_cents: 250,
      reorder_level: 100,
    });
  });
});
