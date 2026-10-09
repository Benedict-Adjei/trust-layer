# TrustLayer frontend

React, Vite, TypeScript, Lucide icons, and Recharts. All scenario, audit, policy,
profile and metric data comes from FastAPI. There is no mock API fallback.

```powershell
npm ci
# Optional configuration; existing .env files should be preserved:
Copy-Item .env.example .env
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Start the backend on localhost:8000 first. See the root README for the complete
demo walkthrough. VITE_API_URL defaults to http://127.0.0.1:8000. Vite reads this
at startup/build time, so restart/rebuild after configuration changes.

```powershell
npm run lint
npm run typecheck
npm run build
npm run preview -- --host 127.0.0.1 --port 5173 --strictPort
```

Navigation uses URL hashes for direct links and browser back/forward without a
router dependency. Audit history has server-side decision filtering and pagination.
Lifetime metric counts use backend audit totals. Risk charts use up to the latest
200 records, and clearly identify the sample. Charts also have accessible summaries.
API requests time out after 15 seconds and are never retried automatically,
especially analyses that could already have been recorded. Each analysis refreshes
subsequent dashboard/audit views. The health indicator checks every 30 seconds.

The UI supports mobile layouts, keyboard navigation, reduced motion, loading,
empty and error states. The seeded scenarios are read-only proposals: no sending,
payment, cloud access, or destructive operations are performed.

## Contextual evidence

New analyses request `?contextual=true` from FastAPI. Result and audit views show
an advisory AI Contextual Analysis section when the backend supplies validated
evidence: conflict flags, threats, self-reported confidence, reasoning,
recommendation and configured model. The deterministic badge, score and next action
remain authoritative. Older records and provider failures display an unavailable
state without blocking the result. There is no frontend provider call, API key,
activation control or production mock fallback. Enable the provider only through
backend configuration after choosing to permit paid usage.
