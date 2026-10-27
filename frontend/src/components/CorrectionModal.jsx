import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import { api, ApiError } from "../api/client";

// Record a stock count correction (an ADJUST) for a negative level.
// Pre-fills the change needed to bring the level back to zero; the user can change it.
export default function CorrectionModal({ alert, onSaved, onCancel }) {
  const [delta, setDelta] = useState("");
  const [reason, setReason] = useState("Stock count correction");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (alert) {
      setDelta(String(-alert.quantity));
      setReason("Stock count correction");
      setError(null);
    }
  }, [alert]);

  if (!alert) return null;

  const submit = async (e) => {
    e.preventDefault();
    const change = Number(delta);
    if (!Number.isInteger(change) || change === 0) {
      setError("Enter a whole number that is not zero.");
      return;
    }
    if (!reason.trim()) {
      setError("A reason is required.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.adjust({
        item_id: alert.item_id,
        location_id: alert.location_id,
        delta: change,
        reason: reason.trim(),
      });
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not record the correction.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal show onHide={onCancel} centered>
      <Form onSubmit={submit} noValidate>
        <Modal.Header closeButton>
          <Modal.Title as="h2" className="h5">Record correction</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          <p className="mb-3">
            {alert.sku} at {alert.location} is at <strong>{alert.quantity}</strong>.
            Enter the change that matches your stock count.
          </p>
          <Form.Group className="mb-3" controlId="correction-delta">
            <Form.Label>Change (+ or −)</Form.Label>
            <Form.Control type="number" step="1" value={delta}
              onChange={(e) => setDelta(e.target.value)} />
          </Form.Group>
          <Form.Group controlId="correction-reason">
            <Form.Label>Reason</Form.Label>
            <Form.Control value={reason} onChange={(e) => setReason(e.target.value)} />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onCancel}>Cancel</Button>
          <Button type="submit" disabled={busy}>{busy ? "Saving…" : "Record correction"}</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
