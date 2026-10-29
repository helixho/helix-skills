#!/usr/bin/env python3
"""Check every published skill and recursively run repository unit tests."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def validate_skills(root: Path) -> bool:
    directories = sorted(path for path in (root / "skills").iterdir() if path.is_dir())
    if not directories:
        print("FAIL: no skill directories found", flush=True)
        return False
    passed = True
    for directory in directories:
        completed = subprocess.run(
            [sys.executable, str(root / "skills/helix-skill-review/scripts/run.py")],
            input=json.dumps({"command": "validate", "skill_dir": str(directory), "public": True}),
            capture_output=True, text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        try:
            response = json.loads(completed.stdout)
            result = response["result"]
            valid = (
                completed.returncode == 0 and response["ok"]
                and result["conformant"] and not result["isolation_findings"]
            )
            print(f"{'PASS' if valid else 'FAIL'}: {directory.name}", flush=True)
            for message in result["errors"] + result["isolation_findings"]:
                print(f"  {message}", flush=True)
            for message in result["warnings"]:
                print(f"  warning: {message}", flush=True)
        except (ValueError, KeyError, TypeError):
            valid = False
            print(f"FAIL: {directory.name}: validator did not return a valid result", flush=True)
            print(completed.stderr or completed.stdout, flush=True)
        passed = bool(valid) and passed
    return passed


def discover_tests(test_root: Path) -> unittest.TestSuite:
    """Load each test file without requiring packages or unique base filenames."""
    files = sorted(test_root.rglob("test_*.py"))
    if not files:
        raise ValueError("no test files found")
    suite = unittest.TestSuite()
    for path in files:
        name = "repository_tests_" + path.relative_to(test_root).as_posix().encode().hex()
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        tests = unittest.TestLoader().loadTestsFromModule(module)
        if tests.countTestCases() == 0:
            raise ValueError(f"no tests found in {path.relative_to(test_root)}")
        suite.addTests(tests)
    return suite


def run_tests(test_root: Path) -> bool:
    try:
        suite = discover_tests(test_root)
    except Exception as exc:
        print(f"FAIL: test discovery: {exc}", flush=True)
        return False
    print(f"Running {suite.countTestCases()} tests", flush=True)
    return unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful()


def main() -> int:
    try:
        skills_ok = validate_skills(ROOT)
    except Exception as exc:
        print(f"FAIL: skill validation: {exc}", flush=True)
        skills_ok = False
    tests_ok = run_tests(ROOT / "tests")
    return 0 if skills_ok and tests_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
