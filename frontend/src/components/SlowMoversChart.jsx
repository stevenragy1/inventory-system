import { Bar } from "react-chartjs-2";
import { SERIES_COLORS } from "../charts";

// Horizontal bars: days of stock on hand for the slowest-moving items.
// Items with no sales are listed in text, because they have no bar to draw.
export default function SlowMoversChart({ bars, noSales }) {
  const height = Math.max(bars.length * 40 + 80, 160);
  const summary = bars.map((b) => `${b.sku} ${b.days_of_stock} days`).join("; ");

  return (
    <div>
      {bars.length === 0 ? (
        <p className="text-muted mb-0">No items have sales in this window yet.</p>
      ) : (
        <div style={{ position: "relative", width: "100%", height }}>
          <Bar
            data={{
              labels: bars.map((b) => b.sku),
              datasets: [{
                label: "Days of stock",
                data: bars.map((b) => b.days_of_stock),
                backgroundColor: SERIES_COLORS[1],
                borderRadius: 4,
              }],
            }}
            options={{
              indexAxis: "y",
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { display: false } },
              scales: { x: { title: { display: true, text: "Days of stock on hand" } } },
            }}
            role="img"
            aria-label={`Slowest-moving items, days of stock on hand. ${summary}`}
          />
        </div>
      )}
      {noSales.length > 0 && (
        <p className="small text-muted mt-2 mb-0">
          No sales in this window: {noSales.map((r) => r.sku).join(", ")}.
        </p>
      )}
    </div>
  );
}
