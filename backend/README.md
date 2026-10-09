# TrustLayer backend

Run from this directory using the existing virtual environment:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
.\venv\Scripts\python.exe -m pytest -q
```

The frontend request/response contract is preserved. CORS allows localhost and
127.0.0.1 on ports 5173 and 5174. `/` and `/api/health` retain their original responses.

## API

- `POST /api/actions/analyze`: validates an AgentAction, analyzes and durably logs it.
- `GET /api/agents`, `GET /api/agents/{agent_name}`: permission profiles.
- `GET /api/policies`, `GET /api/policies/{policy_id}`: policy descriptions.
- `GET /api/scenarios`, `GET /api/scenarios/{scenario_id}`: six seeded examples.
- `POST /api/scenarios/{scenario_id}/analyze`: analyzes and logs a seeded example.
- `GET /api/audit`: newest first; `limit` 1–200, `offset` >= 0, optional `decision`.
- `GET /api/audit/{action_id}`: one audit record.
- `GET /api/audit-logs`: compatibility listing with `logs`, `total`, `limit`, and `offset`.
- `GET /api/audit-logs/{action_id}`: one record by its UUID.
- `GET /api/audit-logs/export`: downloads all current redacted audit records as JSON.
- `/docs`: interactive OpenAPI documentation.

Risk scores are capped at 100. Instruction override (+40), concealment/bypass
(+30), authority spoofing (+35), untrusted transfer instructions (+40), sensitive
external transfer (+70), unapproved communication (+30), unapproved payment
(+60), and untrusted side effects (+25) contribute signals. Below 30 allows;
30–69 requires review; 70+ blocks. Profile/resource violations, injection,
sensitive exfiltration, and missing destinations hard-block with a minimum 70.
An approval never overrides a hard block. External and payment effects are
inferred from known operation names as well as request flags. Resources are exact
allowlists; unspecified files are not implicitly authorized.

On Vercel, set `DATABASE_URL` to a Supabase transaction pooler PostgreSQL URL.
The backend requires this value on Vercel and stores audit history persistently
in PostgreSQL. See [Vercel setup](../docs/VERCEL.md). Locally without DATABASE_URL,
SQLite defaults to `backend/data/trustlayer.sqlite3`, independent of working
directory. Override with `TRUSTLAYER_DB_PATH`. Startup creates tables and seeds
missing catalog rows without deleting existing records. Audits use UTC timestamps,
UUIDs, request fingerprints and decision evidence. Raw source content, user tasks,
destinations and resource names are omitted. A logging failure fails the analysis
request. Catalogs are read-only; policy/profile definitions in services are the
enforcement source of truth. Existing catalog seeds are not overwritten.

This is a local prototype: request approval and source trust are caller assertions,
not authenticated permissions. Keyword heuristics cannot detect every injection
or establish whether the proposed action satisfies arbitrary natural-language tasks.
There is no action executor or external email/payment/cloud access. Optional model requests are limited to synthetic scenarios. Bind locally; audit and catalog APIs have no authentication.
Featherless is optional evidence only; deterministic behavior remains the decision authority. No separate project specification was available, so these
rules implement the requested requirements and the existing frontend contract.

## Optional contextual analysis

See the root README for architecture and configuration. `backend/.env.example`
contains backend-only settings. Provider use defaults to disabled; a key alone
never enables requests. The adapter uses the official Featherless HTTPS endpoint,
an overall 4-second deadline (configurable 0.5–8), no retries or redirects, and only
code-defined synthetic scenario input. Arbitrary caller content stays local.

`POST /api/actions/analyze?contextual=true` and
`POST /api/scenarios/{id}/analyze?contextual=true` attach validated advisory evidence
or a sanitized unavailable reason. Requests without the query retain their old
shape and make no provider call. The frontend requests the optional evidence.
No model value changes deterministic verdicts, scores, policies or recommendations.
Existing SQLite result JSON stores the contextual evidence without migration;
legacy audit records remain readable. Provider headers, credentials, raw responses
and exception bodies are excluded from API results and logs.

Tests block real external transports. Provider success/failure tests use
httpx.MockTransport, require no key and consume no credits. The existing
Starlette/httpx test-client warning is retained pending a reviewed dependency
migration. Deterministic engines, permissions, scenarios and tests were preserved.

