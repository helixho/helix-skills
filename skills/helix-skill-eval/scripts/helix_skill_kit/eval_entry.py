"""JSON stdin/stdout entrypoint for helix-skill-eval."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .contracts import ContractError, JsonResult, json_error, json_success, read_json_request
from .conformance import validate_skill_directory
from .eval import EvaluationService, load_rubric
from .identity import content_hash, make_identity
from .source_profile import SourceProfileService, load_source_profile_rubric


def _required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{name} must be a non-empty string")
    return value


def _text_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ContractError(f"{name} must be a list of strings")
    return value


def _item(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("every item must be an object")
    if rejected := sorted({"content_hash", "runtime_status", "runtime_evidence", "authoring_evidence"}.intersection(value)):
        raise ContractError(
            f"not accepted: {', '.join(rejected)}; the content hash is computed from skill_dir and runtime behavior is not assessed"
        )
    skill_dir = Path(_required_text(value.get("skill_dir"), "skill_dir"))
    scores = value.get("scores")
    if not isinstance(scores, dict):
        raise ContractError("scores must be an object")
    return {
        "identity": make_identity(
            _required_text(value.get("source_project"), "source_project"),
            _required_text(value.get("skill_unit"), "skill_unit"),
        ),
        "content_hash": content_hash(skill_dir),
        "scores": scores,
        "evidence": _text_list(value.get("evidence", []), "evidence"),
        "findings": _text_list(value.get("findings", []), "findings"),
        "suggestions": _text_list(value.get("suggestions", []), "suggestions"),
    }


def handle(request: dict[str, Any]) -> JsonResult:
    command = request.get("command")
    if command == "describe":
        rubric = load_rubric()
        source_rubric = load_source_profile_rubric()
        return json_success(
            entrypoint="helix-skill-eval",
            commands=["describe", "validate", "evaluate", "evaluate_many", "profile_source"],
            writes_external_state=False,
            persistence="none",
            rubric={"id": rubric.identifier, "hash": rubric.hash},
            source_profile_rubric={"id": source_rubric.identifier, "hash": source_rubric.source_hash},
        )
    try:
        rubric_fields = {"rubric", "rubric_id", "rubric_hash"}
        if supplied := sorted(rubric_fields.intersection(request)):
            raise ContractError(f"rubric is built in; caller-supplied fields are not accepted: {', '.join(supplied)}")
        if command == "validate":
            skill_dir = Path(_required_text(request.get("skill_dir"), "skill_dir"))
            return json_success(**validate_skill_directory(skill_dir))
        if command == "evaluate":
            item = _item(request)
            return json_success(assessment=EvaluationService().evaluate(**item))
        if command == "evaluate_many":
            raw_items = request.get("items")
            if not isinstance(raw_items, list):
                raise ContractError("items must be a list")
            items = [_item(item) for item in raw_items]
            return json_success(**EvaluationService().evaluate_many(items))
        if command == "profile_source":
            return json_success(profile=SourceProfileService().evaluate(request))
        return json_error(
            "unknown_command",
            "command must be describe, validate, evaluate, evaluate_many, or profile_source",
        )
    except (KeyError, TypeError, ValueError, ContractError) as exc:
        return json_error("invalid_request", str(exc))


def main() -> int:
    try:
        result = handle(read_json_request(sys.stdin))
    except ContractError as exc:
        result = json_error("invalid_json", str(exc))
    print(result.to_json())
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
