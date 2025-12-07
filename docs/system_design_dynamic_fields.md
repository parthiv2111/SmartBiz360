**System Design — Dynamic Modules & Custom Fields**

Purpose
- Provide a concrete, implementable design to add per-company module selection and editable, dynamic custom fields for entities (products, customers, orders, employees).

Summary
- Approach: Keep core relational model stable; store custom values in Postgres `JSONB` columns on target entities. Maintain metadata (field definitions) in a new `custom_fields` table (per-company). Provide management APIs, dynamic server-side validation, optional index creation for searchable fields, and a frontend field-builder + dynamic form renderer.

Goals & Non-Goals
- Goals:
  - Allow companies to enable/disable modules (CRM, HR, Inventory, Finance, etc.).
  - Allow admins to create/edit/remove custom fields for specific entities at any time.
  - Validate custom data server-side and persist in `custom_data` JSONB on entities.
  - Support search/filter on commonly-used custom fields via GIN or expression indexes.
- Non-Goals:
  - Not performing per-company separate physical schemas (single-tenant DB assumed).
  - Not automatically converting arbitrary custom fields into core relational columns by default.

Data Model
- New/changed tables (high level):
  - `companies` (if not present)
    - `id UUID PK`, `name`, `slug`, `settings JSONB`, `created_at`
  - `company_modules`
    - `id`, `company_id FK`, `module_name`, `enabled BOOL`, `config JSONB`
  - `custom_fields`
    - `id UUID PK`
    - `company_id FK`
    - `module` (string: 'hr','crm','inventory',...)
    - `entity` (string: 'product','customer','order','employee')
    - `label` (human text)
    - `key` (snake_case unique per company+entity)
    - `type` (enum: 'string','text','integer','decimal','boolean','date','datetime','select','multiselect','json')
    - `required` (bool)
    - `options JSONB` (for select/multiselect; array of {value,label})
    - `validation JSONB` (e.g., {min:0,max:100,regex:'/^\\w+$/'})
    - `default` (nullable)
    - `is_indexed` (bool) — if true, admin may create index for queries
    - `order` (int), `meta JSONB`, `created_by`, `created_at`, `updated_at`, `deleted_at`

- Entity table change (example):
  - `products` table: add `custom_data JSONB NOT NULL DEFAULT '{}'`
  - Repeat for `customers`, `orders`, `users` (employees) where needed.

SQL examples
- Add `custom_data` and GIN index:
```
ALTER TABLE products ADD COLUMN custom_data JSONB DEFAULT '{}'::jsonb NOT NULL;
CREATE INDEX idx_products_custom_data_gin ON products USING GIN (custom_data);
```

- Create `custom_fields` (simplified):
```
CREATE TABLE custom_fields (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL,
  module TEXT NOT NULL,
  entity TEXT NOT NULL,
  label TEXT NOT NULL,
  key TEXT NOT NULL,
  type TEXT NOT NULL,
  required BOOLEAN DEFAULT FALSE,
  options JSONB,
  validation JSONB,
  default TEXT,
  is_indexed BOOLEAN DEFAULT FALSE,
  created_by UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  deleted_at TIMESTAMP WITH TIME ZONE
);
CREATE UNIQUE INDEX ux_custom_fields_company_entity_key ON custom_fields(company_id, entity, key) WHERE deleted_at IS NULL;
```

APIs (backend)
- Management endpoints (admin/company-admin only):
  - `GET /api/v1/companies/:id/modules` — list modules & enabled status
  - `PUT /api/v1/companies/:id/modules` — set module toggles
  - `GET /api/v1/companies/:id/custom-fields?entity=product` — list fields definitions
  - `POST /api/v1/companies/:id/custom-fields` — create field (body: label, key, type, required, options, validation, is_indexed)
  - `PUT /api/v1/custom-fields/:id` — update field metadata
  - `DELETE /api/v1/custom-fields/:id` — soft-delete field (set `deleted_at`)
  - `POST /api/v1/custom-fields/:id/create-index` — (admin) trigger index creation for this field

- Entity endpoints (existing) must be extended to accept and validate `custom_data` keys. Examples:
  - `POST /api/v1/products` accepts payload `{ name, sku, ..., custom_data: { custom_key: value } }` — server validates `custom_data` against `custom_fields` for company + entity.

Validation & Server-side enforcement
- Dynamic Marshmallow schema generation approach (in `backend/schemas.py`):
  - Implement `build_dynamic_schema(company_id, entity)` which loads `custom_fields` rows and constructs a `marshmallow.Schema` with fields mapped from `type` and `validation` metadata.
  - Use `load_only`/`dump_only` and `required` flags as defined.
  - On entity create/update, call the generated schema to `load()` and validate `custom_data` before saving to `custom_data` column.

Example (pseudocode):
```
def build_dynamic_schema(company_id, entity):
  fields_meta = CustomField.query.filter_by(company_id=company_id, entity=entity, deleted_at=None)
  class DynamicSchema(Schema):
    pass
  for meta in fields_meta:
    if meta.type == 'string':
      setattr(DynamicSchema, meta.key, fields.Str(required=meta.required, validate=...))
    # handle other types
  return DynamicSchema()
```

Indexing & Searchability
- Default: GIN index on `custom_data` supports containment and existence queries.
- For filter/sort on typed values (numeric/date), support optional expression indexes (generated column or index on cast):
  - Example: `CREATE INDEX idx_products_custom_price ON products (((custom_data->>'custom_price')::numeric));`
- Workflow: creation of expression indexes should be admin-triggered and performed as an async job (long running); `is_indexed` flag requires validation before creating index (ensure safe `key` name pattern).

