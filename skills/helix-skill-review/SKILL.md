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

1. Establish the user's goal, designated scope, constraints and relevant preferences.
   Run `validate` with `skill_dir`; add `"public": true` for a published skill.
   Keep its `content_hash` as the reviewed version and account for every listed file.
   If there is no usable root `SKILL.md`, assess nested skills, or report and stop.
2. Apply [review-guide.md](references/review-guide.md): establish positioning,
   interpret lint in context, inspect source and relevant tests, and obtain external
   evidence when it could change a recommendation. AI integrates these inputs;
   a lint pass or warning is not the overall verdict.
3. Recheck candidate findings against context, exceptions and counter-evidence.
   Recommend the smallest useful change, or retention when no change is justified.
   Score the nine dimensions in [scorecard-rubric.md](references/scorecard-rubric.md).
4. Submit `evaluate` with the original hash as `expected_content_hash` and the
   evidence, findings and suggestions defined in [report-contract.md](references/report-contract.md).
   If source changed, inspect the changes and redo affected judgments before
   obtaining a new hash; never refresh the hash just to bypass the check.
5. Present AI's overall conclusion and prioritized recommendations, their evidence,
   tradeoffs and verification limits; scores summarize the review, not dictate it.

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
`evaluate`. The report contract includes a complete request example. The rubric is built in and its ID and file hash are recorded with
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

## Feedback and verification

Correct the current review first. Turn reproducible mechanical errors into checks,
judgment errors into acceptance cases, and only general method gaps into instructions.
Keep one-off preferences in task context; change standing rules only when confirmed.
Rerun affected checks after changes. Generated reports stay outside the skill package.
For each material claim distinguish automatic verification, AI assessment, human
confirmation and unverified work, naming the object and evidence. Local citation
checks do not establish semantic support; source review is not runtime verification.
