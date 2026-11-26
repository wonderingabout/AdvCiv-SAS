# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable, tempfile builds small repositories, shutil removes them and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

# <!-- custom: Import the same documentation helper used by checks-documentation.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "documentation"))
import ci_markers_listed as checker


class CiMarkersListedTests(unittest.TestCase):
	def repo(self, readme_rows, scripts=None):
		root = Path(tempfile.mkdtemp())
		self.addCleanup(shutil.rmtree, root)
		readme = "# W\n\n## CI markers in commit messages\n\n| Marker | Intent | What CI still checks |\n| --- | --- | --- |\n"
		readme += "".join("| `%s` | x | y |\n" % row for row in readme_rows) + "\n## Run Locally\n"
		(root / ".github/workflows/build/source").mkdir(parents=True)
		(root / ".github/workflows/lib").mkdir(parents=True)
		(root / ".github/workflows/README.md").write_text(readme, encoding="utf-8")
		for name, text in (scripts or {}).items():
			(root / ".github/workflows/build/source" / name).write_text(text, encoding="utf-8")
		return root

	def all_rows(self):
		return sorted(checker.markers().values())

	def test_every_marker_listed_passes(self):
		self.assertEqual(checker.problems(self.repo(self.all_rows())), [])

	def test_unlisted_marker_fails(self):
		rows = [row for row in self.all_rows() if row != "ci_define_uncached:"]
		errors = checker.problems(self.repo(rows))
		self.assertEqual(len(errors), 1)
		self.assertIn("DEFINE_UNCACHED", errors[0])

	def test_listed_but_undefined_marker_fails(self):
		errors = checker.problems(self.repo(self.all_rows() + ["[ci_unknown]"]))
		self.assertEqual(len(errors), 1)
		self.assertIn("[ci_unknown]", errors[0])

	def test_marker_spelled_in_a_script_fails(self):
		errors = checker.problems(self.repo(self.all_rows(), {"a.py": "x = 'say why with a ci_define_uncached: comment'\n"}))
		self.assertEqual(len(errors), 1)
		self.assertIn("a.py:1", errors[0])

	def test_new_marker_shape_in_a_script_fails(self):
		errors = checker.problems(self.repo(self.all_rows(), {"a.py": "MARK = \"[ci_new_intent]\"\n"}))
		self.assertEqual(len(errors), 1)

	def test_comments_and_docstrings_may_name_a_marker(self):
		text = "# the [ci_update_dll] marker\ndef f():\n\t\"\"\"Reads ci_define_uncached: comments.\"\"\"\n\treturn 1\n"
		self.assertEqual(checker.problems(self.repo(self.all_rows(), {"a.py": text})), [])

	# <!-- custom: Codex's second review reproduced these three against the token-based first version (GPT-6.2-Sol, 2026-11-25). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def test_marker_alone_on_a_line_in_brackets_fails(self):
		errors = checker.problems(self.repo(self.all_rows(), {"a.py": "x = (\n\t\"[ci_new_marker]\"\n)\n"}))
		self.assertEqual(len(errors), 1)

	def test_marker_split_across_adjacent_literals_fails(self):
		errors = checker.problems(self.repo(self.all_rows(), {"a.py": "x = \"[ci_\" \"new_marker]\"\n"}))
		self.assertEqual(len(errors), 1)

	def test_docstring_with_a_trailing_comment_passes(self):
		text = "def f():\n\t\"\"\"Reads [ci_update_dll].\"\"\"  # note\n\treturn 1\n"
		self.assertEqual(checker.problems(self.repo(self.all_rows(), {"a.py": text})), [])

	def test_repository_passes(self):
		self.assertEqual(checker.main([]), 0)


if __name__ == "__main__":
	unittest.main()