Storage & Limits
- Enforce per-company limits:
  - Max number of custom fields (e.g., 200)
  - Max size of `custom_data` JSONB per row (e.g., 64KB)
- Validate `key` names to match regex `^[a-z0-9_]{1,64}$` to avoid SQL injection when building indexes.

Delete / Migration strategy for custom fields
- Soft-delete fields: set `deleted_at`, stop exposing in API, do not remove stored data immediately.
- Hard deletion process (manual/admin):
  1. Export affected `custom_data` values for audit.
  2. Run an update to remove keys from `custom_data` or rename them to `archived__{key}`.
  3. Drop any expression indexes related to field.

Frontend design
- New pages/components:
  - `Settings -> Modules` — toggle available modules (call `PUT /companies/:id/modules`).
  - `Settings -> Custom Fields` — field builder UI to add/edit fields (label, key, type, options, validation, index flag).
  - `components/dynamic-form` — generic form renderer that accepts field definitions and renders inputs using existing UI components (text, textarea, number, date, select, multi-select, checkbox).

- Workflow for forms:
  1. On form open fetch `GET /companies/:id/custom-fields?entity=...` (cache per-company with TTL).
  2. Merge returned custom fields with static form schema and render inputs.
  3. On submit, send `custom_data` object nested under entity payload.
  4. On server validation error, show field-specific errors mapped by `key`.

- Caching & realtime:
  - Cache field definitions client-side (in memory or localStorage) for short TTL (e.g., 5 minutes).
  - Subscribe to websocket event `custom_fields_updated` to invalidate cache and refetch definitions.

Security & Permissions
- Only company admins (role enforcement in `routes/auth.py` or `decorators.py`) may create/modify/delete `custom_fields` and modules.
- Sanitize `key` before use in any DDL (index creation) and only permit keys matching the safe regex.
- Audit: write change records to `custom_fields_audit` on create/update/delete with `user_id`, diff and timestamp.

Background jobs & async tasks
- Long-running tasks:
  - Expression index creation (may lock table depending on PG version) — run via background job (Celery, RQ, or an async management command).
  - Backfill/migrate existing data into `custom_data` — background script.

Testing strategy
- Unit tests:
  - `build_dynamic_schema` behavior for types and validations.
  - `custom_fields` CRUD endpoints.
- Integration tests:
  - Create field, insert entity payload with that field, verify validation & persistence.
  - Test index creation job (on small test table) and verify queries use index.
- Migration tests:
  - Alembic migration creating `custom_data` and `custom_fields` table; test that GIN index exists.

Monitoring & performance
- Monitor query plans for queries touching `custom_data`.
- Track size growth of `custom_data` and number of indexed custom fields.
- Use PG stats (pg_stat_user_tables, pg_stat_user_indexes) and slow query logging.

Rollout plan
- Phase 0 — Design & infra: schema + migrations + small API + feature flag.
- Phase 1 — Admin UIs: field builder + module toggles behind feature flag; no indexing.
- Phase 2 — Pilot: enable for 1-2 companies, monitor, add index creation for needed fields.
- Phase 3 — Gradual rollout, add migration/backfill tools and documentation.

Estimated effort (single developer)
- Schema & migrations: 1 day
- Backend APIs + dynamic validation: 2-3 days
- Frontend field builder + form renderer: 2-3 days
- Index tooling + background jobs: 1-2 days
- Tests & staging verification: 1-2 days
- Total: ~7-11 dev-days

Files to add / edit (concrete)
- `backend/models.py` — add `Company`, `CompanyModule`, `CustomField`, and `custom_data` columns.
- `backend/migrations/versions/` — new Alembic revision(s).
- `backend/routes/custom_fields.py` — endpoints for CRUD and index management.
- `backend/routes/companies.py` (or `settings.py`) — module toggles endpoint.
- `backend/schemas.py` — implement `build_dynamic_schema(company_id, entity)` and use in entity endpoints.
- `backend/websocket_server.py` — emit `custom_fields_updated` events.
- `new-frontend/.../src/components/dynamic-form` — dynamic form renderer.
- `new-frontend/.../src/pages/settings/*` — modules and custom fields UIs.

Developer checklist (ready-to-ship)
- [ ] Add migrations and run on staging
- [ ] Implement and test dynamic validation engine
- [ ] Implement frontend field-builder and dynamic-form renderer
- [ ] Add audit logging and role checks
- [ ] Add index creation job and docs
- [ ] Create migration/backfill scripts for existing fields (if needed)

Appendix: Example API payloads
- Create custom field (POST `/api/v1/companies/:id/custom-fields`)
```
{
  "module": "crm",
  "entity": "customer",
  "label": "Customer Tier",
  "key": "customer_tier",
  "type": "select",
  "required": false,
  "options": [{"value":"gold","label":"Gold"},{"value":"silver","label":"Silver"}],
  "default": "silver",
  "is_indexed": true
}
```

- Create product with custom data (POST `/api/v1/products`)
```
{
  "name": "Widget X",
  "sku": "WX-01",
  "price": 199.99,
  "custom_data": {
    "custom_color": "blue",
    "custom_dimensions": {"w":10,"h":20}
  }
}
```

If you want, I can now:
- generate the model/migration skeleton in `backend/models.py` + an Alembic revision template, or
- implement the `custom_fields` CRUD endpoints + dynamic schema builder in `backend/schemas.py`, or
- scaffold the frontend `dynamic-form` component and `Settings -> Custom Fields` UI.

Tell me which next step to implement and I will start it and update the todo list accordingly.
