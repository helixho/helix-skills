---
name: helix-skill-review
description: >-
  评估 skill 以找出改进点：按批判性思维、MECE、奥卡姆剃刀、独立性原则以及 Agent Skills 规范和渐进式披露检查，按内置评分标准记录评分、证据、发现和改进建议，
  也评估外部 skill 值得借鉴什么、是否值得单独启用。用于“评估这个 skill”“给 skill 打分”“检查 skill 结构”“这个外部 skill 有什么值得借鉴”。
  只读源码，不测试运行行为，也不修改 skill 或运行时。
---

# Helix Skill Review

Two uses: assess a skill, or judge what an external skill offers.

## Assess a skill

The default for any request to assess, check, or score a skill.

1. Run `validate` with the skill's source directory as `skill_dir`; for a
   published skill add `"public": true` to scan for personal home paths. It
   also lists every file in the skill; step 2 accounts for each one. Every
   conformance error and personal home path it reports is a finding. If the directory has
   no usable root `SKILL.md`, assess the nested skills it contains instead, or
   report that and stop when there are none.
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

To judge an external skill, follow "Reviewing an external skill as a
reference" in `references/review-guide.md`: with a target, what to absorb into
one of the user's own skills, with no scorecard. Without a target, assess it with
"Assess a skill" above, ending in whether to enable it on its own or not adopt
it.

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
