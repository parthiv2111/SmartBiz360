**Purpose**

This file gives concise, repo-specific guidance to AI coding agents so they can be immediately productive while working on SmartBiz360.

**Big Picture**:
- **Backend**: Flask app in `backend/` with routes registered as Blueprints in `backend/app.py` under `/api/v1`.
- **DB & Models**: SQLAlchemy models in `backend/models.py` and validation schemas in `backend/schemas.py`.
- **Migrations**: Alembic/Flask-Migrate lives in `backend/migrations/` (use `flask db migrate` / `flask db upgrade`).
- **Frontend**: Vite + React in `new-frontend/smartbussiness360-47/` — dev server runs on port `8080` by default (`package.json` scripts).
- **Realtime**: WebSocket/socket support initialized via `backend/websocket_server.py` and run with Flask-SocketIO (`socketio.run` in `backend/app.py`).

**Key Workflows & Commands (explicit)**
- Start backend (recommended, includes WebSocket): `python backend/app.py` (this initializes socketio and background tasks).
- Alternative start script: `python backend/start.py` — check return value of `create_app()` if using this entrypoint.
- Create virtualenv and install deps: `python -m venv venv` then `venv\Scripts\activate` and `pip install -r backend/requirements.txt`.
- DB setup (repo includes helpers): `python backend/init_db.py` to create tables; use `flask db migrate` / `flask db upgrade` for migrations.
- Frontend dev: `cd new-frontend/smartbussiness360-47` then `npm install` and `npm run dev` (Vite; port 8080).
- Docker-compose dev: `docker-compose up` from repository root uses a `db` and `backend` service (note: top-level `Dockerfile` referenced by compose may be missing; verify before building).

**Critical Environment Variables**
- `DATABASE_URL` — Postgres connection used across the app (`backend/config.py`).
- `JWT_SECRET_KEY` & `SECRET_KEY` — must be set in `.env` to avoid login/session issues; `backend/app.py` warns if defaults are used.
- `CORS_ORIGINS` — comma-separated origins for Flask-CORS (defaults include localhost and Vite ports).
- `UPLOAD_FOLDER` — files saved under this folder; referenced in `backend/app.py` and mounted by `docker-compose.yml`.

**Patterns & Conventions Specific To This Repo**
- Blueprints: endpoints are registered with `url_prefix='/api/v1'` in `backend/app.py`. Look for `routes/*.py` files exporting `<name>_bp`.
- Marshmallow schemas live in `backend/schemas.py` and are used to validate/serialize payloads — follow the existing `Schema` patterns when adding endpoints.
- UUIDs: models use PostgreSQL UUID columns (`sqlalchemy.dialects.postgresql.UUID`). Return `str(id)` in `to_dict()` helpers.
- Pagination: default page size is `10` (see `backend/config.py`); endpoints usually implement `page`/`per_page` query params.

**Integration Points & Gotchas**
- WebSockets: `backend/websocket_server.py` initializes socketio and background tasks; use `socketio.emit` for realtime updates.
- File uploads: uploaded files are saved under `uploads/` with subfolders `avatars/` and `products/` — ensure permissions and `UPLOAD_FOLDER` are correct.
- Migrations: migrations directory is present; prefer `flask db` workflow. If using `python init_db.py` it may bypass migrations and create tables directly.
- Docker: `docker-compose.yml` sets `backend` to `build: .` but a top-level `Dockerfile` may not exist — verify before CI/docker runs.

**Concrete Examples**
- Health check: `GET /health` implemented in `backend/app.py`.
- Create product (cURL): `POST /api/v1/products` — payload shape matches `ProductSchema` in `backend/schemas.py` (fields: `name`, `sku`, `category`, `price`, `stock`).
- Auth: JWT via `Flask-JWT-Extended` — tokens read from `Authorization: Bearer <token>` header (see `config.py` JWT_* settings).

**When Editing Code**
- Follow patterns found in `routes/*.py`: create a blueprint, use schema validation, return consistent error JSON (`{ "success": false, "error": "..." }`).
- Keep model `to_dict()` shapes consistent — frontend expects specific keys (e.g., `products` endpoint includes `price`, `sku`, `status`).
- Update or add migrations under `backend/migrations/versions/` when changing DB models.

If anything here is unclear or you'd like me to expand examples (e.g., add a quick code template for a new route or migration), tell me which part to flesh out.
