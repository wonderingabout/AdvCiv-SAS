# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib locates the checker, sys makes it importable and unittest checks each kind of workflow text. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same repository helper used by checks-repository.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "repository"))
import workflow_keep_going as checker

SETUP = "steps:\n  - uses: actions/checkout@v7\n  - uses: actions/setup-python@v7\n    id: setup\n"
GOOD = "  - name: First\n    %s\n    run: python a.py\n" % checker.KEEP_GOING


class WorkflowKeepGoingTests(unittest.TestCase):
    def test_every_step_with_the_condition_passes(self):
        self.assertEqual(checker.check_workflow("a.yml", SETUP + GOOD + GOOD.replace("First", "Second")), [])

    def test_all_missing_steps_are_reported_together(self):
        failures = checker.check_workflow("a.yml", SETUP + "  - name: First\n    run: x\n" + GOOD + "  - name: Third\n    run: y\n")
        self.assertEqual(len(failures), 2)
        self.assertIn("'First'", failures[0])
        self.assertIn("'Third'", failures[1])

    def test_a_comment_may_precede_the_condition(self):
        self.assertEqual(checker.check_workflow("a.yml", SETUP + "  - name: First\n    # why\n    %s\n    run: x\n" % checker.KEEP_GOING), [])

    def test_missing_setup_id_fails(self):
        self.assertIn("id: setup", checker.check_workflow("a.yml", "steps:\n  - name: First\n    run: x\n")[0])


if __name__ == "__main__":
    unittest.main()
