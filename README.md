# Vectera Coding Test

A small meeting-notes app: create meetings, add notes, and generate an AI summary of a meeting's notes asynchronously.
- **Backend**: Django + DRF - models, REST API, async summary generation backed by the Anthropic API
- **Frontend**: Angular - meetings list & detail, note-taking, summary generation with status polling
- **Docker**: Postgres + Backend
- **CI**: GitHub Actions - lint (black/isort/eslint) + tests for both backend and frontend (`.github/workflows/ci.yml`)

See `DECISIONS.md` for design trade-offs, deviations from the original spec, and time spent per area.

## Getting Started

### 1) Configure the Anthropic API key
Summary generation calls the real Anthropic API, so it needs credentials:
```bash
cp backend/.env.example backend/.env
# then fill in ANTHROPIC_API_KEY & ANTHROPIC_MODEL
```
Everything else works without this, but “Generate summary” will fail until it's set.

### 2) Run with Docker (DB + Backend)
```bash
docker compose up --build
```
- Backend: http://localhost:8000
- Health: http://localhost:8000/api/health/
- DB: postgres://app:app@localhost:5432/app

**Note:** The backend image installs Python dependencies and runs migrations automatically.

### 3) Frontend (Angular)
```bash
cd frontend
npm install
npm start
```
- Angular dev server: http://localhost:4200 (proxies /api to http://localhost:8000)

### 4) Running tests
```bash
# Backend
cd backend && python -m pytest

# Frontend
cd frontend && npm test
```

## What's implemented
Backend (Django + DRF):
- Data models for `Meeting`, `Note`, `Summary`
- REST endpoints for meetings, notes, and the summary flow
- Async summary generation (threaded job + Postgres advisory lock, see `backend/meetings/models.py`) via the Anthropic API (`backend/meetings/services/ai.py`)
- Validation, pagination, logging & `/api/health/`

Frontend (Angular):
- `/meetings` list (title, started_at, note count, summary badge)
- `/meetings/:id` detail (notes feed, add note form, “Generate summary”, summary panel)
- Loading/error states, typed API models, clean module structure
- Polling summary status until `ready` or `failed`

Tests:
- Backend: model tests, happy-path API tests, validation/edge-case tests (`backend/meetings/tests/`)
- Frontend: service and component unit tests (`*.spec.ts`)

## Docs
`DECISIONS.md` has the full log of decisions, trade-offs, and possible future improvements.
