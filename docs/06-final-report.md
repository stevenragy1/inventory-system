# 06 · Final report

## Project

**Inventory Management System.** Manages inventory records and stock levels for a company that sells cups and bottles from two locations: the Main Warehouse and the Showroom.

## Feature checklist

| Key feature | Done | Where |
|---|---|---|
| Inventory tracking | ✔ | Items page; item, category, and location management; per-location quantities |
| Stock updates | ✔ | Stock updates page: receive, issue with warning, adjust; correction from the dashboard |
| Search and filter | ✔ | Search page: name or SKU, category, location, stock status |
| Reports dashboard | ✔ | Dashboard and Reports page: metrics, charts, alerts, valuation, movements, turnover |

| Step | Done |
|---|---|
| 1. Design inventory modules | ✔ `01-design.md` |
| 2. Implement stock management | ✔ `02-stock-management.md` |
| 3. Create inventory reports | ✔ `03-reports.md` |
| 4. Add search and filtering | ✔ `04-search-filter.md` |
| 5. Test data accuracy | ✔ `05-testing.md` |

## Skills demonstrated

| Skill | Evidence |
|---|---|
| Database design | Five tables with constraints, foreign keys, and indexes; the database refuses malformed movements |
| Business logic | Over-issue warning, non-negative rule, correction flow, transactions, status rules |
| Data analysis | Turnover calculation (units sold, average stock, ratio, days of stock) and the slow-movers recommendation |
| Reporting systems | Valuation, low stock, negative stock, movement history, and the dashboard with charts |

## Rubric

| Criterion | How it is addressed |
|---|---|
| Task completion | All five steps and four key features are built and tested |
| Code quality | Layered backend (routes, services, repositories); components and helpers kept apart; each rule in one place |
| Website responsiveness | Bootstrap grid; checked at 375, 768, and 1280 px |
| User interface design | Consistent navigation, status badges with text as well as colour, clear warning and confirmation dialogs |
| Creativity and implementation | Charts, a slow-movers analysis, and negative-level alerts with a correction action |
| Professional presentation | This documentation set, a README, and a demo script |
| Project functionality | Seed data shows every feature on first run |

## Test results

| Suite | Result |
|---|---|
| Backend | 65 tests pass |
| Frontend | 30 tests pass across 8 files |
| Build | Succeeds |

## Demo script

1. **Start:** run the backend and the frontend (see `00-setup.md`).
2. **Dashboard:** point out the six metric cards. The glass bottles show a negative alert at the Showroom. Click **Record correction** and save; the alert clears.
3. **Charts:** the stock chart shows the Warehouse and Showroom per item. The slow-movers chart shows the item with the most days of stock on hand.
4. **Items:** add a new item (CUP-CER-004, Espresso cup 90ml, Cups, 2.50, 100). Try a duplicate SKU to show the error.
5. **Stock updates:** receive 10 of the new item. Issue more than is available to show the warning. Cancel, then confirm to show the over-issue.
6. **Search:** type "glass" to find the item. Filter by Negative, then by a location.
7. **Reports:** on the Turnover tab, sort by days of stock. On the Valuation tab, show the total. On the Movement history tab, show the over-issue badge.

## Lessons learned

- **Keep the rules in one place.** Putting the over-issue and status rules in the service layer meant the same logic served the API, the reports, and the tests.
- **Test the books independently.** The accuracy suite recalculates the figures with plain SQL. It caught nothing wrong in the end, but it would have caught a broken flag, and it was confirmed by deliberately breaking the flag.
- **Read the plan critically.** The "fewest days of stock" chart would have shown the fastest sellers. The fix was to show the most days.
- **Define edge cases before coding.** The Negative filter first ignored negative levels hidden inside a positive total. The test found it, and the rule was changed.

## Limitations

- Single user, with no login.
- One currency, stored as whole cents.
- Dates use UTC, so for a few hours after midnight in Cairo, "today" in reports is still the previous day.
- Turnover covers the window the user chooses; the dashboard uses the last 30 days.
- Transfers between locations are recorded as two movements (an issue and a receipt), not as one action.
- The turnover table scrolls sideways on phones rather than turning into cards.
- No automated browser tests; responsive checks were manual.
- No linter results: ruff and ESLint could not be installed in the build environment.
- pytest was not available, so the backend tests use `unittest`.

## Future work

- A transfer action between locations.
- Login and user roles.
- Cards layout for tables on phones.
- Automated browser tests.
- Multi-currency support.
