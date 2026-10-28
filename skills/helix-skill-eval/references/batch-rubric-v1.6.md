---
rubric_id: helix-skill-scorecard
version: 1.6.0
status: active
---

# Skill Scorecard Rubric

Use this rubric for one independently addressable skill package in a source
tree. It is advisory evidence only: it never authorizes runtime linking,
unlinking, archival, removal, or source edits. The lifecycle unit for an
upstream source is the source project, never one skill inside that project.

## Preconditions

Record source and structure facts before applying this rubric. Never normalize
or patch an upstream skill during assessment.

- `broken`: the selected skill directory has no usable root `SKILL.md`. Do not
  score it.
- `nested-root`: the selected directory lacks `SKILL.md` but contains one or
  more nested skills. Select the actual skill directory; do not score the
  container.
- `valid`: a usable root `SKILL.md` exists and is eligible for a human or LLM
  assessment. Missing or nonstandard frontmatter remains a source-native
  conformance fact and is reflected in Structure maturity; it is not a reason
  to alter or retire an upstream skill.

## Dimensions

Score each dimension from 1 to 5 and attach concise file-backed evidence where
available. A score is not evidence of runtime behavior.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Value and fit | No credible use in the user's workflows | Situational personal use | Repeated, high-value workflow for the user |
| Structure maturity | Thin or incomplete workflow | Clear workflow with useful support | Clear, testable, progressively disclosed capability |
| Uniqueness | Duplicates an active capability | Partial overlap with a distinguishable niche | Distinct responsibility and trigger boundary |
| Maintainability | Fragile, stale, or opaque dependency | Ordinary upkeep | Small, explicit, portable maintenance surface |
| Portability and configuration | Requires a developer-machine path, undocumented setup, or a secret in source | Some configuration/dependency ambiguity, but failure is visible | Uses own install-relative resources and PATH discovery; required business configuration is discoverable or has an explicit first-run path; secrets stay outside source and notes |
| Trust boundary | Unexplained side effects or opaque authority | Side effects and dependencies named | Authority, external actions, and limits explicit |
| Trigger quality | Trigger is missing, exclusion-only, or written for a different audience | Positive trigger exists but needs interpretation | Positive, concrete use scenarios match the intended user's working language |
| Actionability | Trigger/output cannot be used reliably | Usable with some interpretation | Concrete trigger, procedure, and handoff/output |
| Evidence quality | Assertion or metadata only | SKILL.md and selected support read | File-backed evidence plus relevant behavior check |

## Evidence phases

Keep one scorecard with two evidence sections:

- `authoring`: source content, conformance, dependencies, and deterministic
  checks.
- `runtime`: fresh-session behavior naming the runtime, scenario, selected
  skill, and observed invocation path.

Set `runtime_status` to `not_checked`, `passed`, or `failed`. `not_checked`
does not invalidate an authoring assessment, but the result must not be called
runtime-verified. A symlink, unit test, current-session source read, or the
score itself is not runtime evidence.

## Portability review rules

- Do not deduct for a skill that intentionally operates a named target host or
  platform and stores that target's topology as its business input.
- Do deduct for a source-repository path, a specific runtime installation path,
  or a developer-home fallback used to locate the skill's own resources.
- A command already discoverable on PATH must not be made a required custom
  variable. An explicit override remains acceptable.
- Missing configuration must surface what semantic choice is needed; an agent
  may ask the user and run the skill's documented first-run setup. Do not reward
  silent local-path guesses.

## Filesystem scope review rules

Apply these rules to any skill that inventories, cleans, moves, or rewrites
paths under a host-managed root (an application home, agent runtime home, or
user data directory). They are scored inside Structure maturity and Trust
boundary; they add no dimension.

- Deduct Structure maturity when path rules were written without a recorded
  discovery pass: a full inventory of each managed root's top-level entries and
  a search for residue families (`*.bak*`, `*.backup*`, `*.orig`, `*.old`,
  `*~`, `*.tmp*`), with the observation date and counts kept next to the rule.
- Deduct Structure maturity when any top-level entry of a managed root can be
  neither classified (deletable, protected, known-keep) nor reported. Every
  scan must surface entries outside the classified set as unclassified
  findings instead of silently skipping them.
- Deduct Trust boundary when a preview hides the objects a sensitive action
  would touch. Backups, configuration-adjacent files, user sessions,
  databases, launch and permission registrations, and unclassified findings
  must be listed item by item with path, size, modification time, in-use
  state, and deletion method, and must default to unselected.
- Deduct Trust boundary when in-use or recently written objects can enter a
  deletion plan without being escalated to item-level owner review.
- Do not deduct for summarizing low-risk, rebuildable objects (caches,
  temporary clones, update staging) in the terminal, provided the complete
  item list is written to a review file and apply is limited to the frozen
  reviewed plan.

`overall_score` is the arithmetic mean of the nine dimension scores, rounded
to one decimal place. The formula is deliberately equal-weighted: a reviewer
may explain a trade-off in evidence, but may not silently change weights per
skill or per run.

## Interpretation boundary

The assessor returns only dimension scores and evidence. Score bands are query
views, not lifecycle instructions. Source-project-level management metadata
(source availability, duplicate routing, or a project retirement review) is
maintained separately and does not modify the source artifact.

## Versioning and comparability

- Every scored observation records this `rubric_id`, `version`, and rubric file
  hash.
- Scores are comparable only when all three match.
- Imported historical reports retain their original rubric identifiers and are
  evidence references, not converted scores.
