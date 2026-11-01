"""Identity normalization for source projects and their skill units."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .contracts import ContractError, SkillIdentity


def make_identity(source_project: str, skill_unit: str) -> SkillIdentity:
    return SkillIdentity(source_project=source_project, skill_unit=skill_unit)


def content_hash(skill_dir: Path) -> str:
    """Hash every file under the skill directory by relative path and bytes."""
    root = skill_dir.expanduser().resolve()
    if not root.is_dir():
        raise ContractError("skill_dir must be an existing directory")
    digest = hashlib.sha256()
    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store"
    )
    for path in files:
        data = path.read_bytes()
        digest.update(f"{path.relative_to(root).as_posix()}\0{len(data)}\0".encode("utf-8"))
        digest.update(data)
    return digest.hexdigest()
