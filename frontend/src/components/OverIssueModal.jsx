import { Button, Modal } from "react-bootstrap";

// Shown when the backend answers a stock-out with a 409 warning.
// Nothing has been recorded yet; the user decides.
export default function OverIssueModal({ warning, onConfirm, onCancel }) {
  if (!warning) return null;
  return (
    <Modal show onHide={onCancel} centered>
      <Modal.Header closeButton>
        <Modal.Title as="h2" className="h5">Not enough stock</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p className="mb-2">
          Available: <strong>{warning.available}</strong>
        </p>
        <p className="mb-2">
          Requested: <strong>{warning.requested}</strong>
        </p>
        <p className="mb-0 text-muted">
          Continuing will take the level below zero. The movement will be
          recorded and flagged as an over-issue.
        </p>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onCancel} data-testid="over-issue-cancel">
          Cancel
        </Button>
        <Button variant="warning" onClick={onConfirm} data-testid="over-issue-confirm">
          Continue anyway
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
