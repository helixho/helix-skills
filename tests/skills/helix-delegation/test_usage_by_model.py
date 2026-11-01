"""Synthetic trace regressions; never read the user's retained sessions."""
import contextlib
from datetime import date
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "usage_by_model", ROOT / "skills/helix-delegation/scripts/usage_by_model.py"
)
usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(usage)


def event(kind, payload, timestamp="2026-10-01T12:00:00Z"):
    return {"type": kind, "payload": payload, "timestamp": timestamp}


def meta(sid, **fields):
    return event("session_meta", {"id": sid, **fields})


def model(name="gpt-6-luna", effort="high"):
    return event("turn_context", {"model": name, "effort": effort})


def tokens(total=True):
    counts = {"input_tokens": 100, "cached_input_tokens": 25,
              "output_tokens": 20, "reasoning_output_tokens": 5}
    info = {"last_token_usage": counts}
    if total:
        info["total_token_usage"] = counts
    return event("event_msg", {"type": "token_count", "info": info})


class UsageTraces(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "sessions"
        self.root.mkdir()

    def trace(self, name, events, root=None):
        path = (root or self.root) / (name + ".jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
        return path

    def test_adjacent_repeated_cumulative_snapshot_counts_once(self):
        self.trace("root", [meta("root"), model(), tokens(), tokens()])
        models, _, sessions, *_ = usage.scan(self.root, None)
        self.assertEqual(models["gpt-6-luna"]["input"], 100)
        self.assertEqual(models["gpt-6-luna"]["output"], 20)
        self.assertEqual(sessions[0]["skipped_duplicate_events"], 1)

    def test_equal_usage_without_cumulative_evidence_is_not_deduplicated(self):
        self.trace("root", [meta("root"), model(), tokens(False), tokens(False)])
        models, *_ = usage.scan(self.root, None)
        self.assertEqual(models["gpt-6-luna"]["input"], 200)

    def test_model_switch_preserves_both_segments_and_one_session_status(self):
        self.trace("root", [meta("root"), model(), tokens(),
                            model("gpt-6.1-sol"), tokens()])
        models, _, sessions, *_ = usage.scan(self.root, None)
        self.assertEqual(set(models), {"gpt-6-luna", "gpt-6.1-sol"})
        self.assertEqual(sum(v["input"] for v in models.values()), 200)
        self.assertEqual(len(usage.unique_session_rows(usage.session_rows(sessions))), 1)

    def test_task_filter_includes_nested_children_and_resolves_child_id(self):
        self.trace("root", [meta("root"), model(), tokens()])
        self.trace("child", [meta("child", source={"subagent": {"thread_spawn": {
            "parent_thread_id": "root", "agent_role": "Executor", "agent_path": "/root/fix"
        }}}), model(), tokens()])
        self.trace("grandchild", [meta("grandchild", parent_thread_id="child"), model(), tokens()])
        self.trace("unrelated", [meta("unrelated"), model(), tokens()])
        models, _, sessions, _, included, _, task = usage.scan(self.root, None, "child")
        self.assertEqual(task, "root")
        self.assertEqual(included, 3)
        self.assertEqual(models["gpt-6-luna"]["input"], 300)
        self.assertEqual(sorted(s["depth"] for s in sessions), [0, 1, 2])
        self.assertEqual(next(s for s in sessions if s["session_id"] == "child")["agent_role"], "Executor")

    def test_newer_resumed_copy_wins_over_older_completed_archive(self):
        archive = Path(self.tmp.name) / "archive"
        self.trace("old", [meta("root"), model(), tokens(),
                           event("event_msg", {"type": "task_complete"}, "2026-10-02T12:00:00Z")], archive)
        current = self.trace("new", [meta("root"), model(), tokens(),
                                    event("event_msg", {"type": "task_started"}, "2026-10-03T12:00:00Z")])
        diagnostics = {}
        models, _, sessions, _, included, *_ = usage.scan(self.root, None, archived_root=archive, diagnostics=diagnostics)
        self.assertEqual(included, 1)
        self.assertEqual(sessions[0]["path"], current)
        self.assertEqual(sessions[0]["terminal_status"], "incomplete")
        self.assertEqual(models["gpt-6-luna"]["input"], 100)
        self.assertEqual(diagnostics["duplicate_session_files"], 1)

    def test_creation_date_filter_does_not_count_old_resumed_task_as_new(self):
        self.trace("root", [meta("root"), model(),
                            event("event_msg", {"type": "task_started"}, "2026-10-05T12:00:00Z"), tokens()])
        self.assertEqual(usage.scan(self.root, date(2026, 10, 4))[4], 0)
        self.assertEqual(usage.scan(self.root, None, "root")[4], 1)

    def test_resumed_turn_requires_a_new_final_report(self):
        self.trace("root", [meta("root"), model(), tokens(),
                            event("response_item", {"role": "assistant", "channel": "final", "content": [{"text": "Done"}]}),
                            event("event_msg", {"type": "task_complete"}),
                            event("event_msg", {"type": "task_started"}),
                            event("event_msg", {"type": "turn_aborted"})])
        session = usage.scan(self.root, None)[2][0]
        self.assertTrue(session["final_report_present"])
        self.assertFalse(session["last_turn_final_report_present"])
        self.assertFalse(session["task_complete"])
        self.assertEqual(session["terminal_status"], "interrupted")

    def test_incomplete_trace_and_malformed_line_remain_reportable(self):
        path = self.trace("minimal", [meta("minimal"), tokens(False)])
        with path.open("a") as stream:
            stream.write('{"truncated":\n')
        models, _, sessions, _, included, malformed, _ = usage.scan(self.root, None)
        self.assertEqual(included, 1)
        self.assertEqual(malformed, 1)
        self.assertEqual(models["unknown"]["input"], 100)
        self.assertEqual(sessions[0]["terminal_status"], "incomplete")

    def test_unknown_pricing_is_explicit_and_reasoning_is_not_double_counted(self):
        counts = {"events": 1, "input": 100, "cached": 25, "output": 20, "reasoning": 5}
        row = usage.usage_row("new-model", counts)
        self.assertEqual(row["total_processed_tokens"], 120)
        self.assertIsNone(row["estimated_standard_credits"])
        summary = usage.usage_summary([row])
        self.assertFalse(summary["estimated_standard_credits_complete"])
        self.assertEqual(summary["unpriced_processed_tokens"], 120)

    def test_json_command_uses_only_explicit_fixture_root(self):
        self.trace("root", [meta("root"), model(), tokens()])
        output = io.StringIO()
        with patch("sys.argv", ["usage", "--sessions-root", str(self.root), "--all", "--json"]), contextlib.redirect_stdout(output):
            result = usage.main()
        report = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual(report["summary"]["total_processed_tokens"], 120)
        self.assertIsNone(report["archived_sessions_root"])
        self.assertEqual(report["session_files_included"], 1)


if __name__ == "__main__":
    unittest.main()
