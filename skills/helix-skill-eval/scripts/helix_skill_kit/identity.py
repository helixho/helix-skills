"""Identity normalization for source projects and their skill units."""

from __future__ import annotations

from .contracts import SkillIdentity


def make_identity(source_project: str, skill_unit: str) -> SkillIdentity:
    return SkillIdentity(source_project=source_project, skill_unit=skill_unit)
