"""Behavior checks for recursive discovery and failure propagation."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("repository_check", ROOT / "scripts/check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class RepositoryCheckTests(unittest.TestCase):
    def write_test(self, root, relative, body="self.assertTrue(True)"):
        path = Path(root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "import unittest\nclass Example(unittest.TestCase):\n"
            f"    def test_example(self):\n        {body}\n", encoding="utf-8",
        )

    def run_fixture(self, root):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return check.run_tests(Path(root))

    def test_nested_directories_and_duplicate_filenames(self):
        with tempfile.TemporaryDirectory() as root:
            self.write_test(root, "one/nested/test_example.py")
            self.write_test(root, "two/test_example.py")
            suite = check.discover_tests(Path(root))
            self.assertEqual(suite.countTestCases(), 2)
            self.assertTrue(self.run_fixture(root))

    def test_no_test_files_fails(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertFalse(self.run_fixture(root))

    def test_empty_test_module_fails_even_with_other_tests(self):
        with tempfile.TemporaryDirectory() as root:
            self.write_test(root, "test_pass.py")
            (Path(root) / "test_empty.py").write_text("", encoding="utf-8")
            self.assertFalse(self.run_fixture(root))

    def test_assertion_failure_propagates(self):
        with tempfile.TemporaryDirectory() as root:
            self.write_test(root, "test_failure.py", "self.fail('expected failure')")
            self.assertFalse(self.run_fixture(root))

    def test_import_failure_propagates(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "test_import.py").write_text("raise RuntimeError('broken import')\n", encoding="utf-8")
            self.assertFalse(self.run_fixture(root))

    def test_existing_skill_tests_are_discovered(self):
        suite = check.discover_tests(ROOT / "tests/skills")
        self.assertGreaterEqual(suite.countTestCases(), 19)


if __name__ == "__main__":
    unittest.main()
