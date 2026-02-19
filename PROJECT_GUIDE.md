# No Lose — Project Guide

A quick-start reference for understanding the project and working on tasks.

---

## Overview

A SaaS platform for WhatsApp management via Evolution API. Users connect their WhatsApp by scanning a QR code, sync contacts and message history, and send/receive messages through a web interface.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI 0.109, SQLAlchemy 2.0, PostgreSQL 15, Alembic |
| Frontend | Next.js 16.1, React 19, TypeScript, Tailwind CSS 4 |
| Auth | JWT (python-jose + bcrypt) |
| WhatsApp | Evolution API (primary), WhatsApp Cloud API (legacy) |
| Infrastructure | Docker Compose, Nginx reverse proxy |
| CI/CD | GitHub Actions → SSH deploy to GCP VM |
| Hosting | GCP e2-micro (1 vCPU, 1GB RAM, 2GB swap) |

---

## Project Structure

```
backend/
  app/
    main.py              — FastAPI entrypoint, router registration, CORS
    core/
      config.py          — Settings (DB, JWT, Evolution API, WhatsApp)
      auth.py            — JWT tokens, password hashing, get_current_user
      database.py        — SQLAlchemy engine, SessionLocal, Base
    models/
      __init__.py        — all model imports
      user.py            — User (email, password, name)
      whatsapp.py        — Contact, Message, Conversation
      evolution.py       — EvolutionInstance (WhatsApp connection state)
    services/
      evolution.py       — EvolutionAPIService: instance management, sync, sending
      whatsapp.py        — WhatsApp Cloud API (legacy, not primary)
    api/
      routes.py          — /health, /stats, /messages, /contacts, webhook
      auth.py            — /auth/register, /auth/login, /auth/me
      evolution.py       — /evolution/instance/*, /evolution/sync/*, /evolution/send/*
  alembic/
    versions/            — DB migrations
  Dockerfile
  requirements.txt

frontend/
  src/
    app/
      page.tsx           — landing page
      layout.tsx         — root layout + AuthProvider
      login/page.tsx     — login page
      register/page.tsx  — registration page
      dashboard/page.tsx — user dashboard
      account/page.tsx   — account settings
      whatsapp/page.tsx  — WhatsApp connection (QR code)
      whatsapp/sync/page.tsx — chat sync
    contexts/
      AuthContext.tsx     — auth context (user state, login/logout)
    lib/
      api.ts             — API client (auth + Evolution API methods)
  Dockerfile
  package.json
  next.config.ts

nginx/
  nginx.conf             — /api → backend:8000, /evolution → evolution:8080, / → frontend:3000

docker-compose.yml       — dev environment (postgres + evolution only)
docker-compose.prod.yml  — full stack (5 containers: nginx, frontend, backend, postgres, evolution)
.github/workflows/deploy.yml — CI/CD (push to main → deploy to GCP)
deploy/
  init-db.sh             — creates wa_evolution DB on first postgres start
  gcp-setup.sh           — VM provisioning
  server-setup.sh        — server setup (Docker, swap)
```

---

## Architecture

### Containers (production)

```
Nginx (:80) ─┬─ /api      → Backend (:8000)
              ├─ /evolution → Evolution API (:8080)
              └─ /          → Frontend (:3000)

Backend ──→ PostgreSQL (:5432)
Backend ──→ Evolution API (:8080)
```

### Key Flows

**WhatsApp Connection:**
1. User clicks "Connect" → `POST /api/evolution/instance/create`
2. Backend creates an instance in Evolution API, receives a QR code
3. Frontend displays the QR code, auto-refreshes every 30 sec
4. User scans → webhook `connection.update` → status becomes `connected`

**Sync:**
1. `POST /api/evolution/sync/contacts` — fetch contacts
2. `POST /api/evolution/sync/chats` — fetch chat list
3. `POST /api/evolution/sync/messages/{contact_id}` — fetch last 30 messages per chat

**Incoming Messages:**
Webhook `POST /webhook/evolution` → `messages.upsert` event → saved to DB

---

## Database

### Models

- **users** — id, email, hashed_password, name, created_at
- **evolution_instances** — id, user_id (FK), instance_name (`user_{id}`), status (disconnected/qr/connecting/connected), qr_code, phone_number, profile_name
- **contacts** — id, user_id, phone_number, name, evolution_remote_jid
- **messages** — id, user_id, contact_id, content, direction, timestamp, evolution_key_id, source (cloud_api/evolution_api)
- **conversations** — id, user_id, contact_id, last_message_at

### Migrations

```bash
# Create a migration
cd backend && alembic revision --autogenerate -m "description"

# Apply
alembic upgrade head

# In Docker (production)
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## Running the Project

### Local Development (without Docker)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in the variables
uvicorn app.main:app --reload --port 8000

# Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

Requires a locally running PostgreSQL (see `backend/.env` for connection string).

### Local Development via Docker (full stack)

Runs all 5 services (nginx, frontend, backend, postgres, evolution) locally — identical to production.

**Prerequisites:** Docker Desktop running.

**1. Configure environment:**

```bash
# Root .env (create or verify)
cat .env
```

Should contain:
```env
DOMAIN=localhost
EVOLUTION_API_KEY=evolution_api_key_dev
EVOLUTION_API_URL=http://evolution:8080
```

**2. Create SSL directory (needed for nginx volume mount):**

```bash
mkdir -p nginx/ssl
```

**3. Build and start:**

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

**4. Verify:**

```bash
# All 5 containers should be running
docker-compose -f docker-compose.prod.yml ps

