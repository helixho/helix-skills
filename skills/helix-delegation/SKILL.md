---
name: helix-delegation
description: "Run subagents inside one agent session when the user asks: parallel read-only research, isolating bulky test or log loops, an independent review or second opinion, or a team of planner, builder and verifier roles the user launched from this session. Covers role-to-profile mapping, briefs, ownership, waiting, and checking results; it does not decide task complexity or choose models."
disable-model-invocation: true
metadata:
  compatibility: "Runtime adapters for Codex and Claude Code; CLI executors need the target CLI installed and signed in. Diagnostics scripts need Python 3.10+."
---

# Delegation

Use this skill only when the user asks for subagents in the current session. It covers four uses:

- **Parallel read-only research:** several `explorer` questions that do not overlap.
- **Bulky loops:** one child owns a test, environment, or log-triage loop and returns conclusions, keeping the main thread small.
- **Independent check:** a `verifier`, `reviewer`, or `expert` the user asked for.
- **A team the user launched here:** `planner` → `builder` → `verifier`, when this session is the user's chosen orchestration entry. Which roles a task needs comes from the project's delivery rules and the user's decision; this skill does not judge task complexity or assemble a team on its own.

A child assigned a role does that role only and does not spawn further roles. The main agent owns the breakdown, unresolved product decisions, integration, and final acceptance. Delegation spends tokens twice: the child rebuilds context and the main agent reviews the result.

## Runtime adapter

Read the one adapter for the runtime you are running in, and only it:

- **Codex:** [runtime-codex.md](references/runtime-codex.md)
- **Claude Code:** [runtime-claude-code.md](references/runtime-claude-code.md)

To run another vendor's agent CLI headless (Grok Build, `codex exec`) from any runtime, read [CLI executors](references/cli-executors.md).

## Roles

Roles define duties, independence, and when they are used. They carry no model: which model and effort a role runs on is set in the runtime's installed agent profiles, not chosen at dispatch. Each adapter maps the roles to its profiles.

- `planner` — the approach and its trade-offs, the breakdown, and the acceptance cases the work must satisfy; also checks that the builder delivered what was designed. Usually the main agent.
- `builder` — implements a slice against the acceptance cases and writes its unit and contract tests in the same task. The default executor.
- `verifier` — checks the changed flow end to end against the acceptance cases, in its own context, with expectations taken from the requirements rather than the implementation. Prefer a different underlying model from the builder's where one is configured.
- `explorer` — a bounded, read-only codebase-discovery question that returns primary files, entry points and their connections with brief evidence. Avoid duplicate general maps; the main agent combines results before deciding changes.
- `reviewer` — independent code-level review, for high-risk changes only.
- `expert` — an independent plan for a major architecture or key decision. Use it only when the user asks or after a builder has twice failed to deliver; never escalate to it on the agent's own judgment of difficulty.

## Splitting the work

- **Delegate work packages.** The unit of delegation is a work package the child can finish and check on its own: an implementation slice, broad discovery, an end-to-end verification, or expert work. The child carries it through locating, changing, testing, and reporting within its authority, without returning to the main agent for each step.
- **Do it directly** when the scope and change are already clear to the main agent: cleanups, small fixes, documentation and configuration edits, git work, lookups. Size alone is not a reason to delegate.
- **Match agents to ready work.** Use one agent per distinct question, slice, or review lens that can work and report independently. Parallelize only slices whose prerequisites are met; run dependent slices in order. Before parallel dispatch, settle any interface or contract the slices share. Do not add agents just to fill a planned count.
- **Give each target one owner.** A file, change area, or shared service (dev server, port, database, container, account) has one owner at a time; work on the same service runs in sequence. Writers with separate files can share one checkout. If parallel writers could still collide (the same build outputs, lockfiles, services, or tests), run them in sequence or isolate each in its own worktree that the main agent integrates. Run at most five writers in parallel.
- **Follow the project's test cadence.** Run the checks the project's delivery rules assign to each stage. By default, unit tests and a minimal smoke check are enough during implementation, and end-to-end or browser acceptance runs once when a package completes or shared behavior changes, unless the user asks otherwise or the change cannot be judged another way. If the user has said where tests run, follow that.
- **Classify each failure first.** Decide whether it is a product, test, or environment problem before choosing the next step. After a fix, recheck the failing point and what it affects. Reuse earlier test evidence only while the code, dependencies, and environment it ran against still apply. When the same failure repeats without new evidence, re-explain the cause or change the verification method instead of rerunning.

## The brief

State the goal, the hard constraints, and what done looks like. Leave the method to the executor. For work that spans turns, changes hands, or needs independent verification, write the brief as a contract file in the project's agreed location and pass its path; a short one-off question can stay in the message. A child loads the contract and the files it names, not the parent's whole conversation.

