// Convert a money string typed by the user (e.g. "2.50") into whole cents (250).
// Returns null when the text is not a valid non-negative amount.
// Cents avoid floating-point rounding errors in totals.
export function toCents(text) {
  const value = String(text ?? "").trim();
  if (!/^\d+(\.\d{1,2})?$/.test(value)) return null;
  const [whole, fraction = ""] = value.split(".");
  return Number(whole) * 100 + Number(fraction.padEnd(2, "0"));
}

// Format whole cents for display, e.g. 250 -> "2.50".
export function fromCents(cents) {
  return (Number(cents) / 100).toFixed(2);
}
