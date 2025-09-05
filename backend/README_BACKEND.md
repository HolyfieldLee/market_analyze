# Backend (Flask) — 상권분석 API

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
export FLASK_APP=wsgi.py  # Windows: set FLASK_APP=wsgi.py
flask run -p 5000
```

## Endpoints
- `GET /api/health` → `{ "status": "ok" }`
- `POST /api/auth/register` → `{ email, password, name }`
- `POST /api/auth/login` → returns `access_token`
- `GET /api/auth/me` (JWT) → current user
- `POST /api/recs/score` → `{ "features": { "foot_traffic": 0.9, ... } }` ⇒ `{ "score", "breakdown" }`
- `GET /api/recs/sample` → demo list for FE

## CORS
CORS is enabled for all `/api/*` routes for quick integration with React/SwiftUI during dev.
