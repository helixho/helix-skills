# Codex agent profiles

Read this when installing or diagnosing roles. Ordinary dispatch uses the runtime adapter.

## Install

The four templates in `assets/codex-agents/` are the source for role names, model
and effort defaults, and instructions. Copy the selected files into
`~/.codex/agents/` or `<project>/.codex/agents/`. Compare existing same-named files
before replacing them; leave unrelated profiles alone.

| Role | Purpose |
| --- | --- |
| Explorer | Locate primary code paths for a bounded question. |
| Executor | Implement a result within clear write ownership. |
| Reviewer | Independently review a stable result. |
| ExpertAdvisor | Independently investigate a complex decision or assigned outcome. |

Defaults are examples for accounts that offer those models. Select available
models at installation; this skill does not require a private provider, a fixed
model allowlist, or access to every template's model.

## Precedence and verification

A custom agent file's model and effort take precedence over explicit spawn
values. Before the file is applied, settings resolve from the explicit spawn,
then the corresponding `[agents]` default, then the parent. Set effort along
with model when changing templates so the inherited effort remains compatible.
See [official custom-agent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

An optional `[agents]` default model/effort can limit the cost of accidentally
spawning without an intended role. Choose it from the account's available models.
Set `model_auto_compact_token_limit` well below the context window (for example
about 300K) so a long orchestration run does not re-read a near-full context on
every call.
Profiles inherit parent permissions, provider, MCP configuration and service tier;
this package does not override those settings.

After installation, parse the TOML and confirm that a fresh session exposes the
intended role. For a real delegated task, inspect its effective role, model and
effort in the trace. A template, accepted request or agent self-report is not
proof of what ran. If the intended role is absent, keep the work in the main
agent while diagnosing discovery rather than silently using a different role.

The optional usage script reports locally retained traces and estimates using
a dated Standard rate snapshot. It does not measure mixed service-tier billing
or account limits. Check [current pricing](https://learn.chatgpt.com/docs/pricing)
for a current rate; the script's rate date and limitations accompany every report.
