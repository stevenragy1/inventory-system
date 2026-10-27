// Helpers that prepare dashboard data for the charts.

// Items with no sales have no days-of-stock figure, so they cannot be
// drawn as a bar. Split them out so the page can say how many there are.
export function splitSlowMovers(rows) {
  const withSales = rows.filter((r) => r.days_of_stock !== null && r.days_of_stock !== undefined);
  const noSales = rows.filter((r) => r.days_of_stock === null || r.days_of_stock === undefined);
  return {
    bars: [...withSales].sort((a, b) => b.days_of_stock - a.days_of_stock),
    noSales,
  };
}

// Default turnover window: the 30 days ending on the UTC date, matching the backend.
export function defaultWindow(days = 30, now = new Date()) {
  const end = now.toISOString().slice(0, 10);
  const startDate = new Date(now.getTime() - (days - 1) * 24 * 60 * 60 * 1000);
  return { start: startDate.toISOString().slice(0, 10), end };
}
