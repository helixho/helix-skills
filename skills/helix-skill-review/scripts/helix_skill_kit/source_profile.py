"""Source-project profiles; separate from individual skill scoring."""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .contracts import ContractError, canonical_source_project


SOURCE_PROFILE_DIMENSIONS = frozenset({
    "system_coherence",
    "internal_dependency_value",
    "learning_value",
    "operational_health",
    "library_fit",
})
SOURCE_CLASSES = frozenset({"whole-project-preserve", "study-first", "standalone-friendly", "source-review-needed"})
_RUBRIC_PATH = Path(__file__).resolve().parents[2] / "references/source-profile-rubric.md"


@dataclass(frozen=True)
class SourceProfileRubric:
    identifier: str
    source_hash: str


def load_source_profile_rubric() -> SourceProfileRubric:
    raw = _RUBRIC_PATH.read_bytes()
    text = raw.decode("utf-8")
    match = re.match(r"---\n(?P<frontmatter>.*?)\n---\n", text, re.DOTALL)
    if match is None:
        raise ContractError("source-profile rubric has invalid frontmatter")
    fields = {key.strip(): value.strip() for line in match.group("frontmatter").splitlines() if ":" in line for key, value in [line.split(":", 1)]}
    if fields.get("rubric_id") != "helix-source-profile":
        raise ContractError("built-in source-profile rubric has an unexpected rubric_id")
    return SourceProfileRubric("helix-source-profile", hashlib.sha256(raw).hexdigest())


def validate_profile(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("source profile must be an object")
    source_project = canonical_source_project(value.get("source_project", ""))
    source_hash = value.get("source_hash")
    if not isinstance(source_hash, str) or not source_hash.strip():
        raise ContractError("source_hash is required")
    classification = value.get("classification")
    if classification not in SOURCE_CLASSES:
        raise ContractError("classification is not registered")
    dimensions = value.get("dimensions")
    if not isinstance(dimensions, dict) or set(dimensions) != SOURCE_PROFILE_DIMENSIONS:
        raise ContractError("dimensions must contain the five registered source-profile dimensions")
    if any(isinstance(score, bool) or not isinstance(score, (int, float)) or not 1 <= score <= 5 for score in dimensions.values()):
        raise ContractError("every source-profile dimension score must be between 1 and 5")
    output = {"source_project": source_project, "source_hash": source_hash, "classification": classification, "dimensions": dimensions}
    for field in ("evidence", "findings", "guidance"):
        entries = value.get(field, [])
        if not isinstance(entries, list) or any(not isinstance(item, str) or not item.strip() for item in entries):
            raise ContractError(f"{field} must be a list of non-empty strings")
        output[field] = entries
    return output


class SourceProfileService:
    def __init__(self) -> None:
        self.rubric = load_source_profile_rubric()

    def evaluate(self, value: dict[str, Any]) -> dict[str, Any]:
        profile = validate_profile(value)
        assessed_at = datetime.now(UTC).isoformat(timespec="seconds")
        profile_id = str(uuid.uuid4())
        return {
            "profile_id": profile_id,
            "assessed_at": assessed_at,
            **profile,
            "rubric": {
                "id": self.rubric.identifier,
                "hash": self.rubric.source_hash,
            },
        }
