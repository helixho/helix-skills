---
name: helix-skill-eval
description: >-
  评估 skill 以找出改进点：检查目录与 SKILL.md frontmatter 是否合规，按内置评分标准和评估指南记录评分、证据、发现和改进建议，
  也评估外部 skill 有哪些值得借鉴到自己的 skill。用于“评估这个 skill”“给 skill 打分”“检查 skill 结构”“这个外部 skill 有什么值得借鉴”。
  只读源码，不测试运行行为，也不修改 skill 或运行时。
---

# Helix Skill Eval

## Choose the depth

- Routine edits need `validate` and a focused review of the changed behavior;
  do not require a nine-dimension scorecard for every edit.
- Use the scorecard for an explicitly requested score, comparison,
  or formal audit. The caller supplies the evidence and judgments; `evaluate`
  validates and packages those inputs, computes the content hash from
  `skill_dir`, and computes the mean score. It does not judge the skill or
  establish that it works.
- To improve one of the user's own skills from an external skill, follow
  "Reviewing an external skill as a reference" in `references/review-guide.md`;
  no scorecard is required.
- Source Profile is only for reviewing an upstream repository as a whole.

## Formal assessment

Use this skill to evaluate a skill, skill set, or upstream source project.
Produce comparable evidence, not automatic lifecycle actions. Keep one Skill
Scorecard per assessed content snapshot.
A Source Profile evaluates the upstream project as an interdependent system;
it does not overwrite the Skill Scorecard.

Source Profile is available only to a source acquired as a Git upstream. Local
packs and application-origin bundles have no repository identity to profile:
retain their per-skill evaluation and provenance record only.

Run the local entrypoint with `python3 scripts/run.py` (Python 3.11+ with
PyYAML from `scripts/requirements.txt`).
It accepts one JSON request on stdin and returns JSON on stdout. It is stateless
and never writes SQLite or runtime state.

Before scoring a skill, run the `validate` command with its source directory as
`skill_dir`. This deterministic precheck validates the current Agent Skills
directory and frontmatter contract, including the closed set of allowed
top-level fields; known runtime extensions such as Claude Code's
`disable-model-invocation` pass with a warning. For a published skill, also
pass `"public": true` to scan for personal home paths. Keep every reported
conformance error and isolation finding as a finding; do not normalize or edit
the assessed skill.

The individual-skill scoring standard is the built-in
`references/scorecard-rubric.md`. Source Profile uses the separate, built-in
`references/source-profile-rubric.md`.
The capability's design is in `references/architecture.md` and its concepts in
`references/ontology.md`; read them only when changing this skill.
Its ID and complete-file hash are recorded automatically. The rubric is built
in; do not accept a caller-supplied rubric or override. Judge each dimension
with the checks in `references/review-guide.md`, label evidence as it
describes, and end with prioritized improvements to the assessed skill.

Pass the skill's source directory as `skill_dir` and file-backed findings as
`evidence`. This skill assesses source only: it does not test runtime behavior,
and no scorecard claims runtime verification.

Return the scorecard to the caller. This skill does not persist assessments: it
creates no note, record, or assessment database. Storing an assessment is a
separate operation outside this skill.

## Boundary

- Read skill source directories only; do not write a skill, runtime link, or
  upstream source.
- Return the rubric ID and hash, content snapshot hash, evidence,
  findings, and advisory suggestions for every assessment.
- A suggestion to Study, link, defer, or consider a source project is not a
  user decision and never authorizes an operation.
- A `whole-project-preserve` Source Profile means individual low scores are
  local diagnostics only; they are never a cleanup recommendation for that
  source project or its entries.
- Return external pattern suggestions to the current task. Approved skill edits
  and runtime link changes are outside this skill.
