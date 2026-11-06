"""Deterministic tests for case orchestration, not AI semantic accuracy."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills/helix-logic-review/scripts/cases.py"
spec = importlib.util.spec_from_file_location("review_cases", SCRIPT)
cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cases)
FIXTURE = Path(__file__).with_name("cases.md")


class CaseTools(unittest.TestCase):
    def test_blind_packet_has_all_inputs_and_no_answers(self):
        digest, source = cases.read_cases(FIXTURE)
        packet = cases.run("inputs", FIXTURE)
        self.assertEqual(packet["cases_hash"], digest)
        self.assertTrue({f"C{number:02d}" for number in range(1, 26)} <= {item["id"] for item in source})
        self.assertEqual([item["id"] for item in packet["cases"]], [item["id"] for item in source])
        self.assertTrue(all(set(item) == {"id", "input"} for item in packet["cases"]))
        self.assertEqual(packet["cases"][0]["input"], source[0]["input"])

    def test_skill_review_acceptance_cases_can_use_same_packet_format(self):
        fixture = ROOT / "tests/skills/helix-skill-review/cases.md"
        packet = cases.run("inputs", fixture)
        self.assertEqual(len(packet["cases"]), 5)
        self.assertTrue(all(set(item) == {"id", "input"} for item in packet["cases"]))

    def test_judge_and_summary_do_not_claim_semantic_or_human_approval(self):
        packet = cases.run("inputs", FIXTURE)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.json"
            results = {"cases_hash": packet["cases_hash"], "results": [
                {"id": item["id"], "judgment": "test output", "reason": "test reasoning", "revision": "no revision", "changes_premises": False}
                for item in packet["cases"]]}
            path.write_text(json.dumps(results), encoding="utf-8")
            judge = cases.run("judge", FIXTURE, path)
            self.assertIn("expected", judge["cases"][0])
            review_file = Path(tmp) / "reviews.json"
            review_file.write_text(json.dumps(results), encoding="utf-8")
            judgments = {"cases_hash": packet["cases_hash"], "results_hash": judge["results_hash"], "judgments": [
                {"id": item["id"], "outcome": "uncertain", "reason": "Test has no actual AI judgment"}
                for item in packet["cases"]]}
            path.write_text(json.dumps(judgments), encoding="utf-8")
            summary = cases.run("summarize", FIXTURE, path, review_file)
            self.assertEqual(summary["ai_assessment"]["pass"], 0)
            self.assertEqual(summary["ai_assessment"]["uncertain"], len(packet["cases"]))
            self.assertEqual(summary["human_confirmation"], "not recorded by this tool")
            results["results"][0]["reason"] = "changed output"
            review_file.write_text(json.dumps(results), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outputs changed"):
                cases.run("summarize", FIXTURE, path, review_file)
            results["results"][0]["reason"] = "test reasoning"
            review_file.write_text(json.dumps(results), encoding="utf-8")
            judgments["judgments"].pop()
            path.write_text(json.dumps(judgments), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "every case"):
                cases.run("summarize", FIXTURE, path, review_file)

    def test_drift_duplicate_unknown_ids_and_incomplete_cases_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.md"
            path.write_text("### C01\n#### 输入\na\n#### 预期\nb\n", encoding="utf-8")
            digest, source = cases.read_cases(path)
            results = Path(tmp) / "results.json"
            base = {"id": "C01", "outcome": "pass", "reason": "AI reasoning"}
            for records in ([base, base], [{**base, "id": "C99"}], [{**base, "outcome": []}]):
                results.write_text(json.dumps({"cases_hash": digest, "judgments": records}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    cases.read_results(results, digest, source, "judgments")
            results.write_text(json.dumps({"cases_hash": digest, "judgments": [base]}), encoding="utf-8")
            path.write_text(path.read_text() + "\nchanged", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed"):
                cases.read_results(results, cases.read_cases(path)[0], source, "judgments")
            path.write_text("### C01\n#### 输入\na\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "incomplete"):
                cases.read_cases(path)
