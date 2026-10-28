# Helix Skills Box

English | [简体中文](README.zh-CN.md)

Reusable Agent Skills for clarifying intent, delegating work, handing off sessions, defining a brand, logically reviewing rules and arguments, and evaluating skills.

Each skill is a self-contained directory with a `SKILL.md` entry point and any templates, references, or scripts it needs. Skill instructions are primarily in Chinese; some references and code are in English.

## Skills

| Skill | Purpose | Example request |
|---|---|---|
| [helix-clarify](skills/helix-clarify/SKILL.md) | Resolve omissions, references, and self-corrections in conversational Chinese; ask only questions that affect execution. | “Help me clarify this request before deciding how to proceed.” |
| [helix-delegation](skills/helix-delegation/SKILL.md) | Split substantial work, brief agents, and verify delegated results across Codex and Claude Code. | “Delegate independent parts of this task and review the results.” |
| [helix-handoff](skills/helix-handoff/SKILL.md) | Produce a reviewable session handoff that works across tools. | “Prepare a handoff so the next session can finish verification.” |
| [helix-ip](skills/helix-ip/SKILL.md) | Define brand facts, positioning, messaging, and visual direction; review materials against that definition. | “Turn these materials into a brand IP.md.” |
| [helix-rule-review](skills/helix-rule-review/SKILL.md) | Logically review rules for contradictions, gaps, precedence, terms, redundancy, and broken references, and arguments for support, causation, and premises. | “Use rule review to check whether these rules contradict each other.” |
| [helix-skill-eval](skills/helix-skill-eval/SKILL.md) | Check skill package structure and record evaluations against a versioned rubric with evidence. | “Check this skill's structure; use the full assessment only if a score is needed.” |

`helix-clarify`, `helix-handoff`, `helix-ip`, and `helix-rule-review` use instructions or templates. Delegation uses the host runtime; its optional local usage reporter needs Python 3.10+. The `helix-skill-eval` scripts require Python 3.11+ and PyYAML.

## Get started

Clone the source:

```bash
git clone https://github.com/helixho/helix-skills-box.git
cd helix-skills-box
```

Install the selected skill directory in your agent's skills location, or create a symbolic link to its source. Each skill can be used independently.

For example, link `helix-clarify` into Codex's user-level skills directory:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD/skills/helix-clarify" "$HOME/.agents/skills/helix-clarify"
```

If the target name already exists, inspect the existing installation and choose which source to use. In a new session, invoke the skill explicitly with `$helix-clarify`.

In Codex, `helix-clarify`, `helix-delegation`, and `helix-ip` allow automatic selection by description. `helix-handoff`, `helix-rule-review`, and `helix-skill-eval` are explicit-only by default: invoke them with `$helix-handoff`, `$helix-rule-review`, and `$helix-skill-eval`. `helix-rule-review` is also explicit-only in Claude Code (`/helix-rule-review`). Follow the skill discovery and invocation conventions of other runtimes.

You can also ask an agent to read a selected `SKILL.md` and follow it for the current task.

For delegation, install the selected runtime's role templates using its [Codex adapter](skills/helix-delegation/references/runtime-codex.md) or [Claude Code adapter](skills/helix-delegation/references/runtime-claude-code.md). Model defaults are replaceable examples; the skill does not install or change your runtime configuration.

## Run a structural check

From the repository root, create a Python environment and install the script dependency:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/helix-skill-eval/scripts/requirements.txt
```

List supported commands and rubric metadata:

```bash
printf '%s\n' '{"command":"describe"}' | .venv/bin/python skills/helix-skill-eval/scripts/run.py
```

Check a skill directory and its frontmatter:

```bash
printf '%s\n' '{"command":"validate","skill_dir":"skills/helix-clarify"}' | .venv/bin/python skills/helix-skill-eval/scripts/run.py
```

The `conformant` result reports structural conformance. For a full assessment, the caller supplies judgments and evidence; the script validates those inputs and aggregates the result. Structural conformance or a score alone does not establish runtime behavior. See [helix-skill-eval](skills/helix-skill-eval/SKILL.md) for the full workflow.

## Run behavior tests

The delegation reporter is tested with synthetic traces; tests never read your sessions:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/skills/helix-delegation
```

## License

Licensed under [MIT](LICENSE). Use, modification, distribution, and commercial use are permitted with the copyright and license notice retained.
