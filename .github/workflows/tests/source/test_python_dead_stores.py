# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_dead_stores as checker


def method(*lines):
	return "class A:\n\tdef f(self):\n" + "".join("\t\t%s\n" % line for line in lines)


class PythonDeadStoresTests(unittest.TestCase):
	def test_overwritten_store_fails(self):
		hits = checker.dead_stores(method("self.X = 50", "self.Y = 1", "self.X = 0"))
		self.assertEqual(hits, [(3, 5, "X")])

	def test_read_between_passes(self):
		self.assertEqual(checker.dead_stores(method("self.X = 50", "y = self.X", "self.X = 0")), [])

	def test_second_store_reading_the_first_passes(self):
		self.assertEqual(checker.dead_stores(method("self.X = 50", "self.X = self.X + 1")), [])

	def test_method_call_between_passes(self):
		# <!-- custom: getNextWidgetName reads and advances nWidgetCount, as in SevoPediaMain.py. (Claude code Opus 5.5) -->
		self.assertEqual(checker.dead_stores(method("self.nWidgetCount = 0", "screen.deleteWidget(self.getNextWidgetName())", "self.nWidgetCount = 0")), [])

	def test_self_passed_on_passes(self):
		self.assertEqual(checker.dead_stores(method("self.X = 50", "helper(self)", "self.X = 0")), [])

	def test_bracketed_attribute_is_not_self_passed_on(self):
		self.assertEqual(checker.dead_stores(method("self.X = 50", "self.W = (self.H * 2) / 3", "self.X = 0")), [(3, 5, "X")])

	def test_early_return_between_passes(self):
		# <!-- custom: Starts from 50, not None, so the test fails if the early-exit guard goes, as Codex's review noted the first version would not. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		self.assertEqual(checker.dead_stores(method("self.X = 50", "if n <= 0:", "\treturn", "self.X = 1")), [])

	# <!-- custom: The next four are Codex's reproductions of false positives in the first version (GPT-6.2-Sol, 2026-11-24). (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	def test_hash_inside_string_does_not_hide_a_read(self):
		self.assertEqual(checker.dead_stores(method("self.X = 1", "helper(\"#\", self)", "self.X = 2")), [])

	def test_stores_inside_a_docstring_are_not_code(self):
		self.assertEqual(checker.dead_stores(method("\"\"\"", "self.X = 1", "self.X = 2", "\"\"\"")), [])

	def test_store_inside_try_passes(self):
		self.assertEqual(checker.dead_stores(method("try:", "\tself.X = 1", "\tself.X = risky()", "finally:", "\tprint(self.X)")), [])

	def test_alias_of_self_passes(self):
		self.assertEqual(checker.dead_stores(method("alias = self", "self.X = 1", "read(alias)", "self.X = 2")), [])

	def test_none_is_not_an_accepted_reset(self):
		self.assertEqual(checker.dead_stores(method("self.X = None", "self.X = 1")), [(3, 4, "X")])

	def test_store_in_branch_is_not_compared(self):
		self.assertEqual(checker.dead_stores(method("self.X = 50", "if b:", "\tself.X = 0")), [])

	def test_empty_reset_passes(self):
		self.assertEqual(checker.dead_stores(method("self.plotTypes = [] # reinit", "self.plotTypes = [0] * 4")), [])

	def test_name_in_comment_is_not_a_read(self):
		self.assertEqual(checker.dead_stores(method("self.X = 50", "self.Y = 1 # X stays", "self.X = 0")), [(3, 5, "X")])

	def test_repository_passes(self):
		self.assertEqual(checker.main([]), 0)


if __name__ == "__main__":
	unittest.main()
