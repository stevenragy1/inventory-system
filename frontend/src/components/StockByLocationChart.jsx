import { Bar } from "react-chartjs-2";
import { SERIES_COLORS } from "../charts";

// Quantity per item, one bar per location. Negative bars show below zero.
export default function StockByLocationChart({ data }) {
  const datasets = data.series.map((s, i) => ({
    label: s.location,
    data: s.data,
    backgroundColor: SERIES_COLORS[i % SERIES_COLORS.length],
    borderRadius: 4,
  }));

  const summary = data.series
    .map((s) => `${s.location}: ${s.data.join(", ")}`)
    .join("; ");

  return (
    <div>
      <div className="d-flex flex-wrap gap-3 mb-2 small text-muted" aria-hidden="true">
        {data.series.map((s, i) => (
          <span key={s.location} className="d-flex align-items-center gap-1">
            <span style={{
              width: 10, height: 10, borderRadius: 2,
              background: SERIES_COLORS[i % SERIES_COLORS.length], display: "inline-block",
            }} />
            {s.location}
          </span>
        ))}
      </div>
      <div style={{ position: "relative", width: "100%", height: 300 }}>
        <Bar
          data={{ labels: data.labels, datasets }}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { ticks: { autoSkip: false, maxRotation: 45 }, grid: { display: false } },
              y: { title: { display: true, text: "Units" } },
            },
          }}
          role="img"
          aria-label={`Stock by item and location. ${summary}`}
        />
      </div>
    </div>
  );
}
