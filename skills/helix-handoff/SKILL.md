---
name: helix-handoff
description: >-
  Session handoff——在用户要求交接（换 session、换 agent、暂停后继续）时，生成跨工具中立、用户可审阅的 continuation brief，保留目标、边界、决策、已完成事项、未完成事项、相关 artifact、风险和下一步，不写长期 memory。
  触发于用户说"交接一下/换个会话继续/handoff/把上下文整理给下一个 agent"。
disable-model-invocation: true
metadata:
  author: Helix
---

# helix-handoff

A visible, reviewable manual compact for continuation. Not a hidden runtime
compact, not long-term memory, not a spec or a plan.

## Input

Optional focus: “下一场会话要聚焦什么”。

- Current session state, at the moment the user asks to hand off.
- The focus the user gave when invoking the skill, if any: what the next session will focus on. Tailor the
  brief to it — carry the context that focus needs and drop the rest.

## Output

Inline continuation brief, in the pattern below. Inline is a valid completion
state.

Write a file only when the user explicitly asks for a handoff artifact. Prefer a
temporary location unless the user approves a repository path; never default to
project `docs/`. If file output is unavailable or unsafe, produce the inline
brief instead.

## Rules

**Scope**

- Summarize only what is needed to continue. Lead with what the next agent must
  know before acting.
- Preserve intent, original goal, current scope, constraints, key decisions, and
  unresolved questions before compressing any detail.
- Distinguish verified facts, user decisions, assumptions, and open questions.
- List completed work and remaining work separately.
- Include risks, approvals, environment constraints, and known blockers that
  matter for continuation.
- Drop temporary noise, repeated discussion, stale attempts, and historical
  detail that does not help continuation.
- If there is no clear next step, say so and name the decision needed from the
  user.

**Reference, don't copy**

- Point at artifacts by path, commit, issue, PR, URL, or other stable handle.
  Never duplicate specs, plans, diffs, logs, or previous summaries when a stable
  reference is enough.
- Include exact paths, commands already run, or verification results only when
  they matter for continuation.
- Prefer stable facts and artifacts over narrative history.

**Boundaries**

- Never write long-term memory.
- A handoff is not proof that work was completed — verification still requires
  fresh evidence.
- Redact secrets, credentials, tokens, and sensitive personal information.

**Cross-tool neutrality**

- Do not emit tool-specific fields such as `suggested_skills`, and do not assume
  any particular runtime will consume the brief.
- The brief must be understandable without this skill loaded.

**Review**

- Do not silently replace context. The user must be able to read the brief and
  correct it.

## Output Pattern

```text
handoff_purpose:
continuation_focus:
current_state:
key_decisions:
completed_work:
open_items:
relevant_artifacts:
risks_and_constraints:
recommended_next_steps:
redactions:
```
