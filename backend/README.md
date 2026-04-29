# Park — Backend API

FastAPI + SQLite backend for the Park car parking management system.

## Stack
- **Python 3.10+**
- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM (SQLite database)
- **python-jose** — JWT authentication
- **Uvicorn** — ASGI server

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed the database (creates parking.db + 104 spots)
python seed.py

# 3. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | — | Register (name, phone, plate) |
| POST | `/api/auth/login` | — | Login with phone number |
| GET | `/api/me` | ✅ | Current user + active reservation |
| GET | `/api/spots?floor=A` | — | List spots (filter by floor) |
| POST | `/api/spots/{id}/reserve` | ✅ | Reserve a spot |
| DELETE | `/api/reservations/mine` | ✅ | Cancel reservation, save trip |
| GET | `/api/history` | ✅ | User trip history |
| GET | `/api/health` | — | Health check |

## Project Structure

```
park-backend/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI app + all routes
│   ├── database.py    # SQLAlchemy models
│   └── auth.py        # JWT utilities
├── seed.py            # Seed parking spots
├── requirements.txt
└── parking.db         # SQLite database (auto-created)
```

## Connecting the Frontend

The frontend expects the API at `http://localhost:8000`.  
To change this, update `API_BASE` at the top of:
- `src/parking.js`
- `src/login.html`
- `src/register.html`
- `src/history.html`
