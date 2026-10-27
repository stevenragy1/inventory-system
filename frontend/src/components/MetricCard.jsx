import { Card } from "react-bootstrap";

// A single summary number with a label. tone colors the number and adds text cues elsewhere.
export default function MetricCard({ label, value, tone }) {
  const color = tone === "danger" ? "text-danger" : tone === "warning" ? "text-warning-emphasis" : "";
  return (
    <Card body className="h-100">
      <div className="small text-muted">{label}</div>
      <div className={`h3 mb-0 ${color}`}>{value}</div>
    </Card>
  );
}
