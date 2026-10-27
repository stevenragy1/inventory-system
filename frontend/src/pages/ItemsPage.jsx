import { useCallback, useEffect, useState } from "react";
import { Alert, Badge, Button, Table } from "react-bootstrap";
import { api, ApiError } from "../api/client";
import ConfirmDialog from "../components/ConfirmDialog";
import ItemFormModal from "../components/ItemFormModal";

// Stock status uses text as well as color, so it reads without color.
function statusFor(item) {
  if (item.total < 0) return <Badge bg="danger">Negative</Badge>;
  if (item.total === 0) return <Badge bg="secondary">Out</Badge>;
  if (item.total <= item.reorder_level) return <Badge bg="warning" text="dark">Low</Badge>;
  return <Badge bg="success">In stock</Badge>;
}

export default function ItemsPage() {
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [toDeactivate, setToDeactivate] = useState(null);
  const [busy, setBusy] = useState(false);

  // Reload the table. Totals per item come from the item detail endpoint.
  const load = useCallback(async () => {
    try {
      const list = await api.getItems();
      const detailed = await Promise.all(list.map((i) => api.getItem(i.id)));
      setItems(detailed);
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    load();
    api.getCategories().then(setCategories).catch((e) => setError(e.message));
  }, [load]);

  const onSaved = (item) => {
    setShowForm(false);
    setNotice(`Saved ${item.sku}.`);
    load();
  };

  const confirmDeactivate = async () => {
    setBusy(true);
    try {
      await api.deactivateItem(toDeactivate.id);
      setNotice(`${toDeactivate.sku} is now inactive. Its history is kept.`);
      setToDeactivate(null);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not deactivate the item.");
      setToDeactivate(null);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
        <h1 className="h3 mb-0">Items</h1>
        <Button onClick={() => { setNotice(null); setShowForm(true); }}>New item</Button>
      </div>

      {notice && <Alert variant="success" dismissible onClose={() => setNotice(null)}>{notice}</Alert>}
      {error && <Alert variant="danger" dismissible onClose={() => setError(null)}>{error}</Alert>}

      <div className="table-responsive">
        <Table hover className="align-middle">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Item</th>
              <th>Category</th>
              <th className="text-end">Main Warehouse</th>
              <th className="text-end">Showroom</th>
              <th className="text-end">Total</th>
              <th>Status</th>
              <th><span className="visually-hidden">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const qty = (name) =>
                item.levels.find((l) => l.location === name)?.quantity ?? 0;
              return (
                <tr key={item.id}>
                  <td><code>{item.sku}</code></td>
                  <td>{item.name}</td>
                  <td>{item.category}</td>
                  <td className="text-end">{qty("Main Warehouse")}</td>
                  <td className={`text-end ${qty("Showroom") < 0 ? "text-danger fw-semibold" : ""}`}>
                    {qty("Showroom")}
                  </td>
                  <td className="text-end">{item.total}</td>
                  <td>{statusFor(item)}</td>
                  <td className="text-end">
                    <Button size="sm" variant="outline-danger"
                      onClick={() => setToDeactivate(item)}>
                      Deactivate
                    </Button>
                  </td>
                </tr>
              );
            })}
            {items.length === 0 && (
              <tr>
                <td colSpan={8} className="text-center text-muted py-4">No active items yet.</td>
              </tr>
            )}
          </tbody>
        </Table>
      </div>

      <ItemFormModal
        show={showForm}
        categories={categories}
        onSaved={onSaved}
        onCancel={() => setShowForm(false)}
      />

      <ConfirmDialog
        show={!!toDeactivate}
        title="Deactivate item?"
        message={toDeactivate
          ? `${toDeactivate.sku} will be hidden from the lists and can no longer receive or issue stock. Its movement history stays.`
          : ""}
        confirmLabel="Deactivate"
        busy={busy}
        onConfirm={confirmDeactivate}
        onCancel={() => setToDeactivate(null)}
      />
    </>
  );
}
