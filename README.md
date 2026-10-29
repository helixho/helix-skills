# Helix Skills

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
| [helix-logic-review](skills/helix-logic-review/SKILL.md) | Review any content against the four laws of logic, the rules of definition and division (MECE), and common fallacies (straw man, slippery slope, false dilemma, and more) for fallacies, contradictions, overlaps, and gaps. | “Use rule review to check whether these rules contradict each other.” |
| [helix-skill-review](skills/helix-skill-review/SKILL.md) | Assess skills for improvements by critical thinking, MECE, Occam's razor, independence, the Agent Skills specification, and progressive disclosure; judge what an external skill offers your own. | “Check this skill's structure; use the full assessment only if a score is needed.” |

`helix-clarify`, `helix-handoff`, `helix-ip`, and `helix-logic-review` use instructions or templates. Delegation uses the host runtime; its optional local usage reporter needs Python 3.10+. The `helix-skill-review` scripts require Python 3.11+ and PyYAML.

## Get started

### Install selected skills with the skills CLI

Requires Node.js 22.20+. Run this from the project where you want to use the skills, then choose the skills and agents interactively:

```bash
npx skills add helixho/helix-skills
```

List available skills without installing, or install one selected skill for Codex:

```bash
npx skills add helixho/helix-skills --list
npx skills add helixho/helix-skills --skill helix-clarify --agent codex
```

Installation is project-level by default; add `-g` for a user-level installation. `--skill` accepts multiple names; use `--agent claude-code` for Claude Code. Install only what you need. The CLI includes each skill's references, scripts, and templates, but does not install script dependencies or register Delegation runtime roles. See the [skills CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) for all options.

### Install manually from source

Clone the source:

```bash
git clone https://github.com/helixho/helix-skills.git
cd helix-skills
```

Install the selected skill directory in your agent's skills location, or create a symbolic link to its source. Each skill can be used independently.

For example, link `helix-clarify` into Codex's user-level skills directory:

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD/skills/helix-clarify" "$HOME/.agents/skills/helix-clarify"
```

If the target name already exists, inspect the existing installation and choose which source to use. In a new session, invoke the skill explicitly with `$helix-clarify`.

In Codex, `helix-clarify`, `helix-delegation`, and `helix-ip` allow automatic selection by description. `helix-handoff`, `helix-logic-review`, and `helix-skill-review` are explicit-only by default: invoke them with `$helix-handoff`, `$helix-logic-review`, and `$helix-skill-review`. `helix-handoff` and `helix-logic-review` are also explicit-only in Claude Code (`/helix-handoff`, `/helix-logic-review`). Follow the skill discovery and invocation conventions of other runtimes.

You can also ask an agent to read a selected `SKILL.md` and follow it for the current task.

For delegation, install the selected runtime's role templates using its [Codex adapter](skills/helix-delegation/references/runtime-codex.md) or [Claude Code adapter](skills/helix-delegation/references/runtime-claude-code.md). Model defaults are replaceable examples; the skill does not install or change your runtime configuration.

## Update and uninstall

For skills installed with the skills CLI, update or remove them with the CLI:

```bash
npx skills update helix-clarify -p
npx skills remove helix-clarify --agent codex
```

These commands target the current project; use `-g` for user-level updates or removal.

For a manual symlink to the source repository, run `git pull --ff-only` in the source repository to update; the next new session uses the updated files. For a copied installation, update the source and copy the complete skill directory again, checking for local modifications in the installation first.

To uninstall the symlink example above, first confirm that `~/.agents/skills/helix-clarify` is a symlink to this repository, then run:

```bash
unlink "$HOME/.agents/skills/helix-clarify"
```

For a copied skill, use the runtime's management feature or remove its installed directory manually. Remove any separately installed Delegation role templates separately.

## Check the repository

Checks require Python 3.11+ and PyYAML. Prepare an environment from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/helix-skill-review/scripts/requirements.txt
```

Run all automated checks:

```bash
.venv/bin/python scripts/check.py
```

This checks each skill under `skills/` for structural conformance, relative Markdown links, and personal home paths, then recursively runs `test_*.py` under `tests/`. Structural errors, personal home paths, test loading errors, failed tests, or no discovered tests produce a nonzero exit code. Compatible runtime extensions are reported as warnings. GitHub Actions runs the same entrypoint on pushes, pull requests, and manual dispatch.

Automated tests cover the Delegation usage reporter, the Skill Review script entrypoint contract, and the repository checker's test discovery and failure propagation. Tests use synthetic traces and temporary fixtures, never real sessions. `tests/skills/helix-logic-review/cases.md` contains model behavior acceptance cases that must be run separately; they are outside the automated suite. Passing structural checks and script tests does not establish model behavior.

To check just one skill, use the existing entrypoint:

```bash
printf '%s\n' '{"command":"validate","skill_dir":"skills/helix-clarify","public":true}' | .venv/bin/python skills/helix-skill-review/scripts/run.py
```

The `conformant` result reports structural conformance; public path scan results are listed separately in `isolation_findings`. For a full assessment, the caller supplies judgments and evidence; the script validates those inputs and aggregates the result. Structural conformance or a score alone does not establish runtime behavior. See [helix-skill-review](skills/helix-skill-review/SKILL.md) for the full workflow.

## License

Licensed under [MIT](LICENSE). Use, modification, distribution, and commercial use are permitted with the copyright and license notice retained.
