# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys make the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import custom_comment_closing as checker

OPEN = "<!-- custom:"


class CustomCommentClosingTests(unittest.TestCase):
	def test_closed_comments_pass(self):
		text = "# " + OPEN + " one line. (X) -->\nx = 1\n# " + OPEN + " first line\n# second line. (X) -->\ny = 2\n"
		self.assertEqual(list(checker.unclosed(text, True)), [])

	def test_comment_left_open_before_code_fails(self):
		text = "# " + OPEN + " never closed\nx = 1\n"
		self.assertEqual(list(checker.unclosed(text, True)), [(1, "not closed before code at line 2")])

	def test_comment_left_open_before_the_next_one_fails(self):
		# <!-- custom: The 2026-11-26 case: the next note's closing ended both, so they read as one block. (Claude code Opus 5.5) -->
		text = "# " + OPEN + " left open\n# " + OPEN + " next note. (X) -->\nx = 1\n"
		self.assertEqual(list(checker.unclosed(text, True)), [(1, "not closed before another custom comment opens at line 2")])

	def test_marker_inside_a_string_is_no_comment(self):
		text = "OPEN = \"" + OPEN + "\"\nx = 1\n"
		self.assertEqual(list(checker.unclosed(text, True)), [])

	def test_cpp_comments(self):
		text = "\t// " + OPEN + " open\n\tint i = 0;\n\tint j = 1; // " + OPEN + " trailing, closed. (X) -->\n"
		self.assertEqual(list(checker.unclosed(text, False)), [(1, "not closed before code at line 2")])

	def test_marker_in_a_triple_quoted_string_is_no_comment(self):
		# <!-- custom: Codex's review (GPT-6.2-Sol) reproduced the first version taking this for an open note. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
		text = 'DOC = """\n# ' + OPEN + ' example\n"""\nx = 1\n'
		self.assertEqual(list(checker.unclosed(text, True)), [])

	def test_note_left_open_in_a_block_comment_fails(self):
		text = "int i = 0; /* " + OPEN + " dangling */\nint j = 1;\n"
		self.assertEqual(list(checker.unclosed(text, False)), [(1, "not closed before its block comment ends at line 1")])

	def test_second_note_opened_on_the_same_line_fails(self):
		text = "# " + OPEN + " first " + OPEN + " second. (X) -->\nx = 1\n"
		self.assertEqual(list(checker.unclosed(text, True)), [(1, "not closed before another custom comment opens at line 1")])

	def test_open_at_the_end_of_the_file_fails(self):
		text = "x = 1\n# " + OPEN + " last line"
		self.assertEqual(list(checker.unclosed(text, True)), [(2, "not closed before the end of the file")])


if __name__ == "__main__":
	unittest.main()
