# 소담(Sodam) Backend Starter (Flask)

## Quickstart
```bash
# 1) Create & activate venv
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Copy env
cp .env.example .env

# 4) DB init (SQLite)
flask --app app:create_app db init
flask --app app:create_app db migrate -m "init"
flask --app app:create_app db upgrade

# 5) Run
python app.py
# visit: http://localhost:5000/home
```

## Endpoints (initial)
- GET  /home, /about
- GET  /api/ping
- POST /api/echo
- POST /api/auth/signup
- POST /api/profile/preferences
- GET  /api/trends?region=강남구
