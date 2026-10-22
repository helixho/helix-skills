# CLI executors

The main agent runs another agent's CLI headless, waits for it, and reviews the result. This applies to any main agent, including Claude Code. Write the brief to a file and pass it by path or content. Redirect all output to a log the main agent can read.

## Launch

Specify the model and effort on the command line so that a changed default does not change the run. Close stdin.

**Grok Build**

```sh
grok --cwd <repo> -m <model> --reasoning-effort <low|medium|high> \
  --prompt-file <brief.md> --always-approve --output-format plain --disable-web-search \
  --deny "Bash(git push*)" --deny "<other hard limits>" \
  < /dev/null > <log> 2>&1
```

- `--deny` rules take precedence over approval. Encode the brief's hard limits as deny rules too, for example push, branch rewrites, or test commands when tests must not run locally.
- To continue the same executor with its context, resume the session with `-r <session-id>` and pass a short follow-up brief. Sessions are under `~/.grok/sessions/<encoded cwd>/<id>/`.

**Codex**

```sh
codex exec -C <repo> <permission flag> -m <model> -c model_reasoning_effort=<effort> \
  -o <last-message.txt> "$(cat <brief.md>)" < /dev/null > <log> 2>&1
```

- Pass the permission mode explicitly; otherwise the run inherits the user's `config.toml`, and a sandbox that blocks writes or commits leaves the brief impossible to finish. Use `--dangerously-bypass-approvals-and-sandbox` where the user runs without a sandbox, or `-s workspace-write` where a sandbox is wanted.
- Close inherited stdin for headless execution. A pipe kept open by the parent can leave `codex exec` waiting for additional input.

## Waiting for completion

A main agent whose background commands notify it on exit (Claude Code) runs the launch command itself in the background and needs nothing more. Otherwise, launch detached, record the PID, and run a separate background watcher on that PID:

```sh
nohup <launch command> & echo $! > <pidfile>
pid=$(cat <pidfile>); while kill -0 "$pid" 2>/dev/null; do sleep 60; done; tail -c 1500 <log>
```

Waiting on the recorded PID avoids matching another executor's process or missing a CLI that runs under a different process name. A watcher from an earlier session does not survive a restart; start a new one from the same PID file.

## Known failure modes

- **Ends early.** Grok Build may end its turn right after starting a long command in the background, saying it will report later. Nothing gets finished or reported. Put "do not end before the changes and the report file exist" in the brief, prefer short foreground commands, and after the run check the changes and report instead of trusting the last message.
- **Hits the host.** On an environment fault, an executor may restart the container engine or create helper containers to work around it. If the user has not allowed that, put it in the hard limits and deny the commands.
- **Writes outside the brief.** Check for helper containers, port forwards, files in shared state directories, and runtime output left in the repository.
- **Session context fills up.** Long runs auto-compact and may lose detail from the brief. Keep the brief self-contained, and on resume restate the goal and done criteria in the follow-up brief.
