# Helix Skills

This public repository is the canonical source for the skills under `skills/`.

- Keep each skill self-contained at `skills/<name>/`. Its instructions belong in
  `SKILL.md`; runtime resources belong alongside it in `references/`, `scripts/`,
  `agents/` or `assets/` when needed.
- Keep public installation and usage guidance in the root `README.md`. Do not
  add per-skill READMEs, maintenance records or generated evaluation reports.
- Keep tests and fixtures outside runtime-linked skill directories. Verify
  changes in proportion to their behavior; structural validation alone is not
  evidence of runtime behavior.
- Edit source here, not installed runtime copies. Preserve skill names and
  invocation policies unless the requested change requires updating them.
- Keep machine-specific configuration, credentials, sessions, logs and private
  working material outside this repository.
- Keep every published skill usable by anyone: no reference to or dependency on
  the owner's private tools, knowledge base, installed applications or
  workflows. Integrations with those belong in the owner's private repository.
- Include only resources needed by the published skills. Do not copy private
  repository history, runtime homes or third-party skill collections here.
