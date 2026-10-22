# Claude Code runtime

For a main agent running in Claude Code. The shared rules are in the skill entry; this file covers the Claude Code mechanics.

## Roles

| Role | Subagent type | Model and effort |
| --- | --- | --- |
| `Explorer` | built-in `Explore` | its own default |
| `Executor` | `Executor` | Sonnet, `high` |
| `Reviewer` | `Reviewer` | Opus, `high`; edit and write tools removed |
| `ExpertAdvisor` | `ExpertAdvisor` | Opus, `high` |

The three custom profiles are in `assets/claude-agents/`. Install them by linking each file into `~/.claude/agents/`. Claude Code watches that directory and picks up changes within seconds; restart only when the directory itself was created during the current session. If a custom type is missing, use `general-purpose` with the same model and effort passed at spawn time.

A spawn-time `model` or `effort` overrides the profile, the opposite of Codex. Pass one only to change a role deliberately, for example Opus for a complex `Executor` slice. Request only models available to the current account.

The profiles remove the `Agent` tool, so a child cannot spawn further subagents. `Reviewer` can still write through Bash, so leaving the work unchanged remains an instruction boundary. It returns findings inline; the main agent saves a lasting report when one helps. For a high-risk result, a review by another model family through `codex exec` ([CLI executors](cli-executors.md)) gives a more independent view.

## Context and isolation

- Never fork a role. A fork runs on the main session's model, tools, and prompt instead of the role's profile, and it inherits the conversation's conclusions. A subagent starts without this conversation, so the brief carries everything it needs. Reuse a running child through `SendMessage` for a direct continuation of its own assignment.
- When the skill entry calls for isolation, give the writer `isolation: "worktree"`. Its worktree starts from the repository's default branch, not the main agent's current branch: commit any prerequisite work to a branch before dispatch and tell the child to merge that branch first. An unchanged worktree is removed automatically; for a changed one the main agent merges the branch and removes the worktree and branch.
- Run independent children in the background and keep working; their completion arrives as a notification, so do not poll. The same holds for a CLI executor started with a background Bash command: its exit notifies the main agent, so the separate watcher in [CLI executors](cli-executors.md) is not needed.
- Claude Code compacts a long conversation automatically; continue in the current session.
