# Contextual analysis phase — verification (2026-10-07)

## Inspection and baseline

Inspected the repository layout; action and result schemas; risk/policy engines;
three permission profiles; six scenario definitions; SQLite seeding/audits; API
routes and startup; environment handling; dependencies; all original tests; and
the frontend API client, shared result component, audit rendering and threat model.

Before edits: **38 backend tests passed**, and frontend lint, TypeScript checks
and production build passed. The original test file, deterministic engines,
permission profiles, scenarios and dependency pins remain byte-for-byte unchanged.

## Implementation

The authoritative policy result is computed first. Optional contextual analysis
receives a JSON-separated user task, untrusted content, proposal and deterministic
evidence. The server validates the model assessment, supplies provider/model
metadata itself, and attaches only advisory evidence. Verdicts, scores, risk
levels, policy violations, signals and deterministic recommendations cannot be
changed by the model. No action executor or provider tools were added.

Legacy API requests retain their original nine response fields. The new frontend
opts in with `?contextual=true`. Validated evidence or a sanitized unavailable
reason is persisted in the existing audit result JSON; old records need no migration.

### Added files (this phase)

- `backend/app/config.py`
- `backend/app/schemas/contextual.py`
- `backend/app/services/contextual_analyzer.py`
- `backend/app/services/analysis_pipeline.py`
- `backend/tests/conftest.py`
- `backend/tests/test_contextual.py`
- `backend/.env.example`
- `frontend/src/components/ContextualPanel.tsx`
- `docs/CONTEXTUAL_VERIFICATION.md`

### Modified files (this phase)

- `backend/app/schemas/action.py` — optional evidence field.
- `backend/app/main.py` — backend-only environment/configuration initialization.
- `backend/app/api/actions.py`, `backend/app/api/catalog.py` — optional pipeline,
  backward-compatible serialization, audit writes outside the async event loop.
- `backend/app/database.py` — omit absent optional fields when persisting legacy results.
- `backend/.gitignore`, root `.gitignore` — local settings/generated artifact safety.
- `frontend/src/services/api.ts` — contextual response types and opt-in query.
- `frontend/src/components/shared.tsx` — shared contextual section for current and audited results.
- `frontend/src/components/About.tsx` — updated provider boundary explanation.
- `frontend/src/App.css` — focused contextual-section styling and responsive layout.
- `frontend/.env.example` — backend-only credential guidance.
- Root, backend and frontend README files — configuration, architecture, limits and demo instructions.

Two previously tracked generated `.pyc` files were removed from Git's index;
the physical local files were retained. No history was rewritten.

## Exact checks

| Check | Result |
| --- | --- |
| Baseline pytest | 38 passed, 1 existing warning, 6.03s |
| Final complete pytest suite | **124 passed**, 1 existing warning, 7.86s (default plugin loading) |
| New contextual cases | 86 passing cases |
| Frontend lint | Passed, no warnings |
| TypeScript typecheck | Passed |
| Production build | Passed, 2.56s; no oversized-chunk warning |
| HTTP integration, mocked provider available | All six passed |
| HTTP integration, provider disabled | All six passed |
| HTTP integration, mocked provider timeout | All six passed |
| CORS, health, legacy shape and audit persistence | Passed in all three HTTP modes |
| Browser safe / injection scenarios | ALLOW 0 and BLOCK 100 with available and disabled evidence |
| Browser timeout | BLOCK 100 retained; deadline fallback displayed |
| Browser audit inspection | Stored contextual evidence rendered correctly |
| Responsive contextual layout | Desktop verified; mobile 390px viewport / 375px content, no page overflow, two-column indicators |
| Browser console errors/warnings | None observed |
| Git whitespace check | Passed |

