// Thin wrapper around fetch for the Flask API.
// Errors are returned as objects so pages can show warnings and messages.

const BASE = "/api";

export class ApiError extends Error {
  constructor(status, body) {
    super(body?.message || `Request failed (${status})`);
    this.status = status;
    this.body = body || {};
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(response.status, body);
  }
  return body;
}

export const api = {
  getItems: () => request("/items"),
  getItem: (id) => request(`/items/${id}`),
  createItem: (payload) =>
    request("/items", { method: "POST", body: JSON.stringify(payload) }),
  deactivateItem: (id) =>
    request(`/items/${id}/deactivate`, { method: "POST" }),
  getCategories: () => request("/categories"),
  getLocations: () => request("/locations"),
  getMovements: (itemId) =>
    request(`/movements${itemId ? `?item_id=${itemId}` : ""}`),

  getDashboard: () => request("/dashboard"),
  search: (queryString) => request(`/search${queryString ? `?${queryString}` : ""}`),
  getValuation: () => request("/reports/valuation"),
  getLowStock: () => request("/reports/low-stock"),
  getNegativeStock: () => request("/reports/negative-stock"),
  getTurnover: (start, end) =>
    request(`/reports/turnover?start=${start}&end=${end}`),
  getReportMovements: (start, end) =>
    request(`/reports/movements?start=${start}&end=${end}`),

  receive: (payload) =>
    request("/stock/receive", { method: "POST", body: JSON.stringify(payload) }),
  issue: (payload) =>
    request("/stock/issue", { method: "POST", body: JSON.stringify(payload) }),
  adjust: (payload) =>
    request("/stock/adjust", { method: "POST", body: JSON.stringify(payload) }),
};
