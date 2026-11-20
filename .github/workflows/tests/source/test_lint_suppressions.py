# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: importlib loads the check from its file, so no sys.path entry and late import are needed. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location("lint_suppressions", ROOT / ".github/workflows/build/source/lint_suppressions.py")
assert _SPEC is not None and _SPEC.loader is not None
lint_suppressions = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(lint_suppressions)


class LintSuppressionTests(unittest.TestCase):
	def problems(self, text):
		return [problem for _, problem in lint_suppressions.check_text(text)]

	def test_bare_noqa_fails(self):
		self.assertIn("without a named rule", self.problems("import os  # noqa\n")[0])

	def test_rule_without_reason_fails(self):
		self.assertIn("without a reason", self.problems("import os  # noqa: F401\n")[0])

	def test_rule_with_reason_passes(self):
		self.assertEqual(self.problems("import os  # noqa: F401  (re-exported for callers)\n"), [])

	def test_reason_on_line_above_passes(self):
		self.assertEqual(self.problems("# Civ4 engine import that linters cannot see\nimport os  # pyright: ignore[reportMissingImports]\n"), [])

	def test_suppression_text_inside_a_string_is_ignored(self):
		self.assertEqual(self.problems("value = 'x  # noqa'\n"), [])


if __name__ == "__main__":
	unittest.main()
