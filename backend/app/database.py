"""Persistent PostgreSQL storage on Vercel, SQLite for local development."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import Column, Index, MetaData, Table, Text, create_engine, func, select, text
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import URL, make_url
from sqlalchemy.pool import NullPool

from app.services.agent_permissions import PROFILES
from app.services.policy_engine import POLICIES
from app.services.scenarios import SCENARIOS

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "trustlayer.sqlite3"
metadata = MetaData()
catalog_tables = {
    name: Table(name, metadata, Column("id", Text, primary_key=True),
                Column("payload", Text, nullable=False))
    for name in ("agents", "policies", "scenarios")
}
audit_table = Table(
    "audit", metadata,
    Column("action_id", Text, primary_key=True),
    Column("created_at", Text, nullable=False),
    Column("decision", Text, nullable=False),
    Column("agent_name", Text, nullable=False),
    Column("action_metadata", Text, nullable=False),
    Column("result", Text, nullable=False),
)
Index("audit_created", audit_table.c.created_at)
Index("audit_decision", audit_table.c.decision)


def postgres_url(value):
    """Select psycopg without logging or echoing the connection credential."""
    try:
        url = make_url(value)
    except Exception:
        raise ValueError("DATABASE_URL must be a valid PostgreSQL connection URL") from None
    if url.drivername not in {"postgres", "postgresql", "postgresql+psycopg"}:
        raise ValueError("DATABASE_URL must use PostgreSQL")
    return url.set(drivername="postgresql+psycopg")


class Database:
    def __init__(self, path=None):
        database_url = os.environ.get("DATABASE_URL", "").strip()
        if path is None and database_url:
            self.path = None
            # Supabase transaction pooling manages server connections. Disable
            # client pooling and prepared statements for transaction poolers.
            self.engine = create_engine(
                postgres_url(database_url), poolclass=NullPool,
                connect_args={"connect_timeout": 10, "prepare_threshold": None},
                hide_parameters=True,
            )
        else:
            if path is None and os.environ.get("VERCEL") == "1":
                raise RuntimeError("Configure DATABASE_URL for persistent audit storage on Vercel")
            self.path = Path(path or os.environ.get("TRUSTLAYER_DB_PATH", DEFAULT_PATH))
            self.engine = create_engine(
                URL.create("sqlite", database=str(self.path)),
                connect_args={"timeout": 10, "check_same_thread": False},
                poolclass=NullPool, hide_parameters=True,
            )

    def connect(self):
        return self.engine.begin()

    def close(self):
        self.engine.dispose()

    def initialize(self):
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            # Serialize cold-start table creation across PostgreSQL instances.
            if self.engine.dialect.name == "postgresql":
                conn.execute(text("SELECT pg_advisory_xact_lock(824739102)"))
            metadata.create_all(conn)
            if self.engine.dialect.name == "postgresql":
                # Supabase's browser Data API must not expose these tables.
                # The privileged backend connection owns all reads and writes.
                for table in metadata.sorted_tables:
                    conn.execute(text(f'ALTER TABLE "{table.name}" ENABLE ROW LEVEL SECURITY'))
            insert = postgres_insert if self.engine.dialect.name == "postgresql" else sqlite_insert
            for name, items in (
                ("agents", [{"id": name, "name": name, **profile}
                            for name, profile in PROFILES.items()]),
                ("policies", POLICIES), ("scenarios", SCENARIOS),
            ):
                table = catalog_tables[name]
                rows = [{"id": item["id"], "payload": json.dumps(item)} for item in items]
                # One multi-row statement avoids psycopg executemany pipelining
                # on the Supabase transaction pooler.
                conn.execute(insert(table).values(rows).on_conflict_do_nothing(index_elements=["id"]))

    def catalog(self, table, identifier=None):
        if table not in catalog_tables:
            raise ValueError("Unsupported catalog")
        relation = catalog_tables[table]
        query = select(relation.c.payload)
        with self.connect() as conn:
            if identifier is not None:
                payload = conn.execute(query.where(relation.c.id == identifier)).scalar_one_or_none()
                return json.loads(payload) if payload is not None else None
            return [json.loads(payload) for payload in
                    conn.execute(query.order_by(relation.c.id)).scalars()]

    def record(self, action, result):
        # Avoid retaining source content, tasks, destinations or resource names.
        action_metadata = action.model_dump(exclude={
            "external_content", "user_task", "action_target", "requested_resources",
        })
        action_metadata["requested_resource_count"] = len(action.requested_resources)
        action_metadata["has_target"] = bool(action.action_target)
        action_metadata["request_sha256"] = hashlib.sha256(action.model_dump_json().encode()).hexdigest()
        with self.connect() as conn:
            conn.execute(audit_table.insert().values(
                action_id=result.action_id,
                created_at=datetime.now(timezone.utc).isoformat(),
                decision=result.decision, agent_name=action.agent_name,
                action_metadata=json.dumps(action_metadata),
                result=result.model_dump_json(exclude_none=True),
            ))

    def audit(self, limit=50, offset=0, decision=None, identifier=None):
        filters = []
        if identifier:
            filters.append(audit_table.c.action_id == identifier)
        if decision:
            filters.append(audit_table.c.decision == decision)
        query = select(audit_table).where(*filters).order_by(
            audit_table.c.created_at.desc(), audit_table.c.action_id,
        ).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        with self.connect() as conn:
            total = conn.execute(select(func.count()).select_from(audit_table).where(*filters)).scalar_one()
            rows = conn.execute(query).mappings().all()
        items = [{"action_id": row["action_id"], "created_at": row["created_at"],
                  "action": json.loads(row["action_metadata"]), "result": json.loads(row["result"])}
                 for row in rows]
        return {"items": items, "total": total, "limit": limit, "offset": offset}
