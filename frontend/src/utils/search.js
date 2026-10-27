// Turn the filter form values into a query string for /api/search.
// Empty filters are left out, so "All categories" sends nothing.
export function buildSearchParams(filters) {
  const params = new URLSearchParams();
  const text = (filters.q || "").trim();
  if (text) params.set("q", text);
  if (filters.category_id) params.set("category_id", filters.category_id);
  if (filters.location_id) params.set("location_id", filters.location_id);
  if (filters.status) params.set("status", filters.status);
  return params.toString();
}

export const STATUS_OPTIONS = [
  { value: "", label: "Any status" },
  { value: "in_stock", label: "In stock" },
  { value: "low", label: "Low" },
  { value: "out", label: "Out" },
  { value: "negative", label: "Negative" },
];
