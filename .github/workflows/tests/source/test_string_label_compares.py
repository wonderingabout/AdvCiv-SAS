# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and tempfile hold a sample file, sys makes the checker importable and unittest checks it. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import tempfile
import unittest

# <!-- custom: Import the same source helper used by checks-source.yml. (Claude code Opus 5.5) -->
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "build" / "source"))
import string_label_compares as checker

NOTE = "\t# <!-- custom: %s why. (Claude code Opus 5.5) -->\n" % checker.NOTE


class StringLabelComparesTests(unittest.TestCase):
    def errors(self, text):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.py"
            path.write_text(text, encoding="utf-8")
            return checker.file_errors(path, "sample.py")

    def test_unnoted_comparison_fails_and_noted_one_passes(self):
        self.assertEqual(len(self.errors("\tif kind == \"btn\":\n\t\tpass\n")), 1)
        self.assertEqual(self.errors(NOTE + "\tif kind == \"btn\":\n\t\tpass\n"), [])

    def test_note_above_an_if_covers_its_elif_chain(self):
        text = NOTE + "\tif kind == \"a\":\n\t\tpass\n\telif kind == \"b\":\n\t\tpass\n\t# other\n\telif kind == \"c\":\n\t\tpass\n"
        self.assertEqual(self.errors(text), [])

    def test_a_new_if_starts_a_new_chain(self):
        text = NOTE + "\tif kind == \"a\":\n\t\tpass\n\tif kind == \"b\":\n\t\tpass\n\telif kind == \"c\":\n\t\tpass\n"
        self.assertEqual(len(self.errors(text)), 2)

    def test_comparisons_in_comments_are_ignored(self):
        self.assertEqual(self.errors("\tx = 1  # was kind == \"btn\"\n"), [])


if __name__ == "__main__":
    unittest.main()
