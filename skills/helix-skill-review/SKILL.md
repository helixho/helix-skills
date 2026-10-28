---
name: helix-skill-review
description: >-
  评估 skill 以找出改进点：检查目录与 SKILL.md frontmatter 是否合规，按内置评分标准和评估指南记录评分、证据、发现和改进建议，
  也评估外部 skill 有哪些值得借鉴到自己的 skill。用于“评估这个 skill”“给 skill 打分”“检查 skill 结构”“这个外部 skill 有什么值得借鉴”。
  只读源码，不测试运行行为，也不修改 skill 或运行时。
---

# Helix Skill Review

Two uses, both ending in concrete improvements to a skill the user owns.

## Assess a skill

The default for any request to assess, check, or score a skill.

1. Run `validate` with the skill's source directory as `skill_dir`; for a
   published skill add `"public": true` to scan for personal home paths. Every
   conformance error and isolation finding is a finding.
2. Apply `references/review-guide.md`: settle Positioning first, then judge each
   dimension with its checks, labeling every piece of evidence as the guide
   describes.
3. Score the nine dimensions of `references/scorecard-rubric.md` and submit them
   with `evaluate`, passing `skill_dir`, the labeled `evidence`, `findings`, and
   `suggestions`. It computes the content hash and the average.
4. Report prioritized improvements tied to findings, with the scores as a
   summary.

For several skills, assess each one, then rank the improvements across them.

## Borrow from an external skill

To improve one of the user's own skills from an external one, follow
"Reviewing an external skill as a reference" in `references/review-guide.md`.
No scorecard is needed.

## Script

Run `python3 scripts/run.py` (Python 3.11+ with PyYAML from
`scripts/requirements.txt`). It reads one JSON request on stdin, writes one JSON
result on stdout, and keeps no state. Commands: `describe`, `validate`,
`evaluate`. The rubric is built in and its ID and file hash are recorded with
every scorecard; a caller cannot supply or override it.

The design is in `references/architecture.md` and the concepts in
`references/ontology.md`; read them only when changing this skill.

## Boundary

- Read the assessed skill's source and, for Positioning, the configuration and
  rules that invoke it or overlap with it. Write nothing: no skill, runtime
  link, or assessment record.
- Assess source only; no scorecard claims runtime verification.
- Suggestions are advisory. Edits and runtime link changes happen outside this
  skill after the user approves them.
