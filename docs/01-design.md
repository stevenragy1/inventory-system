# 01 · Design

## Goal

Manage inventory records and stock levels for a company that sells cups and bottles, from two locations: the Main Warehouse and the Showroom. The software is general, so it works for any business that stocks items in several places.

## Requirements

| ID | Requirement | Feature |
|---|---|---|
| FR-1 | Create, edit, and deactivate items (SKU, name, category, unit cost, reorder level) | Inventory tracking |
| FR-2 | Organise items into categories (Cups, Bottles) | Inventory tracking |
| FR-3 | Track stock per item per location | Inventory tracking |
| FR-4 | Record stock-in, stock-out, and adjustments, each with a reason | Stock updates |
| FR-5 | A stock-out beyond the available quantity shows a warning; on confirmation it is recorded with `over_issue = true` | Stock updates |
| FR-6 | Movement history is append-only | Stock updates |
| FR-7 | Search by name or SKU; filter by category, location, and status | Search and filter |
| FR-8 | Reports: valuation, low stock, negative stock, movement history, stock turnover | Reports dashboard |
| FR-9 | Dashboard with totals, charts, negative-stock alerts with a correction action, and a turnover chart | Reports dashboard |

**Non-functional goals**

- A stock level always equals the sum of its movements.
- Each stock change runs in one database transaction.
- Business rules live only in the Python service layer.
- Every movement records what changed, when, and why.
- The layout is responsive at phone, tablet, and desktop widths.

## Architecture

```
React frontend (Vite)                 Flask API (Python)                 SQLite
pages → components → api/client  →  routes /api  →  services  →  repositories  →  database
                                                    (rules)       (SQL only)
```

- The frontend shows results and warnings. It contains no business rules.
- Services enforce the rules and are the only code that writes data.
- Repositories hold all SQL. Reports and search only read.

## Data model

| Table | Key fields | Notes |
|---|---|---|
| `category` | `id`, `name` (unique) | Cups, Bottles |
| `location` | `id`, `name` (unique) | Main Warehouse, Showroom |
| `item` | `id`, `sku` (unique), `name`, `category_id`, `unit_cost_cents`, `reorder_level`, `is_active` | Deactivated, never deleted |
| `stock_level` | `item_id` + `location_id` (primary key), `quantity` | Current quantity; may be negative |
| `stock_movement` | `id`, `item_id`, `location_id`, `movement_type` (IN, OUT, ADJUST), `quantity_change`, `reason`, `over_issue`, `created_at` | Append-only history |

**Constraints in the database**

- `quantity_change` cannot be zero.
- IN must be positive, OUT must be negative. ADJUST may be either.
- Foreign keys are enforced.
- SKUs are unique.

**Indexes:** `item.category_id`, and `stock_movement(item_id, created_at)`.

## Key decisions

| Decision | Reason |
|---|---|
| Keep both `stock_level` and `stock_movement` | Levels give fast reads; movements give an audit trail. Step 5 checks they agree. |
| Store unit cost as whole cents | Avoids rounding errors in totals |
| Store SKUs in upper case | Makes duplicates easy to detect |
| Over-issue is a warning, not a block | The business may still sell; the record shows it happened |
| Negative levels are allowed and flagged | The count may be wrong; the system shows the gap instead of hiding it |
| Corrections are new ADJUST rows | The history keeps the original sale and the fix |
| Items are deactivated, not deleted | Deleting would break the history |
| Warning uses HTTP 409 and a confirm flag | The backend enforces the rule; the UI only asks |

## Stock turnover (design)

- Units sold = OUT quantity in the period.
- Average stock = (opening stock + closing stock) ÷ 2.
- Turnover ratio = units sold ÷ average stock.
- Days of stock on hand = days in the period ÷ turnover ratio.

When there is no average stock or no sales, the ratio shows "n/a".

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET / POST | `/api/items` | List or create items |
| GET | `/api/items/<id>` | Item with levels per location |
| POST | `/api/items/<id>/deactivate` | Deactivate an item |
| GET / POST | `/api/categories`, `/api/locations` | List or create categories and locations |
| POST | `/api/stock/receive`, `/api/stock/issue`, `/api/stock/adjust` | Stock changes |
| GET | `/api/movements` | Movement history |
| GET | `/api/search` | Search and filter |
| GET | `/api/reports/valuation`, `low-stock`, `negative-stock`, `movements`, `turnover` | Reports |
| GET | `/api/dashboard` | Dashboard totals and chart data |

## Demo data

Six items across two categories, and two locations. Stock is set so that every feature appears on first run: one negative level (glass bottles at the Showroom, −30), low stock (travel mug at the Warehouse), and out-of-stock items.

## Module responsibilities

| Module | Responsibility |
|---|---|
| Catalog | Items, categories, locations |
| Stock | Receive, issue (with warning), adjust, consistency check |
| Search | Filters and stock status |
| Reports | Valuation, low and negative stock, movements, turnover, dashboard |
| Web | Pages, forms, modals, charts |
