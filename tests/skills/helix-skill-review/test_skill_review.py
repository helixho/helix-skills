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
        **extra,
    })


class ValidateTests(unittest.TestCase):
    def test_conformant_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = call({"command": "validate", "skill_dir": str(write_skill(tmp))})["result"]
        self.assertTrue(result["conformant"])
        self.assertEqual(result["warnings"], [])

    def test_unknown_field_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = call({"command": "validate", "skill_dir": str(write_skill(tmp, "foo: 1\n"))})["result"]
        self.assertFalse(result["conformant"])
        self.assertIn("unsupported top-level frontmatter fields: foo", result["errors"])

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
            response = call({
                "command": "evaluate",
                "source_project": "fixture",
                "skill_unit": "demo-skill",
                "skill_dir": str(write_skill(tmp)),
                "scores": {"Value and fit": 4},
            })
        self.assertFalse(response["ok"])
        self.assertIn("missing=", response["error"]["message"])


if __name__ == "__main__":
    unittest.main()
