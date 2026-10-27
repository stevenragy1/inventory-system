# 04 · Search and filter

## Goal

Let the user find items quickly by name, SKU, category, location, or stock status.

## What was built

### Backend

- **Search rules** (`app/services/search_service.py`):
  - Text matches the SKU or the name, case-insensitively. Blank text is ignored.
  - Category filters by category ID.
  - Location scopes the status to that location's quantity.
  - Status filter accepts `in_stock`, `low`, `out`, or `negative`. Any other value is refused.
- **API**: `GET /api/search` with optional `q`, `category_id`, `location_id`, and `status`.
- **Repository**: the search reuses the item-location grid from the reports, so the numbers match the other pages.

### Frontend

- **Search page**: four filters (text, category, location, status) that update results as you change them. Text waits 250 ms after typing before searching.
- **Results table**: SKU, item, category, a column per location, total, and a status badge with text, not colour alone.
- **Navigation**: a Search link in the navbar.

## Status rule

| Status | Meaning |
|---|---|
| Negative | Quantity below zero |
| Out | Quantity is zero |
| Low | Above zero and at or below the reorder level |
| In stock | Above the reorder level |

- **With a location chosen:** the status uses that location's quantity.
- **Without a location:** an item is negative if **any** location is negative, so the Negative filter finds every level that needs a correction. Otherwise the total across locations is used.

## Decision

A first version used only the total for the Negative filter. The glass bottles total 90 (120 at the Warehouse, −30 at the Showroom), so they were not found as negative. This was caught by the tests and corrected so that any negative level counts.

## Tests

Backend (`tests/test_search.py`), 14 tests:

- The status rule for each band.
- Text matching SKU and name, case-insensitively; blank text ignored.
- Category filter; status filters with and without a location.
- A location with no stock row counts as zero.
- Filters combine; no match returns an empty list.
- Each result lists its levels per location.
- An unknown status is refused; deactivated items are not found.

Frontend (`utils/search.test.js`), 4 tests: empty filters are left out; text is trimmed; the status options match the backend.

## Results

- Backend: 14 search tests pass.
- Frontend: the search query helper passes.
