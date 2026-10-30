---
name: helix-delegation
description: "Split, brief, and review delegated work. Use when the user requests delegation or independent review, when a large task can be split into non-overlapping parts and parallel work is clearly faster, or when a risky result or high-impact decision warrants an independent review or expert view."
metadata:
  compatibility: "Runtime adapters for Codex and Claude Code; CLI executors need the target CLI installed and signed in. Diagnostics scripts need Python 3.10+."
---

# Delegation

Delegate when the user asks for it, when a large task can be split into non-overlapping parts and parallel work is clearly faster, or when a result or decision warrants an independent `Reviewer` or `ExpertAdvisor` (see Roles and Independent review). Otherwise work directly. The main agent owns the task breakdown, unresolved product decisions, integration, and final acceptance. Delegation spends tokens twice: the executor rebuilds context and the main agent reviews the result.

## Runtime adapter

Read the one adapter for the runtime you are running in, and only it:

- **Codex:** [runtime-codex.md](references/runtime-codex.md)
- **Claude Code:** [runtime-claude-code.md](references/runtime-claude-code.md)

To run another vendor's agent CLI headless (Grok Build, `codex exec`) from any runtime, read [CLI executors](references/cli-executors.md).

## Roles

The adapters map these roles to their runtime:

- `Explorer` — a bounded codebase-discovery question that returns primary files, entry points and their connections with brief evidence. Avoid duplicate general maps; the main agent combines results before deciding changes.
- `Executor` — implementation of a slice whose intended result and file ownership are clear.
- `Reviewer` — independent review of a stable result.
- `ExpertAdvisor` — an independent plan for a complex or high-impact decision, a problem unresolved after repeated attempts, or assigned modeling or complex automation.

## Splitting the work

- **Delegate bounded parts** that need substantial independent work: an implementation slice, broad discovery, an independent review, or expert work.
- **Do it directly** when the scope and change are already clear to the main agent: cleanups, small fixes, documentation and configuration edits, git work, lookups. Size alone is not a reason to delegate.
- **Match agents to ready work.** Use one agent per distinct question, slice, or review lens that can work and report independently. Parallelize only slices whose prerequisites are met; run dependent slices in order. Before parallel dispatch, settle any interface or contract the slices share. Do not add agents just to fill a planned count.
- **Give each target one owner.** A file, change area, or shared service (dev server, port, database, container, account) has one owner at a time; work on the same service runs in sequence. Writers with separate files can share one checkout. If parallel writers could still collide (the same build outputs, lockfiles, services, or tests), run them in sequence or isolate each in its own worktree that the main agent integrates. Run at most five writers in parallel.
- **Defer slow checks.** During implementation, unit tests and a minimal smoke check are enough. Run end-to-end or browser acceptance once at the end of a batch, unless the user asks otherwise or the change cannot be judged another way. If the user has said where tests run, follow that.

## The brief

State the goal, the hard constraints, and what done looks like. Leave the method to the executor.

- **Goal:** the outcome, with the decision or spec it comes from. Pass files, symptoms, and prior attempts as leads, not a fixed diagnosis or a step list.
- **Hard constraints:** what must not change (public interfaces, contracts, data), forbidden commands, shared environments, and where tests run. Where the project or a skill already defines a judgment, cite it rather than restating or simplifying it.
- **Approval-gated actions:** actions that need the user's approval before they happen (for example irreversible deletion, publishing, changing live services, screen control) are forbidden unless the user already approved that specific action. Get any needed approval before dispatch, write the approved ones into the brief, and encode the rest as deny rules where the executor supports them. Checking afterwards cannot undo them.
- **Done:** the changes, and a report of what changed, what was run with its actual results, and what remains. In a shared checkout the executor leaves its changes uncommitted for the main agent; in its own worktree it commits on that worktree's branch. The report is the executor's final reply; an executor without a reply channel (a headless CLI) writes it to a path outside the repository that the brief names. The executor finishes those before ending.
- **Boundary:** the executor reports blockers, shared-file conflicts, needed scope changes, or missing authority to the main agent instead of crossing its assignment. An executor that cannot ask mid-run stops and puts them in its report.

Keep briefs short. A long brief, or repeated amendments, usually means the main agent should decide the open point or do the work itself.

## Review the result

Check what came back before accepting it:

1. **Goal met:** the result achieves the brief's goal and done criteria, confirmed by the main agent's own targeted check, not only by the report.
2. **Scope:** the diff stays inside the brief, with no unrelated refactors and nothing written outside the repository that belongs elsewhere.
3. **Criteria intact:** assertions, timeouts, and acceptance checks were not weakened or removed to make something pass.
4. **Evidence real:** the commands and logs the report cites exist and show what the report claims. "Ran" is not "passed".
5. **Safety:** no secrets or tokens in commits, reports, or logs; no unapproved side effects (deleted data, restarted services, pushed commits).

Then decide: accept, send back with the specific defect, or take over. If the executor stopped without finishing, read its last state first and finish small remainders directly. If a send-back does not resolve the defect, take over or rethink the brief instead of sending it back again. When a reviewer's finding conflicts with the executor's evidence, the main agent reproduces it and decides; only product decisions go to the user.

Accepting a child's result is not completion. Before reporting completion, confirm the accepted changes are present in the final target and verify the resulting behavior there. The main agent commits accepted work, integrates it into the target branch following the user's Git workflow, and removes child worktrees and branches.

## Independent review

Use a `Reviewer` that does not inherit the main thread's conclusions when a result carries meaningful risk of unnoticed defects or the user asks for review. Unless the user asked for a separate simplification pass, the same review also looks for needless complexity in the code this task wrote; it proposes structural refactors (splitting files or components) only when the user asked for them. When the user asks to simplify code, follow [Simplify](references/simplify.md).

Review per batch, not per small fix; test-only or fixture-only changes are covered by the batch review. Start a fresh `Reviewer` for each batch instead of sending new batches to a long-running one. If a finding is still open after one send-back round, the main agent reproduces it and decides instead of cycling the review again.

## Long runs

Keep the main thread small: decisions, status, and the next step. Every main-agent call re-reads the whole thread, so bulky output is paid for again on each later step.

- **Delegate bulky loops.** Give one delegated owner the command loops whose output is bulky: remote or test-environment runs, repeated test cycles, log triage. It returns conclusions and evidence paths; the main agent spot-checks the evidence instead of rerunning the loop.
- **Wait, do not poll.** Wait for children with the runtime's blocking wait or completion notification, not short repeated sleeps; each wake-up is another full-context call.
- **Stop at acceptance points.** When the user lets a long run continue without asking, stop at each agreed acceptance point (the end of a package or batch) and report the result, the remaining work, and the usage so far before starting the next.

How to handle a filling context follows the runtime adapter.

For interactive-state checks that code inspection cannot settle, read [interactive testing guidance](references/interactive-testing.md).
