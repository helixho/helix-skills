# Skill Review Guide

How to judge a skill's source so the assessment ends in concrete improvements
to that skill. Start with Positioning, then use the checks that bear on each
scorecard dimension; record what they find as evidence, findings, and
suggestions. Logical conflicts inside
the instructions are reviewed with `helix-logic-review`.

## Evidence labels

Label every finding by what supports it:

- `file-backed`: cites a file and line, or a deterministic check result.
- `inferred`: reasoned from the source without direct confirmation.
- `missing`: needed for the judgment but not available.

Never present inferred or missing evidence as file-backed.

## Positioning

Settle these before any dimension check; every later judgment is made against
the positioning established here.

1. **Intended positioning**: establish what the skill is meant to do and when,
   from the owner's statements, the description, and how it is wired in (for
   example a hook or routing entry that invokes it on every request). Do not
   judge it against an assumed narrower or wider role.
2. **Positioning fit**: the skill does one coherent job, and a skill is the right
   carrier for it, rather than an always-on rule, a script, or part of a sibling
   skill.
3. **Boundary**: what the skill does and does not do is stated. Each overlap with
   a sibling skill, a host built-in, or the owner's always-on rules is resolved
   by a handoff, or for a duplicated rule, by Rule placement below.
4. **Capability gaps**: list the cases the job requires and check that each is
   handled; an unhandled required case is a finding.
5. **Rule placement**: a rule any user of the skill needs belongs in the skill; a
   rule that is the owner's personal habit belongs in the owner's personal
   rules. A rule kept in both places is a finding; keep it where it belongs and
   drop the other copy.
6. **Name**: the name states the job as positioned, neither narrower nor wider;
   carries no term that suggests a capability the skill excludes or that was
   left behind by an earlier role; follows the naming pattern of its siblings;
   and is distinguishable from other skills and host built-ins. A rename
   suggestion lists what refers to the old name: invocations, links, and other
   documents.

Positioning findings feed Value and fit (positioning), Uniqueness (boundary and
placement), Actionability (capability gaps), and Trigger quality (name).

## Checks by dimension

**Value and fit**

- The skill names a repeated job it does for the user; one-off or hypothetical
  use scores low.

**Structure maturity**

- `SKILL.md` carries the stable protocol: entrypoint, routing, boundaries,
  order of operations, and non-goals.
- Low-frequency detail sits in a support file, reached by a pointer that says
  when to read it.
- Files are split by durable responsibility: one workflow justifies one entry
  script, one stable topic one reference. Many thin files with unclear
  ownership are a finding.
- `SKILL.md` and its references hold the current state only: no changelog,
  TODO list, version or revision record, status note, or debugging scratchpad.

**Uniqueness**

- Compare trigger and boundary with sibling skills and the host's built-in
  capabilities. A different trigger phrase is not a different capability.
- An overlap with a sibling that no handoff resolves calls for a merge
  suggestion.

**Maintainability**

- Read every file `validate` lists. Each one is reached through the skill's own
  reading path (a pointer in `SKILL.md` or in another reached file, or code
  that loads it) or loaded by a host convention such as `agents/openai.yaml`,
  and is needed for the job. Flag unreached files, fixtures no runner uses,
  compatibility shims with no caller, material for work the skill hands off,
  and concepts named but never defined or defined but never used.
- Prose states the capability and leaves the mechanism to the script, config,
  or schema that declares it, so there is one source of truth.
- Machine-checkable rules (routing, accepted inputs, failure conditions, output
  shape) are enforced by code or validation, not prose alone.

**Portability and configuration**

- Resources are found relative to the skill and commands through `PATH`.
- Dependencies are declared in `compatibility`, a requirements file, or a clear
  import error.
- Apply Independence below.

**Trust boundary**

- Scripts, hooks, configuration, network access, secrets, and external
  commands are named together with their authority and limits.

**Trigger quality**

- The description says what the skill does and when to use it, in the user's
  working language, with concrete request phrases.
- One trigger per distinct case; synonyms of one case are not separate cases.
- The trigger is neither wider nor narrower than what the body handles. A broad
  automatic trigger for a narrow job is a finding.

**Actionability**

- Each step ends with a clear done condition, and the output or handoff format
  is explicit.
- Another skill is named only for a real handoff or routing dependency, and
  each named skill exists and still matches the reference.

**Evidence quality**

- Judged by the labels above and how many of the files `validate` lists the
  evidence covers.

## Independence

Apply to every skill: it must work as a standalone package.

- Each file a reader loads under the skill's own reading rules stands on its
  own. It does not rely on content the skill tells that reader not to load,
  such as another runtime's adapter.
- It assumes no tool, CLI, runtime, service, or account is available unless it
  declares the dependency (in the description, `compatibility`, or a
  requirements file) or makes the step conditional on it.
- It does not reference or depend on its owner's private environment (tools,
  knowledge base, installed applications, repository layout, or workflows)
  unless that environment is the skill's declared job.
- It explains itself without private project history.

A published skill also has no dependency on its owner's private environment
at all, and contains no personal home paths; examples use placeholders such as
`/Users/example/`, `/home/user/`, or `<skill-name>`. `validate` with
`"public": true` scans the skill's text files for personal home paths; the other
checks remain review judgment.

Brand and author names, such as a namespace prefix, are identity, not a
finding.

## Reviewing an external skill as a reference

Use when an external skill is studied to improve one of the user's own skills,
the target.

1. Decompose only what could change the target: purpose, trigger model,
   workflow and gates, file layout, output contract, and trust surface.
2. Classify each pattern as `absorb`, `do not absorb`, or `defer` (plausible but
   needs real-use evidence first).
3. Before recommending absorption, answer:
   - Does the reference do the same job, or only resemble it?
   - Would the pattern reduce repeated work, routing ambiguity, or review risk?
   - Does it add more context, files, or process than the benefit justifies?
   - Does it fit as one rule in the target's `SKILL.md`, or need a support file?
   - Does it belong in the target, in another skill, or nowhere?
4. Do not absorb whole directory systems when one rule is enough; reports,
   registries, or release gates without a real need; prose that sounds polished
   but changes no behavior; or brand-specific workflows and private assumptions.

Also say whether the reference itself is worth enabling on its own, merging
into the target, or not adopting.

## Recommendations

End with prioritized, concrete improvements to the assessed or target skill,
each tied to a finding. When warranted, add one lifecycle suggestion: keep,
merge into another skill, absorb parts into another skill, archive, or not
adopt. Suggestions are advisory; edits happen outside this skill after the user
approves them.

## Pitfalls

- Keeping duplicate skills because both are good enough.
- Leaving old entrypoints active after a merge.
- Copying a whole standard instead of its actionable checks.
- Optimizing file size instead of context and maintenance cost.
- Adding manifests, changelogs, or archive directories that version control
  already covers.
