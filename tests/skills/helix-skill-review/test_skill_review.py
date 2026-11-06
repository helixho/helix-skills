"""Contract tests for the helix-skill-review entrypoint on temporary fixture skills."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "skills/helix-skill-review/scripts/run.py"
DIMENSIONS = [
    "Value and fit",
    "Structure maturity",
    "Uniqueness",
    "Maintainability",
    "Portability and configuration",
    "Trust boundary",
    "Trigger quality",
    "Actionability",
    "Evidence quality",
]


def call(request):
    completed = subprocess.run(
        [sys.executable, str(RUN)], input=json.dumps(request), capture_output=True, text=True, check=False
    )
    return json.loads(completed.stdout)


def write_skill(root, frontmatter="", body="Body.\n"):
    skill = Path(root) / "demo-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        f"---\nname: demo-skill\ndescription: Demo.\n{frontmatter}---\n{body}", encoding="utf-8"
    )
    return skill


def evaluate(skill, **extra):
    return call({
        "command": "evaluate",
        "source_project": "fixture",
        "skill_unit": "demo-skill",
        "skill_dir": str(skill),
        "scores": {name: 4 for name in DIMENSIONS},
        "expected_content_hash": call({"command": "validate", "skill_dir": str(skill)})["result"]["content_hash"],
        "evidence": [{"id": "E1", "kind": "file-backed", "source": "SKILL.md", "line": 4, "detail": "Body exists."}],
        **extra,
    })


class ValidateTests(unittest.TestCase):
    def test_conformant_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = call({"command": "validate", "skill_dir": str(write_skill(tmp))})["result"]
        self.assertTrue(result["conformant"])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["files"], ["SKILL.md"])

    def test_unknown_field_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = call({"command": "validate", "skill_dir": str(write_skill(tmp, "foo: 1\n"))})["result"]
        self.assertFalse(result["conformant"])
        self.assertIn("unsupported top-level frontmatter fields: foo", result["errors"])

    def test_broken_relative_link_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, body="See [guide](references/guide.md) and [site](https://example.com).\n")
            broken = call({"command": "validate", "skill_dir": str(skill)})["result"]
            (skill / "references").mkdir()
            (skill / "references/guide.md").write_text("Guide.\n", encoding="utf-8")
            fixed = call({"command": "validate", "skill_dir": str(skill)})["result"]
        self.assertFalse(broken["conformant"])
        self.assertIn("broken link SKILL.md:5: references/guide.md", broken["errors"])
        self.assertTrue(fixed["conformant"])

    def test_runtime_extension_warns_and_is_type_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok = call({"command": "validate", "skill_dir": str(write_skill(tmp, "disable-model-invocation: true\n"))})
        with tempfile.TemporaryDirectory() as tmp:
            bad = call({"command": "validate", "skill_dir": str(write_skill(tmp, "disable-model-invocation: yes-please\n"))})
        self.assertTrue(ok["result"]["conformant"])
        self.assertEqual(len(ok["result"]["warnings"]), 1)
        self.assertIn("disable-model-invocation must be a bool", bad["result"]["errors"])

    def test_public_scan_flags_personal_home_paths_only(self):
        body = "Run /Users/alice/tools/x.\nSee /Users/example/demo and /home/user/demo.\nC:\\Users\\bob\\x\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, body=body)
            public = call({"command": "validate", "skill_dir": str(skill), "public": True})["result"]
            private = call({"command": "validate", "skill_dir": str(skill)})["result"]
        self.assertEqual(len(public["isolation_findings"]), 2)
        self.assertIn("/Users/alice", public["isolation_findings"][0])
        self.assertNotIn("isolation_findings", private)


class EvaluateTests(unittest.TestCase):
    def test_source_drift_and_missing_snapshot_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp)
            before = call({"command": "validate", "skill_dir": str(skill)})["result"]["content_hash"]
            (skill / "SKILL.md").write_text("changed\n", encoding="utf-8")
            self.assertIn("source changed", evaluate(skill, expected_content_hash=before)["error"]["message"])
            self.assertFalse(evaluate(skill, expected_content_hash=None)["ok"])

    def test_empty_unlabeled_or_dangling_evidence_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp)
            for evidence in ([], ["unlabeled"], [{"id": "E1", "kind": "unknown"}]):
                self.assertFalse(evaluate(skill, evidence=evidence)["ok"])
            finding = {"id": "F1", "detail": "Gap", "evidence_ids": ["missing"]}
            self.assertFalse(evaluate(skill, findings=[finding])["ok"])

    def test_citation_location_is_checked_but_not_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp)
            evidence = {"id": "E1", "kind": "file-backed", "source": "SKILL.md", "line": 999, "detail": "Claim"}
            self.assertFalse(evaluate(skill, evidence=[evidence])["ok"])
            evidence["line"] = 4
            self.assertTrue(evaluate(skill, evidence=[evidence])["ok"])
            evidence["source"] = "absent.md"
            self.assertFalse(evaluate(skill, evidence=[evidence])["ok"])

    def test_findings_and_suggestions_must_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp)
            finding = {"id": "F1", "detail": "Missing completion check", "evidence_ids": ["E1"]}
            suggestion = {"detail": "Add completion check", "finding_ids": ["F1"]}
            self.assertFalse(evaluate(skill, findings=[finding])["ok"])
            self.assertTrue(evaluate(skill, findings=[finding], suggestions=[suggestion])["ok"])
            self.assertFalse(evaluate(skill, findings=[finding, finding], suggestions=[suggestion])["ok"])
            suggestion["finding_ids"] = ["unknown"]
            self.assertFalse(evaluate(skill, findings=[finding], suggestions=[suggestion])["ok"])

    def test_external_and_user_evidence_are_distinct_from_file_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp)
            evidence = [{"id": "E1", "kind": "external-backed", "source": "https://example.com/docs", "detail": "Observed behavior; retrieved during review."},
                        {"id": "E2", "kind": "user-stated", "source": "current request", "detail": "Private single-user use."}]
            self.assertTrue(evaluate(skill, evidence=evidence)["ok"])
            evidence[0]["source"] = "not a URL"
            self.assertFalse(evaluate(skill, evidence=evidence)["ok"])

    def test_average_and_rubric(self):
        with tempfile.TemporaryDirectory() as tmp:
            assessment = evaluate(write_skill(tmp))["result"]["assessment"]
        self.assertEqual(assessment["average"], 4.0)
        self.assertEqual(assessment["rubric"]["id"], "helix-skill-scorecard")
        self.assertNotIn("version", assessment["rubric"])
        self.assertNotIn("runtime_status", assessment)

    def test_content_hash_follows_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp)
            first = evaluate(skill)["result"]["assessment"]["content_hash"]
            again = evaluate(skill)["result"]["assessment"]["content_hash"]
            (skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Demo.\n---\nChanged.\n", encoding="utf-8")
            changed = evaluate(skill)["result"]["assessment"]["content_hash"]
        self.assertEqual(first, again)
        self.assertNotEqual(first, changed)

    def test_rejects_caller_hash_and_runtime_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp)
            for field, value in (("content_hash", "x"), ("runtime_status", "passed"), ("runtime_evidence", ["x"])):
                with self.subTest(field=field):
                    response = evaluate(skill, **{field: value})
                    self.assertFalse(response["ok"])
                    self.assertIn(field, response["error"]["message"])

    def test_dimension_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            response = evaluate(write_skill(tmp), scores={"Value and fit": 4})
        self.assertFalse(response["ok"])
        self.assertIn("missing=", response["error"]["message"])


if __name__ == "__main__":
    unittest.main()
