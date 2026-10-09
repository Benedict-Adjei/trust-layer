import json
import sqlite3

import pytest
from sqlalchemy.pool import NullPool

from app.database import Database, postgres_url
from app.schemas.action import AgentAction
from app.services.policy_engine import analyze
from app.services.scenarios import SCENARIOS


@pytest.mark.parametrize("scheme", ["postgres", "postgresql", "postgresql+psycopg"])
def test_postgres_configuration_uses_transaction_pooler(monkeypatch, scheme):
    monkeypatch.setenv("DATABASE_URL", f"{scheme}://user:password@example.invalid:6543/postgres?sslmode=require")
    monkeypatch.setenv("VERCEL", "1")
    database = Database()
    assert database.path is None
    assert database.engine.url.drivername == "postgresql+psycopg"
    assert database.engine.url.query["sslmode"] == "require"
    assert isinstance(database.engine.pool, NullPool)
    # Inspect driver arguments without opening an outbound connection.
    calls = []
    def capture_connect(*args, **kwargs):
        calls.append(kwargs)
        raise RuntimeError("mock connection")
    monkeypatch.setattr(database.engine.dialect, "connect", capture_connect)
    with pytest.raises(RuntimeError, match="mock connection"):
        with database.connect():
            pass
    assert calls[0]["prepare_threshold"] is None
    assert calls[0]["connect_timeout"] == 10
    database.close()


def test_vercel_requires_persistent_database(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    with pytest.raises(RuntimeError, match="Configure DATABASE_URL"):
        Database()


@pytest.mark.parametrize("value", ["not-a-url", "sqlite:///secret", "mysql://user:secret@host/db"])
def test_invalid_database_url_is_sanitized(value):
    with pytest.raises(ValueError) as failure:
        postgres_url(value)
    assert value not in str(failure.value)
    assert "secret" not in str(failure.value)


def test_existing_sqlite_audit_survives_storage_upgrade(tmp_path):
    path = tmp_path / "existing.sqlite3"
    action = AgentAction.model_validate(SCENARIOS[0]["action"])
    result = analyze(action)
    # Reproduce the pre-deployment schema and an existing audit record.
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE audit (action_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, decision TEXT NOT NULL, agent_name TEXT NOT NULL, action_metadata TEXT NOT NULL, result TEXT NOT NULL)")
        connection.execute("INSERT INTO audit VALUES (?,?,?,?,?,?)", (
            result.action_id, "2026-10-09T00:00:00+00:00", result.decision,
            action.agent_name, json.dumps({"agent_name": action.agent_name}),
            result.model_dump_json(),
        ))
    database = Database(path)
    database.initialize()
    assert database.audit()["total"] == 1
    assert database.audit()["items"][0]["result"]["action_id"] == result.action_id
    database.record(action, analyze(action))
    database.close()
    reopened = Database(path)
    reopened.initialize()
    assert reopened.audit()["total"] == 2
    assert len(reopened.catalog("scenarios")) == 6
    reopened.close()
