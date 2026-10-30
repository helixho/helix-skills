# Codex runtime

For a main agent running in Codex with the custom agent profiles in `assets/codex-agents/`. The shared rules are in the skill entry; this file covers the Codex-specific mechanics.

## Roles

Use the named custom agents for their roles; complex implementation can use the built-in `worker` as described below. Dispatch non-overlapping independent parts together. Respect the host's active-agent limit; if parallel dispatch is unavailable, continue sequentially or inline without silently dropping coverage.

For each dispatch, name the intended `agent_type`; a spawn without one runs as a generic child on the configured fallback model. Also name the count, independent scope, expected return, and write ownership. `Explorer` handles substantial discovery only; do small lookups and general research directly. `Reviewer` reviews the assigned result without steering toward a suspected answer and returns findings in its reply; when a lasting record helps, the brief names a report path outside the changed source. For `ExpertAdvisor`, ask for an independent plan or assign a concrete outcome to produce.

Other configured roles and models are allowed when appropriate. Model and effort defaults are described in [profile setup](codex-profiles.md); normal dispatch does not require reading it.

## Implementation model selection

Use `Executor` for a bounded implementation with clear acceptance criteria.
When correctness requires reasoning across module contracts, parser edge cases,
or deletion/state/lifecycle transactions, use built-in `worker` with `model="gpt-6.1-sol"`,
`reasoning_effort="high"`, and `fork_turns="none"`. Complexity of the behavior,
not file count alone, determines this choice. Keep the same brief, ownership,
and result review required for an Executor.

Do not request a different model on the fixed `Executor` profile: its configured
model takes precedence. Explicitly select the model on `worker`; a full-history
fork inherits the parent's model and effort. If the requested model is unavailable,
keep the work in the main agent and report the limitation. Model choice does not
replace verification of the result.

## Context and handoff

Start a new child with `fork_turns="none"` by default. Always use it for `Reviewer` and `ExpertAdvisor`, whose value depends on an independent view. Use it for `Explorer` too: a question and codebase path are usually enough.

An `Executor` may inherit the parent conversation when decisions in it cannot be conveyed reliably in a short brief. The current `fork_turns` API accepts only `"none"` or `"all"`; use `"all"` only when the full history is genuinely needed. Reuse an existing child for a direct continuation of its own assignment; a new review batch is not one, so start a fresh `Reviewer`.

Give the child its assigned question or deliverable, relevant context, and scope. Include the broader user goal when it helps explain the assignment. The child chooses its method within the assigned part; the main agent handles changes to the task breakdown and checks the returned work.

Children run in the parent's checkout. When the skill entry calls for isolation, create a worktree per writer with the runtime's managed worktree tool when available, otherwise `git worktree add <path> -b <branch> <base>` from the branch that holds its prerequisites, and name that path as the child's working directory in the brief. After acceptance, merge the branch and remove the worktree and branch.

Codex compacts a long thread only when it reaches the configured limit; until then every call re-reads the whole thread, so keep the main thread small as the skill entry describes. Wait for children with `wait_agent` and a long timeout, not `sleep`.

## Expert help

`ExpertAdvisor` runs on the strongest model in [profile setup](codex-profiles.md); its value is an independent view, so use it even when the parent runs the same model.

Give it the decision or outcome, relevant context, evidence, constraints, and scope. The expert may produce a plan or carry out assigned modeling or complex automation; computer automation that takes over the user's screen is an approval-gated action. Check its result before accepting it.

Which model a role actually runs with, including whether a spawn-time choice can override `Explorer`, `Executor`, or `Reviewer`, is defined in [profile setup](codex-profiles.md).

## Diagnostics

For a requested Codex usage report, run `python3 <skill directory>/scripts/usage_by_model.py`; to evaluate delegation, read [evaluation guidance](evaluation.md).