- **Goal:** the outcome and its acceptance conditions, with the decision or spec it comes from, the inputs and the code version to start from, and decisions already made together with approaches ruled out and why. Pass files, symptoms, and prior attempts as leads, not a fixed diagnosis or a step list.
- **Hard constraints:** what must not change (public interfaces, contracts, data), forbidden commands, shared environments, and where tests run. Where the project or a skill already defines a judgment, cite it rather than restating or simplifying it.
- **Approval-gated actions:** actions that need the user's approval before they happen (for example irreversible deletion, publishing, changing live services, screen control) are forbidden unless the user already approved that specific action. Get any needed approval before dispatch, write the approved ones into the brief, and encode the rest as deny rules where the executor supports them. Checking afterwards cannot undo them.
- **Done:** the changes, and a short report of what changed, what was run with its actual results and the exact version and environment they apply to, what remains, and where the evidence is. Full logs, test reports, and screenshots stay in files the report points to. In a shared checkout the executor leaves its changes uncommitted for the main agent; in its own worktree it commits on that worktree's branch. The report is the executor's final reply; an executor without a reply channel (a headless CLI) writes it to a path outside the repository that the brief names. The executor finishes those before ending.
- **Boundary:** the executor reports blockers, shared-file conflicts, needed scope changes, or missing authority to the main agent instead of crossing its assignment. An executor that cannot ask mid-run stops and puts them in its report.

Keep briefs short. A long brief, or repeated amendments, usually means the main agent should decide the open point or do the work itself.

## Review the result

Check what came back before accepting it:

1. **Goal met:** the result achieves the brief's goal and done criteria, confirmed by the main agent's own targeted check, not only by the report.
2. **Scope:** the diff stays inside the brief, with no unrelated refactors and nothing written outside the repository that belongs elsewhere.
3. **Criteria intact:** assertions, timeouts, and acceptance checks were not weakened or removed to make something pass.
4. **Evidence real:** the commands and logs the report cites exist and show what the report claims. "Ran" is not "passed".
5. **Safety:** no secrets or tokens in commits, reports, or logs; no unapproved side effects (deleted data, restarted services, pushed commits).

Check by sampling the evidence and the integrated behavior, not by redoing the child's work. Then decide: accept, send back with the specific defect, or take over. If the executor stopped without finishing, read its last state first and finish small remainders directly. Send defects back to the same builder and have the same verifier recheck them; the main agent steps in only when the same failure repeats without new evidence, the reading of the acceptance conditions conflicts, or a cross-module decision is needed. When a finding conflicts with the executor's evidence, the main agent reproduces it and decides; only product decisions go to the user.

Accepting a child's result is not completion. Before reporting completion, confirm the accepted changes are present in the final target and verify the resulting behavior there. The main agent commits accepted work, integrates it into the target branch following the user's Git workflow, and removes child worktrees and branches.

## Verification and review

Use a `verifier` that does not inherit the main thread's conclusions when the user asks for one or the team calls for it. It covers the flows the change touches; a full regression runs only where the project's delivery rules put it. Add a `reviewer` for high-risk changes. Unless the user asked for a separate simplification pass, the review also looks for needless complexity in the code this task wrote; it proposes structural refactors (splitting files or components) only when the user asked for them. When the user asks to simplify code, follow [Simplify](references/simplify.md).

Verify per package, not per small fix. Keep the same `builder` and `verifier` through a package's fix loop, since they already understand the problem; start fresh ones for a new package, or when a thread is full of unrelated exploration. Rechecks after rework cover the change and whether the open findings are closed. Changes to tests, assertions, expected values, or fixtures are not low risk by default: check that they keep the original acceptance strength.

## Long runs

Keep the main thread small: decisions, status, and the next step. Every main-agent call re-reads the whole thread, so bulky output is paid for again on each later step.

- **Delegate bulky loops.** Give one delegated owner the command loops whose output is bulky: remote or test-environment runs, repeated test cycles, log triage. It returns conclusions and evidence paths; the main agent spot-checks the evidence instead of rerunning the loop.
- **Wait, do not poll.** Keep working on independent work; otherwise wait with the runtime's blocking wait or completion notification. Each wake-up makes the model reread the thread just to decide to keep waiting. Query status only to judge a timeout, a blocker, or the next step.
- **Checkpoint at acceptance points.** At each acceptance point the project's delivery rules define (by default, the end of a work package), write the results to files, check them, and give the user a short progress note; then continue under the existing authorization. Stop only for a decision the user must make.
- **Measure per package.** Record each agent's model calls, uncached input, cached input, output and its reasoning part, elapsed time, rework, and whether the acceptance conditions were met, so changes to the method can be compared.

How to handle a filling context follows the runtime adapter.

For interactive-state checks that code inspection cannot settle, read [interactive testing guidance](references/interactive-testing.md).
