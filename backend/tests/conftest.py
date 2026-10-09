"""Tests cannot use a real provider credential or outbound HTTP transport."""
import httpx
import pytest


@pytest.fixture(autouse=True)
def isolate_provider(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setenv("FEATHERLESS_ENABLED", "false")
    monkeypatch.setenv("FEATHERLESS_API_KEY", "")
    monkeypatch.setenv("FEATHERLESS_MODEL", "")
    monkeypatch.setenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
    monkeypatch.setenv("FEATHERLESS_TIMEOUT_SECONDS", "4")

    def reject_sync(*args, **kwargs):
        raise AssertionError("Tests must mock outbound HTTP")

    async def reject_async(*args, **kwargs):
        raise AssertionError("Tests must mock outbound HTTP")

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", reject_sync)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", reject_async)
