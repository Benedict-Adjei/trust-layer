"""Strict models for untrusted provider output and server-owned metadata."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

Threat = Literal[
    "indirect_prompt_injection", "data_exfiltration", "authority_impersonation",
    "social_engineering", "payment_fraud", "privilege_escalation", "secret_extraction",
    "intent_mismatch", "unrelated_resource_access", "instruction_override",
    "suspicious_recipient", "coercion",
]


class ModelAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True, allow_inf_nan=False)
    instruction_conflict: StrictBool
    untrusted_instruction: StrictBool
    intent_mismatch: StrictBool
    threats: list[Threat] = Field(max_length=12)
    reasoning: str = Field(min_length=1, max_length=1500)
    recommendation: str = Field(min_length=1, max_length=800)
    confidence: float = Field(ge=0, le=1)

    @field_validator("threats")
    @classmethod
    def unique_threats(cls, threats):
        if len(threats) != len(set(threats)):
            raise ValueError("Threat categories must be unique")
        return threats


class ContextualAvailable(ModelAssessment):
    available: Literal[True] = True
    provider: Literal["featherless"] = "featherless"
    model: str = Field(min_length=1, max_length=200)


class ContextualUnavailable(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    available: Literal[False] = False
    reason: Literal[
        "disabled", "missing_api_key", "missing_model", "invalid_configuration",
        "non_simulated_action", "timeout", "provider_error", "invalid_response",
    ]


ContextualAnalysis = Annotated[
    ContextualAvailable | ContextualUnavailable, Field(discriminator="available")
]
