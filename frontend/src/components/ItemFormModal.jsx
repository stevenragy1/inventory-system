import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import { api, ApiError } from "../api/client";
import { toItemPayload, validateItemForm } from "../utils/validation";

const EMPTY = { sku: "", name: "", category_id: "", unit_cost: "", reorder_level: "" };

// Create a new item. Calls onSaved with the created item.
export default function ItemFormModal({ show, categories, onSaved, onCancel }) {
  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (show) {
      setValues(EMPTY);
      setErrors({});
      setServerError(null);
    }
  }, [show]);

  const update = (field) => (e) => {
    setValues({ ...values, [field]: e.target.value });
    // Clear the message for a field as soon as the user edits it.
    if (errors[field]) setErrors({ ...errors, [field]: undefined });
  };

  const submit = async (e) => {
    e.preventDefault();
    const found = validateItemForm(values);
    setErrors(found);
    if (Object.keys(found).length > 0) return;

    setSaving(true);
    setServerError(null);
    try {
      const item = await api.createItem(toItemPayload(values));
      onSaved(item);
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Could not save the item.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal show={show} onHide={onCancel} centered>
      <Form onSubmit={submit} noValidate>
        <Modal.Header closeButton>
          <Modal.Title as="h2" className="h5">New item</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {serverError && <Alert variant="danger">{serverError}</Alert>}

          <Form.Group className="mb-3" controlId="item-sku">
            <Form.Label>SKU</Form.Label>
            <Form.Control value={values.sku} onChange={update("sku")}
              isInvalid={!!errors.sku} placeholder="e.g. CUP-CER-004" />
            <Form.Control.Feedback type="invalid">{errors.sku}</Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3" controlId="item-name">
            <Form.Label>Name</Form.Label>
            <Form.Control value={values.name} onChange={update("name")}
              isInvalid={!!errors.name} />
            <Form.Control.Feedback type="invalid">{errors.name}</Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3" controlId="item-category">
            <Form.Label>Category</Form.Label>
            <Form.Select value={values.category_id} onChange={update("category_id")}
              isInvalid={!!errors.category_id}>
              <option value="">Choose a category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">{errors.category_id}</Form.Control.Feedback>
          </Form.Group>

          <div className="row g-3">
            <div className="col-6">
              <Form.Group controlId="item-cost">
                <Form.Label>Unit cost</Form.Label>
                <Form.Control inputMode="decimal" value={values.unit_cost}
                  onChange={update("unit_cost")} isInvalid={!!errors.unit_cost}
                  placeholder="2.50" />
                <Form.Control.Feedback type="invalid">{errors.unit_cost}</Form.Control.Feedback>
              </Form.Group>
            </div>
            <div className="col-6">
              <Form.Group controlId="item-reorder">
                <Form.Label>Reorder level</Form.Label>
                <Form.Control type="number" min="0" step="1" value={values.reorder_level}
                  onChange={update("reorder_level")} isInvalid={!!errors.reorder_level} />
                <Form.Control.Feedback type="invalid">{errors.reorder_level}</Form.Control.Feedback>
              </Form.Group>
            </div>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onCancel}>Cancel</Button>
          <Button type="submit" disabled={saving}>{saving ? "Saving…" : "Save item"}</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
