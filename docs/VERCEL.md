# Vercel Services deployment

Import the repository with Root Directory `./` and the Services preset.
The root `vercel.json` defines `frontend` (Vite) and `backend` (FastAPI,
entrypoint `app.main:app`). `/api/*` reaches the backend with the original
path preserved; all other paths reach the frontend. The existing backend API
routes already include `/api`, so no prefix stripping is needed.

The React application calls FastAPI from the browser using relative `/api` URLs.
There are no server-side calls between these two services and hence no internal
service bindings. A runtime binding cannot be consumed by a static Vite bundle.
Making the backend internal would require adding a server function to proxy the
browser's API requests and placing a backend binding on that function's service.

Leave `VITE_API_URL` unset in Production and Preview. Do not configure it with
localhost, a fixed production domain, or a runtime binding URL. Provider settings
are read only by the backend; leave `FEATHERLESS_ENABLED` disabled unless you
intend to enable provider calls. No provider credential is required for the demo.

## Persistent audit storage: Supabase PostgreSQL

The backend uses PostgreSQL when `DATABASE_URL` is set and otherwise uses the
existing SQLite file locally. On Vercel it requires `DATABASE_URL`; there is no
temporary SQLite fallback. Local SQLite history is not automatically migrated.

1. Open your Supabase project's **Connect** panel and select **Transaction pooler**.
2. Copy the PostgreSQL connection string (port 6543), substitute your database
   password, and percent-encode reserved characters in the password.
3. Add `sslmode=require` to the URL's query string unless an SSL setting is
   already provided. Configure the resulting URL as `DATABASE_URL` in Vercel.
4. Set it for Production. For Preview, use a separate Supabase database/project
   if preview actions must not enter the production audit history.
5. Redeploy after changing environment variables. Startup creates the four
   storage tables and missing catalog seeds without deleting existing records.
   It enables Row Level Security on these tables with no browser policies; use
   the backend's privileged PostgreSQL connection for access.

The backend disables prepared statements for Supabase transaction pooling and
uses SQLAlchemy NullPool so connections close after each transaction. PostgreSQL
startup uses a transaction advisory lock to serialize table creation across
instances. The database URL is a secret; never set it as a VITE_* variable.
Supabase is external storage, not a Vercel service, so it uses DATABASE_URL rather
than a service binding.

Connection setup reference: https://supabase.com/docs/guides/database/connecting-to-postgres

## Verification

From the repository root, use `vercel dev` to test both services together once
`DATABASE_URL` is configured. For separate local development, run
Uvicorn on port 8000 and Vite on port 5173; Vite proxies `/api` to Uvicorn.
After deploying, verify `/api/health`, the console analysis flow, and the audit
view on the same deployment domain. Backend `/docs` is not exposed by the
current public route table, which reserves non-API paths for the frontend.

The user confirmed `frontend` public at `/`, `backend` public at `/api/*`, no
internal-only services or bindings, and persistent storage in Supabase PostgreSQL.
The provider connection and live deployment still need verification in Vercel.
