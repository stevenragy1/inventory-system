# 00 · Setup

## Goal

Create a project skeleton with a Flask backend and a React frontend, and confirm both start.

## What was set up

```
inventory-system/
├── backend/        Flask JSON API, services, repositories, tests, seed script
├── frontend/       React (Vite) user interface, component tests
├── docs/           Step documentation (this folder)
├── data/           SQLite database file (created by the backend)
└── README.md
```

- Git repository initialised in `inventory-system/`.
- `.gitignore` excludes `__pycache__`, `*.pyc`, `data/*.db`, `node_modules/`, and `dist/`.

## Tools

| Tool | Version used | Why |
|---|---|---|
| Python | 3.13 (3.10+ works) | Backend language |
| Flask | 3.1.3 | JSON API |
| SQLite | bundled with Python | Database, no server needed |
| Node.js | 22 (18+ works) | Frontend build and tests |
| Vite | 5.4.8 | Frontend dev server and build |
| React | 18.3.1 | User interface |
| react-bootstrap / Bootstrap | 2.10.4 / 5.3.3 | Responsive layout and components |
| react-chartjs-2 / Chart.js | 5.2.0 / 4.4.4 | Charts |
| react-router-dom | 6.26.0 | Pages and navigation |
| Vitest, Testing Library | 2.1.1, 16.0.1 | Frontend tests |
| Plus Jakarta Sans | Google Fonts | Typeface from the Figma design, loaded in `index.html` |

The visual theme is in `frontend/src/theme.css`. See `07-ui-design.md`.

## Running the project

Backend (port 5000):

```
cd backend
python -m venv .venv
.venv\Scripts\activate          (Windows)
pip install -r requirements.txt
python seed.py
python run.py
```

Frontend (port 5173):

```
cd frontend
npm install
npm run dev
```

The Vite dev server forwards `/api` requests to the Flask server.

## Checks

- `GET /api/health` returns `{"status": "ok"}`.
- The Items page loads six seeded items.

## Deviations from the plan

- **Tests:** the plan named pytest. pytest could not be installed in the build environment, so the backend tests use Python's built-in `unittest`. They run with `python -m unittest discover -s tests -v`.
- **Linting:** the plan named ruff and ESLint. Neither could be installed in the build environment, so no linter results are reported.
