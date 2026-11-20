# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile build a small repository, sys makes the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

# <!-- custom: Import the same repository helper used by checks-repository.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "repository"))
import workflow_script_coverage as checker


class WorkflowScriptCoverageTests(unittest.TestCase):
    def test_only_run_scripts_count_and_helpers_are_left_out(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for path in ("build/xml/run_check.py", "build/xml/unrun_check.py", "build/lib/shared.py", "build/xml/_helpers.py"):
                (root / ".github/workflows" / path).parent.mkdir(parents=True, exist_ok=True)
                (root / ".github/workflows" / path).write_text("", encoding="utf-8")
            scripts = checker.build_scripts(root)
            self.assertEqual(scripts, [".github/workflows/build/xml/run_check.py", ".github/workflows/build/xml/unrun_check.py"])
            failures = checker.check_scripts(scripts, "run: python .github/workflows/build/xml/run_check.py\n")
            self.assertEqual(len(failures), 1)
            self.assertIn("unrun_check.py", failures[0])


if __name__ == "__main__":
    unittest.main()
