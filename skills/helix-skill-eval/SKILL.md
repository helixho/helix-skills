---
name: helix-skill-eval
description: >-
  Validate Agent Skills directory and SKILL.md frontmatter conformance, then
  evaluate one or more skills with a versioned rubric and record evidence,
  findings, overlap observations, and advisory suggestions. Use for skill
  conformance checks and scorecards; it is read-only to skills and runtimes.
---

# Helix Skill Eval

## Choose the depth

- Routine edits need `validate` and a focused review of the changed behavior;
  do not require a nine-dimension scorecard for every edit.
- Use the versioned scorecard for an explicitly requested score, comparison,
  or formal audit. The caller supplies the evidence and judgments; `evaluate`
  validates and packages those inputs and computes their mean. It does not
  independently inspect the skill or establish that it works.
- Source Profile is only for reviewing an upstream repository as a whole.

## Formal assessment

Use this skill to evaluate a skill, skill set, or upstream source project.
Produce comparable evidence, not automatic lifecycle actions. Keep one Skill
Scorecard per assessed content snapshot, with separate authoring and runtime
evidence inside that record. Do not split them into separate evaluation skills.
A Source Profile evaluates the upstream project as an interdependent system;
it does not overwrite the Skill Scorecard.

Source Profile is available only to a source acquired as a Git upstream. Local
packs and application-origin bundles have no
repository identity to profile: retain their per-skill evaluation and provenance
record only.

Run the local entrypoint with `python3 scripts/run.py`.
It accepts one JSON request on stdin and returns JSON on stdout. It is stateless
and never writes SQLite or runtime state.

Before scoring a skill, run the `validate` command with its source directory as
`skill_dir`. This deterministic precheck validates the current Agent Skills
directory and frontmatter contract, including the closed set of allowed
top-level fields. Keep every reported conformance error as a finding; do not
normalize or edit the assessed skill.

The individual-skill scoring standard is the built-in
`references/batch-rubric-v1.5.md`. Source Profile uses the separate, built-in
`references/source-profile-rubric.md`.
The capability's design is in `references/architecture.md` and its concepts in
`references/ontology.md`; read them only when changing this skill.
Its ID, version, and complete-file hash are recorded automatically. Do not
accept a caller-supplied rubric or override; a new standard requires a new
versioned reference file and an explicit registry change in this kit.

For every scorecard, set `runtime_status` to `not_checked`, `passed`, or
`failed`. Put source/conformance evidence in `authoring_evidence`. Use
`runtime_evidence` only for a fresh-session behavior check that names the
runtime, scenario, selected skill, and observed invocation path. A symlink,
unit test, or current-session source read is not runtime evidence.

Return the scorecard to the caller. Do not create or update a registry, knowledge-base
note, or assessment database. Helix-owned source skills remain source-only and
must never be registered in a knowledge base by this skill. Recording an explicitly
requested external/upstream assessment is a separate knowledge-base operation outside
Eval.

## Boundary

- Read skill source directories and runtime state only; do not write a skill,
  runtime link, or upstream source.
- Do not persist or register Helix-owned skills in a knowledge base.
- Return the rubric ID, version, hash, content snapshot hash, authoring/runtime
  evidence, findings, and advisory suggestions for every assessment.
- A suggestion to Study, link, defer, or consider a source project is not a
  user decision and never authorizes an operation.
- A `whole-project-preserve` Source Profile means individual low scores are
  local diagnostics only; they are never a cleanup recommendation for that
  source project or its entries.
- Return external pattern suggestions to the current task; approved skill edits
  use `skill-creator`. Runtime link changes are outside this skill and need no dedicated routing skill.
