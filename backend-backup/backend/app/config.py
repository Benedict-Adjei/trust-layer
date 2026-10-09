"""Backend-only configuration. Loading a key does not enable paid requests."""
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"


def load_environment():
    # Explicit path; no search through parent folders or frontend configuration.
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


@dataclass(frozen=True)
class ContextualSettings:
    enabled: bool = False
    api_key: SecretStr | None = None
    model: str = ""
    timeout_seconds: float = 4.0
    valid: bool = True

    @classmethod
    def from_environment(cls):
        enabled = os.getenv("FEATHERLESS_ENABLED", "false").strip().lower() == "true"
        key = os.getenv("FEATHERLESS_API_KEY", "").strip()
        model = os.getenv("FEATHERLESS_MODEL", "").strip()
        base_url = os.getenv("FEATHERLESS_BASE_URL", FEATHERLESS_BASE_URL).strip().rstrip("/")
        try:
            timeout = float(os.getenv("FEATHERLESS_TIMEOUT_SECONDS", "4"))
        except ValueError:
            timeout = 4.0
            valid = False
        else:
            valid = math.isfinite(timeout) and 0.5 <= timeout <= 8
        # Never send a credential to an arbitrary configured host or redirect.
        valid = valid and base_url == FEATHERLESS_BASE_URL
        valid = valid and len(model) <= 200 and (not model or bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._/-]{0,160}", model)))
        if key and key in model:
            valid = False
        return cls(enabled, SecretStr(key) if key else None, model, timeout, valid)