New tests cover structured success; missing key/model and disabled provider;
configuration rejection; timeouts and total-deadline cancellation; connection,
rate-limit, HTTP and protocol errors; invalid JSON/schema/lengths/confidence;
duplicate JSON fields; rejected tool calls; credential echoes including escaped
values; synthetic-input isolation; unchanged deterministic fields for every
scenario even when the model claims safety; legacy compatibility; and audit
records with AI available/unavailable. Four additional threat variants from the
request were tested without replacing the simulator catalog.

Real HTTP transports are blocked during pytest. External provider requests are
mocked. The temporary browser/HTTP harness used the actual repository backend and
frontend with an isolated SQLite database; only the Featherless transport was
mocked. The harness is outside the production repository and exposes no production
mock toggle. No paid inference, deployment or external action occurred.

## Six scenario outcomes

Each outcome was unchanged in enabled-with-mocks, disabled and timeout modes:

| Existing scenario | Verdict | Risk |
| --- | --- | --- |
| Safe Internal Project Update | ALLOW | 0/100 (low) |
| Indirect Prompt Injection | BLOCK | 100/100 (critical) |
| Safe Public Research | ALLOW | 0/100 (low) |
| Email Requires Approval | REVIEW REQUIRED | 30/100 (medium) |
| Payment Requires Approval | REVIEW REQUIRED | 60/100 (medium) |
| Research Permission Escalation | BLOCK | 100/100 (critical) |

Additional fixtures: supplier secret extraction BLOCK; manager/mobile-money
impersonation BLOCK; known-vendor confirmation REVIEW REQUIRED; excessive
admin/cloud permissions BLOCK. They are not outbound-provider-eligible because
only the six unchanged code-defined synthetic actions may be transmitted.

## Configuration, safeguards and limitations

Local provider configuration is **disabled**, with no key or model configured.
The available path was tested using mocks, not live Featherless inference. Real
model availability, account permissions, latency and output quality remain
unverified. Configure backend `.env` only after choosing to permit provider usage;
select an available model and restart FastAPI. Merely adding a key cannot enable it.

Provider calls use the verified official HTTPS endpoint, never an arbitrary host
or redirect. There are no retries or tools. A 4-second total deadline defaults;
valid configuration permits 0.5–8 seconds. Input is restricted to known synthetic
scenarios. Output is bounded to 32 KB with strict field/type/category validation.
Credentials never enter prompts; raw exceptions/responses are not exposed;
credential echoes are rejected; UI text is rendered through React text nodes.

Credential-pattern audit found no matches in 60 eligible worktree files and seven
local historical blobs. No environment files, virtual environments, node_modules,
databases, logs or bytecode are tracked in the current index. Ignore checks passed.
Twelve production build files also had no credential-pattern or backend API-key variable matches. Pattern scanning is a check, not a proof against every possible secret format.

The existing warning comes from Starlette selecting its deprecated httpx fallback
when httpx2 is absent. The installed source was inspected. A dependency migration
was deferred rather than changing the tested stack or hiding the warning.

The prototype still lacks authentication and trusted approval provenance;
deterministic heuristics are incomplete; model evidence can be wrong. AI confidence
is self-reported. No model output can authorize or execute anything.

Git contains intended local changes and pre-existing uncommitted MVP work. No
commit, push, force-push or history rewrite was performed. Backups are ignored under
`.trustlayer-backups/contextual-20261007-005948`.

## Run commands

Backend terminal:

```powershell
cd C:\Users\chrisB\trust-layer\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend terminal:

```powershell
cd C:\Users\chrisB\trust-layer\frontend
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Open http://127.0.0.1:5173. Verification:

```powershell
cd C:\Users\chrisB\trust-layer\backend
.\venv\Scripts\python.exe -m pytest -q
cd C:\Users\chrisB\trust-layer\frontend
npm run lint
npm run typecheck
npm run build
```

Next phase: authenticated agent identity and approval provenance, plus an adversarial
evaluation suite. A live provider smoke test needs a chosen key/model and explicit
permission to use the account's inference allowance.


