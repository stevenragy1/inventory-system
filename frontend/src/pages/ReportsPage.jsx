import { useEffect, useMemo, useState } from "react";
import { Alert, Button, Card, Col, Form, Table, Tab, Tabs } from "react-bootstrap";
import { api } from "../api/client";
import { defaultWindow } from "../utils/dashboard";
import { fromCents } from "../utils/money";
import { sortRows } from "../utils/sort";

const shown = (value) => (value === null || value === undefined ? "n/a" : value);

function ValuationTab() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getValuation().then(setReport).catch((e) => setError(e.message));
  }, []);

  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!report) return <p className="text-muted">Loading…</p>;

  return (
    <>
      <p className="mb-3">
        Total stock value: <strong>{fromCents(report.total_value_cents)}</strong>.
        Negative levels reduce the total.
      </p>
      <div className="table-responsive">
        <Table hover size="sm" className="align-middle">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Item</th>
              <th>Location</th>
              <th className="text-end">Quantity</th>
              <th className="text-end">Unit cost</th>
              <th className="text-end">Value</th>
            </tr>
          </thead>
          <tbody>
            {report.rows.map((r) => (
              <tr key={`${r.item_id}-${r.location}`}>
                <td><code>{r.sku}</code></td>
                <td>{r.name}</td>
                <td>{r.location}</td>
                <td className={`text-end ${r.quantity < 0 ? "text-danger fw-semibold" : ""}`}>{r.quantity}</td>
                <td className="text-end">{fromCents(r.unit_cost_cents)}</td>
                <td className="text-end">{fromCents(r.value_cents)}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
    </>
  );
}

function DateRange({ start, end, onChange, onApply }) {
  return (
    <Form className="row g-2 align-items-end mb-3" onSubmit={(e) => { e.preventDefault(); onApply(); }}>
      <Col xs={6} md="auto">
        <Form.Group controlId="report-start">
          <Form.Label>From</Form.Label>
          <Form.Control type="date" value={start} onChange={(e) => onChange({ start: e.target.value, end })} />
        </Form.Group>
      </Col>
      <Col xs={6} md="auto">
        <Form.Group controlId="report-end">
          <Form.Label>To</Form.Label>
          <Form.Control type="date" value={end} onChange={(e) => onChange({ start, end: e.target.value })} />
        </Form.Group>
      </Col>
      <Col xs="auto">
        <Button type="submit">Apply</Button>
      </Col>
    </Form>
  );
}

function MovementsTab() {
  const initial = defaultWindow(30);
  const [range, setRange] = useState(initial);
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(null);

  const load = (r) => {
    setError(null);
    api.getReportMovements(r.start, r.end)
      .then(setRows)
      .catch((e) => setError(e.message));
  };

  useEffect(() => {
    load(initial);
    // Load once on first view; Apply reloads for a new range.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <DateRange start={range.start} end={range.end} onChange={setRange} onApply={() => load(range)} />
      {error && <Alert variant="danger">{error}</Alert>}
      {!rows ? <p className="text-muted">Loading…</p> : (
        rows.length === 0 ? <p className="text-muted">No movements in this range.</p> : (
          <div className="table-responsive">
            <Table hover size="sm" className="align-middle">
              <thead>
                <tr>
                  <th>When (UTC)</th>
                  <th>SKU</th>
                  <th>Location</th>
                  <th>Type</th>
                  <th className="text-end">Change</th>
                  <th>Reason</th>
                  <th>Flag</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((m) => (
                  <tr key={m.id}>
                    <td className="small">{m.created_at.replace("T", " ").slice(0, 16)}</td>
                    <td><code>{m.sku}</code></td>
                    <td>{m.location}</td>
                    <td>{m.movement_type}</td>
                    <td className={`text-end ${m.quantity_change < 0 ? "text-danger" : ""}`}>
                      {m.quantity_change > 0 ? `+${m.quantity_change}` : m.quantity_change}
                    </td>
                    <td>{m.reason}</td>
                    <td>{m.over_issue ? <span className="badge bg-warning text-dark">Over-issue</span> : null}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        )
      )}
    </>
  );
}

const TURNOVER_COLUMNS = [
  { key: "sku", label: "SKU" },
  { key: "name", label: "Item" },
  { key: "units_sold", label: "Units sold", numeric: true },
  { key: "average_stock", label: "Average stock", numeric: true },
  { key: "turnover", label: "Turnover", numeric: true },
  { key: "days_of_stock", label: "Days of stock", numeric: true },
];

function TurnoverTab() {
  const initial = defaultWindow(30);
  const [range, setRange] = useState(initial);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [sort, setSort] = useState({ key: "sku", direction: "asc" });

  const load = (r) => {
    setError(null);
    api.getTurnover(r.start, r.end)
      .then(setReport)
      .catch((e) => setError(e.message));
  };

  useEffect(() => {
    load(initial);
    // Load once on first view; Apply reloads for a new range.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sorted = useMemo(
    () => (report ? sortRows(report.rows, sort.key, sort.direction) : []),
    [report, sort],
  );

  const toggleSort = (key) => {
    setSort((s) => ({
      key,
      direction: s.key === key && s.direction === "asc" ? "desc" : "asc",
    }));
  };

  return (
    <>
      <p className="small text-muted">
        Days of stock = days in the period ÷ turnover ratio. Turnover = units sold ÷ average stock.
        "n/a" means there was no stock or no sales to measure.
      </p>
      <DateRange start={range.start} end={range.end} onChange={setRange} onApply={() => load(range)} />
      {error && <Alert variant="danger">{error}</Alert>}
      {!report ? <p className="text-muted">Loading…</p> : (
        <div className="table-responsive">
          <Table hover size="sm" className="align-middle">
            <thead>
              <tr>
                {TURNOVER_COLUMNS.map((c) => (
                  <th key={c.key} className={c.numeric ? "text-end" : ""}>
                    <button
                      type="button"
                      className="btn btn-link p-0 text-decoration-none text-reset fw-semibold"
                      onClick={() => toggleSort(c.key)}
                      aria-label={`Sort by ${c.label}`}
                    >
                      {c.label}
                      {sort.key === c.key ? (sort.direction === "asc" ? " ▲" : " ▼") : ""}
                    </button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sorted.map((r) => (
                <tr key={r.item_id}>
                  <td><code>{r.sku}</code></td>
                  <td>{r.name}</td>
                  <td className="text-end">{r.units_sold}</td>
                  <td className="text-end">{r.average_stock}</td>
                  <td className="text-end">{shown(r.turnover)}</td>
                  <td className="text-end">{shown(r.days_of_stock)}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </>
  );
}

export default function ReportsPage() {
  return (
    <>
      <h1 className="h3 mb-3">Reports</h1>
      <Card body>
        <Tabs defaultActiveKey="turnover" className="mb-3">
          <Tab eventKey="turnover" title="Turnover">
            <TurnoverTab />
          </Tab>
          <Tab eventKey="valuation" title="Valuation">
            <ValuationTab />
          </Tab>
          <Tab eventKey="movements" title="Movement history">
            <MovementsTab />
          </Tab>
        </Tabs>
      </Card>
    </>
  );
}
