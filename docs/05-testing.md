# 05 · Testing

## Goal

Show that the stock figures are accurate, that the business rules hold, and that the interface works on phone, tablet, and desktop widths.

## Test layers

| Layer | Tool | What it covers |
|---|---|---|
| Unit (backend) | `unittest` | Business rules and formulas |
| API (backend) | `unittest` with Flask's test client | Routes, status codes, and warnings over HTTP |
| Accuracy (backend) | `unittest` | Long random runs checked against an independent calculation |
| Unit and component (frontend) | Vitest and Testing Library | Helpers, forms, dialogs |
| Build | Vite | The app compiles without errors |
| Responsive and visual | Manual, in the browser | Layout at three widths |

## Data accuracy

The accuracy suite (`tests/test_accuracy.py`) checks the books without using the service code to verify itself.

- **Random activity:** 400 receive, issue, and adjust steps across three items and two locations. The random seed is fixed, so the run is repeatable. Warnings and refusals are included.
- **Every level equals its movements:** checked every 50 steps and at the end.
- **Warnings and refusals write nothing:** the movement count is checked before and after each one.
- **Reports match raw SQL:** valuation, total units, and negative count are recalculated with plain SQL.
- **Over-issue flags are correct:** the test replays each level's history. An issue is flagged exactly when the balance after it is below zero.
- **Turnover is consistent:** closing stock equals the level, and units sold equals the issues.
- **Search matches stock:** each search result's levels equal the stock table.

**Database guards:** the database refuses a zero change, a positive issue, a negative receipt, an unknown movement type, and a duplicate SKU, even when the service is bypassed.

## Proof that the tests catch mistakes

The over-issue flag was set to the wrong value on purpose. Two tests failed. The correct code was restored and all tests passed again.

## Browser and width checks

Checked at **375 px** (phone), **768 px** (tablet), and **1280 px** (desktop), in the browser's device mode.

| Page | Phone 375 px | Tablet 768 px | Desktop 1280 px |
|---|---|---|---|
| Dashboard | _to fill in_ | _to fill in_ | _to fill in_ |
| Items | _to fill in_ | _to fill in_ | _to fill in_ |
| Stock updates | _to fill in_ | _to fill in_ | _to fill in_ |
| Search | _to fill in_ | _to fill in_ | _to fill in_ |
| Reports | _to fill in_ | _to fill in_ | _to fill in_ |

Record for each cell whether the page fits without sideways scrolling, and whether the tables and modals stay usable. Any issue found, and how it was fixed, goes in the notes below.

**Notes:** _to fill in_

## Results

| Suite | Result |
|---|---|
| Backend (`unittest`) | 65 tests, all pass |
| Frontend (Vitest) | 8 files, 30 tests, all pass |
| Frontend build (`npm run build`) | Succeeds |

## Known gaps

- No automated browser tests. The responsive checks are manual.
- No linter results. ruff and ESLint could not be installed in the build environment.
- The charts are checked by eye, not by automated tests.
