# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
# <!-- custom: importlib loads the check from its file, as in test_lint_suppressions.py. (Claude code Opus 5.5) -->
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
_SPEC = importlib.util.spec_from_file_location("sevopedia_top_attributes", ROOT / ".github/workflows/build/source/sevopedia_top_attributes.py")
assert _SPEC is not None and _SPEC.loader is not None
sevopedia_top_attributes = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sevopedia_top_attributes)

MAIN = "class SevoPediaMain:\n\tX_ITEMS = 10\n\tdef __init__(self):\n\t\tself.iCategory = 0\n\tdef placeItems(self):\n\t\tpass\n"


class SevopediaTopAttributeTests(unittest.TestCase):
	def failures(self, page):
		return sevopedia_top_attributes.check({"SevoPediaMain.py": MAIN, "SevoPediaPage.py": page})

	def test_removed_attribute_fails(self):
		# <!-- custom: The KI#1086 case: a color moved out of SevoPediaMain while a page still read it. (Claude code Opus 5.5) -->
		self.assertIn("self.top.COLOR_HIGHLIGHT_TEXT", self.failures("x = self.top.COLOR_HIGHLIGHT_TEXT\n")[0])

	def test_assigned_method_and_class_attributes_pass(self):
		self.assertEqual(self.failures("a = self.top.iCategory\nself.top.placeItems()\nb = self.top.X_ITEMS\n"), [])

	def test_attribute_assigned_by_a_page_passes(self):
		self.assertEqual(self.failures("self.top.activeRefresher = f\ng = self.top.activeRefresher\n"), [])

	def test_comment_is_ignored_but_string_hash_is_not_a_comment(self):
		self.assertEqual(self.failures("# Was self.top.COLOR_HIGHLIGHT_TEXT\ns = '#'  # self.top.GONE\n"), [])
		self.assertEqual(len(self.failures("s = '#'; y = self.top.GONE\n")), 1)

	def test_strings_and_escaped_quotes_are_not_code(self):
		# <!-- custom: Codex's review cases for the first, regex-based draft. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		self.assertEqual(self.failures("s = 'see self.top.Example'\n"), [])
		self.assertEqual(self.failures("s = 'it\\'s'  # self.top.GONE\n"), [])

	def test_comparison_is_a_read_not_an_assignment(self):
		self.assertEqual(len(self.failures("if self.top.GONE == 1:\n\tpass\n")), 1)


if __name__ == "__main__":
	unittest.main()
