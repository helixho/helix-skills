"""Versioned, advisory skill evaluation."""

from __future__ import annotations

import hashlib
import math
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .contracts import ContractError, SkillIdentity


@dataclass(frozen=True)
class Rubric:
    identifier: str
    version: str
    content: str
    source_hash: str

    def __post_init__(self) -> None:
        values = (self.identifier, self.version, self.content, self.source_hash)
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ContractError("rubric id, version, and content are required")

    @property
    def hash(self) -> str:
        return self.source_hash

    @property
    def dimensions(self) -> tuple[str, ...]:
        section = re.search(r"^## Dimensions\s*\n(.*?)(?=^## |\Z)", self.content, re.M | re.S)
        if section is None:
            raise ContractError("registered rubric has no Dimensions section")
        rows = re.findall(r"^\|\s*([^|]+?)\s*\|", section.group(1), re.M)
        names = tuple(row.strip() for row in rows if row.strip() != "Dimension" and not re.fullmatch(r"[-: ]+", row))
        if not names or len(names) != len(set(names)):
            raise ContractError("registered rubric dimensions must be non-empty and unique")
        return names


_RUBRIC_ROOT = Path(__file__).resolve().parents[2] / "references"
_RUBRIC_REGISTRY = {
    ("helix-skill-scorecard", "1.6.0"): _RUBRIC_ROOT / "batch-rubric-v1.6.md",
}
_RUNTIME_STATUSES = frozenset({"not_checked", "passed", "failed"})


def load_rubric(identifier: str = "helix-skill-scorecard", version: str = "1.6.0") -> Rubric:
    path = _RUBRIC_REGISTRY.get((identifier, version))
    if path is None:
        raise ContractError("rubric id/version is not registered")
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    match = re.match(r"---\n(?P<frontmatter>.*?)\n---\n(?P<content>.*)", text, re.DOTALL)
    if match is None:
        raise ContractError("registered rubric has invalid frontmatter")
    fields = {
        key.strip(): value.strip()
        for line in match.group("frontmatter").splitlines()
        if ":" in line
        for key, value in [line.split(":", 1)]
    }
    if fields.get("rubric_id") != identifier or fields.get("version") != version:
        raise ContractError("registered rubric metadata does not match its registry key")
    return Rubric(identifier, version, match.group("content"), hashlib.sha256(raw).hexdigest())


def evaluate_scores(scores: dict[str, float], rubric: Rubric | None = None) -> dict[str, Any]:
    if not isinstance(scores, dict) or not scores:
        raise ContractError("scores are required")
    if any(not isinstance(key, str) or not key.strip() for key in scores):
        raise ContractError("score dimensions must be non-empty strings")
    expected = set((rubric or load_rubric()).dimensions)
    missing = sorted(expected - scores.keys())
    unexpected = sorted(scores.keys() - expected)
    if missing or unexpected:
        raise ContractError(f"scores must match the registered rubric dimensions; missing={missing}; unexpected={unexpected}")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 1 or value > 5 or not math.isfinite(value) for value in scores.values()):
        raise ContractError("every score must be between 1 and 5")
    return {"scores": scores, "average": round(sum(scores.values()) / len(scores), 1)}


class EvaluationService:
    def __init__(self) -> None:
        self.rubric = load_rubric()

    def evaluate(
        self,
        identity: SkillIdentity,
        content_hash: str,
        scores: dict[str, float],
        authoring_evidence: list[str],
        runtime_evidence: list[str],
        runtime_status: str,
        findings: list[str],
        suggestions: list[str],
        assessed_at: str | None = None,
    ) -> dict[str, Any]:
        if runtime_status not in _RUNTIME_STATUSES:
            raise ContractError("runtime_status must be not_checked, passed, or failed")
        if runtime_status != "not_checked" and not runtime_evidence:
            raise ContractError("passed or failed runtime_status requires runtime_evidence")
        if runtime_status == "not_checked" and runtime_evidence:
            raise ContractError("runtime_evidence requires passed or failed runtime_status")
        assessment = evaluate_scores(scores, self.rubric)
        timestamp = assessed_at or datetime.now(UTC).isoformat(timespec="seconds")
        assessment_id = str(uuid.uuid4())
        payload = {
            **assessment,
            "evidence": {
                "authoring": authoring_evidence,
                "runtime": runtime_evidence,
            },
            "runtime_status": runtime_status,
            "findings": findings,
            "suggestions": suggestions,
        }
        return {
            "assessment_id": assessment_id,
            "assessed_at": timestamp,
            "identity": {
                "source_project": identity.source_project,
                "skill_unit": identity.skill_unit,
            },
            "content_hash": content_hash,
            "rubric": {
                "id": self.rubric.identifier,
                "version": self.rubric.version,
                "hash": self.rubric.hash,
            },
            **payload,
        }

    def evaluate_many(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        if not isinstance(items, list) or not items:
            raise ContractError("items must be a non-empty list")
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        assessments = [self.evaluate(**item, assessed_at=timestamp) for item in items]
        return {
            "assessments": assessments,
            "comparison": sorted(
                [{"assessment_id": item["assessment_id"], "average": item["average"]} for item in assessments],
                key=lambda item: item["average"],
                reverse=True,
            ),
        }
