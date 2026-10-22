"""Read-only structural conformance checks for the Agent Skills specification."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ALLOWED_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}


def _parse_skill_markdown(path: Path) -> tuple[dict[str, Any] | None, str, list[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, "", ["SKILL.md must be valid UTF-8"]
    if not text.startswith("---\n"):
        return None, "", ["SKILL.md must start with YAML frontmatter at the first byte"]
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, "", ["SKILL.md frontmatter must close with --- before the Markdown body"]
    try:
        frontmatter = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        return None, "", [f"SKILL.md frontmatter must be valid YAML: {exc}"]
    if not isinstance(frontmatter, dict):
        return None, "", ["SKILL.md frontmatter must be a YAML mapping"]
    return frontmatter, text[end + 5 :], []


def validate_skill_directory(skill_dir: Path) -> dict[str, Any]:
    """Return deterministic Agent Skills conformance facts without writing files."""
    root = skill_dir.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = root / "SKILL.md"

    if not root.is_dir():
        errors.append("skill_dir must be an existing directory")
    elif not skill_md.is_file():
        errors.append("skill directory must contain SKILL.md at its root")

    frontmatter: dict[str, Any] | None = None
    body = ""
    if not errors:
        frontmatter, body, parse_errors = _parse_skill_markdown(skill_md)
        errors.extend(parse_errors)

    if frontmatter is not None:
        unknown = sorted(set(frontmatter) - _ALLOWED_FRONTMATTER_FIELDS)
        if unknown:
            errors.append(f"unsupported top-level frontmatter fields: {', '.join(unknown)}")

        name = frontmatter.get("name")
        if not isinstance(name, str) or not name:
            errors.append("name must be a non-empty string")
        elif len(name) > 64 or not _NAME_RE.fullmatch(name):
            errors.append("name must be 1-64 lowercase letters, numbers, or single hyphens")
        elif name != root.name:
            errors.append("name must match the parent directory name")

        description = frontmatter.get("description")
        if not isinstance(description, str) or not description:
            errors.append("description must be a non-empty string")
        elif len(description) > 1024:
            errors.append("description must be at most 1024 characters")

        compatibility = frontmatter.get("compatibility")
        if compatibility is not None and (
            not isinstance(compatibility, str) or not 1 <= len(compatibility) <= 500
        ):
            errors.append("compatibility must be a 1-500 character string")

        metadata = frontmatter.get("metadata")
        if metadata is not None and (
            not isinstance(metadata, dict)
            or any(not isinstance(key, str) or not isinstance(value, str) for key, value in metadata.items())
        ):
            errors.append("metadata must map string keys to string values")

        for field in ("license", "allowed-tools"):
            value = frontmatter.get(field)
            if value is not None and (not isinstance(value, str) or not value):
                errors.append(f"{field} must be a non-empty string")

        if not body.strip():
            errors.append("SKILL.md must contain a non-empty Markdown body")
        if len(skill_md.read_text(encoding="utf-8").splitlines()) > 500:
            warnings.append("SKILL.md exceeds the recommended 500-line limit")

    return {
        "skill_dir": str(root),
        "conformant": not errors,
        "errors": errors,
        "warnings": warnings,
        "specification": "https://agentskills.io/specification",
    }
