import { useEffect, useState } from "react";
import { Alert, Badge, Card, Col, Form, Row, Table } from "react-bootstrap";
import { api } from "../api/client";
import { buildSearchParams, STATUS_OPTIONS } from "../utils/search";

const EMPTY_FILTERS = { q: "", category_id: "", location_id: "", status: "" };

// Status uses text as well as color, so it reads without color.
function StatusBadge({ status }) {
  const labels = {
    in_stock: { text: "In stock", bg: "success" },
    low: { text: "Low", bg: "warning", fg: "dark" },
    out: { text: "Out", bg: "secondary" },
    negative: { text: "Negative", bg: "danger" },
  };
  const s = labels[status] || { text: status, bg: "light" };
  return <Badge bg={s.bg} text={s.fg}>{s.text}</Badge>;
}

export default function SearchPage() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [categories, setCategories] = useState([]);
  const [locations, setLocations] = useState([]);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.getCategories(), api.getLocations()])
      .then(([c, l]) => {
        setCategories(c);
        setLocations(l);
      })
      .catch((e) => setError(e.message));
  }, []);

  // Search again whenever a filter changes. Typing waits briefly so each
  // keystroke does not send a request.
  useEffect(() => {
    let cancelled = false;
    const wait = setTimeout(() => {
      api.search(buildSearchParams(filters))
        .then((rows) => {
          if (!cancelled) {
            setResults(rows);
            setError(null);
          }
        })
        .catch((e) => {
          if (!cancelled) setError(e.message);
        });
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(wait);
    };
  }, [filters]);

  const update = (field) => (e) => setFilters({ ...filters, [field]: e.target.value });

  return (
    <>
      <h1 className="h3 mb-3">Search items</h1>

      <Card body className="mb-4">
        <Row className="g-3">
          <Col xs={12} md={6} lg={4}>
            <Form.Group controlId="search-text">
              <Form.Label>Name or SKU</Form.Label>
              <Form.Control value={filters.q} onChange={update("q")}
                placeholder="e.g. glass or BTL-" />
            </Form.Group>
          </Col>
          <Col xs={6} md={3} lg={2}>
            <Form.Group controlId="search-category">
              <Form.Label>Category</Form.Label>
              <Form.Select value={filters.category_id} onChange={update("category_id")}>
                <option value="">All categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col xs={6} md={3} lg={3}>
            <Form.Group controlId="search-location">
              <Form.Label>Location</Form.Label>
              <Form.Select value={filters.location_id} onChange={update("location_id")}>
                <option value="">All locations</option>
                {locations.map((l) => (
                  <option key={l.id} value={l.id}>{l.name}</option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col xs={12} lg={3}>
            <Form.Group controlId="search-status">
              <Form.Label>Stock status</Form.Label>
              <Form.Select value={filters.status} onChange={update("status")}>
                {STATUS_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
        </Row>
        <p className="small text-muted mt-3 mb-0">
          With a location chosen, the status applies to that location. Without one,
          an item is negative if any location is negative; otherwise the total is used.
        </p>
      </Card>

      {error && <Alert variant="danger">{error}</Alert>}

      {results === null ? (
        <p className="text-muted">Searching…</p>
      ) : (
        <>
          <p className="mb-2 text-muted small">
            {results.length} {results.length === 1 ? "item" : "items"} found
          </p>
          {results.length === 0 ? (
            <Alert variant="light">No items match these filters. Try clearing one of them.</Alert>
          ) : (
            <div className="table-responsive">
              <Table hover size="sm" className="align-middle">
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th>Item</th>
                    <th>Category</th>
                    {locations.map((l) => (
                      <th key={l.id} className="text-end">{l.name}</th>
                    ))}
                    <th className="text-end">Total</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r) => (
                    <tr key={r.item_id}>
                      <td><code>{r.sku}</code></td>
                      <td>{r.name}</td>
                      <td>{r.category}</td>
                      {locations.map((loc) => {
                        const qty = r.levels.find((l) => l.location_id === loc.id)?.quantity ?? 0;
                        return (
                          <td key={loc.id}
                            className={`text-end ${qty < 0 ? "text-danger fw-semibold" : ""}`}>
                            {qty}
                          </td>
                        );
                      })}
                      <td className="text-end">{r.total}</td>
                      <td><StatusBadge status={r.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </>
      )}
    </>
  );
}
