# Inventory Management System

A web application that tracks inventory records and stock levels for a company that sells cups and bottles from two locations: the Main Warehouse and the Showroom. The software is general, so it works for any business that stocks items in several places.

## Features

- **Inventory tracking:** items with SKU, category, unit cost, and reorder level; stock per location; deactivation that keeps history.
- **Stock updates:** receive, issue (with an over-issue warning), and adjust, each with a reason. Corrections clear negative levels.
- **Search and filter:** by name or SKU, category, location, and stock status.
- **Reports dashboard:** summary cards, stock and slowest-mover charts, negative-stock alerts, low-stock list, valuation, movement history, and stock turnover.

## Technology

| Part | Tools |
|---|---|
| Backend | Python 3, Flask (JSON API), SQLite |
| Frontend | React, Vite, React Router, Bootstrap 5 (react-bootstrap), Chart.js (react-chartjs-2) |
| Tests | `unittest` (backend), Vitest and Testing Library (frontend) |

## Project structure

```
inventory-system/
├── backend/      Flask API, services, repositories, tests, seed script
├── frontend/     React user interface and component tests
├── docs/         Step-by-step documentation and the final report
└── data/         SQLite database (created on first run)
```

## Running the project

Open two terminals.

**Backend**

```
cd backend
python -m venv .venv
.venv\Scripts\activate        (Windows; use source .venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
python seed.py
python run.py
```

The API runs at `http://127.0.0.1:5000`.

**Frontend**

```
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Testing

```
cd backend
python -m unittest discover -s tests -v      # 65 tests

cd frontend
npm test                                      # 30 tests
npm run build                                 # production build
```

`docs/05-testing.md` describes the accuracy suite, the database guards, and the browser and width checks.

## Documentation

| File | Contents |
|---|---|
| `docs/00-setup.md` | Setup and running the project |
| `docs/01-design.md` | Requirements, data model, architecture, API |
| `docs/02-stock-management.md` | Items and stock actions, over-issue warning |
| `docs/03-reports.md` | Reports, turnover formulas, dashboard |
| `docs/04-search-filter.md` | Search and the stock status rule |
| `docs/05-testing.md` | Test layers, accuracy checks, responsive checks |
| `docs/06-final-report.md` | Feature checklist, rubric, demo script, limitations |
| `docs/07-ui-design.md` | Figma design source, theme, and how it was applied |

## Demo

Run `python seed.py` to load the demo data: six items, two locations, and one negative level so the alert appears on the dashboard. The demo script is in `docs/06-final-report.md`.
