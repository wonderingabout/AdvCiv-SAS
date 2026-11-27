# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

# <!-- custom: pathlib and sys put the checker folder on the import path; unittest runs the tests. (Claude code Opus 5.5) -->
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".github/workflows/build/documentation"))
# <!-- custom: disclaimers_first is the checker module under test, imported as checker. (Claude code Opus 5.5) -->
import disclaimers_first as checker


class DisclaimersFirstTests(unittest.TestCase):
	def test_disclaimer_under_title_passes(self):
		text = "# Guide\n\n> **Read me:** at your own risk.\n\nWhat this guide is.\n\n## Menu\n"
		self.assertEqual(checker.errors_for("guide.md", text, "Read me:"), [])

	def test_description_before_disclaimer_fails(self):
		text = "# Guide\n\nWhat this guide is.\n\n> **Read me:** at your own risk.\n"
		errors = checker.errors_for("guide.md", text, "Read me:")
		self.assertEqual(len(errors), 1)
		self.assertIn("What this guide is.", errors[0])

	def test_disclaimer_as_section_fails(self):
		text = "# Guide\n\n## Read me\n\nAt your own risk.\n"
		self.assertEqual(len(checker.errors_for("guide.md", text, "Read me:")), 1)

	def test_repository_guides_pass(self):
		self.assertEqual(checker.main(), 0)


if __name__ == "__main__":
	unittest.main()
