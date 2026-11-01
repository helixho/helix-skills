"""Shared domain contracts for the three agent-facing skill entrypoints."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Any, TextIO


class ContractError(ValueError):
    """Raised when caller input cannot satisfy a stable core contract."""


class OperationScope(StrEnum):
    SKILL_UNIT = "skill_unit"
    SOURCE_PROJECT = "source_project"


class RequestState(StrEnum):
    DRAFT = "draft"
    PREVIEWED = "previewed"
    APPROVED = "approved"
    EXECUTING = "executing"
    DRIFTED = "drifted"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class SkillIdentity:
    """Stable identity composed from a source project and relative skill path."""

    source_project: str
    skill_unit: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_project", canonical_source_project(self.source_project))
        object.__setattr__(self, "skill_unit", canonical_skill_unit(self.skill_unit))

    @property
    def key(self) -> str:
        return json.dumps([self.source_project, self.skill_unit], ensure_ascii=False, separators=(",", ":"))


def _has_control_character(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


def canonical_source_project(value: str) -> str:
    normalized = value.strip().rstrip("/")
    if not normalized or _has_control_character(normalized):
        raise ContractError("source_project must be non-empty and free of control characters")
    return normalized


def canonical_skill_unit(value: str) -> str:
    candidate = value.strip().replace("\\", "/")
    path = PurePosixPath(candidate)
    if (
        not candidate
        or path.is_absolute()
        or ".." in path.parts
        or candidate == "."
        or _has_control_character(candidate)
    ):
        raise ContractError("skill_unit must be a relative canonical subpath")
    return path.as_posix()


@dataclass(frozen=True)
class JsonResult:
    """The common stdout shape for every local entrypoint."""

    ok: bool
    result: dict[str, Any] | None = None
    error: dict[str, str] | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)


def read_json_request(stream: TextIO) -> dict[str, Any]:
    """Read one JSON object, raising ContractError without leaking parser details."""

    raw = stream.read()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError("request must be valid JSON") from exc
    if not isinstance(value, dict):
        raise ContractError("request must be a JSON object")
    return value


def json_success(**result: Any) -> JsonResult:
    return JsonResult(ok=True, result=result)


def json_error(code: str, message: str) -> JsonResult:
    return JsonResult(ok=False, error={"code": code, "message": message})
