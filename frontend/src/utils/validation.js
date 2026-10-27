import { toCents } from "./money";

// Client-side checks for the item form. These give quick feedback only;
// the backend repeats every check and has the final say.
// Returns an object of field -> message. An empty object means valid.
export function validateItemForm(values) {
  const errors = {};

  if (!values.sku || !values.sku.trim()) {
    errors.sku = "SKU is required.";
  }
  if (!values.name || !values.name.trim()) {
    errors.name = "Item name is required.";
  }
  if (!values.category_id) {
    errors.category_id = "Choose a category.";
  }
  if (toCents(values.unit_cost) === null) {
    errors.unit_cost = "Enter a price such as 2.50 (zero or more).";
  }
  const reorder = values.reorder_level;
  if (reorder === "" || reorder === null || reorder === undefined
      || !Number.isInteger(Number(reorder)) || Number(reorder) < 0) {
    errors.reorder_level = "Enter a whole number, zero or more.";
  }
  return errors;
}

// Turn validated form values into the JSON the API expects.
export function toItemPayload(values) {
  return {
    sku: values.sku.trim(),
    name: values.name.trim(),
    category_id: Number(values.category_id),
    unit_cost_cents: toCents(values.unit_cost),
    reorder_level: Number(values.reorder_level),
  };
}