# Health check
curl http://localhost/api/health
# → {"status":"ok"}
```

**Access:**
- Frontend: http://localhost
- API docs: http://localhost/api/docs
- API health: http://localhost/api/health

**Stop:**

```bash
docker-compose -f docker-compose.prod.yml down
```

**Full reset (including database):**

```bash
docker-compose -f docker-compose.prod.yml down -v
```

**Important notes:**
- PostgreSQL creates two databases: `wa_database` (backend) and `wa_evolution` (Evolution API) — via `deploy/init-db.sh`
- The init script only runs on first start (empty volume). To re-run it: `docker-compose down -v` first
- Evolution API may take 10–20 seconds to fully initialize after container start

### Deploying to GCP (production)

**Automatic (CI/CD):** every push to `main` triggers GitHub Actions → SSH deploy to GCP VM.

```bash
git add -A
git commit -m "description"
git push origin main
```

GitHub Actions workflow (`.github/workflows/deploy.yml`) will:
1. SSH into the GCP VM
2. `git pull origin main`
3. `docker compose -f docker-compose.prod.yml up -d --build --force-recreate`
4. Ensure `wa_evolution` database exists
5. Run Alembic migrations

**Manual deploy (on GCP VM):**

```bash
gcloud compute ssh no-lose-app --zone=us-west1-b
cd ~/no-lose
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
```

**Check logs:**

```bash
docker-compose -f docker-compose.prod.yml logs -f <service>
```

---

## API Endpoints

### Auth
- `POST /api/auth/register` — register {email, password, name}
- `POST /api/auth/login` — login → JWT token
- `GET /api/auth/me` — current user (requires Bearer token)

### Evolution (WhatsApp) — all require JWT
- `POST /api/evolution/instance/create` — create instance + QR
- `GET /api/evolution/instance/status` — connection status
- `GET /api/evolution/instance/qrcode` — get/refresh QR
- `DELETE /api/evolution/instance/disconnect` — disconnect

- `POST /api/evolution/sync/contacts` — sync contacts
- `POST /api/evolution/sync/chats` — fetch chat list
- `POST /api/evolution/sync/messages/{contact_id}` — fetch message history

- `POST /api/evolution/send/text` — send a message

### General
- `GET /api/health` — healthcheck
- `GET /api/stats` — statistics
- `GET /api/contacts` — user's contacts
- `GET /api/messages` — messages

### Webhooks
- `POST /webhook/evolution` — incoming events from Evolution API

---

## Environment Variables

### Backend (backend/.env)
```
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/dbname
SECRET_KEY=<openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_MINUTES=43200
EVOLUTION_API_URL=http://evolution:8080      # inside Docker
EVOLUTION_API_KEY=<openssl rand -hex 32>
```

### Frontend
```
NEXT_PUBLIC_API_URL=/api     # in production via Nginx
```

### Production (.env at project root on VM)
```
DOMAIN=34.123.68.109
DATABASE_URL=postgresql://wa_user:wa_password@postgres:5432/wa_database
SECRET_KEY=...
EVOLUTION_API_URL=http://evolution:8080
EVOLUTION_API_KEY=...
```

---

## Common Tasks

### Add a new API endpoint
1. If a new model is needed → create in `backend/app/models/` → import in `__init__.py`
2. Create or extend a router in `backend/app/api/`
3. Register the router in `backend/app/main.py` via `app.include_router()`
4. Create a migration if models changed

### Add a new frontend page
1. Create `frontend/src/app/<route>/page.tsx`
2. For API calls — add a method in `frontend/src/lib/api.ts`
3. For protected pages — use `useAuth()` from `AuthContext`

### Change configuration
- Backend settings: `backend/app/core/config.py` (Settings class, Pydantic)
- Nginx routing: `nginx/nginx.conf`
- Docker services: `docker-compose.prod.yml`

---

## Constraints and Notes

- **Memory:** e2-micro server (1GB RAM + 2GB swap) — everything is optimized for this
- **Sync limit:** 30 most recent messages per chat
- **QR code:** expires in 40–60 sec, requires auto-refresh
- **Evolution API** may lose connection during inactivity — handled via webhook
- **Message deduplication:** based on the `evolution_key_id` field
- **Archival:** messages older than 2 years are subject to archival

---

## Production

- **URL:** http://34.123.68.109
- **API Health:** http://34.123.68.109/api/health
- **5 containers:** nginx, frontend, backend, postgres, evolution
- **CI/CD:** push to `main` → GitHub Actions → SSH deploy to VM
- **Cost:** ~$0/mo (GCP free tier)

### Production Environment Notes

- **Disk:** VM has ~10GB disk (may show 9.7G if partition not resized). Deploy uses incremental builds with layer cache, cleans only when usage > 80%.
- **Deploy time:** ~30–45 min for full rebuild. Incremental deploys (code-only changes) are much faster.
- **Concurrency:** Only one deploy runs at a time (`cancel-in-progress: true`).
- **Migrations:** If `alembic upgrade head` fails (e.g. tables already exist), deploy stamps `alembic_version` to sync state.
- **Instance name:** GCP VM may be `wa-app` or `no-lose-app` depending on setup script used.

### Useful Server Commands

```bash
# SSH
gcloud compute ssh no-lose-app --zone=us-west1-b

# Logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f evolution

# Restart a service
docker-compose -f docker-compose.prod.yml restart backend

# Database
docker exec -it wa_postgres psql -U wa_user -d wa_database

# Resources
df -h && free -h && swapon --show

# Backup
docker exec wa_postgres pg_dump -U wa_user wa_database > backup_$(date +%Y%m%d).sql
```
