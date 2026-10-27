# 03 · Reports and dashboard

## Goal

Turn the stock records into information: value, what needs reordering, what is wrong, how fast stock sells, and a dashboard that shows it at a glance.

## What was built

### Backend

- **Turnover formulas** (`app/reports/turnover.py`): pure functions, so they can be tested with known numbers.
- **Report queries** (`app/repositories/report_repo.py`): read-only SQL.
- **Report rules** (`app/services/report_service.py`):
  - **Valuation:** quantity × unit cost, per item and location, with a total.
  - **Low stock:** above zero and at or below the reorder level, per location.
  - **Negative stock:** every level below zero.
  - **Movement history:** optional item, location, and date filters.
  - **Turnover:** for every active item over a date range.
  - **Dashboard:** totals, chart data, negative-stock alerts, low-stock list, and the 10 slowest movers.
- **API**: `/api/reports/valuation`, `/api/reports/low-stock`, `/api/reports/negative-stock`, `/api/reports/movements`, `/api/reports/turnover`, and `/api/dashboard`.

### Frontend

- **Dashboard (home page)**:
  - Six metric cards.
  - A negative-stock alert with **Record correction**, which opens a form pre-filled to bring the level to zero and records an ADJUST.
  - A bar chart of stock per item and location.
  - A horizontal bar chart of the slowest movers.
  - A low-stock table.
- **Reports page** with three tabs:
  - **Turnover:** date range, sortable columns, and "n/a" where nothing can be measured.
  - **Valuation:** value per item and location, with the total.
  - **Movement history:** date range, with an over-issue badge.

## Formulas

- Units sold = total OUT quantity in the period.
- Average stock = (opening stock + closing stock) ÷ 2.
- Turnover ratio = units sold ÷ average stock.
- Days of stock on hand = days in the period ÷ turnover ratio.

**Worked example:** the Showroom sold 60 glass bottles in 30 days, and average stock was 120. Turnover = 60 ÷ 120 = 0.5. Days of stock = 30 ÷ 0.5 = 60. The owner holds about two months of glass bottles.

## Rules and decisions

| Decision | Reason |
|---|---|
| Low stock counts only above zero | Zero is reported as "out", so an item is not listed twice |
| Valuation counts negative levels as negative | The total then matches the books |
| The slowest-movers chart shows the most days of stock | The plan first said "fewest days", which would show fast sellers. The chart is meant to highlight slow movers, so this was corrected. |
| Items with no sales are listed as text under the chart | They have no ratio, so they cannot be drawn as bars |
| Dates use UTC | Movements are stored in UTC. Between midnight and 3 a.m. Cairo time, "today" is still yesterday in UTC. |
| The default window is the last 30 days | Long enough to include sales, short enough to show current behaviour |

## Tests

Backend (`tests/test_reports.py`), 23 tests:

- The formulas against the worked example, zero average stock, no sales, and the average of opening and closing.
- Valuation equals quantity × cost.
- Low stock excludes zero; negative stock lists over-issued levels and clears after a correction.
- Movement history: date filters, end before start is refused, bad date format is refused.
- Turnover: sales today give 2.0 turnover and 0.5 days in the constructed case; adjustments are not sales; opening stock carries forward.
- Dashboard: totals, one chart series per location, and items without sales sort first.
- Reports do not change stock.

Frontend, for the Step 3 components:

- `sort.test.js`: nulls always sort last; text and number sorting.
- `dashboard.test.js`: the slow-movers split and the default 30-day window.
- `CorrectionModal.test.jsx`: pre-fill, sending the ADJUST, and refusing a zero change.

## Results

- Backend: 58 tests pass after Step 4 was added (23 of them are Step 3).
- Frontend: all tests pass.
- The build succeeds.

## Known limits

- The turnover table scrolls sideways on phones rather than turning into cards.
- The charts are checked by eye in the browser, not by automated tests.
