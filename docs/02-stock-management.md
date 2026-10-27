# 02 · Stock management

## Goal

Build the core of the system: items, locations, and the three stock actions (receive, issue, adjust), with the over-issue warning and the correction flow.

## What was built

### Backend

- **Database** (`app/db.py`): the schema from `01-design.md`, and a `transaction()` helper.
- **Repositories** (`app/repositories/`): all SQL for items, locations, stock levels, and movements.
- **Services** (`app/services/`):
  - `CatalogService`: create and list categories and locations; create, read, list, and deactivate items.
  - `StockService`: receive, issue, adjust, the consistency check, and history.
- **Errors** (`app/errors.py`): `DomainError`, `NotFoundError`, `DuplicateError`, and `OverIssueWarning`.
- **API** (`app/api/__init__.py`): item, category, location, stock, and movement routes.
- **Seed** (`seed.py`): resets the database and loads the demo data through the services.

### Frontend

- **Items page**: lists active items with quantities per location, a status badge, and a **Deactivate** action with confirmation. A **New item** form validates each field before sending.
- **Stock updates page**: tabs for Receive, Issue, and Adjust.
- **Over-issue modal**: shown when the backend returns the warning. **Continue anyway** resubmits with `confirm: true`.

## Rules implemented

| Rule | Where it is enforced |
|---|---|
| Quantities for receive and issue are whole numbers above zero | `StockService` |
| Adjustments are whole numbers and not zero | `StockService` |
| Every change needs a reason | `StockService` |
| Only active items accept stock | `StockService` |
| A stock-out below zero returns a warning and writes nothing | `StockService.issue_stock` |
| A confirmed stock-out below zero is recorded with `over_issue = true` | `StockService.issue_stock` |
| Each change writes the level and the movement in one transaction | `transaction()` |
| SKUs are unique and stored in upper case | `CatalogService.create_item` |
| Unit cost is zero or more, in whole cents | `CatalogService.create_item` |

## Tests

Backend (`tests/test_stock_service.py`, `tests/test_api.py`), 22 tests:

- Catalog: unique SKUs, deactivated items refuse stock, unknown locations are rejected.
- Stock in: levels and movements are recorded; zero or negative quantities are refused; a reason is required.
- Stock out: a normal issue needs no confirmation; over-issue warns and writes nothing; a confirmed over-issue goes negative and is flagged; issuing exactly to zero is not an over-issue.
- Adjustments: a correction clears a negative level; zero is refused.
- Accuracy: mixed activity keeps every level equal to its movements; a failed warning leaves the books unchanged.
- API: item creation, duplicate SKUs, validation errors, deactivation, and the warning flow over HTTP.

Frontend (Vitest and Testing Library), tests for:

- `money.js`: converting typed amounts to cents, and rejecting bad text.
- `validation.js`: required fields, price and reorder rules, and the payload sent to the API.
- `OverIssueModal`: shows the amounts; confirm and cancel call the right handlers.
- `ItemFormModal`: shows errors without calling the API; sends cents; shows the server message for a duplicate SKU.

## Results

- Backend: 22 tests pass.
- Frontend: 16 tests pass (at the end of Step 2).

## Decisions and reasons

| Decision | Reason |
|---|---|
| Over-issue is a warning, not a block | The business may still sell; the record shows the gap |
| Cents, not decimals | Avoids rounding errors |
| Deactivate, never delete | Keeps the history intact |
