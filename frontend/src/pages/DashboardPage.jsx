import { useCallback, useEffect, useMemo, useState } from "react";
import { Alert, Button, Card, Col, Row, Table } from "react-bootstrap";
import { api } from "../api/client";
import CorrectionModal from "../components/CorrectionModal";
import MetricCard from "../components/MetricCard";
import SlowMoversChart from "../components/SlowMoversChart";
import StockByLocationChart from "../components/StockByLocationChart";
import { splitSlowMovers } from "../utils/dashboard";
import { fromCents } from "../utils/money";

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [correcting, setCorrecting] = useState(null);

  const load = useCallback(() => {
    api.getDashboard()
      .then((d) => {
        setData(d);
        setError(null);
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const slow = useMemo(
    () => (data ? splitSlowMovers(data.chart_slow_movers) : { bars: [], noSales: [] }),
    [data],
  );

  if (!data && !error) return <p className="text-muted">Loading the dashboard…</p>;

  return (
    <>
      <h1 className="h3 mb-3">Dashboard</h1>

      {notice && <Alert variant="success" dismissible onClose={() => setNotice(null)}>{notice}</Alert>}
      {error && <Alert variant="danger">{error}</Alert>}

      {data && (
        <>
          <Row className="g-3 mb-4">
            <Col xs={6} md={4} xl={2}>
              <MetricCard label="Active items" value={data.totals.active_items} />
            </Col>
            <Col xs={6} md={4} xl={2}>
              <MetricCard label="Units on hand" value={data.totals.total_units} />
            </Col>
            <Col xs={6} md={4} xl={2}>
              <MetricCard label="Stock value" value={fromCents(data.totals.total_value_cents)} />
            </Col>
            <Col xs={6} md={4} xl={2}>
              <MetricCard label="Low stock" value={data.totals.low_stock_count} tone="warning" />
            </Col>
            <Col xs={6} md={4} xl={2}>
              <MetricCard label="Out of stock" value={data.totals.out_count} />
            </Col>
            <Col xs={6} md={4} xl={2}>
              <MetricCard label="Negative levels" value={data.totals.negative_count}
                tone={data.totals.negative_count > 0 ? "danger" : undefined} />
            </Col>
          </Row>

          {data.alerts_negative.length > 0 && (
            <Alert variant="danger" className="mb-4">
              <Alert.Heading as="h2" className="h5">Negative stock</Alert.Heading>
              <p className="mb-2">
                These levels are below zero. Record a correction once a stock count is done.
              </p>
              <Table size="sm" className="mb-0 bg-white">
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th>Location</th>
                    <th className="text-end">Quantity</th>
                    <th><span className="visually-hidden">Action</span></th>
                  </tr>
                </thead>
                <tbody>
                  {data.alerts_negative.map((a) => (
                    <tr key={`${a.item_id}-${a.location_id}`}>
                      <td><code>{a.sku}</code></td>
                      <td>{a.location}</td>
                      <td className="text-end text-danger fw-semibold">{a.quantity}</td>
                      <td className="text-end">
                        <Button size="sm" variant="outline-dark" onClick={() => setCorrecting(a)}>
                          Record correction
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Alert>
          )}

          <Row className="g-3 mb-4">
            <Col lg={7}>
              <Card body className="h-100">
                <h2 className="h6">Stock by item and location</h2>
                {data.chart_stock_by_location.labels.length === 0 ? (
                  <p className="text-muted mb-0">No items yet.</p>
                ) : (
                  <StockByLocationChart data={data.chart_stock_by_location} />
                )}
              </Card>
            </Col>
            <Col lg={5}>
              <Card body className="h-100">
                <h2 className="h6">Slowest movers (days of stock on hand)</h2>
                <SlowMoversChart bars={slow.bars} noSales={slow.noSales} />
              </Card>
            </Col>
          </Row>

          <Card body>
            <h2 className="h6">Low stock</h2>
            {data.low_stock.length === 0 ? (
              <p className="text-muted mb-0">Nothing is at or below its reorder level.</p>
            ) : (
              <div className="table-responsive">
                <Table size="sm" className="mb-0 align-middle">
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Item</th>
                      <th>Location</th>
                      <th className="text-end">Quantity</th>
                      <th className="text-end">Reorder level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.low_stock.map((r) => (
                      <tr key={`${r.item_id}-${r.location_id}`}>
                        <td><code>{r.sku}</code></td>
                        <td>{r.name}</td>
                        <td>{r.location}</td>
                        <td className="text-end">{r.quantity}</td>
                        <td className="text-end">{r.reorder_level}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            )}
          </Card>
        </>
      )}

      <CorrectionModal
        alert={correcting}
        onCancel={() => setCorrecting(null)}
        onSaved={() => {
          setCorrecting(null);
          setNotice("Correction recorded. The history shows both the original sale and the fix.");
          load();
        }}
      />
    </>
  );
}
