"""Local SQLite storage. No network services or action execution."""
import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.services.agent_permissions import PROFILES
from app.services.policy_engine import POLICIES
from app.services.scenarios import SCENARIOS

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "trustlayer.sqlite3"


class Database:
    def __init__(self, path=None):
        self.path = Path(path or os.environ.get("TRUSTLAYER_DB_PATH", DEFAULT_PATH))

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS agents (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS policies (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS scenarios (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS audit (
                    action_id TEXT PRIMARY KEY, created_at TEXT NOT NULL,
                    decision TEXT NOT NULL, agent_name TEXT NOT NULL,
                    action_metadata TEXT NOT NULL, result TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS audit_created ON audit(created_at);
                CREATE INDEX IF NOT EXISTS audit_decision ON audit(decision);
            ''')
            for table, items in (
                ("agents", [{"id": name, "name": name, **profile} for name, profile in PROFILES.items()]),
                ("policies", POLICIES), ("scenarios", SCENARIOS),
            ):
                conn.executemany(f"INSERT OR IGNORE INTO {table}(id,payload) VALUES (?,?)",
                                 [(item["id"], json.dumps(item)) for item in items])

    def catalog(self, table, identifier=None):
        if table not in {"agents", "policies", "scenarios"}:
            raise ValueError("Unsupported catalog")
        with self.connect() as conn:
            if identifier is not None:
                row = conn.execute(f"SELECT payload FROM {table} WHERE id=?", (identifier,)).fetchone()
                return json.loads(row[0]) if row else None
            return [json.loads(row[0]) for row in conn.execute(f"SELECT payload FROM {table} ORDER BY id")]

    def record(self, action, result):
        # Avoid retaining source content, tasks, destinations or resource names.
        metadata = action.model_dump(exclude={"external_content", "user_task", "action_target", "requested_resources"})
        metadata["requested_resource_count"] = len(action.requested_resources)
        metadata["has_target"] = bool(action.action_target)
        metadata["request_sha256"] = hashlib.sha256(action.model_dump_json().encode()).hexdigest()
        with self.connect() as conn:
            conn.execute("INSERT INTO audit VALUES (?,?,?,?,?,?)", (
                result.action_id, datetime.now(timezone.utc).isoformat(), result.decision,
                action.agent_name, json.dumps(metadata), result.model_dump_json(exclude_none=True),
            ))

    def audit(self, limit=50, offset=0, decision=None, identifier=None):
        where, params = [], []
        if identifier:
            where.append("action_id=?")
            params.append(identifier)
        if decision:
            where.append("decision=?")
            params.append(decision)
        clause = " WHERE " + " AND ".join(where) if where else ""
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM audit" + clause, params).fetchone()[0]
            rows = conn.execute("SELECT * FROM audit" + clause + " ORDER BY created_at DESC, action_id LIMIT ? OFFSET ?",
                                [*params, -1 if limit is None else limit, offset]).fetchall()
        items = [{"action_id": row["action_id"], "created_at": row["created_at"],
                  "action": json.loads(row["action_metadata"]), "result": json.loads(row["result"])} for row in rows]
        return {"items": items, "total": total, "limit": limit, "offset": offset}
