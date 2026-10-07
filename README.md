# Travel.pk Booking Service

FastAPI backend with SQLite for fare holds, payments, PSP webhooks, and airline ticketing stubs, plus a React admin UI for local demos and interviews.

## Running Backend

From the project root (with virtualenv activated):

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

SQLite database file: `travelpk.db` (created automatically on startup).

## Running Frontend

```powershell
cd frontend
npm install
npm run dev
```

Optional: copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL=http://127.0.0.1:8080`.  
If unset, the dev server proxies API calls through `/api` to the backend.

## Application URLs

| Service   | URL |
|-----------|-----|
| Frontend  | http://localhost:5173 |
| Backend   | http://127.0.0.1:8080 |
| Swagger   | http://127.0.0.1:8080/docs |

## Architecture

```text
React UI
   ↓ HTTP
FastAPI
   ↓
Service Layer
   ↓
SQLAlchemy
   ↓
SQLite
```

## Authentication (local demo)

- **Partner API key** (header `Authorization: Bearer …`): seeded key id `partner-admin` for fares, holds, payments, and admin read APIs.
- **Customer token**: returned when a hold is created; stored in browser `localStorage` for that booking reference. Customer tokens cannot access other bookings (404).

Configure the partner key in the UI header or use the default `partner-admin`.

## UI Features

- Dashboard with live stats and recent bookings
- Fare browsing (integer paisa displayed as PKR)
- Hold creation with 20-minute countdown (server-authoritative expiry)
- Payment start with generated `Idempotency-Key`
- Booking detail, timeline, ticketing status, cancellation with server-calculated refund preview
- Payments list
- PSP webhook and airline request monitoring

## Backend tests

```powershell
pytest -q
```

## API overview

| Method | Path | Auth |
|--------|------|------|
| GET | `/fares` | Partner `fares:read` |
| POST | `/holds` | Partner `holds:create` |
| POST | `/payments` | Partner `payments:create` + `Idempotency-Key` |
| GET | `/bookings` | Partner `bookings:read` |
| GET | `/bookings/{reference}` | Customer token **or** partner `bookings:read` |
| GET | `/bookings/{reference}/cancellation-preview` | Customer token **or** partner `bookings:read` |
| POST | `/bookings/{reference}/cancel` | Customer token **or** partner `bookings:cancel` |
| GET | `/admin/payments` | Partner `bookings:read` |
| GET | `/admin/webhook-events` | Partner `bookings:read` |
| GET | `/admin/airline-requests` | Partner `bookings:read` |
| POST | `/webhooks/psp` | PSP signature headers |
