"""Esquemas públicos S08: metadatos, identidad y observaciones delimitadas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PublicModel(BaseModel):
    """Contrato estricto, sin campos adicionales ni coerción silenciosa."""
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Health(PublicModel):
    """Disponibilidad del proceso, no salud de la infraestructura."""
    project: Literal["NETLAB360"] = "NETLAB360"
    schema_version: Literal[1] = 1
    service: Literal["netlab360-s08-console"] = "netlab360-s08-console"
    mode: Literal["BOOTSTRAP_READ_ONLY", "AUTHENTICATED_READ_ONLY"] = "BOOTSTRAP_READ_ONLY"
    healthy: Literal[True] = True
    infrastructure_state: Literal["UNKNOWN"] = "UNKNOWN"
    generated_at_utc: datetime
    network_mutations_authorized: Literal[False] = False


class Capabilities(PublicModel):
    """Inventario de funciones disponibles y pendientes durante el arranque."""
    project: Literal["NETLAB360"] = "NETLAB360"
    schema_version: Literal[1] = 1
    mode: Literal["BOOTSTRAP_READ_ONLY", "AUTHENTICATED_READ_ONLY"] = "BOOTSTRAP_READ_ONLY"
    health_available: Literal[True] = True
    source_readers_enabled: bool = False
    persistence_enabled: bool = False
    authentication_enabled: bool = False
    frontend_enabled: Literal[False] = False
    diagnostics_enabled: bool = False
    advisory_enabled: bool = False
    network_mutations_authorized: Literal[False] = False


class ApiError(PublicModel):
    """Error HTTP sin detalles internos, rutas locales ni credenciales."""
    error: Literal["NOT_FOUND", "METHOD_NOT_ALLOWED", "HTTP_ERROR", "BAD_REQUEST",
                   "UNAUTHENTICATED", "FORBIDDEN", "BODY_TOO_LARGE",
                   "UNSUPPORTED_MEDIA_TYPE", "RATE_LIMITED", "UNAVAILABLE"]
    network_mutations_authorized: Literal[False] = False

class LoginInput(PublicModel):
    """Credenciales recibidas sin coerción; nunca se devuelven al cliente."""
    username: str
    password: str


class Identity(PublicModel):
    """Identidad local autenticada, sin autorización administrativa."""
    username: str
    role: Literal["VIEWER", "OPERATOR"]
    network_mutations_authorized: Literal[False] = False


class LoginResult(Identity):
    """El token de sesión viaja únicamente en la cookie HttpOnly."""
    csrf_token: str
    expires_at: int


class LogoutResult(PublicModel):
    """Confirmación de revocación local."""
    logged_out: Literal[True] = True
    network_mutations_authorized: Literal[False] = False


class SourceObservation(PublicModel):
    """Observación delimitada; los detalles no vigentes se omiten."""
    schema_id: Literal["NETLAB360_S08_SOURCE_V1"] = Field(alias="schema")
    source: Literal["EXPORTER_S04", "NOC_S05", "PROMETHEUS_S04", "IA_S06", "ADVISORY_S07"]
    kind: Literal["OBSERVATION", "INFERENCE", "ADVISORY_SNAPSHOT"]
    transport: Literal["OK", "UNAVAILABLE", "NOT_STARTED", "INVALID"]
    quality: Literal["VALID", "MISSING", "INVALID", "FUTURE", "STALE"]
    state: Literal["NORMAL", "DEGRADED", "FAULT", "RECOVERY", "UNKNOWN"]
    observed_at_utc: str | None
    received_at_utc: str
    age_seconds: float | None
    max_age_seconds: int
    resource: str
    scope: str
    details: dict[str, str | int | float | bool | None]
    network_mutations_authorized: Literal[False] = False


class SourceBatch(PublicModel):
    """Resultados independientes, sin inferencia global de salud."""
    project: Literal["NETLAB360"] = "NETLAB360"
    schema_version: Literal[1] = 1
    observations: list[SourceObservation]
    infrastructure_state: Literal["UNKNOWN"] = "UNKNOWN"
    network_mutations_authorized: Literal[False] = False
