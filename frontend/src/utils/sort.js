// Sort rows by one column. Null or undefined values always sort last,
// whichever direction is chosen, so "n/a" rows do not jump to the top.
// Returns a new array; the input is not changed.
export function sortRows(rows, key, direction = "asc") {
  const factor = direction === "desc" ? -1 : 1;
  return [...rows].sort((a, b) => {
    const x = a[key];
    const y = b[key];
    const xMissing = x === null || x === undefined;
    const yMissing = y === null || y === undefined;
    if (xMissing && yMissing) return 0;
    if (xMissing) return 1;
    if (yMissing) return -1;
    if (typeof x === "string") return x.localeCompare(y) * factor;
    return (x - y) * factor;
  });
}
