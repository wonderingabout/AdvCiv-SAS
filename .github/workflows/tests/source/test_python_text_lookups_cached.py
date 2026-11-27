# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import python_text_lookups_cached as checker


class PythonTextLookupsCachedTests(unittest.TestCase):
	def test_lookup_in_loop_body_fails(self):
		text = 'def f(a):\n\tfor x in a:\n\t\tif x:\n\t\t\ts = localText.getText("TXT_KEY_X", ())\n'
		self.assertEqual(checker.loop_lookups(text), [(4, "TXT_KEY_X")])

	def test_lookup_in_while_body_fails(self):
		text = 'def f():\n\twhile g():\n\t\ts = localText.getText("TXT_KEY_X", ())\n'
		self.assertEqual(checker.loop_lookups(text), [(3, "TXT_KEY_X")])

	def test_lookup_outside_loop_and_in_for_header_pass(self):
		text = 'def f():\n\ts = localText.getText("TXT_KEY_X", ())\n\tfor x in [localText.getText("TXT_KEY_Y", ())]:\n\t\tpass\n'
		self.assertEqual(checker.loop_lookups(text), [])

	def test_lookup_with_arguments_passes(self):
		text = 'def f(a):\n\tfor x in a:\n\t\ts = localText.getText("TXT_KEY_X", (x,))\n'
		self.assertEqual(checker.loop_lookups(text), [])

	def test_def_inside_loop_passes(self):
		# <!-- custom: A loop around a def runs the def statement, not its body. (Claude code Opus 5.5) -->
		text = 'for x in a:\n\tdef f():\n\t\treturn localText.getText("TXT_KEY_X", ())\n'
		self.assertEqual(checker.loop_lookups(text), [])

	def test_one_line_loop_and_split_call_fail(self):
		text = 'def f(a):\n\tfor x in a: s = localText.getText("TXT_KEY_X", ())\n\tfor x in a:\n\t\ts = localText.getText(\n\t\t\t"TXT_KEY_Y", ())\n'
		self.assertEqual(checker.loop_lookups(text), [(2, "TXT_KEY_X"), (4, "TXT_KEY_Y")])

	def test_codex_false_hits_pass(self):
		# <!-- custom: Codex's review (GPT-6.2-Sol) reproduced both: a colon inside the iterable's brackets, and a one-line def inside a loop. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		text = 'def f():\n\tfor x in {1: localText.getText("TXT_KEY_X", ())}:\n\t\tpass\n\tfor x in a:\n\t\tdef g(): return localText.getText("TXT_KEY_Y", ())\n'
		self.assertEqual(checker.loop_lookups(text), [])

	def test_comment_and_other_strings_pass(self):
		text = 'def f(a):\n\tfor x in a:\n\t\t# localText.getText("TXT_KEY_X", ())\n\t\ts = screen.getText("Widget", ())\n'
		self.assertEqual(checker.loop_lookups(text), [])


if __name__ == "__main__":
	unittest.main()
