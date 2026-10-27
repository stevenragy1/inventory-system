import { useEffect, useState } from "react";
import { Alert, Button, Card, Col, Form, Row, Tab, Tabs } from "react-bootstrap";
import { api, ApiError } from "../api/client";
import OverIssueModal from "../components/OverIssueModal";

const ACTIONS = {
  receive: { label: "Receive", reasonHint: "e.g. Supplier delivery #118" },
  issue: { label: "Issue", reasonHint: "e.g. Customer sale #2281" },
  adjust: { label: "Adjust", reasonHint: "e.g. Stock count" },
};

export default function StockPage() {
  const [items, setItems] = useState([]);
  const [locations, setLocations] = useState([]);
  const [action, setAction] = useState("receive");
  const [form, setForm] = useState({ item_id: "", location_id: "", quantity: "", reason: "" });
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [warning, setWarning] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([api.getItems(), api.getLocations()])
      .then(([i, l]) => {
        setItems(i);
        setLocations(l);
      })
      .catch((e) => setError(e.message));
  }, []);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  // Build the request body for the chosen action.
  const payloadFor = (confirm) => {
    const base = {
      item_id: Number(form.item_id),
      location_id: Number(form.location_id),
      reason: form.reason,
    };
    if (action === "adjust") return { ...base, delta: Number(form.quantity) };
    if (action === "issue") return { ...base, quantity: Number(form.quantity), confirm };
    return { ...base, quantity: Number(form.quantity) };
  };

  const send = async (confirm = false) => {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const result = await api[action](payloadFor(confirm));
      setMessage(`Saved. New quantity at this location: ${result.quantity}.`);
      setWarning(null);
      setForm({ ...form, quantity: "", reason: "" });
    } catch (err) {
      if (err instanceof ApiError && err.body?.warning) {
        setWarning(err.body);
      } else {
        setError(err.message);
      }
    } finally {
      setBusy(false);
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    send(false);
  };

  return (
    <>
      <h1 className="h3 mb-3">Stock updates</h1>

      {message && <Alert variant="success">{message}</Alert>}
      {error && <Alert variant="danger">{error}</Alert>}

      <Card body>
        <Tabs activeKey={action} onSelect={(k) => setAction(k)} className="mb-3">
          {Object.entries(ACTIONS).map(([key, { label }]) => (
            <Tab eventKey={key} title={label} key={key} />
          ))}
        </Tabs>

        <Form onSubmit={onSubmit}>
          <Row className="g-3">
            <Col xs={12} md={6}>
              <Form.Group controlId="item">
                <Form.Label>Item</Form.Label>
                <Form.Select value={form.item_id} onChange={update("item_id")} required>
                  <option value="">Choose an item</option>
                  {items.map((i) => (
                    <option key={i.id} value={i.id}>{i.sku} · {i.name}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col xs={12} md={6}>
              <Form.Group controlId="location">
                <Form.Label>Location</Form.Label>
                <Form.Select value={form.location_id} onChange={update("location_id")} required>
                  <option value="">Choose a location</option>
                  {locations.map((l) => (
                    <option key={l.id} value={l.id}>{l.name}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col xs={12} md={4}>
              <Form.Group controlId="quantity">
                <Form.Label>{action === "adjust" ? "Change (+ or −)" : "Quantity"}</Form.Label>
                <Form.Control
                  type="number"
                  step="1"
                  min={action === "adjust" ? undefined : 1}
                  value={form.quantity}
                  onChange={update("quantity")}
                  required
                />
              </Form.Group>
            </Col>
            <Col xs={12} md={8}>
              <Form.Group controlId="reason">
                <Form.Label>Reason</Form.Label>
                <Form.Control
                  value={form.reason}
                  onChange={update("reason")}
                  placeholder={ACTIONS[action].reasonHint}
                  required
                />
              </Form.Group>
            </Col>
          </Row>
          <div className="mt-3 d-flex justify-content-end">
            <Button type="submit" disabled={busy}>
              {busy ? "Saving…" : `Save ${ACTIONS[action].label.toLowerCase()}`}
            </Button>
          </div>
        </Form>
      </Card>

      <OverIssueModal
        warning={warning}
        onCancel={() => setWarning(null)}
        onConfirm={() => {
          setWarning(null);
          send(true);
        }}
      />
    </>
  );
}
